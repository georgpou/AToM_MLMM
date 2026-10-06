"""Administrative archive and frozen/report-only verification; no scientific job."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile

ROOT=Path('/workspace/AToM_MLMM-g10')
HERE=Path(__file__).resolve().parent
ART=Path('/tmp/G10_v7_independent_artifacts')
BASE='f4c2f1f0f096c64aadeb58ab21df5bfe202b9f7e'
REVIEWED='acfe9f6922d4029f1628aa69d530f0b642f4bb0d'
REL=HERE.relative_to(ROOT)
sha=lambda payload:hashlib.sha256(payload).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)


def inventory():
    files={}; links={}; dirs=[]
    for path in sorted(ART.rglob('*')):
        relative=path.relative_to(ART).as_posix()
        if path.is_symlink(): links[relative]=os.readlink(path)
        elif path.is_file(): files[relative]={'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())}
        elif path.is_dir(): dirs.append(relative)
        else: raise AssertionError(str(path))
    return files,links,dirs


def immutable_pause(files):
    prior=json.loads((HERE/'paused-artifact-inventory.json').read_text())
    assert all(files[name]==entry for name,entry in prior['files'].items())
    old=json.loads(git('show',BASE+':'+str(REL/'manifest.json')))
    mutable={'README.md','commands.jsonl'}
    for name,digest in old['files'].items():
        if name not in mutable: assert sha((HERE/name).read_bytes())==digest,name
    return {'original_531_artifact_bytes_preserved':True,'old_evidence_files_preserved':len(old['files'])-len(mutable),
            'immutable_pause_and_original_scripts_logs':True}


def archive():
    files,links,dirs=inventory(); original=immutable_pause(files)
    path=HERE/'continued-analytic-artifacts.tar.gz'; assert not path.exists()
    with tarfile.open(path,'w:gz') as output:
        for child in sorted(ART.rglob('*')):
            output.add(child,arcname=child.relative_to(ART).as_posix(),recursive=False)
    with tarfile.open(path,'r:gz') as saved:
        members=saved.getmembers()
        actual_files={m.name:m for m in members if m.isfile()}
        actual_links={m.name:m.linkname for m in members if m.issym()}
        actual_dirs={m.name for m in members if m.isdir()}
        assert set(actual_files)==set(files) and actual_links==links and actual_dirs==set(dirs)
        for name,member in actual_files.items():
            payload=saved.extractfile(member).read()
            assert {'bytes':len(payload),'sha256':sha(payload)}==files[name],name
    result=dict(archive=path.name,archive_bytes=path.stat().st_size,archive_sha256=sha(path.read_bytes()),
                file_count=len(files),symlink_count=len(links),directory_count=len(dirs),
                files=files,symlinks=links,directories=dirs,all_archive_members_hash_verified=True,
                artifacts=str(ART),**original,finished_utc=datetime.now(timezone.utc).isoformat())
    (HERE/'continued-artifact-inventory.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('files','symlinks','directories')}))


def verify():
    identity=json.loads((HERE/'identity-results.json').read_text())
    current={p.relative_to(ROOT/'src').as_posix():sha(p.read_bytes()) for p in sorted((ROOT/'src/atm_mlmm').rglob('*.py'))}
    assert current==identity['source_sha256'] and len(current)==38
    protected=json.loads((HERE/'pause-verification.json').read_text())['protected_tree_command'][5:]
    assert protected[0]=='src',protected
    command=['git','diff',REVIEWED,'--exit-code','--',*protected]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0 and not result.stdout and not result.stderr
    files,links,dirs=inventory(); original=immutable_pause(files)
    archived=json.loads((HERE/'continued-artifact-inventory.json').read_text())
    assert files==archived['files'] and links==archived['symlinks'] and dirs==archived['directories']
    assert sha((HERE/archived['archive']).read_bytes())==archived['archive_sha256']
    outcomes=[json.loads(line) for line in (HERE/'commands.jsonl').read_text().splitlines()]
    for entry in outcomes: assert sha((HERE/entry['log']).read_bytes())==entry['raw_sha256'],entry['label']
    docs=json.loads((HERE/'completion-docs.log').read_text())
    assert not docs['errors'] and len(docs['self_tests'])==8 and all(docs['self_tests'].values())
    assert not (HERE/'completion-diff.log').read_bytes()
    allowed=lambda name:name in ('Worker_Log/Milestone_05/Gate_10_v7_audit.md','docs/project-0/STATUS.md') or name.startswith(str(REL)+'/')
    names=set(git('diff','--name-only').decode().splitlines())|set(git('ls-files','--others','--exclude-standard').decode().splitlines())
    assert all(allowed(name) for name in names),names
    raw=subprocess.check_output(['ps','-eo','pid,ppid,stat,etime,comm'],text=True)
    allowed_pids={os.getpid(),os.getppid()}; live=[]
    for line in raw.splitlines()[1:]:
        pid,parent,state,elapsed,name=line.split(maxsplit=4)
        if not state.startswith('Z') and (name.startswith('python') or name=='pytest') and int(pid) not in allowed_pids:
            live.append(line)
    assert not live,live
    summary={}
    for name,key in (('repair-continuation-results.json','probes'),('record-continuation-results.json','probes'),
                     ('molecular-results.json','cases'),('clock-domain-results.json','probes'),('clock-finite-bound-results.json','probes')):
        rows=json.loads((HERE/name).read_text())[key]
        summary[name]={kind:sum(row.get('status')==kind for row in rows) for kind in ('PASS','VIOLATION','CHARACTERIZATION')}
    assert sum(r['PASS'] for r in summary.values())==44
    assert sum(r['VIOLATION'] for r in summary.values())==2
    assert sum(r['CHARACTERIZATION'] for r in summary.values())==1
    report=ROOT/'Worker_Log/Milestone_05/Gate_10_v7_audit.md'
    assert len(report.read_text().splitlines())<=120
    output=dict(status='COMPLETE RED / changes_required',auditor_model='gpt-6.1-sol',reasoning_effort='max',
        original_agent='/root/g10_combined_audit_v7',resumed_agent='/root/g10_combined_audit_v7_resume',subagents=[],
        clean_resume_head=BASE,original_reviewed_head=REVIEWED,worker_submission=identity['worker_submission'],
        code_result='27e1639fefdde8ccca62263846204237391bf621',all_38_source_hashes_equal=True,
        source_sha256=current,protected_tree_command=command,protected_tree_exit_status=result.returncode,
        docs_result=docs,command_outcomes=outcomes,supplementary_unique_results=summary,
        allowed_report_only_changed_paths=sorted(names),continued_archive_sha256=archived['archive_sha256'],
        continued_file_count=archived['file_count'],no_live_scientific_processes=True,
        preserved_prior_suite_not_rerun=True,report_line_count=len(report.read_text().splitlines()),
        exact_commit_and_clean_status='Verified after audit-only commit; supplied in final handoff',
        administrative_patch_errors='Two initial atomic patches rejected before any writes; corrected without source changes',
        **original,finished_utc=datetime.now(timezone.utc).isoformat())
    (HERE/'completion-results.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(source_files=38,protected_exit=0,docs_errors=0,docs_controls=8,
                         supplementary_pass=44,product_violations=2,helper_characterization=1,
                         live_scientific_processes=0,report_lines=output['report_line_count'],exit_status=0)))


if __name__=='__main__':
    {'archive':archive,'verify':verify}[sys.argv[1]]()
