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
import json
import shutil
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


def estimate_uwham(reduced_potentials, sample_counts):
    """Pinned Python UWHAM core on the exact shared dimensionless states.

    Supplying explicit counts avoids the upstream dataframe path's one-based
    labels, leg reversal, kcal gas constant, and midpoint-identity assumption.
    Upstream ze is log Z; common free energies are -ze. W has mean one,
    so divide by the total count to obtain the MBAR normalization.
    """
    if importlib.metadata.version('atom-openmm') != '8.5.0b0':
        raise UnsupportedCapability('UWHAM requires pinned AToM 8.5.0b0')
    from atom_openmm.uwham import _obj_fcn, _uwham
    from scipy.optimize import minimize
    from ..schema import QualificationError
    potentials = np.asarray(reduced_potentials, dtype=float)
    # The pinned core exponentiates density ratios directly. Reject unsupported
    # range instead of clipping potentials, altering data or pretending support.
    state_zeros = potentials[:, 0].copy()
    canonical = potentials-state_zeros[:, None]
    ratios = canonical-canonical[0]
    if np.max(np.abs(ratios)) > 600.:
        raise QualificationError('pinned UWHAM density support exceeds admitted finite numerical range')
    counts = np.asarray(sample_counts, dtype=int)
    # The upstream entry point does not expose optimizer options. Refine its
    # exact pinned objective/gradient/Hessian independently of MBAR, then use
    # its entry point for weights and Fisher covariance at that stationary point.
    objective = lambda z: _obj_fcn(z, -ratios, counts, 0)
    fit = minimize(lambda z: objective(z)[0], np.zeros(len(counts)-1), method='trust-exact',
                   jac=lambda z: objective(z)[1], hess=lambda z: objective(z)[2],
                   options={'gtol': 1.e-12, 'maxiter': 1000})
    if not np.isfinite(fit.x).all() or np.max(np.abs(fit.jac)) > 1.e-6:
        raise QualificationError('independent pinned UWHAM objective did not converge')
    z = fit.x.copy()
    # Near a stationary point objective differences can round to zero before
    # its gradient does. Newton refinement uses the same independent exact
    # Hessian, rather than accepting SciPy's success flag as numerical evidence.
    for _ in range(8):
        _, grad, hessian = objective(z)
        if np.max(np.abs(grad)) <= 1.e-12:
            break
        try:
            z -= np.linalg.solve(hessian, grad)
        except np.linalg.LinAlgError as exc:
            raise QualificationError('pinned UWHAM Hessian has disconnected/insufficient support') from exc
    output = _uwham(logQ=-canonical.T, size=counts, base=0, init=np.r_[0., z], fisher=True)
    residual = float(np.max(np.abs(output['check']-1.)))
    gradient = float(np.max(np.abs(output['result'].jac)))
    if not np.isfinite(residual) or residual > 1.e-8 or not np.isfinite(gradient) or gradient > 1.e-10:
        raise QualificationError('pinned UWHAM optimizer failed normalization/stationarity checks')
    return dict(free_energies_dimensionless=-output['ze']+state_zeros-state_zeros[0], covariance_dimensionless=output['Ve'],
                normalized_weights=output['W']/potentials.shape[1], solver_residual=max(residual, gradient),
                optimizer_success=bool(fit.success), optimizer_message=str(fit.message))


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
    atoms = [(physical.real_to_final[a.atom_id],a) for a in physical.topology.atoms]
    atoms += [(link.final_particle_index,link) for link in physical.links]
    lookup, chains, residues = {}, {}, {}
    cap_residue = None
    for _,atom in sorted(atoms,key=lambda item:item[0]):
        if not hasattr(atom,'atom_id'):
            if cap_residue is None:
                cap_residue = topology.addResidue('CAP',topology.addChain('CAP'))
            topology.addAtom('Hcap',app.element.hydrogen,cap_residue,atom.cap_id)
            continue
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


