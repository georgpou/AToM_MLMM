"""Read-only actual admission and single-contact arithmetic, plus plain MM XML.

No model/QM imports or calls. All outputs stay in this independent directory.
"""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import datetime as dt
import hashlib
import json
import math
import re
import subprocess
import sys
import numpy as np
import openmm as mm
from openmm import unit

E = Path(__file__).resolve().parent
R = E.parents[3]
V2 = R/'Worker_Log/Milestone_03/evidence/G07_v2'
ACTUAL = V2/'quantum-attempt-v1'
ROW = 'ethanol-methanol-d3-r0'
PILOT = ROW+'--full-parent'
sys.path.insert(0, str(R/'tools'))
import resume_joint_quantum as joint

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text())

def put(name, data):
    with (E/name).open('x') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')

started = dt.datetime.now(dt.timezone.utc).isoformat()
original = ACTUAL/'jobs'/PILOT/'attempt-0001'
correction = original.parent/'attempt-0002'
initial = read(R/'Worker_Log/Milestone_03/evidence/G07_v2_revalidation_independent/source-check-initial.json')
original_hashes = {p.name:sha(p) for p in original.iterdir() if p.is_file()}
progress_hash = sha(ACTUAL/'progress.json')
state = read(ACTUAL/'progress.json')
old_receipt, new_receipt = read(original/'receipt.json'), read(correction/'receipt.json')
note = read(correction/'revalidation.json')
assert original_hashes == initial['actual_attempt_hashes']
assert sha(original/'receipt.json') == joint.REJECTED_PILOT_RECEIPT_SHA256
copied = {}
for path in original.iterdir():
    assert path.is_file() and not path.is_symlink()
    name = 'original-receipt.json' if path.name == 'receipt.json' else path.name
    assert path.read_bytes() == (correction/name).read_bytes()
    copied[name] = sha(path)
expected = dict(old_receipt)
expected.pop('validation_error')
expected.update(completion_kind='validation_only_correction',
    original_receipt_sha256=sha(original/'receipt.json'), original_receipt_path=str(original/'receipt.json'),
    revalidated_utc=note['revalidated_utc'])
expected['diagnostic_sha256'] = dict(copied, **{'revalidation.json':sha(correction/'revalidation.json')})
assert expected == new_receipt
assert note['copied_file_sha256'] == copied
assert note['validator_source_sha256'] == sha(R/'tools/resume_joint_quantum.py')
assert len(state['record_hashes']) == 1 and len(state['expected_names']) == 30
assert state['record_hashes'][PILOT] == sha(correction/'record.json')
provenance = state['provenance'][PILOT]
assert provenance['source'] == str(correction/'record.json')
assert provenance['receipt_sha256'] == sha(correction/'receipt.json')
assert provenance['recovered'] is True and provenance['coordinator_exit'] == 0
for suffix in ('.json', '.psi4.txt', '.psi4.log'):
    assert (ACTUAL/'records'/(PILOT+suffix)).read_bytes() == (correction/('record'+suffix)).read_bytes()
assert len(state['sessions']) == 2 and all(s['status'] == 'finished' for s in state['sessions'])
assert state['sessions'][-1]['stop_reason'] == 'pilot_assessment_pending'
debit = state['prior_wall_seconds'] + sum(s['wall_seconds'] for s in state['sessions'])
assert debit == state['wall_seconds_debited']
old_debit = read(R/'Worker_Log/Milestone_03/evidence/G07_v2_revalidation_independent/probes-durable/successful-idempotent-promotion/output/progress.json')['sessions'][0]['wall_seconds']
assert state['sessions'][0]['wall_seconds'] == old_debit
assert debit-old_debit == state['sessions'][-1]['wall_seconds']
assert state['remaining_wall_seconds'] == 86400-debit
assert not joint.recovery.attempt_processes(ACTUAL)
assert not joint.recovery.group_members(read(original/'worker-identity.json')['pid'])
assert not list(ACTUAL.glob('jobs/*/attempt-*/scratch'))
assert sorted(p.name for p in original.parent.iterdir()) == ['attempt-0001','attempt-0002']
v3 = R/'Worker_Log/Milestone_03/Gate_07_v3_audit.md'
assert sha(v3) == '102f678257013779989ca400a4a1fb42645f55e154af685e319ff81894b15ff5'
applied = read(V2/'actual-revalidation-result.json')
assert applied['progress_sha256'] == progress_hash
assert applied['pilot']['pilot_receipt_sha256'] == sha(correction/'receipt.json')

