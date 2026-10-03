"""Freeze G07's actual GAFF/AM1-BCC artifacts, without model or DFT scores.

Run after locked CPU activation. Writes a new directory only; molecular
coordinates come from the approved M00 v3 records and are never optimized here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np


def write(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:
        stream.write(data if isinstance(data,str) else json.dumps(data,indent=2,allow_nan=False)+'\n')


def molecule_from_record(record):
    from rdkit import Chem
    from openff.toolkit import Molecule
    graph = Chem.RWMol()
    for z in record['atomic_numbers']: graph.AddAtom(Chem.Atom(z))
    types = {1.:Chem.BondType.SINGLE,2.:Chem.BondType.DOUBLE,3.:Chem.BondType.TRIPLE}
    for i,j,order in record['bonds']: graph.AddBond(i,j,types[order])
    molecule = graph.GetMol(); Chem.SanitizeMol(molecule)
    conformer = Chem.Conformer(len(record['atomic_numbers']))
    for i,position in enumerate(record['positions_angstrom']): conformer.SetAtomPosition(i,position)
    molecule.AddConformer(conformer)
    Chem.AssignAtomChiralTagsFromStructure(molecule)
    Chem.AssignStereochemistry(molecule,cleanIt=True,force=True)
    actual = Chem.FindMolChiralCenters(molecule,includeUnassigned=True)
    if [list(c) for c in actual] != record.get('stereocenters',[]):
        raise ValueError(f'frozen stereochemistry mismatch: {actual} vs {record.get("stereocenters")}')
    result = Molecule.from_rdkit(molecule,hydrogens_are_explicit=True,allow_undefined_stereo=False)
    if [a.atomic_number for a in result.atoms] != record['atomic_numbers']:
        raise ValueError('OpenFF changed frozen atom order')
    np.testing.assert_allclose(result.conformers[0].m_as('angstrom'),record['positions_angstrom'],atol=1e-12,rtol=0)
    for atom, name in zip(result.atoms,record['atom_ids']): atom.name = name
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists(): raise FileExistsError('never overwrite a frozen preparation attempt')
    args.output.mkdir(parents=True)
    root = Path(__file__).resolve().parents[1]
    structures = root/'fixtures/chemical_reference_v3/structures'
    source_rows = {family:json.loads((structures/(family+'-methanol-d3'+('.8' if family=='butane' else '')+'-r0.json')).read_text())
                   for family in ('ethanol','butane')}
    records = {family:row['g07_controls']['parent'] for family,row in source_rows.items()}
    records.update({name:json.loads((structures/(baseline+'.json')).read_text())
                    for name,baseline in (('methanol','methanol-baseline'),('acetamide','acetamide-0'))})
    from openff.toolkit import Topology
    from openff.toolkit.utils import AmberToolsToolkitWrapper
    from openmmforcefields.generators import GAFFTemplateGenerator
    from openmm import app,unit,XmlSerializer,NonbondedForce
    from openff.units import unit as offunit
    molecules = {}
    for name,record in records.items():
        print('Preparing actual AM1-BCC/GAFF parameters:',name,flush=True)
        molecule = molecule_from_record(record)
        molecule.assign_partial_charges('am1bcc',toolkit_registry=AmberToolsToolkitWrapper(),
            use_conformers=[molecule.conformers[0]],normalize_partial_charges=True)
        molecules[name] = molecule
        write(args.output/(name+'-molecule.json'),dict(source=record,
            partial_charges_e=molecule.partial_charges.m_as(offunit.elementary_charge).tolist(),
            charge_method='AM1-BCC via locked AmberTools26; exact frozen conformer; normalized formal charge 0',
            formal_charge=0,multiplicity=1))
    generator = GAFFTemplateGenerator(molecules=list(molecules.values()),forcefield='gaff-2.2.20',
                                      cache=str(args.output/'gaff-cache.json'))
    for family in ('ethanol','butane'):
        for ligand_names in (('methanol',),('acetamide',),('methanol','acetamide')):
            names = (family,)+ligand_names
            topology = Topology.from_molecules([molecules[name] for name in names]).to_openmm()
            forcefield = app.ForceField()
            forcefield.registerTemplateGenerator(generator.generator)
            system = forcefield.createSystem(topology,nonbondedMethod=app.NoCutoff,
                                             constraints=None,rigidWater=False,removeCMMotion=False)
            for f in system.getForces():
                if isinstance(f,NonbondedForce): f.setUseDispersionCorrection(False)
            xml = XmlSerializer.serialize(system)
            key = '-'.join(names)
            write(args.output/(key+'.xml'),xml)
            nb = next(f for f in system.getForces() if isinstance(f,NonbondedForce))
            write(args.output/(key+'-parameters.json'),dict(names=names,
                real_atom_names=[a.name for a in topology.atoms()],
                charges_e=[nb.getParticleParameters(i)[0].value_in_unit(unit.elementary_charge) for i in range(system.getNumParticles())],
                xml_sha256=hashlib.sha256(xml.encode()).hexdigest(),
                forcefield='GAFF 2.2.20 / actual AM1-BCC on complete neutral molecules',
                no_model_or_quantum_score_used=True))
    from atm_mlmm.joint_reference import quantum_job_matrix
    matrix = quantum_job_matrix(root/'fixtures/chemical_reference_v3')
    write(args.output/'quantum-job-matrix.json',matrix)
    manifest = dict(state='prepared; G07 quantum launch budget/review pending',
        source_input_manifest_sha256=matrix['source_manifest_sha256'],
        files={str(p.relative_to(args.output)):hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(args.output.iterdir()) if p.is_file()},
        software=dict(gaff='2.2.20',ambertools='26.0',openmm='8.6.1',openff_toolkit='0.18.0'),
        geometry='unchanged approved M00 v3, corrected score-free threonine orientation')
    write(args.output/'manifest.json',manifest)
    print('Frozen preparation:',args.output,flush=True)


if __name__ == '__main__': main()