def export_worker_run(run, directory, snapshot, state_id, *, thermodynamics=None, integrator_seed=41):
    """Immutable pinned PDB/System/State export with locally bundled source/assets."""
    from ..atm import save_bundle
    from ..persistence import write_json
    from ..schema import to_json
    if isinstance(integrator_seed,bool) or not isinstance(integrator_seed,int) or not 0 < integrator_seed < 2**31:
        raise MalformedInput('integrator_seed must be a positive bounded integer')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    run.evaluate(snapshot, state_id)
    state = run.evaluator.context.getState(getPositions=True, getVelocities=True,
                                           getParameters=True, getEnergy=True, getForces=True)
    system = run.bundle.system_xml
    (directory/'handover_sys.xml').write_text(system)
    (directory/'handover_0.xml').write_text(mm.XmlSerializer.serialize(state))
    topology = _topology(run.bundle.physical)
    if snapshot.box_nm is not None:
        topology.setPeriodicBoxVectors(tuple(mm.Vec3(*v)*unit.nanometer for v in snapshot.box_nm))
    with (directory/'handover.pdb').open('w') as handle:
        app.PDBFile.writeFile(topology, state.getPositions(), handle)
    save_bundle(directory/'bundle.json', run.bundle)
    (directory/'runtime.json').write_text(to_json(run.runtime)+'\n')
    (directory/'snapshot.json').write_text(to_json(snapshot)+'\n')
    if thermodynamics is not None:
        (directory/'thermodynamics.json').write_text(to_json(thermodynamics)+'\n')
    # Source/assets are copied without Python caches. Default MACE load recipes
    # resolve under this installation root in a relocated offline process.
    root = Path(__file__).resolve().parents[3]
    for path in sorted((root/'src/atm_mlmm').rglob('*.py')):
        target = directory/'runtime/source'/path.relative_to(root/'src')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    for name in ('core-conda-linux-64.lock','core-pip-inventory.txt','upstream-sources.json','package-identities.json'):
        target = directory/'runtime/environment'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root/'environment/cloud-cpu'/name, target)
    if run.bundle.physical.manifest.get('fixture_kind') == 'pinned_mace_candidate':
        from ..models.mace import ASSET, verify_asset
        verify_asset()
        target = directory/'runtime/models/mace-off23-small'
        target.mkdir(parents=True)
        for name in ('MACE-OFF23_small.model','manifest.json','LICENSE.md'):
            shutil.copyfile(ASSET/name, target/name)
    parameters = dict(run.evaluator.context.getParameters())
    manifest = dict(version=1, basename='handover', state_id=state_id, integrator_seed=integrator_seed,
                    physical_identity=run.bundle.physical.content_identity,
                    alchemical_identity=run.bundle.content_identity,
                    runtime_identity=run.runtime.content_identity,
                    real_atom_ids=list(snapshot.real_atom_ids), parameters=parameters,
                    preliminary_pdb_coordinates='generated from current finite full-particle State',
                    source_identity='sha256 of exact bundled source files',
                    files={str(p.relative_to(directory)):hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(directory.rglob('*')) if p.is_file()})
    write_json(directory/'manifest.json', manifest)
    path = directory/'manifest.json'
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def load_worker_run(directory, expected_manifest_sha256, *, trusted=False, integrator_seed=None):
    """Validate the whole bundle before the actual pinned worker constructor."""
    from ..atm import load_bundle
    from ..schema import from_json
    if trusted is not True:
        raise UnsupportedCapability('worker System/PythonForce artifacts require explicitly trusted loading')
    directory = Path(directory).resolve()
    payload = (directory/'manifest.json').read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected_manifest_sha256:
        raise IdentityError('worker manifest digest mismatch before loading')
    manifest = json.loads(payload)
    if manifest.get('version') != 1 or manifest.get('basename') != 'handover':
        raise UnsupportedCapability('unsupported worker export contract')
    for name, digest in manifest['files'].items():
        path = (directory/name).resolve()
        if directory not in path.parents or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise IdentityError(f'worker file identity mismatch: {name}')
    required = {'bundle.json','runtime.json','snapshot.json','handover.pdb','handover_sys.xml','handover_0.xml'}
    if not required <= set(manifest['files']):
        raise IdentityError('worker files do not cover the complete pinned contract')
    bundle = load_bundle(directory/'bundle.json', manifest['files']['bundle.json'], trusted=True)
    runtime = from_json((directory/'runtime.json').read_text())
    if bundle.content_identity != manifest['alchemical_identity'] or runtime.content_identity != manifest['runtime_identity']:
        raise IdentityError('worker bundle/runtime identity mismatch')
    if (directory/'handover_sys.xml').read_text() != bundle.system_xml:
        raise IdentityError('worker executable System differs from sealed bundle')
    state_payload = (directory/'handover_0.xml').read_bytes()
    if ET.fromstring(state_payload).tag != 'State':
        raise IdentityError('worker initial artifact must be a portable State')
    state = mm.XmlSerializer.deserialize(state_payload.decode())
    initial = schedule_state(bundle.schedule,manifest['state_id'])
    parameters = dict(state.getParameters())
    if parameters != manifest['parameters'] or any(parameters.get(k) != v for k,v in initial.parameters.items()):
        raise IdentityError('saved worker State parameters differ from declared state')
    positions = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    if positions.shape != (len(bundle.physical.masses_da),3) or not np.isfinite(positions).all():
        raise IdentityError('worker State positions must cover every finite particle')
    if bundle.physical.content_identity != manifest['physical_identity'] or tuple(manifest['real_atom_ids']) != tuple(a.atom_id for a in bundle.physical.topology.atoms):
        raise IdentityError('worker physical/ordered atom identity mismatch')
    if runtime.platform != 'Reference':
        raise UnsupportedCapability('real worker handover initially admits Reference double only')
    seed = manifest['integrator_seed'] if integrator_seed is None else integrator_seed
    if isinstance(seed,bool) or not isinstance(seed,int) or not 0 < seed < 2**31:
        raise MalformedInput('worker integrator_seed must be a positive bounded integer')
    return WorkerRun(directory, manifest, bundle, runtime, seed)