report = read(V2/'pilot-force-comparison.json')
for name, digest in report['source_sha256'].items():
    assert sha(R/name) == digest, name
assert sha(V2/'compare_pilot_forces.py') == report['script_sha256']
manifest = read(R/'fixtures/fragment_ligand/descriptions-v1/manifest.json')
descriptions = {d['description']:d for d in manifest['rows'] if d['row'] == ROW}
desc = descriptions['baseline']
bundle_path = R/'fixtures/fragment_ligand/descriptions-v1'/desc['artifact']
assert sha(bundle_path) == desc['artifact_sha256']
bundle = read(bundle_path)['data']
retained_xml = bundle['manifest']['retained_mm_xml']
assert hashlib.sha256(retained_xml.encode()).hexdigest() == desc['retained_mm_sha256']
assert sha(R/'fixtures/fragment_ligand/prepared-mm-v1/ethanol-methanol.xml') == desc['prepared_mm_sha256']
ids = desc['real_atom_ids']
real = np.asarray(desc['positions_nm'])
index = {a:i for i,a in enumerate(ids)}
links = [l['data'] for l in desc['links']]
assert len(links) == 1
link, = links
a, b = index[link['ml_parent_id']], index[link['mm_parent_id']]
v = real[b]-real[a]
length = np.linalg.norm(v)
site = real[a]+link['distance_nm']*v/length
Jb = link['distance_nm']*(np.eye(3)/length-np.outer(v,v)/length**3)
J = np.zeros((len(desc['model_input_ids'])*3, len(ids)*3))
for k, atom_id in enumerate(desc['model_input_ids']):
    if atom_id in index:
        J[3*k:3*k+3,3*index[atom_id]:3*index[atom_id]+3] = np.eye(3)
    else:
        assert atom_id == link['cap_id']
        J[3*k:3*k+3,3*a:3*a+3] = np.eye(3)-Jb
        J[3*k:3*k+3,3*b:3*b+3] = Jb
finite_differences = {}
for step in (1e-5,1e-6,1e-7):
    worst = 0.
    for parent in (a,b):
        for axis in range(3):
            moved = real.copy(); moved[parent,axis] += step
            vv = moved[b]-moved[a]; plus = moved[a]+link['distance_nm']*vv/np.linalg.norm(vv)
            moved[parent,axis] -= 2*step
            vv = moved[b]-moved[a]; minus = moved[a]+link['distance_nm']*vv/np.linalg.norm(vv)
            analytic = (np.eye(3)-Jb if parent == a else Jb)[:,axis]
            worst = max(worst,float(np.max(np.abs((plus-minus)/(2*step)-analytic))))
    finite_differences[str(step)] = worst
assert finite_differences['1e-06'] < 1e-8
base_path = R/'Worker_Log/Milestone_03/evidence/G07_v1/fifty-description-single-points'/(ROW+'--baseline.json')
base = read(base_path)
raw = base['native_raw_model']
model_x = np.asarray(raw['positions_nm'])
for k, atom_id in enumerate(desc['model_input_ids']):
    assert np.max(np.abs(model_x[k]-(real[index[atom_id]] if atom_id in index else site))) < 1e-13
qcap = read(R/'fixtures/chemical_reference_v3/quantum/records'/(ROW+'.json'))
qfull = read(correction/'record.json')
settings = read(R/'fixtures/chemical_reference_v3/reference-settings.json')
ev_kj = 1.6021766208e-19*6.022140857e23/1000.
q_to_force = settings['hartree_to_kJ_mol']/(settings['bohr_to_nm']*10*ev_kj)
cap_x = np.asarray(qcap['positions_angstrom'])/10
cap_order = []
for xyz, number in zip(model_x, raw['numbers'], strict=True):
    matches = [i for i,point in enumerate(cap_x) if qcap['atomic_numbers'][i] == number and np.max(np.abs(point-xyz)) < 1e-13]
    assert len(matches) == 1
    cap_order.extend(matches)
