"""Read-only verification of the frozen submission and local portable attempts."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
from atm_mlmm.schema import from_json
from atm_mlmm.schedule import reduced_potentials

root = Path(__file__).resolve().parents[4]
evidence = root/'Worker_Log/Milestone_05/evidence'
head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
assert head == 'b11c16750ad111a2fcafcda7a2d51c6690254e97'
result = {'reviewed_head':head}
tested = '5645db24f707adbdaff34dc7de6ac04b518d7d6b'
scientific = json.loads((evidence/'G09_v3/scientific-source-input-manifest.json').read_text())
for name,digest in scientific.items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest() == digest, name
    assert hashlib.sha256(subprocess.check_output(['git','show',f'{tested}:{name}'],cwd=root)).hexdigest() == digest, name
result['scientific_source_input_hashes'] = len(scientific)
for scope in ('G09_v3','G10_v1'):
    lines = (evidence/scope/'file-manifest.sha256').read_text().splitlines()
    for row in lines:
        digest,name = row.split('  ',1)
        assert hashlib.sha256((evidence/scope/name).read_bytes()).hexdigest() == digest, name
    result[scope+'_capture_hashes'] = len(lines)
result['controls'] = {}
for kind in ('abfe','rbfe'):
    attempt = Path('/workspace/cloud-engine-pilots/water-v3')/kind
    metadata = json.loads((attempt/'metadata.json').read_text())
    assert hashlib.sha256((attempt/'metadata.json').read_bytes()).hexdigest() == (attempt/'metadata.sha256').read_text().strip()
    payload = (attempt/'worker/manifest.json').read_bytes()
    assert hashlib.sha256(payload).hexdigest() == metadata['worker_manifest_sha256']
    worker = json.loads(payload)
    for name,digest in worker['files'].items():
        assert hashlib.sha256((attempt/'worker'/name).read_bytes()).hexdigest() == digest, name
    records = from_json((evidence/'G09_v3'/kind/'records.json').read_text())
    observations = json.loads((evidence/'G09_v3'/kind/'observations.json').read_text())
    assert len(observations) == 9
    for row in observations:
        assert np.asarray(row['real_forces_kj_mol_nm']).shape == ((56 if kind == 'abfe' else 65),3)
        assert np.isfinite(row['real_forces_kj_mol_nm']).all()
        np.testing.assert_array_equal(row['box_nm'],np.eye(3)*6.4)
    exchange = json.loads((evidence/'G10_v1'/kind/'exchange-report.json').read_text())
    ex_records = from_json((evidence/'G10_v1'/kind/'records.json').read_text())
    matrix = reduced_potentials(ex_records)[[0,2]][:,[0,2]]
    np.testing.assert_allclose(exchange['reduced_energies'],matrix,atol=1e-8,rtol=0)
    assert exchange['state_ids_after'] == exchange['state_ids_before'][::-1]
    assert exchange['exponent'] == matrix[0,1]+matrix[1,0]-matrix[0,0]-matrix[1,1]
    result['controls'][kind] = {'portable_worker_files':len(worker['files']),
                              'submitted_frames':len(observations),
                              'matrix_shape':list(reduced_potentials(records).shape),
                              'exchange_matrix_and_exponent_match':True}
unchanged = subprocess.check_output(['git','diff','--name-only','8cc7d8a40b15de7c4e1ddc622ef4cb0f8b5ca6d1','HEAD','--',
                                     'Worker_Log/Milestone_03','Worker_Log/Milestone_04',
                                     'fixtures/chemical_references','models','environment'],cwd=root,text=True)
assert not unchanged
result['earlier_scientific_evidence_models_locks_unchanged'] = True
(evidence/'cloud_v3_independent/manifest-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
