"""Render saved actual evidence; does not run QM or evaluate a learned model."""
import csv
import datetime
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from tests.integration.test_chemical_reference import cap_project

evidence = Path(__file__).resolve().parent
repo = evidence.parents[3]
plan = repo / 'fixtures/chemical_reference_v3'
attempt = repo / 'Worker_Log/Milestone_00/evidence/M00_reference_v3/quantum-attempt-v2'
read = lambda p: json.loads(Path(p).read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
settings = read(plan / 'reference-settings.json')
state = read(attempt / 'progress.json')
conformers = read(evidence / 'chemical-comparisons/chemical-conformers.json')
contacts = read(evidence / 'chemical-comparisons/chemical-contacts.json')
controls = read(evidence / 'quantum-numerical-validation/quantum-numerical-controls-prebundle.json')['records']
structures = {p.stem: read(p) for p in (plan / 'structures').glob('*.json')}
forces = conformers['forces'] + contacts['forces']
force_by_name = {r['name']: r for r in forces}
assert len(force_by_name) == len(structures) == 34
assert state['ready_for_comparison'] and len(state['record_hashes']) == 46
families = conformers['families']
interaction = contacts['families']


def json_file(name, data):
    with (evidence / name).open('x') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')


def csv_file(name, data):
    columns = list(dict.fromkeys(k for row in data for k in row))
    with (evidence / name).open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\n')
        writer.writeheader()
        writer.writerows(data)


energy_rows = {}
for family in families:
    for name, error in zip(family['rows'], family['relative_energy_errors_kcal_mol']):
        energy_rows[name] = dict(relative_energy_error_kcal_mol=error)
separated = {r['family']: r for r in contacts['energies'] if r['kind'] == 'separated'}
for row in contacts['energies']:
    energy_rows[row['name']] = dict(model_interaction_kcal_mol=row['model_interaction_kcal_mol'],
        quantum_interaction_kcal_mol=row['quantum_interaction_kcal_mol'],
        interaction_error_kcal_mol=row['error_kcal_mol'],
        contact_minus_separated_error_kcal_mol=row['error_kcal_mol'] - separated[row['family']]['error_kcal_mol'])

metrics = []
cap_evidence = []
signs = []
for name in sorted(structures):
    row = structures[name]
    force = force_by_name[name]
    metric = dict(name=name, capture_index=next(i for i,r in enumerate(forces) if r['name']==name),
                  family=row['family'], kind=row.get('kind', 'conformer'), **energy_rows[name])
    for key in ('force_rms_eV_angstrom', 'force_atom_max_eV_angstrom', 'projected_rms_eV_angstrom',
                'projected_atom_max_eV_angstrom', 'net_ligand_force_error_eV_angstrom'):
        if key in force:
            metric[key] = force[key]
    metric['raw_force_limits_passed'] = (force['force_rms_eV_angstrom'] <= .05 and force['force_atom_max_eV_angstrom'] <= .15)
    metric['projected_force_limits_passed'] = (force.get('projected_rms_eV_angstrom', 0) <= .05 and force.get('projected_atom_max_eV_angstrom', 0) <= .15)
    if 'fragment_count' in row:
        metric['contact_capture_index'] = next(i for i,r in enumerate(contacts['forces']) if r['name']==name)
        n = row['fragment_count']
        fragment = dict(structures[row['fragment_baseline']], parent=row['g07_controls']['parent'])
        pm = np.vstack([cap_project(fragment, force['model_raw_forces_eV_angstrom'][:n]), force['model_raw_forces_eV_angstrom'][n:]])
        pq = np.vstack([cap_project(fragment, force['quantum_raw_forces_eV_angstrom'][:n]), force['quantum_raw_forces_eV_angstrom'][n:]])
        cap_index = n - 1
        energy = next(r for r in contacts['energies'] if r['name'] == name)
        required_attraction = energy['quantum_interaction_kcal_mol'] <= -settings['sign_attraction_minimum_kcal_mol']
        required_repulsion = name in settings['compressed_rows'] and force['quantum_net_ligand_force_eV_angstrom'][0] > 0
        sign = dict(name=name, attraction_required=required_attraction,
                    attraction_passed=(not required_attraction or energy['model_interaction_kcal_mol'] < 0),
                    repulsion_required=required_repulsion,
                    repulsion_passed=(not required_repulsion or force['model_net_ligand_force_eV_angstrom'][0] > 0),
                    model_interaction_kcal_mol=energy['model_interaction_kcal_mol'],
                    quantum_interaction_kcal_mol=energy['quantum_interaction_kcal_mol'],
                    model_ligand_approach_force_eV_angstrom=force['model_net_ligand_force_eV_angstrom'][0],
                    quantum_ligand_approach_force_eV_angstrom=force['quantum_net_ligand_force_eV_angstrom'][0])
        signs.append(sign)
        metric['net_ligand_force_limit_passed'] = force['net_ligand_force_error_eV_angstrom'] <= .05
    elif row.get('cap') is not None:
        pm = np.asarray(force['model_parent_forces_eV_angstrom'])
        pq = np.asarray(force['quantum_parent_forces_eV_angstrom'])
        cap_index = len(row['atomic_numbers']) - 1
    else:
        pm = pq = None
    if pm is not None:
        mf = np.asarray(force['model_raw_forces_eV_angstrom'])[cap_index]
        qf = np.asarray(force['quantum_raw_forces_eV_angstrom'])[cap_index]
        metric['cap_raw_force_error_eV_angstrom'] = float(np.linalg.norm(mf - qf))
        cap_evidence.append(dict(name=name, raw_cap_model_force_eV_angstrom=mf.tolist(),
            raw_cap_quantum_force_eV_angstrom=qf.tolist(), model_full_parent_and_ligand_forces_eV_angstrom=pm.tolist(),
            quantum_full_parent_and_ligand_forces_eV_angstrom=pq.tolist(),
            independent_projection_error_rms_eV_angstrom=float(np.sqrt(np.mean((pm - pq)**2))),
            independent_projection_error_max_eV_angstrom=float(np.max(np.linalg.norm(pm - pq, axis=1)))))
        assert abs(cap_evidence[-1]['independent_projection_error_rms_eV_angstrom'] - force['projected_rms_eV_angstrom']) < 1e-12
        assert abs(cap_evidence[-1]['independent_projection_error_max_eV_angstrom'] - force['projected_atom_max_eV_angstrom']) < 1e-12
    metrics.append(metric)

jobs = []
for name in state['expected_names']:
    record = read(attempt / 'records' / (name + '.json'))
    provenance = state['provenance'][name]
    original = Path(provenance['source'])
    log = original.with_suffix('.psi4.txt')
    assert 'Energy and wave function converged.' in log.read_text(), name
    receipt = read(provenance['receipt']) if 'receipt' in provenance else {}
    assert sha(attempt / 'records' / (name + '.json')) == state['record_hashes'][name]
    jobs.append(dict(name=name, atom_count=len(record['atomic_numbers']), status=record['status'],
        recovered=provenance['recovered'], coordinator_exit=provenance['coordinator_exit'],
        worker_wall_seconds=record['wall_seconds'], coordinator_wall_seconds=receipt.get('wall_seconds'),
        runtime_memory=record['memory'], peak_worker_rss_gib=(record['peak_rss_bytes'] / 2**30 if 'peak_rss_bytes' in record else None),
        scf_converged_in_log=True, record_sha256=state['record_hashes'][name]))
new_jobs = [j for j in jobs if not j['recovered']]
assert len(new_jobs) == 38 and all(j['coordinator_exit'] == 0 for j in new_jobs)
assert all(r['raw_force_limits_passed'] and r['projected_force_limits_passed']
           and r.get('net_ligand_force_limit_passed', True) for r in metrics)
assert all(r['attraction_passed'] and r['repulsion_passed'] for r in signs)
summary = dict(generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    calculation_source_commit='419b64f7bd79199a0bf999e456f1564fc184cf75',
    quantum_count=46, new_quantum_workers=38, chemical_structures=34, numerical_controls=12,
    quantum_numerical_controls_passed=True, chemical_tests_passed=2, independent_audit_performed=False,
    qualification_status='pending independent full-G05 audit',
    charged_wall_hours=state['wall_seconds_debited']/3600,
    new_session_wall_hours=state['sessions'][-1]['wall_seconds']/3600,
    peak_new_worker_rss_gib=max(j['peak_worker_rss_gib'] for j in new_jobs),
    conformer_families=families, contact_families=interaction,
    maxima={k:max((r[k] for r in forces if k in r), default=None) for k in [
        'force_rms_eV_angstrom','force_atom_max_eV_angstrom','projected_rms_eV_angstrom',
        'projected_atom_max_eV_angstrom','net_ligand_force_error_eV_angstrom']},
    numerical_control_maxima={k:max(r[k] for r in controls) for k in [
        'energy_error_kcal_mol','force_rms_eV_angstrom','force_max_eV_angstrom']},
    attraction_sign_checks=sum(r['attraction_required'] for r in signs),
    compressed_repulsion_sign_checks=sum(r['repulsion_required'] for r in signs),
    figure='chemical-reference-results.png',
    model_sha256='165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f')
json_file('results-summary.json', summary)
json_file('cap-parent-force-evidence.json', cap_evidence)
csv_file('chemical-row-metrics.csv', metrics)
csv_file('contact-sign-checks.csv', signs)
csv_file('quantum-job-summary.csv', jobs)
csv_file('quantum-numerical-controls.csv', controls)

plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
fig, axes = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)
names = [r['family'] for r in families]
y = np.arange(len(names))
axes[0,0].barh(y-.16, [r['energy_rms_kcal_mol'] for r in families], height=.3, label='RMS error')
axes[0,0].barh(y+.16, [r['energy_max_kcal_mol'] for r in families], height=.3, label='Maximum error')
axes[0,0].set_yticks(y, names); axes[0,0].set_title('Conformer relative energies')
axes[0,0].set_xlabel('Error (kcal/mol)'); axes[0,0].axvline(1, ls='--', color='gray', label='RMS limit 1')
axes[0,0].axvline(2, ls=':', color='black', label='Maximum limit 2'); axes[0,0].legend(fontsize=7)
names = [r['family'] for r in interaction]; y = np.arange(len(names))
axes[0,1].barh(y-.16,[r['contact_minus_separated_rms'] for r in interaction],height=.3,label='RMS error')
axes[0,1].barh(y+.16,[r['contact_minus_separated_max'] for r in interaction],height=.3,label='Maximum error')
axes[0,1].set_yticks(y,names); axes[0,1].set_title('Contact minus separated energies')
axes[0,1].set_xlabel('Error (kcal/mol)'); axes[0,1].axvline(.5,ls='--',color='gray',label='RMS limit 0.5')
axes[0,1].axvline(1,ls=':',color='black',label='Maximum limit 1'); axes[0,1].legend(fontsize=7)
x = np.arange(34)
axes[1,0].plot(x,[r['force_rms_eV_angstrom']/.05 for r in forces],'.',label='Raw RMS / 0.05')
axes[1,0].plot(x,[r['force_atom_max_eV_angstrom']/.15 for r in forces],'.',label='Raw maximum / 0.15')
axes[1,0].axhline(1,ls='--',color='black'); axes[1,0].set_ylim(0,1.1)
axes[1,0].set_title('All 34 structures: Cartesian force errors'); axes[1,0].set_xlabel('Structure index (capture order)')
axes[1,0].set_ylabel('Error / declared limit'); axes[1,0].legend(fontsize=7)
x=np.arange(20)
axes[1,1].plot(x,[r['net_ligand_force_error_eV_angstrom']/.05 for r in contacts['forces']],'.',ms=7)
axes[1,1].axhline(1,ls='--',color='black'); axes[1,1].set_ylim(0,1.1)
axes[1,1].set_title('All 20 contacts/controls: net ligand force error'); axes[1,1].set_xlabel('Contact index (capture order)')
axes[1,1].set_ylabel('Vector error / 0.05 eV/angstrom')
fig.suptitle('MACE-OFF23-small vs frozen omega-B97M-D3(BJ)/def2-TZVPPD references\nCPU float64; actual calculations; independent audit pending',fontsize=12)
fig.savefig(evidence/'chemical-reference-results.png',dpi=180)
fig.savefig(evidence/'chemical-reference-results.pdf')
plt.close(fig)