assert len(set(cap_order)) == len(cap_order)
cap_raw = -np.asarray(qcap['gradient_hartree_bohr'])[cap_order]*q_to_force
mace_raw = -np.asarray(raw['gradient_eV_angstrom'])
pm = (J.T@mace_raw.ravel()).reshape(real.shape)
pq = (J.T@cap_raw.ravel()).reshape(real.shape)
full_job = next(j for j in read(R/'fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json')['new_jobs'] if j['name'] == PILOT)
assert ['a:'+name if name.startswith('l') else name for name in full_job['atom_ids']] == ids
assert np.max(np.abs(np.asarray(qfull['positions_angstrom'])/10-real)) < 1e-13
qf = -np.asarray(qfull['gradient_hartree_bohr'])*q_to_force
hybrid = np.asarray(base['hybrid_real_forces_kj_mol_nm'])/(10*ev_kj)
mm_subtraction = hybrid-pm

# Plain Reference evaluation of the exact frozen retained-MM XML, no PythonForce.
system = mm.XmlSerializer.deserialize(retained_xml)
assert all(type(f) in (mm.HarmonicBondForce,mm.HarmonicAngleForce,mm.PeriodicTorsionForce,mm.RBTorsionForce,mm.NonbondedForce) for f in system.getForces())
positions = np.zeros((system.getNumParticles(),3))
for atom_id, final in bundle['real_to_final'].items():
    positions[final] = real[index[atom_id]]
for i, force in enumerate(system.getForces()):
    force.setForceGroup(i)
integrator = mm.VerletIntegrator(.0005)
context = mm.Context(system, integrator, mm.Platform.getPlatformByName('Reference'))
context.setPositions(positions*unit.nanometer)
context.computeVirtualSites()
full_state = context.getState(getForces=True,getEnergy=True)
all_mm = full_state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer)
real_order = [bundle['real_to_final'][name] for name in ids]
mm_force = np.asarray(all_mm[real_order])/(10*ev_kj)
groups = []
group_sum = np.zeros_like(mm_force)
for i, force in enumerate(system.getForces()):
    group_state = context.getState(getForces=True,getEnergy=True,groups=1<<i)
    gf = group_state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer)[real_order]/(10*ev_kj)
    group_sum += gf
    groups.append(dict(class_name=type(force).__name__,energy_kj_mol=float(group_state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)),maximum_atom_force_eV_angstrom=float(np.max(np.linalg.norm(gf,axis=1)))))
mm_difference = float(np.max(np.abs(mm_force-mm_subtraction)))
assert mm_difference < 1e-9
assert float(np.max(np.abs(group_sum-mm_force))) < 1e-12
del context, integrator
arrays = dict(full_qm=qf,projected_cap_qm=pq,projected_mace=pm,all_retained_mm=mm_subtraction,
    model_error=pm-pq,partition_error=pq+mm_subtraction-qf,hybrid_error=hybrid-qf)
residual = float(np.max(np.abs(arrays['model_error']+arrays['partition_error']-arrays['hybrid_error'])))
assert residual < 1e-13
array_differences = {name:float(np.max(np.abs(values-np.asarray(report['arrays_eV_angstrom'][name])))) for name,values in arrays.items()}
assert max(array_differences.values()) < 1e-12
ligand = [index[name] for name in ids if name.startswith('a:')]
limits = dict(component_rms_eV_angstrom=.05,maximum_atom_vector_eV_angstrom=.15,net_ligand_vector_eV_angstrom=.05)
assert report['unchanged_force_limits'] == limits

def metrics(error):
    values = dict(component_rms_eV_angstrom=float(np.linalg.norm(error)/math.sqrt(error.size)),
        maximum_atom_vector_eV_angstrom=float(np.max(np.linalg.norm(error,axis=1))),
        net_ligand_vector_eV_angstrom=float(np.linalg.norm(np.sum(error[ligand],axis=0))))
    return dict(values,within_each_existing_force_limit={k:values[k] <= lim for k,lim in limits.items()})

uncut = read(R/'Worker_Log/Milestone_03/evidence/G07_v1/fifty-description-single-points'/(ROW+'--uncut.json'))['native_raw_model']
full_mace = np.zeros_like(real)
for atom_id, gradient in zip(descriptions['uncut']['model_input_ids'],uncut['gradient_eV_angstrom'],strict=True):
    full_mace[index[atom_id]] = -np.asarray(gradient)
errors = dict(projected_mace_minus_same_cap_qm=arrays['model_error'],
    capped_qm_plus_all_retained_mm_minus_full_qm=arrays['partition_error'],
    baseline_hybrid_minus_full_qm=arrays['hybrid_error'],full_mace_minus_full_qm=full_mace-qf)
derived_metrics = {name:metrics(values) for name,values in errors.items()}
for name,values in derived_metrics.items():
    for key, value in values.items():
        assert value == report[name][key] if isinstance(value,dict) else abs(value-report[name][key]) < 1e-12
