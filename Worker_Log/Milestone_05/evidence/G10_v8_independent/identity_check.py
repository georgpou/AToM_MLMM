"""Focused read-only byte checks for reuse of the completed independent audit."""
import ast
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path('/workspace/AToM_MLMM-g10'); HERE=Path(__file__).resolve().parent
PACKET=ROOT/'Worker_Log/Milestone_05/evidence/G10_v8_review_packet'
BASE='263a4199a8835b9eef59fc8e33c463cb6ddd669d'
HEAD='2be9334aea5c8fc34a4bb7ca0ebf6c46802aee27'
sha=lambda payload:hashlib.sha256(payload).hexdigest()
git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT)
assert git('rev-parse','HEAD').decode().strip()==HEAD
raw=gzip.decompress((PACKET/'compact-clock-diff.patch.gz').read_bytes())
assert raw==git('diff',BASE,'8bc2ced1d7f88e6503ec0b809e309456c307d786','--','src','tests')
assert len(raw)==10069 and sha(raw)=='7cf58fdf7df304188a593e5047d4846636a6e2e422cf785776ae9ec863251807'
path='src/atm_mlmm/exchange_journal.py'
old=ast.parse(git('show',BASE+':'+path)); current=ast.parse((ROOT/path).read_text())
for module in (old,current):
    module.body=[node for node in module.body if not (isinstance(node,ast.FunctionDef) and node.name=='_validate_expected_clock')]
assert ast.dump(old)==ast.dump(current)
names=git('diff',BASE,HEAD,'--name-only').decode().splitlines()
assert all(name in (path,'tests/workflow/test_persistent_exchange.py','docs/project-0/STATUS.md',
                   'Worker_Log/Milestone_05/Gate_10_v8_worker.md') or name.startswith(
                   ('Worker_Log/Milestone_05/evidence/G10_v8/','Worker_Log/Milestone_05/evidence/G10_v8_review_packet/')) for name in names)
frozen=json.loads((PACKET/'frozen-source-test-sha256.json').read_text())
assert len(frozen)==105
for name,digest in frozen.items(): assert sha((ROOT/name).read_bytes())==digest,name
source={p.relative_to(ROOT/'src').as_posix():sha(p.read_bytes()) for p in sorted((ROOT/'src/atm_mlmm').rglob('*.py'))}
assert len(source)==38
submitted=[]
for line in (ROOT/'Worker_Log/Milestone_05/evidence/G10_v8/sha256-manifest.txt').read_text().splitlines():
    digest,name=line.split('  ',1); path=Path(name) if name.startswith('/') else ROOT/name
    assert sha(path.read_bytes())==digest,name; submitted.append(name)
assert len(submitted)==14
pilot=[]
for line in (ROOT/'Worker_Log/Milestone_05/evidence/G10_v8/pilot-artifact-sha256.txt').read_text().splitlines():
    digest,name=line.split('  ',1); path=Path(name)
    if not path.is_absolute(): path=ROOT/path
    assert sha(path.read_bytes())==digest,name; pilot.append(name)
assert len(pilot)==958
bundles=sorted(Path('/workspace/G10_v8_artifacts/v8-attempt-001').glob('*/*/worker'))
assert len(bundles)==8
for bundle in bundles:
    manifest=json.loads((bundle/'manifest.json').read_text())['files']
    bundled={name[len('runtime/source/'):]:digest for name,digest in manifest.items() if name.startswith('runtime/source/') and name.endswith('.py')}
    assert bundled==source
    for name,digest in manifest.items(): assert sha((bundle/name).read_bytes())==digest
logs={}
for zipped in (ROOT/'Worker_Log/Milestone_05/evidence/G10_v8').glob('*.log.gz'):
    payload=gzip.decompress(zipped.read_bytes()); plain=zipped.with_suffix('')
    assert payload==plain.read_bytes(); logs[plain.name]={'raw_sha256':sha(payload),'tail':payload.decode().splitlines()[-1]}
result=dict(reviewed_head=HEAD,prior_independent_audit=BASE,worker_submission='8bc2ced1d7f88e6503ec0b809e309456c307d786',
            code_result='3f93efa079ae36514d86d34f9dbc263722bcd1cd',compact_diff_bytes=len(raw),compact_diff_sha256=sha(raw),
            only_clock_validator_production_ast_changed=True,protected_old_evidence_science_and_other_code_unchanged=True,
            frozen_hashes=105,submitted_hashes=14,pilot_files=958,bundles=8,source_files=38,source_sha256=source,
            logs=logs,changed_paths=names,auditor_model='gpt-6.1-sol',reasoning_effort='max',
            finished_utc=datetime.now(timezone.utc).isoformat(),exit_status=0)
(HERE/'identity-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','logs','changed_paths')}))