lines=['# G05 actual chemical-reference results', '',
 'All 46 required quantum calculations, all 12 numerical controls and both G05-T4 chemical checks passed. '
 'This is worker evidence; independent full-G05 audit and gate acceptance remain pending.', '',
 'The unchanged academic MACE-OFF23-small checkpoint uses CPU float64, Default head and total `energy`. '
 'The references are restricted omega-B97M-D3(BJ)/def2-TZVPPD with Psi4 1.10.2/LibXC 7.0.0 and frozen basis/settings hashes. '
 'The 34 exact inputs are neutral singlet C/H/N/O structures. A contacting pair is evaluated as one joint graph.', '',
 'Matching the named training-reference level establishes neither identical training numerics nor that these inputs were absent from training. '
 'These results cover the frozen small nonperiodic capped systems; broader chemistry, GPU, periodic/electrostatic physics, protein binding and ABFE/RBFE remain unqualified.', '',
 '## Energy errors', '', '| Conformer family | RMS (kcal/mol) | Maximum (kcal/mol) |', '|---|---:|---:|']
lines += [f"| {r['family']} | {r['energy_rms_kcal_mol']:.6f} | {r['energy_max_kcal_mol']:.6f} |" for r in families]
lines += ['', 'Declared conformer limits: RMS 1 and maximum 2 kcal/mol. Zeros are the frozen within-composition family baselines.', '',
 '| Contact family | Interaction RMS | Interaction maximum | Contact-minus-separated RMS | Contact-minus-separated maximum |', '|---|---:|---:|---:|---:|']
