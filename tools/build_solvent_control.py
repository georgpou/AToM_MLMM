"""Freeze a small explicit-water PME control from the admitted solute inputs.

Run with the unchanged locked CPU environment and PYTHONPATH=src. The eight
waters are a sparse coupling diagnostic, not an equilibrated liquid box.
"""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import openmm as mm
from openmm import app, unit

from atm_mlmm.schema import AtomIdentity, Bond, MoleculeState, Snapshot, TopologyView, from_json, to_json

ROOT = Path(__file__).resolve().parents[1]
BOX = ((6.4, 0., 0.), (0., 6.4, 0.), (0., 0., 6.4))


def build(kind, output):
    source = ROOT / 'fixtures/cloud_fragment_controls/v1' / kind
    original = from_json((source / 'system-input.json').read_text())
    partition = from_json((source / 'partition.json').read_text())
    system = mm.XmlSerializer.deserialize(original.prepared_mm_artifact)
    nb = next(f for f in system.getForces() if isinstance(f, mm.NonbondedForce))
    # Preserve every solute particle/exception and bonded force. This is the
    # already admitted G06 periodic ledger convention, with a fixed mesh.
    system.setDefaultPeriodicBoxVectors(*BOX)
    nb.setNonbondedMethod(mm.NonbondedForce.PME)
    nb.setCutoffDistance(.9)
    nb.setUseSwitchingFunction(True)
    nb.setSwitchingDistance(.75)
    nb.setUseDispersionCorrection(False)
    nb.setEwaldErrorTolerance(1e-7)
    nb.setPMEParameters(4.4, 64, 64, 64)
    atoms, bonds, molecules = list(original.topology.atoms), list(original.topology.bonds), list(original.topology.molecules)
    positions, constraints = list(original.positions_nm), list(original.constraints)
    water_topology = app.Topology()
    chain = water_topology.addChain()
    oxygen = np.array(original.positions_nm[26])
    geometry = np.array(((0., 0., 0.), (.09572, 0., 0.),
                         (.09572*np.cos(np.deg2rad(104.52)), .09572*np.sin(np.deg2rad(104.52)), 0.)))
    for site in (oxygen, oxygen + (2.4, 0., 0.)):
        for direction in ((0., .65, 0.), (0., -.65, 0.), (0., 0., .65), (0., 0., -.95)):
            number = len(molecules) - len(original.topology.molecules)
            ids = tuple(f'water-{number}:{name}' for name in ('O', 'H1', 'H2'))
            residue = water_topology.addResidue('HOH', chain)
            water_atoms = [water_topology.addAtom(name, app.Element.getBySymbol(element), residue)
                           for name, element in (('O', 'O'), ('H1', 'H'), ('H2', 'H'))]
            for h in water_atoms[1:]:
                water_topology.addBond(water_atoms[0], h)
            atoms.extend(AtomIdentity(atom, element, 'W', str(number+1), '', name)
                         for atom, element, name in zip(ids, ('O', 'H', 'H'), ('O', 'H1', 'H2')))
            bonds.extend(Bond(ids[0], h) for h in ids[1:])
            molecules.append(MoleculeState(f'water-{number}', ids, 'solvent', 0, 1))
            positions.extend(map(tuple, site + np.array(direction) + geometry))
    water = app.ForceField('tip3p.xml').createSystem(water_topology, nonbondedMethod=app.NoCutoff,
                                                   rigidWater=True, removeCMMotion=False)
    water_nb = next(f for f in water.getForces() if isinstance(f, mm.NonbondedForce))
    # Rigid water has only intrawater constraints and zero bonded-force terms.
    for force in water.getForces():
        if isinstance(force, mm.HarmonicBondForce):
            assert force.getNumBonds() == 0
        elif isinstance(force, mm.HarmonicAngleForce):
            assert force.getNumAngles() == 0
        else:
            assert isinstance(force, mm.NonbondedForce)
    offset = system.getNumParticles()
    for i in range(water.getNumParticles()):
        system.addParticle(water.getParticleMass(i))
        nb.addParticle(*water_nb.getParticleParameters(i))
    for i in range(water_nb.getNumExceptions()):
        a, b, q, sigma, epsilon = water_nb.getExceptionParameters(i)
        nb.addException(offset+a, offset+b, q, sigma, epsilon)
    for i in range(water.getNumConstraints()):
        a, b, distance = water.getConstraintParameters(i)
        system.addConstraint(offset+a, offset+b, distance)
        constraints.append((atoms[offset+a].atom_id, atoms[offset+b].atom_id,
                            distance.value_in_unit(unit.nanometer)))
    xml = mm.XmlSerializer.serialize(system)
    ff = Path(app.__file__).parent / 'data/tip3p.xml'
    provenance = {**original.force_field_provenance,
                  'solvent': 'OpenMM rigid TIP3P; eight sparse explicit-water controls',
                  'tip3p_xml_sha256': hashlib.sha256(ff.read_bytes()).hexdigest(),
                  'solute_input_identity': original.content_identity,
                  'periodic_convention': 'orthorhombic-pme-v1',
                  'density_equilibration': 'not performed; no liquid-density qualification'}
    solvated = replace(original, prepared_mm_artifact=xml, prepared_mm_sha256=hashlib.sha256(xml.encode()).hexdigest(),
                       topology=TopologyView(tuple(atoms), tuple(bonds), tuple(molecules)), positions_nm=positions,
                       box_nm=BOX, constraints=constraints, force_field_provenance=provenance,
                       masses_da=tuple(system.getParticleMass(i).value_in_unit(unit.dalton) for i in range(system.getNumParticles())))
    snapshot = Snapshot(tuple(a.atom_id for a in atoms), positions, BOX)
    from atm_mlmm.workflow import _domain
    _domain(solvated.topology, snapshot, (2.4, 0., 0.), kind, partition.permitted_cuts)
    output.mkdir(parents=True, exist_ok=False)
    files = {}
    for name, record in (('system-input.json', solvated), ('partition.json', partition), ('snapshot.json', snapshot)):
        payload = (to_json(record)+'\n').encode()
        (output / name).write_bytes(payload)
        files[name] = hashlib.sha256(payload).hexdigest()
    manifest = output / 'manifest.json'
    manifest.write_text(json.dumps({'files': files, 'physical_scope': 'sparse explicit TIP3P PME coupling control; no density/equilibrium qualification',
                                    'source_files': {name: hashlib.sha256((source/name).read_bytes()).hexdigest() for name in files}}, indent=2)+'\n')
    config = json.loads((source / 'config.json').read_text())
    config.update(input_manifest='manifest.json', input_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest())
    (output / 'config.json').write_text(json.dumps(config, indent=2)+'\n')


if __name__ == '__main__':
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'fixtures/solvated_fragment/v1'
    for protocol in ('abfe', 'rbfe'):
        build(protocol, destination / protocol)
