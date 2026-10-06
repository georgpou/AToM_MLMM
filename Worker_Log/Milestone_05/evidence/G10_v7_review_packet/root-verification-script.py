from pathlib import Path
import subprocess,hashlib,json,gzip
root=Path('/workspace/AToM_MLMM-g10')
def git(*args):
    return subprocess.check_output(['git','--no-optional-locks',*args],cwd=root,text=True).strip()
head=git('rev-parse','HEAD')
assert git('branch','--show-current')=='g10-engine-next'
assert not git('status','--porcelain'), 'worker must deliver a clean snapshot'
subprocess.run(['git','merge-base','--is-ancestor','2c02cc2713924140a82aefda37fd5885747e5837',head],cwd=root,check=True)
expected=json.loads(Path('/workspace/g10-v7-suite-frozen-source.json').read_text())
for path,digest in expected.items():
    assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest, ('suite source changed',path)
changed=git('diff','--name-only','a90e192ec0d87524e8fbf77a18d62b4b81a37195',head).splitlines()
allowed_source={'src/atm_mlmm/exchange.py','src/atm_mlmm/exchange_journal.py'}
assert all(p in allowed_source for p in changed if p.startswith('src/'))
assert not [p for p in changed if p.startswith(('fixtures/','environment/','models/'))]
assert not git('diff','--name-only','bd44b2c93a5cba40225dba632f0277e535467be9',head,'--','fixtures','environment','models','docs/project-0/specs')
assert not git('diff','--name-only','bfbaa873cf13570313c945a9665f84580dde7439',head,'--','Worker_Log/Milestone_05/Gate_10_v5_audit.md','Worker_Log/Milestone_05/evidence/G10_v5_independent','Worker_Log/Milestone_05/Gate_10_v6_worker.md','Worker_Log/Milestone_05/evidence/G10_v6')
results={'reviewed_head':head,'root_verification_only':True,'suite_source_hashes':expected,'changed_paths':changed,'protected_trees_unchanged':True,'original_audit_and_task_a_immutable':True,'logs':{}}
evidence=root/'Worker_Log/Milestone_05/evidence/G10_v7'
for p in sorted(evidence.glob('*.log*')):
    data=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
    lines=data.decode(errors='replace').splitlines()
    results['logs'][p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(data).hexdigest(),'tail':lines[-3:]}
frozen=Path('/workspace/G10_v7_artifacts/v7-attempt-001')
source={str(p.relative_to(root/'src')):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root/'src').rglob('*.py'))}
bundles=[]
for path in sorted(frozen.rglob('manifest.json')):
    value=json.loads(path.read_text())
    inventory=value.get('files',{})
    if not isinstance(inventory,dict) or not any(k.startswith('runtime/source/') for k in inventory):
        continue
    base=path.parent
    declared={k.removeprefix('runtime/source/'):v for k,v in inventory.items() if k.startswith('runtime/source/')}
    assert declared==source, ('frozen source inventory mismatch',str(base))
    actual={str(p.relative_to(base/'runtime/source')) for p in (base/'runtime/source').rglob('*.py')}
    assert actual==set(source), ('source paths differ',str(base))
    for name,digest in inventory.items():
        assert hashlib.sha256((base/name).read_bytes()).hexdigest()==digest, ('bundle hash mismatch',str(base),name)
    bundles.append({'path':str(base),'source_files':len(declared),'manifest_files':len(inventory)})
assert bundles, 'no current frozen bundles'
results['fresh_frozen_bundles']=bundles
results['protected_source_inventory']=source
pilot_log=Path('/tmp/G10_v7_fresh-v2-pilots.log').read_bytes()
assert gzip.decompress((evidence/'fresh-v2-pilots.log.gz').read_bytes())==pilot_log
suite_log=Path('/tmp/G10_v7_full-cpu-suite.log').read_bytes()
assert gzip.decompress((evidence/'full-cpu-suite.log.gz').read_bytes())==suite_log
assert b'626 passed in 1221.89s' in suite_log
assert b'2 passed in 208.70s' in pilot_log
Path('/workspace/g10-final-worker-root-verification.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'head':head,'changed_paths':len(changed),'verified_frozen_source_files':len(expected),'logs':{k:v['tail'] for k,v in results['logs'].items()}},indent=2))
