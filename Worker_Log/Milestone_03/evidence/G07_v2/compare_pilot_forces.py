"""Read-only arithmetic for the one completed pilot; no QM or model launch.

This cannot supply the missing within-description separated energy references.
It retains every real MM force and applies each artificial-cap Jacobian once.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
ROW = 'ethanol-methanol-d3-r0'


def main(output):
    paths = dict(
        settings=ROOT/'fixtures/chemical_reference_v3/reference-settings.json',
        capped_input=ROOT/f'fixtures/chemical_reference_v3/structures/{ROW}.json',
        capped_qm=ROOT/f'fixtures/chemical_reference_v3/quantum/records/{ROW}.json',
        capped_separated_qm=ROOT/'fixtures/chemical_reference_v3/quantum/records/ethanol-methanol-separated.json',
        full_qm=ROOT/f'Worker_Log/Milestone_03/evidence/G07_v2/quantum-attempt-v1/records/{ROW}--full-parent.json',
        matrix=ROOT/'fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json',
        proposal=ROOT/'docs/project-0/reference/G07-reference-execution-proposal-v1.md',
        descriptions=ROOT/'fixtures/fragment_ligand/descriptions-v1/manifest.json',
        baseline=ROOT/f'Worker_Log/Milestone_03/evidence/G07_v1/fifty-description-single-points/{ROW}--baseline.json',
        baseline_separated=ROOT/'Worker_Log/Milestone_03/evidence/G07_v1/fifty-description-single-points/ethanol-methanol-separated--baseline.json',
        uncut=ROOT/f'Worker_Log/Milestone_03/evidence/G07_v1/fifty-description-single-points/{ROW}--uncut.json')
    data = {k:json.loads(p.read_text()) for k,p in paths.items() if p.suffix == '.json'}
    desc = {r['description']:r for r in data['descriptions']['rows'] if r['row'] == ROW}
    ids = desc['baseline']['real_atom_ids']
    x = np.asarray(desc['baseline']['positions_nm'])
    ev_to_kj = 1.6021766208e-19 * 6.022140857e23 / 1000.
    qfactor = data['settings']['hartree_to_kJ_mol']/data['settings']['bohr_to_nm']/(10*ev_to_kj)
    full_job = next(j for j in data['matrix']['new_jobs'] if j['name'] == ROW+'--full-parent')
    full_ids = ['a:'+a if a.startswith('l') else a for a in full_job['atom_ids']]
    assert full_ids == ids
    assert data['full_qm']['positions_angstrom'] == full_job['positions_angstrom']
    assert data['full_qm']['atomic_numbers'] == full_job['atomic_numbers']
    assert np.max(np.abs(np.asarray(full_job['positions_angstrom'])/10-x)) < 1e-13
    full_force = -np.asarray(data['full_qm']['gradient_hartree_bohr'])*qfactor

    links = {l['data']['cap_id']:l['data'] for l in desc['baseline']['links']}
    cap_id = next(iter(links))
    cap_ids = [cap_id if a == 'f:cap' else a[2:] if a.startswith('f:') else 'a:'+a[2:]
               for a in data['capped_input']['atom_ids']]
    model_ids = desc['baseline']['model_input_ids']
    order = [cap_ids.index(a) for a in model_ids]
    raw = data['baseline']['native_raw_model']
    assert [data['capped_qm']['atomic_numbers'][i] for i in order] == raw['numbers']
    assert np.max(np.abs(np.asarray(data['capped_qm']['positions_angstrom'])[order]/10-raw['positions_nm'])) < 1e-13
    qcap = -np.asarray(data['capped_qm']['gradient_hartree_bohr'])[order]*qfactor
    mace = -np.asarray(raw['gradient_eV_angstrom'])

    def project(forces, description):
        result = np.zeros_like(x)
        for atom_id, force in zip(description['model_input_ids'], forces, strict=True):
            if atom_id in ids:
                result[ids.index(atom_id)] += force
            else:
                link = links[atom_id]
                a,b = ids.index(link['ml_parent_id']),ids.index(link['mm_parent_id'])
                v = x[b]-x[a]; length = np.linalg.norm(v); unit = v/length
                jb = link['distance_nm']/length*(np.eye(3)-np.outer(unit,unit))
                result[a] += (np.eye(3)-jb).T@force
                result[b] += jb.T@force
        return result

    pm,pq = project(mace,desc['baseline']),project(qcap,desc['baseline'])
    hybrid = np.asarray(data['baseline']['hybrid_real_forces_kj_mol_nm'])/(10*ev_to_kj)
    retained_mm = hybrid-pm  # Already on all real coordinates; never project it again.
    model_error = pm-pq
    partition_error = pq+retained_mm-full_force
    hybrid_error = hybrid-full_force
    assert np.max(np.abs(model_error+partition_error-hybrid_error)) < 1e-13
    raw_full = data['uncut']['native_raw_model']
    full_order = [ids.index(a) for a in desc['uncut']['model_input_ids']]
    assert [full_job['atomic_numbers'][i] for i in full_order] == raw_full['numbers']
    assert np.max(np.abs(x[full_order]-raw_full['positions_nm'])) < 1e-13
    full_mace = project(-np.asarray(raw_full['gradient_eV_angstrom']),desc['uncut'])
    model_contact = (raw['energy_kj_mol']-data['baseline_separated']['native_raw_model']['energy_kj_mol'])/4.184
    cap_contact = (data['capped_qm']['energy_hartree']-data['capped_separated_qm']['energy_hartree'])*data['settings']['hartree_to_kJ_mol']/4.184
    ligand = [i for i,a in enumerate(ids) if a.startswith('a:')]
    def metrics(error):
        assert np.isfinite(error).all()
        return dict(component_rms_eV_angstrom=float(np.sqrt(np.mean(error**2))),
            maximum_atom_vector_eV_angstrom=float(np.max(np.linalg.norm(error,axis=1))),
            net_ligand_vector_eV_angstrom=float(np.linalg.norm(error[ligand].sum(axis=0))))
    limits = dict(component_rms_eV_angstrom=.05, maximum_atom_vector_eV_angstrom=.15,
                  net_ligand_vector_eV_angstrom=.05)
    def qualified(error):
        values = metrics(error)
        return dict(values,within_each_existing_force_limit={k:values[k]<=v for k,v in limits.items()})
    result = dict(row=ROW,scope='single contact force diagnostic only; no physical acceptance',
        energy_comparison='Full-parent separated QM absent; no cross-composition absolute-energy comparison made.',
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths.values()},
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),real_atom_ids=ids,
        cap_parents=[links[cap_id]['ml_parent_id'],links[cap_id]['mm_parent_id']],
        baseline_same_cap_contact_minus_separated_kcal_mol=dict(mace=model_contact,qm=cap_contact,error=model_contact-cap_contact),
        unchanged_force_limits=limits,
        raw_mace_minus_same_cap_qm=dict(
            component_rms_eV_angstrom=float(np.sqrt(np.mean((mace-qcap)**2))),
            maximum_atom_vector_eV_angstrom=float(np.max(np.linalg.norm(mace-qcap,axis=1)))),
        projected_mace_minus_same_cap_qm=qualified(model_error),
        capped_qm_plus_all_retained_mm_minus_full_qm=qualified(partition_error),
        baseline_hybrid_minus_full_qm=qualified(hybrid_error),full_mace_minus_full_qm=qualified(full_mace-full_force),
        arrays_eV_angstrom=dict(full_qm=full_force.tolist(),projected_cap_qm=pq.tolist(),projected_mace=pm.tolist(),
            all_retained_mm=retained_mm.tolist(),model_error=model_error.tolist(),partition_error=partition_error.tolist(),
            hybrid_error=hybrid_error.tolist()),seven_existing_exceedances_preserved=True)
    with Path(output).open('x') as stream:json.dump(result,stream,indent=2,allow_nan=False);stream.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    main(parser.parse_args().output)