lines += [f"| {r['family']} | {r['interaction_rms']:.6f} | {r['interaction_max']:.6f} | {r['contact_minus_separated_rms']:.6f} | {r['contact_minus_separated_max']:.6f} |" for r in interaction]
lines += ['', 'All contact errors are kcal/mol; limits are RMS 0.5 and maximum 1. '
 'Interaction energies use the exact-coordinate uncorrected supermolecule-minus-monomers convention. '
 'Separated comparisons use identical composition; no absolute cross-composition energy comparison is made.', '',
 '## Force and numerical-control maxima', '', '| Check | Observed maximum | Declared limit |', '|---|---:|---:|']
for label,key,limit in [('Raw component RMS','force_rms_eV_angstrom',.05),('Raw atom-vector error','force_atom_max_eV_angstrom',.15),
                       ('Projected full-parent component RMS','projected_rms_eV_angstrom',.05),('Projected full-parent atom-vector error','projected_atom_max_eV_angstrom',.15),
                       ('Net ligand interaction-force vector error','net_ligand_force_error_eV_angstrom',.05)]:
    lines.append(f"| {label} (eV/angstrom) | {summary['maxima'][key]:.8f} | {limit} |")
for label,key,limit in [('Numerical-control energy (kcal/mol)','energy_error_kcal_mol',.02),('Numerical-control force RMS (eV/angstrom)','force_rms_eV_angstrom',.002),('Numerical-control atom-vector force (eV/angstrom)','force_max_eV_angstrom',.005)]:
    lines.append(f"| {label} | {summary['numerical_control_maxima'][key]:.9f} | {limit} |")
