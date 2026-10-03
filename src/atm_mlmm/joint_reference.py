"""G07 matrix construction from immutable M00 v3 inputs; no engine launches."""
import hashlib
import json
from pathlib import Path
import numpy as np
from .schema import IdentityError


def validate_capped_geometry(row):
    parent = row['g07_controls']['parent']
    ids = parent['atom_ids']
    x = np.asarray(parent['positions_angstrom'])
    cap = row['fragment_cap']
    a, b = (ids.index(cap[key]) for key in ('ml_parent_id','mm_parent_id'))
    v = x[b]-x[a]
    if not np.linalg.norm(v) > 0:
        raise IdentityError('coincident cap reference parents')
    expected = np.vstack([x[cap['real_source_indices']], x[a]+cap['distance_angstrom']*v/np.linalg.norm(v)])
    if not np.allclose(expected, np.asarray(row['positions_angstrom'])[:row['fragment_count']], rtol=0, atol=1e-10):
        raise IdentityError('frozen capped input differs from full-parent cap construction')


def quantum_job_matrix(root):
    """20 full-parent and 10 alternative-cap jobs; reuse 20 exact G05 caps.

    Scientific geometry/settings approval is carried by M00. It does not grant
    this new calculation matrix a runtime budget or acceptance.
    """
    root = Path(root)
    inputs = json.loads((root/'input-manifest.json').read_text())
    quantum = json.loads((root/'quantum/manifest.json').read_text())
    rows, new_jobs, reused = [], [], []
    for relative, digest in sorted(inputs['files'].items()):
        if not relative.startswith('structures/'):
            continue
        path = root/relative
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise IdentityError('changed frozen joint input: '+relative)
        data = json.loads(path.read_text())
        if 'g07_controls' not in data:
            continue
        validate_capped_geometry(data)
        controls = data['g07_controls']
        parent = controls['parent']
        ligand_numbers = data['atomic_numbers'][data['fragment_count']:]
        ligand_ids = [a[2:] for a in data['atom_ids'][data['fragment_count']:]]
        ligand_positions = controls['ligand_positions_angstrom']
        full_name = data['name']+'--full-parent'
        common = dict(formal_charge=0,multiplicity=1,units='angstrom',source_input=relative,
                      source_input_sha256=digest,method='wb97m-d3bj/def2-tzvppd')
        new_jobs.append(dict(common,name=full_name,kind='full-parent',
            atom_ids=parent['atom_ids']+ligand_ids,
            atomic_numbers=parent['atomic_numbers']+ligand_numbers,
            positions_angstrom=parent['positions_angstrom']+ligand_positions))
        record_path = 'records/'+data['name']+'.json'
        record_digest = quantum['files'].get(record_path)
        if record_digest is None or hashlib.sha256((root/'quantum'/record_path).read_bytes()).hexdigest() != record_digest:
            raise IdentityError('baseline G05 quantum record absent/changed: '+record_path)
        record = json.loads((root/'quantum'/record_path).read_text())
        if record['atomic_numbers'] != data['atomic_numbers'] or record['positions_angstrom'] != data['positions_angstrom']:
            raise IdentityError('reused quantum geometry differs from frozen capped row')
        reused.append(dict(name=data['name'],kind='baseline',path='quantum/'+record_path,sha256=record_digest))
        descriptions = []
        for choice in controls['choices']:
            name = choice['name']
            job = data['name'] if name == 'baseline' else full_name
            if name == 'alternative-ethane':
                fragment = choice['exact_model_fragment']
                job = data['name']+'--alternative-ethane'
                new_jobs.append(dict(common,name=job,kind=name,
                    atom_ids=fragment['atom_ids']+ligand_ids,
                    atomic_numbers=fragment['atomic_numbers']+ligand_numbers,
                    positions_angstrom=fragment['positions_angstrom']+ligand_positions))
            descriptions.append(dict(name=name,quantum_job=job,protein_ml_ids=choice['protein_ml_ids'],
                                     cut=None if name=='uncut' else (choice['cut_ml_parent_id'],choice['cut_mm_parent_id']),
                                     cap_distance_angstrom=None if name=='uncut' else choice['cap_distance_angstrom']))
        rows.append(dict(name=data['name'],family=data['family'],kind=data['kind'],source_input=relative,
                         source_input_sha256=digest,full_job=full_name,descriptions=descriptions))
    if len(rows) != 20 or sum(len(r['descriptions']) for r in rows) != 50 or len(new_jobs) != 30:
        raise IdentityError('joint matrix differs from frozen 20-row/50-description plan')
    return dict(source_manifest_sha256=hashlib.sha256((root/'input-manifest.json').read_bytes()).hexdigest(),
                reference_settings_sha256=hashlib.sha256((root/'reference-settings.json').read_bytes()).hexdigest(),
                rows=rows,new_jobs=new_jobs,reused_jobs=reused,new_quantum_authorized=False,
                budget_status='G05 budget does not authorize this G07 batch',
                accounting='hybrid-Qfull=(MACE-Qcap)+(Qcap+retained-MM-Qfull), within-description geometry differences')