separated = read(R/'Worker_Log/Milestone_03/evidence/G07_v1/fifty-description-single-points/ethanol-methanol-separated--baseline.json')['native_raw_model']
separated_qm = read(R/'fixtures/chemical_reference_v3/quantum/records/ethanol-methanol-separated.json')
model_contact = (raw['energy_kj_mol']-separated['energy_kj_mol'])/4.184
qm_contact = (qcap['energy_hartree']-separated_qm['energy_hartree'])*settings['hartree_to_kJ_mol']/4.184
energy = dict(mace=model_contact,qm=qm_contact,error=model_contact-qm_contact)
assert energy == report['baseline_same_cap_contact_minus_separated_kcal_mol']

# Independent Gaussian-shell counts, never importing Psi4.
def counts(path):
    result = {}; element = None
    for rawline in Path(path).read_text().splitlines():
        line = rawline.strip()
        head = re.fullmatch(r'([A-Za-z]{1,2})\s+0',line)
        if head:
            element = head[1];result[element] = 0
        elif line == '****':
            element = None
        elif element in ('H','C','N','O'):
            shell = re.match(r'^([SPDFGHI]+)\s+\d+\s+',line)
            if shell:
                result[element] += sum(2*'SPDFGHI'.index(symbol)+1 for symbol in shell[1])
    return {element:result[element] for element in ('H','C','N','O')}

basis_dir = Path('/workspace/atom-mlmm-g07/reference-env/share/psi4/basis')
for name, digest in settings['basis_file_sha256'].items():
    assert sha(basis_dir/name) == digest
orbital, auxiliary = counts(basis_dir/'def2-tzvppd.gbs'), counts(basis_dir/'def2-universal-jkfit.gbs')
basis_screen = read(V2/'basis-and-auxiliary-size-screen.json')
assert orbital == basis_screen['basis_spherical_counts'] and auxiliary == basis_screen['auxiliary_spherical_counts']
matrix = read(R/'fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json')
numbers = {1:'H',6:'C',7:'N',8:'O'}
pilot_orb = sum(orbital[numbers[n]] for n in full_job['atomic_numbers'])
pilot_aux = sum(auxiliary[numbers[n]] for n in full_job['atomic_numbers'])
row_by_name = {j['name']:j for j in basis_screen['jobs']}
sizes = []
for job in matrix['new_jobs']:
    norb = sum(orbital[numbers[n]] for n in job['atomic_numbers'])
    naux = sum(auxiliary[numbers[n]] for n in job['atomic_numbers'])
    recorded = row_by_name[job['name']]
    assert Counter(numbers[n] for n in job['atomic_numbers']) == recorded['composition']
    assert norb == recorded['spherical_basis_functions'] and naux == recorded['auxiliary_basis_functions']
    ratio = naux*norb*norb/(pilot_aux*pilot_orb*pilot_orb)
    assert abs(ratio-recorded['three_index_size_ratio_vs_pilot']) < 1e-14
    if job['name'] not in state['record_hashes']:
        sizes.append((job,norb,naux,ratio))
assessment = read(V2/'pilot-assessment.json')
for key, value in joint.pilot_evidence(ACTUAL).items():
    assert assessment[key] == value
assert assessment['progress_sha256'] == progress_hash
assert assessment['basis_sizing_sha256'] == sha(V2/'basis-and-auxiliary-size-screen.json')
assert assessment['continue_authorized'] is False
wall_floor = 2*new_receipt['wall_seconds']*sum((sum(job['atomic_numbers'])/sum(full_job['atomic_numbers']))**3 for job,_,_,_ in sizes)
scratch_estimate = math.ceil(assessment['pilot_scratch_peak_bytes']*max(s[3] for s in sizes))
rss_estimate = math.ceil(new_receipt['sampled_rss_peak_bytes']*max(s[1]/pilot_orb for s in sizes)**2)
assert abs(wall_floor-assessment['projected_remaining_worker_seconds']) < 1e-8
assert scratch_estimate == assessment['projected_scratch_bytes'] and rss_estimate == assessment['projected_max_rss_bytes']
assert wall_floor > state['remaining_wall_seconds']
assert scratch_estimate+assessment['guards']['disk_min_bytes'] > assessment['resources_at_assessment']['disk_free_bytes']
approval = read(V2/'authorization.json')
false_error = None
try:
    joint.validate_assessment(V2/'pilot-assessment.json',ACTUAL,approval,matrix)
