"""Prepare the M00 proposal without importing/evaluating any learned model.

Run in the locked core environment; all output is full-precision frozen JSON.
No quantum results or scores enter preparation, ordering or selection.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from rdkit import Chem, rdBase
from rdkit.Chem import AllChem, rdMolTransforms

ROOT = Path(__file__).resolve().parents[1] / 'fixtures/chemical_reference'
SEED = 61705
CAP_ANGSTROM = 1.09


def write(name, data):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError('Frozen inputs must never be overwritten: ' + str(path))
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def prepare(smiles):
    molecule = Chem.AddHs(Chem.MolFromSmiles(smiles))
    params = AllChem.ETKDGv3()
    params.randomSeed = SEED
    params.numThreads = 1
    assert AllChem.EmbedMolecule(molecule, params) == 0
    result = AllChem.MMFFOptimizeMolecule(molecule, mmffVariant='MMFF94s', maxIters=2000)
    assert result == 0, 'classical geometry optimization did not converge'
    return molecule


def rotation(axis, angle_degrees):
    axis = np.asarray(axis) / np.linalg.norm(axis)
    cross = np.array([[0., -axis[2], axis[1]], [axis[2], 0., -axis[0]],
                      [-axis[1], axis[0], 0.]])
    angle = np.deg2rad(angle_degrees)
    return np.eye(3) * np.cos(angle) + (1-np.cos(angle))*np.outer(axis, axis) + np.sin(angle)*cross


def align(vector):
    vector = vector / np.linalg.norm(vector)
    target = np.array([1., 0., 0.])
    cross = np.cross(vector, target)
    if np.linalg.norm(cross) < 1e-12:
        return np.eye(3) if vector[0] > 0 else rotation([0., 1., 0.], 180.)
    return rotation(cross, np.rad2deg(np.arccos(np.clip(vector @ target, -1., 1.))))


def topology(molecule, prefix):
    return {
        'smiles': Chem.MolToSmiles(Chem.RemoveHs(molecule), isomericSmiles=True),
        'formal_charge': Chem.GetFormalCharge(molecule), 'multiplicity': 1,
        'atom_ids': [prefix + str(i) for i in range(molecule.GetNumAtoms())],
        'elements': [a.GetSymbol() for a in molecule.GetAtoms()],
        'atomic_numbers': [a.GetAtomicNum() for a in molecule.GetAtoms()],
        'bonds': [[b.GetBeginAtomIdx(), b.GetEndAtomIdx(), float(b.GetBondTypeAsDouble())]
                  for b in molecule.GetBonds()],
        'stereocenters': Chem.FindMolChiralCenters(molecule, includeUnassigned=True),
    }


def parent_record(molecule, name):
    record = topology(molecule, 'p')
    record.update(name=name, positions_angstrom=molecule.GetConformer().GetPositions().tolist(),
                  units='angstrom', preparation={'rdkit_version': rdBase.rdkitVersion,
                  'embed': 'ETKDGv3', 'random_seed': SEED, 'threads': 1,
                  'classical_optimization': 'MMFF94s', 'max_iterations': 2000, 'converged': True},
                  provenance='deterministic classical preparation; no model/quantum score')
    return record


def capped(parent, ml_parent, mm_parent):
    adjacency = {i: set() for i in range(len(parent['atom_ids']))}
    for i, j, _ in parent['bonds']:
        if {i, j} != {ml_parent, mm_parent}:
            adjacency[i].add(j); adjacency[j].add(i)
    component, pending = set(), [ml_parent]
    while pending:
        i = pending.pop()
        if i not in component:
            component.add(i); pending.extend(adjacency[i] - component)
    assert mm_parent not in component
    selected = sorted(component)
    r = np.asarray(parent['positions_angstrom'])
    direction = r[mm_parent] - r[ml_parent]
    cap = r[ml_parent] + CAP_ANGSTROM * direction / np.linalg.norm(direction)
    raw = np.vstack([r[selected], cap])
    inverse = {index: i for i, index in enumerate(selected)}
    return {
        'atom_ids': [parent['atom_ids'][i] for i in selected] + ['cap'],
        'elements': [parent['elements'][i] for i in selected] + ['H'],
        'atomic_numbers': [parent['atomic_numbers'][i] for i in selected] + [1],
        'positions_angstrom': raw.tolist(), 'units': 'angstrom',
        'bonds': [[inverse[i], inverse[j], order] for i, j, order in parent['bonds']
                  if i in component and j in component] + [[inverse[ml_parent], len(selected), 1.]],
        'formal_charge': 0, 'multiplicity': 1, 'protonation': 'neutral ordinary-valence saturated cap',
        'cap': {'id': 'cap', 'raw_index': len(selected), 'ml_parent_id': 'p'+str(ml_parent),
                'mm_parent_id': 'p'+str(mm_parent), 'distance_angstrom': CAP_ANGSTROM,
                'rule': 'a+d*(b-a)/norm(b-a)', 'real_source_indices': selected,
                'mass_da': 0., 'classical_charge': 0., 'classical_lj_epsilon': 0.},
        'parent': parent,
    }


def monomer(molecule, name, family, baseline):
    record = topology(molecule, 'l')
    record.update(name=name, family=family, baseline=baseline,
                  positions_angstrom=molecule.GetConformer().GetPositions().tolist(),
                  units='angstrom', protonation='neutral closed-shell explicit hydrogens',
                  cap=None, provenance='classical preparation and prescribed distortion; no model score')
    return record


def contact(fragment, ligand, family, fragment_anchor, fragment_vector,
            ligand_anchor, ligand_vector, distance, twist=0., separated=False):
    rf = np.asarray(fragment['positions_angstrom']); rl = np.asarray(ligand['positions_angstrom'])
    qf = align(rf[fragment_vector[1]] - rf[fragment_vector[0]])
    ql = rotation([0., 0., 1.], twist) @ align(rl[ligand_vector[1]] - rl[ligand_vector[0]])
    xf = (rf - rf[fragment_anchor]) @ qf.T
    xl = (rl - rl[ligand_anchor]) @ ql.T
    if separated:
        distance = 15. + max(np.linalg.norm(xf, axis=1)) + max(np.linalg.norm(xl, axis=1))
    translation = np.array([distance, 0., 0.])
    xl += translation
    geometry = np.vstack([xf, xl])
    distances = np.linalg.norm(xf[:, None, :] - xl[None, :, :], axis=2)
    parent = fragment['parent']
    parent_positions = (np.asarray(parent['positions_angstrom']) - rf[fragment_anchor]) @ qf.T
    controls = {
        'parent': {**parent, 'positions_angstrom': parent_positions.tolist()},
        'ligand_positions_angstrom': xl.tolist(),
        'choices': [{'name': 'baseline', 'cut_ml_parent_id': fragment['cap']['ml_parent_id'],
                     'cut_mm_parent_id': fragment['cap']['mm_parent_id'],
                     'protein_ml_ids': fragment['atom_ids'][:-1], 'cap_distance_angstrom': CAP_ANGSTROM},
                    {'name': 'uncut', 'cut': None, 'protein_ml_ids': parent['atom_ids'], 'cap': None}],
        'reference_charge_multiplicity': [0, 1],
        'mm_definition': 'GAFF 2.2.20 / AM1-BCC on the complete neutral parent and complete ligand; '
                         'locked Amber profile, no cap parameters; remove ML-internal terms using accepted boundary ledger',
        'future_obligations': ['freeze prepared MM XML/charges/digest before G07-T4 evaluation',
                               'Qfull and every Qcap energy and gradient at all frozen contact/control rows'],
    }
    if family.startswith('butane'):
        transformed = {**parent, 'positions_angstrom': parent_positions.tolist()}
        alternative = capped(transformed, 7, 5)
        controls['choices'].append({'name': 'alternative-ethane', 'cut_ml_parent_id': 'p7',
               'cut_mm_parent_id': 'p5', 'protein_ml_ids': alternative['atom_ids'][:-1],
               'cap_distance_angstrom': CAP_ANGSTROM, 'exact_model_fragment': alternative})
    return {
        'name': family + ('-separated' if separated else f'-d{distance:g}-r{twist:g}'),
        'family': family, 'kind': 'separated' if separated else 'contact',
        'formal_charge': 0, 'multiplicity': 1, 'units': 'angstrom',
        'atom_ids': ['f:'+a for a in fragment['atom_ids']] + ['l:'+a for a in ligand['atom_ids']],
        'atomic_numbers': fragment['atomic_numbers'] + ligand['atomic_numbers'],
        'elements': fragment['elements'] + ligand['elements'],
        'positions_angstrom': geometry.tolist(), 'fragment_count': len(xf),
        'fragment_baseline': fragment['name'], 'ligand_baseline': ligand['name'],
        'anchor_indices': [fragment_anchor, len(xf)+ligand_anchor],
        'anchor_distance_angstrom': distance, 'ligand_rotation_degrees': twist,
        'minimum_intercomponent_distance_angstrom': float(distances.min()),
        'fragment_transform': {'rotation': qf.tolist(), 'source_anchor_angstrom': rf[fragment_anchor].tolist()},
        'ligand_transform': {'rotation': ql.tolist(), 'source_anchor_angstrom': rl[ligand_anchor].tolist(),
                             'translation_angstrom': translation.tolist()},
        'fragment_cap': fragment['cap'], 'g07_controls': controls,
        'energy_zero': 'same-coordinate uncorrected E(joint)-E(fragment)-E(ligand); also contact-minus-separated',
    }


def main():
    thr = prepare('CC(=O)N[C@@H]([C@H](O)C)C(=O)NC')
    ile = prepare('CC(=O)N[C@@H]([C@@H](C)CC)C(=O)NC')
    structures = []
    for molecule, family, torsion, ml, mm in (
            (thr, 'ethanol', (7, 5, 6, next(a.GetIdx() for a in thr.GetAtomWithIdx(6).GetNeighbors() if a.GetAtomicNum()==1)), 5, 4),
            (ile, 'butane', (6, 5, 7, 8), 5, 4)):
        for angle in (180, 60, -60, 120):
            copy = Chem.Mol(molecule)
            rdMolTransforms.SetDihedralDeg(copy.GetConformer(), *torsion, angle)
            record = capped(parent_record(copy, family+'-parent'), ml, mm)
            record.update(name=f'{family}-{angle}', family=family, baseline=f'{family}-180',
                          torsion_parent_indices=list(torsion), torsion_degrees=angle,
                          provenance='prescribed torsion on classically prepared neutral peptide parent; no model score')
            structures.append(record)
    methanol = prepare('CO')
    h = next(a.GetIdx() for a in methanol.GetAtomWithIdx(1).GetNeighbors() if a.GetAtomicNum()==1)
    for kind in ('baseline', 'oh60', 'stretch003'):
        copy = Chem.Mol(methanol); r = copy.GetConformer().GetPositions()
        if kind == 'oh60':
            r[h] = r[1] + rotation(r[1]-r[0], 60.) @ (r[h]-r[1])
        if kind == 'stretch003':
            r[[1, h]] += .03 * (r[1]-r[0]) / np.linalg.norm(r[1]-r[0])
        for i, xyz in enumerate(r): copy.GetConformer().SetAtomPosition(i, xyz)
        structures.append(monomer(copy, 'methanol-'+kind, 'methanol', 'methanol-baseline'))
    acetamide = prepare('CC(N)=O')
    nh = [a.GetIdx() for a in acetamide.GetAtomWithIdx(2).GetNeighbors() if a.GetAtomicNum()==1]
    for twist in (0, 20, -20):
        copy = Chem.Mol(acetamide); r = copy.GetConformer().GetPositions()
        for i in nh:r[i] = r[2] + rotation(r[2]-r[1], twist) @ (r[i]-r[2])
        for i, xyz in enumerate(r):copy.GetConformer().SetAtomPosition(i, xyz)
        structures.append(monomer(copy, 'acetamide-'+str(twist), 'acetamide', 'acetamide-0'))
    by_name = {s['name']: s for s in structures}
    ethanol, butane = by_name['ethanol-180'], by_name['butane-180']
    for fragment, ligand, family, fa, fv, la, lv, distances in (
            (ethanol, by_name['methanol-baseline'], 'ethanol-methanol', 1, (1, next(i for i,z in enumerate(ethanol['elements'])
             if z=='H' and any({a,b}=={1,i} for a,b,_ in ethanol['bonds']))), 1, (1,0), (2.6,3.,3.5)),
            (ethanol, by_name['acetamide-0'], 'ethanol-acetamide', 1, (1, next(i for i,z in enumerate(ethanol['elements'])
             if z=='H' and any({a,b}=={1,i} for a,b,_ in ethanol['bonds']))), 3, (3,1), (2.6,3.,3.5)),
            (butane, by_name['methanol-baseline'], 'butane-methanol', 1, (0,1), 0, (0,1), (3.4,3.8,4.5)),
            (butane, by_name['acetamide-0'], 'butane-acetamide', 1, (0,1), 0, (0,1), (3.4,3.8,4.5))):
        rows = [contact(fragment, ligand, family, fa, fv, la, lv, d) for d in distances]
        rows += [contact(fragment, ligand, family, fa, fv, la, lv, distances[1], 60.),
                 contact(fragment, ligand, family, fa, fv, la, lv, 15., separated=True)]
        structures.extend(rows)
    assert len(structures) == 34
    for structure in structures:write('structures/'+structure['name']+'.json', structure)
    manifest = {'state': 'frozen proposal; user agreement and independent design review pending',
                'preparation_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'no_model_or_quantum_score_used': True, 'g05_structure_count': 34,
                'g07_rows': 20, 'g07_choices': {'threonine': ['baseline','uncut'],
                                             'isoleucine': ['baseline','uncut','alternative-ethane']},
                'files': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted((ROOT/'structures').glob('*.json'))}}
    write('input-manifest.json', manifest)
    print(json.dumps({'structures': len(structures), 'files': len(manifest['files']),
         'contact_minimum_distances': {s['name']:s['minimum_intercomponent_distance_angstrom']
                                     for s in structures if 'fragment_count' in s}}, indent=2))


if __name__ == '__main__':
    main()
