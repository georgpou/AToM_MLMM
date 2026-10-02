"""Narrow adapter for pinned AToM 8.5.0b0 construction/state primitives.

Use upstream protocol constructors, explicit group routing, integrator creation
and worker state translation. Do not duplicate scheduling/replica exchange.
The analytic route does not invoke stock file preparation or periodic barostats;
those molecular workflows require their later gates.
"""
import hashlib
import importlib.metadata
import logging
import math
from numbers import Real
from pathlib import Path
from types import SimpleNamespace
import xml.etree.ElementTree as ET

import numpy as np
import openmm as mm
from openmm import app, unit

from ..atm import (AtmEvaluator, outside_force, seal_alchemical,
                   validate_physical_parameter_ownership, validate_runtime)
from ..geometry import validate_transfer
from ..routing import export_physical
from ..schedule import schedule_state, validate_schedule
from ..schema import IdentityError, MalformedInput, UnsupportedCapability


def timestep_fs_to_ps(timestep_fs):
    """User-facing fs input enters the common ps convention once."""
    if isinstance(timestep_fs, bool) or not isinstance(timestep_fs, Real) or not math.isfinite(timestep_fs) or timestep_fs <= 0:
        raise MalformedInput('timestep_fs must be a positive finite number')
    return float(timestep_fs)*.001


def atom_keywords(physical, transfer, schedule, runtime, *, reserved_group=1):
    validate_runtime(runtime)
    validate_transfer(physical, transfer)
    validate_schedule(schedule)
    if schedule.kind != 'softplus' or runtime.integrator != 'LangevinMiddle':
        raise UnsupportedCapability('AToM production requires the admitted softplus expression and LangevinMiddle')
    p = schedule.states[0].parameters
    displacement = transfer.protocol.geometry_requests['displacement_nm']
    # Upstream displacement is Angstrom, timestep is already ps, and its
    # soft-core configuration energies are kcal/mol. Convert exactly once.
    keywords = dict(VARIABLE_FORCE_GROUP=reserved_group, TIME_STEP=runtime.timestep_ps,
                    FRICTION_COEFF=1., INTEGRATOR='langevinmiddle',
                    DISPLACEMENT=[10.*x for x in displacement], UMAX=p['Umax']/4.184,
                    UBCORE=p['Ubcore']/4.184, ACORE=p['Acore'], PERTE_OFFSET=p['UOffset']/4.184)
    groups = [[physical.real_to_final[a] for a in group.atom_ids] for group in transfer.protocol.mobile_groups]
    if transfer.protocol.kind == 'abfe':
        keywords['LIGAND_ATOMS'] = groups[0]
    else:
        keywords['LIGAND1_ATOMS'], keywords['LIGAND2_ATOMS'] = groups
    return keywords


def _topology(physical):
    topology = app.Topology()
    atoms = sorted(physical.topology.atoms, key=lambda a: physical.real_to_final[a.atom_id])
    lookup, chains, residues = {}, {}, {}
    for atom in atoms:
        if atom.chain not in chains:
            chains[atom.chain] = topology.addChain(atom.chain)
        key = atom.chain, atom.residue, atom.insertion_code
        if key not in residues:
            residues[key] = topology.addResidue('ANA', chains[atom.chain], atom.residue, atom.insertion_code)
        lookup[atom.atom_id] = topology.addAtom(atom.atom_name, app.Element.getBySymbol(atom.element), residues[key], atom.atom_id)
    for bond in physical.topology.bonds:
        topology.addBond(lookup[bond.atom1], lookup[bond.atom2])
    return topology


def _check_and_normalize_conversion(atm_force, transfer):
    if atm_force.getNumParticles() != transfer.final_particle_count:
        raise IdentityError('upstream full-particle map count mismatch')
    for i, (map0, map1) in enumerate(zip(transfer.displacement0_nm, transfer.displacement1_nm)):
        actual1, actual0 = atm_force.getParticleParameters(i)
        for actual, expected in ((actual0, map0), (actual1, map1)):
            values = np.asarray(actual.value_in_unit(unit.nanometer))
            expected = np.asarray(expected)
            # Verify upstream selection/signs first. Only floating-point unit
            # roundoff is canonicalized; final stored maps are exactly equal.
            rounding = 4*np.finfo(float).eps*np.maximum(np.abs(expected), np.finfo(float).tiny)
            if not np.isfinite(values).all() or np.any(np.abs(values-expected) > rounding):
                raise IdentityError(f'upstream fixed map/unit conversion differs at particle {i}')
        atm_force.setParticleParameters(i, mm.Vec3(*map1), mm.Vec3(*map0))


