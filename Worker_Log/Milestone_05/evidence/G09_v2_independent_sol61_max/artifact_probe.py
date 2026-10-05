"""Verify the new pilot capture and the preserved pre-sampling diagnosis."""
from pathlib import Path
import hashlib,json
import numpy as np
from atm_mlmm.persistence import read_sample_chunks

OUT=Path(__file__).resolve().parent
ROOT=Path('/tmp/atm-mlmm-g09-v2-independent-readonly')
evidence=ROOT/'Worker_Log/Milestone_05/evidence/G09_v2'
index=json.loads((evidence/'host-pilot-capture-index.json').read_text())
complete=Path(index['complete_attempt_path'])
for name,digest in index['files'].items():
    data=(evidence/'host-pilot-capture'/name).read_bytes()
    assert hashlib.sha256(data).hexdigest()==digest,name
    assert (complete/name).read_bytes()==data,name
rows=read_sample_chunks(complete/'samples')
assert rows==json.loads((complete/'observations.json').read_text()) and len(rows)==9
assert len({r['sample_id'] for r in rows})==9
for row in rows:
    for key in ('positions_nm','velocities_nm_ps','real_forces_kj_mol_nm'):
        assert np.asarray(row[key]).shape==(48,3) and np.isfinite(row[key]).all()
    assert all(np.isfinite(v) for v in row['raw'].values())
v1=json.loads((ROOT/'Worker_Log/Milestone_05/evidence/G09_v1/host-pilot-capture/summary.json').read_text())
v2=json.loads((complete/'summary.json').read_text())
for key in ('physical_identity','alchemical_identity'):
    assert v1[key]==v2[key]
assert v2['status']=='complete' and v2['binding_result']=='not_evaluated'
diagnostic=json.loads((evidence/'prepared-start-diagnostic.json').read_text())
for name,pair in diagnostic['different_prepared_artifacts'].items():
    assert pair['complete']!=pair['interrupted']
    for attempt,digest in pair.items():
        path=Path('/tmp/g09-r1-green/test_interrupted_actual_worker0')/attempt/name
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
assert (OUT/'integration_failure_probe.py').read_bytes()==(ROOT/'Worker_Log/Milestone_05/evidence/G09_v1_independent_sol61_max/integration_failure_probe.py').read_bytes()
report=dict(captured_files_verified=len(index['files']),pilot_samples=9,pilot_arrays_finite=True,
            unchanged_physical_identity=v2['physical_identity'],unchanged_alchemical_identity=v2['alchemical_identity'],
            differing_prepared_hashes_independently_verified=6,original_reproducer_bytes_unchanged=True)
(OUT/'artifact-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