class WorkerRun:
    """Actual OMMWorkerATMSync constructor, sharing sealed observable extraction."""
    def __init__(self, directory, manifest, bundle, runtime, seed):
        if importlib.metadata.version('atom-openmm') != '8.5.0b0':
            raise UnsupportedCapability('worker handover requires pinned AToM 8.5.0b0')
        from atom_openmm.ommsystem import OMMSystemABFE
        from atom_openmm.ommworker import OMMWorkerATMSync
        from atom_openmm.utils.AtomUtils import AtomUtils
        keywords = atom_keywords(bundle.physical,bundle.transfer,bundle.schedule,runtime)
        keywords['PRNT_FREQUENCY'] = 1
        initial = schedule_state(bundle.schedule,manifest['state_id'])

        class SealedSystem(OMMSystemABFE):
            def create_system(self):
                self.load_system()
                if mm.XmlSerializer.serialize(self.system) != bundle.system_xml:
                    raise IdentityError('actual worker System differs from sealed export')
                # Avoid the stock zero-LJ repair and duplicate ATM/restraint/
                # barostat assembly; the project already owns the complete System.
                self.atm_utils = AtomUtils(self.system, fix_zero_LJparams=False)
                self.atmforce = next(f for f in self.system.getForces() if isinstance(f,mm.ATMForce))
                self.atmforcegroup = self.atmforce.getForceGroup()
                self.cparams = {**initial.parameters, self.parameter['temperature']:runtime.temperature_K}
                self.set_integrator(runtime.temperature_K*unit.kelvin,self.frictionCoeff,self.MDstepsize)
                self.integrator.setRandomNumberSeed(seed)

        basename = str(directory/'handover')
        upstream = SealedSystem(basename,keywords,str(directory/'handover.pdb'),str(directory/'handover_sys.xml'),logging.getLogger('atm_mlmm.worker'))
        self.worker = OMMWorkerATMSync(basename,upstream,keywords,compute=True,logger=logging.getLogger('atm_mlmm.worker'))
        self.bundle,self.runtime,self.manifest,self.upstream = bundle,runtime,manifest,upstream
        self.integrator_seed = seed
        self.evaluator = AtmEvaluator(bundle,runtime,system=self.worker.system,
                                      integrator=self.worker.integrator,external_context=self.worker.context)
        self.set_state(manifest['state_id'])

    def set_state(self, state_id):
        self.evaluator.set_state(state_id,setter=lambda p:self.worker.set_state(AtomRun._worker_parameters(self,p)))

    def evaluate(self, snapshot, state_id):
        self.set_state(state_id)
        result = self.evaluator.evaluate(snapshot,state_id)
        # Actual upstream reporting must be fresh on this same Context.
        upstream = self.worker.get_energy()
        if not math.isclose(upstream['potential_energy'].value_in_unit(unit.kilojoules_per_mole),
                            result.total.energy_kj_mol,rel_tol=0.,abs_tol=1.e-8):
            raise IdentityError('actual worker reported stale/different potential energy')
        return result

    def restore_checkpoint(self, payload, state_id):
        """Same-profile continuation; admit the saved parameters before reporting."""
        self.evaluator._guard()
        requested = schedule_state(self.bundle.schedule,state_id)
        self.evaluator.context.loadCheckpoint(payload)
        actual = self.evaluator.context.getParameters()
        if any(actual[name] != value for name,value in requested.parameters.items()):
            raise IdentityError('checkpoint parameters disagree with recorded state identity')
        self.evaluator._state_id = state_id
        self.evaluator._expected_parameters = dict(requested.parameters)
        self.evaluator._guard()
        self.worker.par = AtomRun._worker_parameters(self,requested.parameters)

    def restore_portable_state(self, payload, state_id):
        """Restore portable observables without promising random-number continuity."""
        if ET.fromstring(payload).tag != 'State':
            raise IdentityError('portable artifact must be a State')
        self.evaluator.restore_state(mm.XmlSerializer.deserialize(payload),state_id)
        self.set_state(state_id)

    def close(self):
        self.evaluator.close()
        self.worker.context = self.worker.simulation = self.worker.integrator = self.worker.system = None
        self.upstream.integrator = self.upstream.system = None

    def __enter__(self):
        return self

    def __exit__(self,*args):
        self.close()