class AtomRun:
    def __init__(self, upstream, bundle, runtime, keywords):
        from atom_openmm.ommworker import OMMWorkerATM
        self.upstream, self.bundle, self.runtime, self.keywords = upstream, bundle, runtime, keywords
        self.evaluator = AtmEvaluator(bundle, runtime, system=upstream.system, integrator=upstream.integrator)
        # Exercise the actual upstream worker's state method on this context,
        # without launching unqualified asynchronous/molecular workflows.
        self.worker = OMMWorkerATM.__new__(OMMWorkerATM)
        self.worker.ommsystem = upstream
        self.worker.integrator = self.evaluator.integrator
        self.worker.context = self.evaluator.context
        self.worker.simulation = SimpleNamespace(context=self.evaluator.context)
        self.set_state(bundle.schedule.states[0].state_id)

    def _worker_parameters(self, parameters):
        p = parameters
        return dict(temperature=self.runtime.temperature_K*unit.kelvin,
                    lambda1=p['Lambda1'], lambda2=p['Lambda2'], alpha=p['Alpha']/unit.kilojoules_per_mole,
                    uh=p['Uh']*unit.kilojoules_per_mole, w0=p['W0']*unit.kilojoules_per_mole,
                    atmdirection=p['Direction'], Umax=p['Umax']*unit.kilojoules_per_mole,
                    Ubcore=p['Ubcore']*unit.kilojoules_per_mole, Acore=p['Acore'],
                    uoffset=p['UOffset']*unit.kilojoules_per_mole)

    def set_state(self, state_id):
        self.evaluator.set_state(state_id, setter=lambda p: self.worker._worker_setstate(self._worker_parameters(p)))

    def evaluate(self, snapshot, state_id):
        self.set_state(state_id)
        return self.evaluator.evaluate(snapshot, state_id)

    def save_initial_state(self, directory, snapshot, state_id):
        self.evaluate(snapshot, state_id)
        state = self.evaluator.context.getState(getPositions=True, getVelocities=True, getParameters=True)
        path = Path(directory)/(self.upstream.basename+'_0.xml')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(mm.XmlSerializer.serialize(state))
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    def load_initial_state(self, path, expected_sha256, state_id):
        payload = Path(path).read_bytes()
        if hashlib.sha256(payload).hexdigest() != expected_sha256:
            raise IdentityError('initial State digest mismatch before loading')
        if ET.fromstring(payload).tag != 'State':
            raise IdentityError('handover artifact must be a portable State, not an executable System')
        self.evaluator.restore_state(mm.XmlSerializer.deserialize(payload.decode()), state_id)
        self.set_state(state_id)

    def close(self):
        self.evaluator.close()
        self.worker.context = None
        self.worker.simulation = None
        self.worker.integrator = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def build_atom(physical, transfer, schedule, restraints, runtime, *, reserved_group=1):
    if importlib.metadata.version('atom-openmm') != '8.5.0b0':
        raise UnsupportedCapability('AToM adapter requires pinned distribution 8.5.0b0/source v8.5.0')
    from atom_openmm.ommsystem import OMMSystemABFE, OMMSystemRBFE
    keywords = atom_keywords(physical, transfer, schedule, runtime, reserved_group=reserved_group)
    export = export_physical(physical, reserved_group=reserved_group)
    export.check()
    validate_physical_parameter_ownership(export.system, schedule)
    cls = OMMSystemABFE if transfer.protocol.kind == 'abfe' else OMMSystemRBFE
    upstream = cls('analytic', keywords, None, None, logging.getLogger('atm_mlmm.atom'))
    upstream.system = export.system
    upstream.system.addForce(outside_force(physical, restraints))
    upstream.topology = _topology(physical)
    upstream.set_ligand_atoms()
    upstream.set_displacement()
    upstream.set_atmforce()
    _check_and_normalize_conversion(upstream.atmforce, transfer)
    # Upstream worker metadata is a global parameter, not an additional energy.
    upstream.atmforce.addGlobalParameter(upstream.parameter['temperature'], runtime.temperature_K)
    upstream.set_integrator(runtime.temperature_K*unit.kelvin, upstream.frictionCoeff, upstream.MDstepsize)
    bundle = seal_alchemical(upstream.system, physical, transfer, schedule, restraints, construction='atom-8.5.0b0')
    return AtomRun(upstream, bundle, runtime, keywords)
