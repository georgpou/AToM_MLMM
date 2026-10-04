#!/usr/bin/env python
"""Freeze a tiny neutral host–guest input without model/quantum score selection."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import openmm as mm
from openmm import unit
from rdkit import Chem, rdBase
from rdkit.Chem import AllChem, rdMolDescriptors

from atm_mlmm.schema import (AtomIdentity, Bond, ComponentState, MoleculeState,
                            PartitionSpec, Snapshot, SystemInput, TopologyView, to_json)


def molecule(smiles, seed):
    result = Chem.AddHs(Chem.MolFromSmiles(smiles))
    parameters = AllChem.ETKDGv3()
    parameters.randomSeed = seed
    parameters.numThreads = 1
    if AllChem.EmbedMolecule(result, parameters) != 0:
        raise RuntimeError('deterministic molecular embedding failed')
    converged = AllChem.MMFFOptimizeMolecule(result, maxIters=2000)
    if converged != 0:
        raise RuntimeError('bounded classical geometry optimization did not converge')
    return result, np.array(result.GetConformer().GetPositions())/10.


def prepare(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    host, hx = molecule('O1CCOCCOCCOCCOCCOCC1', 61709)
    guest, gx = molecule('CO', 61710)
    oxygen = [a.GetIdx() for a in host.GetAtoms() if a.GetSymbol() == 'O']
    hx -= hx[oxygen].mean(axis=0)
    _, _, basis = np.linalg.svd(hx[oxygen], full_matrices=False)
    normal = basis[-1]
    if normal[2] < 0:
        normal = -normal
    first = hx[oxygen[0]]
    axis = first-np.dot(first, normal)*normal
    axis /= np.linalg.norm(axis)
    rotation = np.array((axis, np.cross(normal, axis), normal))
    hx = hx@rotation.T
    # Put an alcohol O-H donor above one crown oxygen. This geometric rule is
    # fixed before MACE evaluation; it is an engine probe, not a docking score.
    go = next(a.GetIdx() for a in guest.GetAtoms() if a.GetSymbol() == 'O')
    gh = next(a.GetIdx() for a in guest.GetAtomWithIdx(go).GetNeighbors() if a.GetSymbol() == 'H')
    direction = gx[gh]-gx[go]
    direction /= np.linalg.norm(direction)
    helper = np.array((1.,0.,0.)) if abs(direction[0]) < .9 else np.array((0.,1.,0.))
    side = helper-direction*np.dot(helper,direction)
    side /= np.linalg.norm(side)
    guest_basis = np.array((side,np.cross(direction,side),direction))
    gx = (gx-gx[go])@guest_basis.T
    gx[:,1:] *= -1
    gx += hx[oxygen[0]]+np.array((0.,0.,.30))
    atoms, bonds, molecules, positions, components = [], [], [], [], []
    for mol, x, prefix, name, role, chain in (
            (host,hx,'h','18-crown-6','host','H'), (guest,gx,'g','methanol','ligand','G')):
        ids = tuple(f'{prefix}{i:03d}' for i in range(mol.GetNumAtoms()))
        atoms.extend(AtomIdentity(a,atom.GetSymbol(),chain,'1','',a) for a,atom in zip(ids,mol.GetAtoms()))
        bonds.extend(Bond(ids[b.GetBeginAtomIdx()],ids[b.GetEndAtomIdx()],b.GetBondTypeAsDouble()) for b in mol.GetBonds())
        molecules.append(MoleculeState(name,ids,role,0,1))
        positions.extend(x)
        components.append(ComponentState(ids,0,1))
    topology = TopologyView(tuple(atoms),tuple(bonds),tuple(molecules))
    system = mm.System()
    nonbonded = mm.NonbondedForce()
    for atom in atoms:
        system.addParticle(Chem.GetPeriodicTable().GetAtomicWeight(atom.element))
        nonbonded.addParticle(0.,.3,0.)
    nonbonded.setName('inert original MM ledger for complete all-ML vacuum')
    system.addForce(nonbonded)
    xml = mm.XmlSerializer.serialize(system)
    provenance = {'physical_scope':'all-ML vacuum; original MM is explicitly inert',
                  'geometry':'ETKDGv3/MMFF94s, seeds61709/61710; fixed O-H donor placement',
                  'selection':'no model, quantum, experimental or docking score used',
                  'source_smiles':{'host':'O1CCOCCOCCOCCOCCOCC1','guest':'CO'}}
    original = SystemInput(xml,hashlib.sha256(xml.encode()).hexdigest(),topology,tuple(positions),None,
        tuple(system.getParticleMass(i).value_in_unit(unit.dalton) for i in range(system.getNumParticles())),(),provenance)
    ids = tuple(a.atom_id for a in atoms)
    records = {'system-input.json':original,'partition.json':PartitionSpec(ids,(),(),tuple(components)),
               'snapshot.json':Snapshot(ids,tuple(positions),None)}
    for name,record in records.items():
        (directory/name).write_text(to_json(record)+'\n')
    manifest = {'name':'18-crown-6 + methanol','version':1,'real_atoms':48,
                'host_formula':rdMolDescriptors.CalcMolFormula(host),'guest_formula':rdMolDescriptors.CalcMolFormula(guest),
                'physical_scope':'all-ML vacuum; no MM or binding-accuracy qualification',
                'chemistry':'two complete neutral singlets; H/C/O; no stereocenters, cuts, solvent, ions or metals',
                'preparation':{'rdkit':rdBase.rdkitVersion,'openmm':mm.version.version,**provenance},
                'files':{name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in records}}
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.output),indent=2))