except ValueError as error:
    false_error = str(error)
assert false_error == 'measured pilot assessment identities or values differ'
flipped = dict(assessment,continue_authorized=True)
put('true-flag-assessment-probe.json',flipped)
true_error = None
with patch.object(joint.recovery,'measurements',lambda:assessment['resources_at_assessment']):
    try:
        joint.validate_assessment(E/'true-flag-assessment-probe.json',ACTUAL,approval,matrix)
    except ValueError as error:
        true_error = str(error)
assert true_error == 'pilot projections exceed the remaining resource/budget envelope'
assert original_hashes == {p.name:sha(p) for p in original.iterdir() if p.is_file()}
assert progress_hash == sha(ACTUAL/'progress.json')
assert not any(name in sys.modules for name in ('torch','mace','psi4'))
peak_atoms = {name:ids[int(np.argmax(np.linalg.norm(values,axis=1)))] for name,values in errors.items()}
put('independent-result.json',dict(started_utc=started,finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
    reviewer_model='gpt-6.1-sol',reasoning_effort='max',execution_source_commit='fcc1de9619f58934ff0c5835e01ecf3848a8a48c',
    observed_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
    source_sha256=dict(report['source_sha256'],**{str(bundle_path.relative_to(R)):sha(bundle_path)}),
    comparison_sha256=sha(V2/'pilot-force-comparison.json'),comparison_script_sha256=report['script_sha256'],
    assessment_sha256=sha(V2/'pilot-assessment.json'),correction_receipt_sha256=sha(correction/'receipt.json'),
    original_bytes_unchanged=True,correction_exact_original_derived=True,provenance_valid=True,
    admitted_count=1,remaining_count=29,worker_launches_before_and_after=1,validation_only_attempts=1,
    wall_seconds_debited=debit,coordinator_only_addition=state['sessions'][-1]['wall_seconds'],
    remaining_wall_seconds=state['remaining_wall_seconds'],progress_sha256=progress_hash,
    live_worker_groups=[],scratch_absent=True,prior_v3_audit_unchanged=True,
    independently_matched_array_max_differences=array_differences,cap_jacobian_fd_max_errors=finite_differences,
    cap_parents=[ids[a],ids[b]],cap_applied_once=True,full_real_force_rows=len(ids),
    mm_source='exact frozen retained_mm_xml; OpenMM Reference double, no model forces',
    retained_mm_sha256=desc['retained_mm_sha256'],retained_mm_subtraction_max_difference_eV_angstrom=mm_difference,
    retained_mm_force_groups=groups,force_decomposition_max_residual_eV_angstrom=residual,
    unchanged_force_limits=limits,metrics=derived_metrics,maximum_error_atom_ids=peak_atoms,
    baseline_same_cap_contact_minus_separated_kcal_mol=energy,full_parent_separated_energy_reference_absent=True,
    orbital_spherical_counts=orbital,auxiliary_spherical_counts=auxiliary,
    pilot_basis_counts=dict(orbital=pilot_orb,auxiliary=pilot_aux),basis_jobs_checked=len(row_by_name),
    projected_remaining_worker_seconds=wall_floor,projected_remaining_hours=wall_floor/3600,
    projected_max_rss_bytes=rss_estimate,projected_scratch_bytes=scratch_estimate,
    scratch_plus_reserve_bytes=scratch_estimate+assessment['guards']['disk_min_bytes'],
    assessment_free_disk_bytes=assessment['resources_at_assessment']['disk_free_bytes'],
    continue_authorized=False,false_flag_rejection=false_error,true_flag_rejection=true_error,
    no_heavy_model_or_qm_imports=True,actual_original_and_ledger_unchanged_by_auditor=True,
    verdict='accepted_for_scope: actual admission, one-contact arithmetic and stop assessment; physical acceptance blocked'))
print(json.dumps(dict(admitted=1,remaining=29,mm_max_difference=mm_difference,identity_residual=residual,
    metrics=derived_metrics,energy=energy,maximum_error_atoms=peak_atoms,
    runtime_hours=wall_floor/3600,remaining_hours=state['remaining_wall_seconds']/3600,
    scratch_plus_reserve_gib=(scratch_estimate+assessment['guards']['disk_min_bytes'])/2**30,
    free_disk_gib=assessment['resources_at_assessment']['disk_free_bytes']/2**30,
    false_flag_rejected=true_error is not None and false_error is not None),indent=2))