lines += ['', f"All {summary['attraction_sign_checks']} required attraction signs and {summary['compressed_repulsion_sign_checks']} compressed repulsion signs passed. Every contact, including weak contacts, is retained in [the sign table](contact-sign-checks.csv).", '',
 'Both cap-parent derivatives and all ligand forces are retained. [Full cap/parent force evidence](cap-parent-force-evidence.json) '
 'reconstructs the independent oracle projections and agrees with captured test metrics to 1e-12 eV/angstrom; this is report analysis, not another production force projection.', '',
 '## Runtime and reproducibility', '',
 f"The 38 resumed workers all exited zero. Eight historical records were reused by exact SHA-256; their coordinator exit statuses were not invented. "
 f"The cumulative debit is {summary['charged_wall_hours']:.6f} h including {state['prior_wall_seconds']/3600:.6f} h for the prior launch-to-stop interval. "
 f"The resumed session used {summary['new_session_wall_hours']:.6f} h, two threads and 3 GiB Psi4 memory under the approved 5 GiB allocation cap. "
 f"Maximum new-worker RSS was {summary['peak_new_worker_rss_gib']:.6f} GiB. Total cgroup usage includes cache and reached its 8 GiB cap; zero OOM/OOM-kill events were recorded. "
 'Every private scratch directory was cleaned after saving its record/receipt.', '',
 'All 46 actual Psi4 logs explicitly record energy/wavefunction convergence. See [job identities and timings](quantum-job-summary.csv), '
 '[all 34 row metrics](chemical-row-metrics.csv), [all 12 numerical controls](quantum-numerical-controls.csv), '
 '[raw comparison captures](chemical-comparisons/) and [bundle validation](quantum-bundle-validation.json). '
 'Record/input/source hashes and immutable job orders/receipts are retained with the complete generation attempt.', '',
 '![Actual energy and force errors](chemical-reference-results.png)', '',
 'The [PDF figure](chemical-reference-results.pdf) is exportable. The source suite and audit handoff are recorded in the [worker log](../../Gate_05_v4_worker.md).', '']
(evidence/'RESULTS.md').write_text('\n'.join(lines))
print(json.dumps({k:v for k,v in summary.items() if k not in ('conformer_families','contact_families')},indent=2))
