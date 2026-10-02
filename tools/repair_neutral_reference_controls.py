"""Score-free correction of the independently found v2 G07 peptide clash."""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
from prepare_neutral_references import rotation

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / 'fixtures/chemical_reference'
TARGET = REPO / 'fixtures/chemical_reference_v3'
RADII = {'H': 1.20, 'C': 1.70, 'N': 1.55, 'O': 1.52}


def moved_parent(parent, fragment_ids, angle):
    result = copy.deepcopy(parent)
    r = np.asarray(parent['positions_angstrom'])
    mm = [i for i, a in enumerate(parent['atom_ids']) if a not in fragment_ids]
    q = rotation(r[4]-r[5], angle)
    out = r.copy(); out[mm] = (r[mm]-r[5]) @ q.T + r[5]
    out[4] = r[4]  # fixed on the cut axis, preserve its exact serialized bytes
    result['positions_angstrom'] = out.tolist()
    result['g07_geometry_preparation'] = {
        'retained_component_rotation_degrees': angle, 'fixed_axis_real_ids': ['p5', 'p4'],
        'rule': 'rigidly rotate only MM component about fixed Cbeta-Calpha axis; capped component unchanged',
        'selection': 'maximum worst retained-parent/ligand Bondi-radius distance ratio over all ten threonine contact/separated rows; '
                     '12 angles 0..330 step30; internal nonbonded ratio >=0.65; ties choose smallest angle',
        'no_energy_or_model_score_used': True,
    }
    return result


def ratios(parent, ligand, ligand_elements, fragment_ids):
    r = np.asarray(parent['positions_angstrom']); l = np.asarray(ligand)
    radii = np.array([RADII[e] for e in parent['elements']]); lr = np.array([RADII[e] for e in ligand_elements])
    mm = [i for i,a in enumerate(parent['atom_ids']) if a not in fragment_ids]
    inter = float(np.min(np.linalg.norm(r[mm,None]-l[None,:],axis=2)/(radii[mm,None]+lr[None,:])))
    graph = {i:set() for i in range(len(r))}
    for i,j,_ in parent['bonds']:graph[i].add(j);graph[j].add(i)
    values=[]
    for i in range(len(r)):
        excluded={i}|graph[i]
        for j in graph[i]:excluded |= graph[j]
        for j in range(i):
            if j not in excluded:values.append(float(np.linalg.norm(r[i]-r[j])/(radii[i]+radii[j])))
    return inter, min(values)


def main():
    if TARGET.exists():raise FileExistsError('Do not overwrite a frozen proposal')
    records={p.name:json.loads(p.read_text()) for p in sorted((SOURCE/'structures').glob('*.json'))}
    rows=[s for s in records.values() if s.get('family','').startswith('ethanol-') and 'g07_controls' in s]
    attempts=[]
    for angle in range(0,360,30):
        inter,internal=[],[]
        for row in rows:
            control=row['g07_controls'];ids=control['choices'][0]['protein_ml_ids']
            parent=moved_parent(control['parent'],ids,angle)
            a,b=ratios(parent,control['ligand_positions_angstrom'],row['elements'][row['fragment_count']:],ids)
            inter.append(a);internal.append(b)
        attempts.append({'angle_degrees':angle,'worst_retained_ligand_ratio':min(inter),
                         'worst_internal_nonbonded_ratio':min(internal),'eligible':min(internal)>=.65})
    chosen=max((r for r in attempts if r['eligible']),key=lambda r:(r['worst_retained_ligand_ratio'],-r['angle_degrees']))
    assert chosen['worst_retained_ligand_ratio']>=.70
    angle=chosen['angle_degrees']
    TARGET.mkdir();(TARGET/'structures').mkdir();(TARGET/'quadrature_controls').mkdir()
    for name,row in records.items():
        if row['family']=='ethanol':
            row['parent']=moved_parent(row['parent'],set(row['atom_ids'][:-1]),angle)
        elif row['family'].startswith('ethanol-'):
            control=row['g07_controls'];control['parent']=moved_parent(control['parent'],
                   set(control['choices'][0]['protein_ml_ids']),angle)
        # G05 raw atoms/coordinates/compositions/contact placements stay exact.
        original=json.loads((SOURCE/'structures'/name).read_text())
        for field in ('positions_angstrom','atomic_numbers','atom_ids','formal_charge','multiplicity'):
            assert row[field]==original[field],(name,field)
        (TARGET/'structures'/name).write_text(json.dumps(row,indent=2,allow_nan=False)+'\n')
    # Freeze one rotational quadrature check for every distinct monomer frame.
    unique={}
    for row in records.values():
        if 'fragment_count' not in row:continue
        n=row['fragment_count']
        for part,start,stop in (('fragment',0,n),('ligand',n,len(row['atom_ids']))):
            baseline=row[part+'_baseline'];q=row[part+'_transform']['rotation']
            key=(baseline,json.dumps(q))
            if key in unique:continue
            positions=np.asarray(row['positions_angstrom'])[start:stop]
            positions-=positions[0]  # translation-independent atomic grid frame
            name=baseline+'-rotation-'+str(sum(k[0]==baseline for k in unique))
            unique[key]=name
            data={'name':name,'kind':'rotation-quadrature-control','baseline':baseline,
                  'formal_charge':0,'multiplicity':1,'units':'angstrom',
                  'atom_ids':row['atom_ids'][start:stop],'atomic_numbers':row['atomic_numbers'][start:stop],
                  'elements':row['elements'][start:stop],'positions_angstrom':positions.tolist(),
                  'rotation':q,'source_contact':row['name'],
                  'energy_difference_max_kcal_mol':.02,'force_component_rms_difference_max_eV_angstrom':.002,
                  'force_atom_vector_difference_max_eV_angstrom':.005}
            (TARGET/'quadrature_controls'/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    for name in ('reference-settings.json','reference-explicit.lock'):
        (TARGET/name).write_bytes((SOURCE/name).read_bytes())
    manifest={'state':'exact corrected proposal; user agreement and fresh independent review pending',
              'predecessor_plan_commit':'321d7e3764a46eb5359a8d96bcab9124dccbc5f5',
              'g05_structure_count':34,'g07_rows':20,'g07_description_count':50,
              'quadrature_control_count':len(unique),'g05_raw_inputs_unchanged_from_v2':True,
              'no_model_or_quantum_score_used':True,'repair_attempts':attempts,'selected_angle':angle,
              'repair_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'files':{str(p.relative_to(TARGET)):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sorted(TARGET.rglob('*')) if p.is_file()}}
    (TARGET/'input-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'selected':chosen,'g05_rows':34,'quadrature_controls':len(unique)},indent=2))


if __name__=='__main__':main()
