"""Independent correction safety checks on isolated copies; no QM launches.

Every real artifact is copied into this audit directory before any mutation.
The canonical original and ledger are read-only and hash-checked afterward.
"""
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys

EVIDENCE=Path(__file__).resolve().parent
REPO=EVIDENCE.parents[3]
ACTUAL=REPO/'Worker_Log/Milestone_03/evidence/G07_v2/quantum-attempt-v1'
PLAN=REPO/'fixtures/chemical_reference_v3'
MATRIX=REPO/'fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json'
AUTH=REPO/'Worker_Log/Milestone_03/evidence/G07_v2/authorization.json'
REFERENCE='/workspace/atom-mlmm-g07/reference-env/bin/python'
REAL_POPEN=subprocess.Popen


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n')


class InjectedCrash(Exception):pass


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-root',type=Path,default=EVIDENCE/'source-final')
    parser.add_argument('--label',default='final')
    options=parser.parse_args();source_root=options.source_root.resolve()
    sys.path[:0]=[str(source_root/'tools'),str(REPO/'src')]
    import resume_joint_quantum as joint
    root=EVIDENCE/('probes-'+options.label);root.mkdir()
    original=ACTUAL/'jobs'/joint.PILOT/'attempt-0001'
    canonical_hashes={p.name:sha(p) for p in original.iterdir() if p.is_file()}
    canonical_progress=sha(ACTUAL/'progress.json')
    receipt_pin=joint.REJECTED_PILOT_RECEIPT_SHA256
    real_approval=json.loads(AUTH.read_text());matrix=json.loads(MATRIX.read_text())
    settings=json.loads((PLAN/'reference-settings.json').read_text())
    order=joint.joint_queue(matrix,settings)[joint.PILOT]
    results={'utc_started':dt.datetime.now(dt.timezone.utc).isoformat(),
        'source_sha256':sha(source_root/'tools/resume_joint_quantum.py'),
        'notice':'Isolated actual-data copies; no actual ledger/attempt writes and no QM launches',
        'checks':{},'worker_launch_calls':0,'harmless_live_processes':0}

    def forbidden(*args,**kwargs):
        results['worker_launch_calls']+=1
        raise AssertionError('A worker launch is forbidden in the independent audit')
    joint.recovery.subprocess.Popen=forbidden

    def case(name):
        folder=root/name;folder.mkdir();output=folder/'output'
        source=output/'jobs'/joint.PILOT/'attempt-0001'
        shutil.copytree(original,source);(output/'records').mkdir()
        approval={**real_approval,'attempt_path':str(output)}
        auth=folder/'authorization.json';write(auth,approval)
        joint.APPROVAL_PATH=auth;joint.APPROVAL_SHA256=sha(auth)
        joint.REJECTED_PILOT_RECEIPT_SHA256=receipt_pin
        state=json.loads((ACTUAL/'progress.json').read_text());state['identity']['approval_sha256']=sha(auth)
        write(output/'progress.json',state)
        return output,source,approval

    def correction(output,approval):
        return joint.revalidate_pilot(output,PLAN,approval,matrix,REFERENCE)

    def rejected(function):
        try:function()
        except (ValueError,KeyError,OSError,TypeError) as error:return {'rejected':True,'error':repr(error)}
        return {'rejected':False}

    # Generic record and actual convergence message are both admitted.
    output,source,approval=case('successful-idempotent-promotion')
    before_progress=sha(output/'progress.json');before_original={p.name:sha(p) for p in source.iterdir() if p.is_file()}
    corrected=correction(output,approval)
    after_creation=sha(output/'progress.json')
    target=corrected.parent;receipt_bytes=corrected.read_bytes()
    repeated=correction(output,approval)
    args=Namespace(plan_root=str(PLAN),approval=str(joint.APPROVAL_PATH),matrix=str(MATRIX),output=str(output),
        reference_python=REFERENCE,check_resume=False,memory_gib=3.,wall_limit_seconds=None,
        continue_batch=False,pilot_assessment=None,revalidate_pilot=True)
    code=joint.run(args);state=json.loads((output/'progress.json').read_text())
    prior_debit=state['wall_seconds_debited'];second_code=joint.run(args)
    after=json.loads((output/'progress.json').read_text())
    results['checks']['normal_promotion_and_idempotence']={
        'correction_does_not_change_ledger':before_progress==after_creation,
        'original_bytes_unchanged':before_original=={p.name:sha(p) for p in source.iterdir() if p.is_file()},
        'repeat_returns_same_receipt':repeated==corrected,'receipt_bytes_unchanged':corrected.read_bytes()==receipt_bytes,
        'first_run_exit':code,'second_run_exit':second_code,'admitted_records':len(after['record_hashes']),
        'attempt_count':len(list((output/'jobs'/joint.PILOT).glob('attempt-*'))),
        'original_debit':json.loads((ACTUAL/'progress.json').read_text())['wall_seconds_debited'],
        'first_promotion_debit':prior_debit,'repeat_debit':after['wall_seconds_debited'],
        'stop_reason':after['sessions'][-1]['stop_reason'],'record_sha256':after['record_hashes'][joint.PILOT]}
    assert code==second_code==1 and len(after['record_hashes'])==1
    assert before_progress==after_creation and corrected.read_bytes()==receipt_bytes
    assert len(list((output/'jobs'/joint.PILOT).glob('attempt-*')))==2
    assert after['wall_seconds_debited']>=prior_debit>=2325.6432226409997
    assert after['wall_seconds_debited']<2340

    # A genuine second calculation after a non-parser failure is not a correction.
    output,source,approval=case('ordinary-second-worker-record')
    first=json.loads((source/'receipt.json').read_text());first['exit']=23
    write(source/'receipt.json',first)
    second=source.parent/'attempt-0002';second.mkdir()
    for filename in ('record.json','record.psi4.txt'):shutil.copyfile(source/filename,second/filename)
    data=joint.validate_joint_record(second/'record.json',order)
    results['checks']['ordinary_second_worker_record']={'accepted':data['status']=='computed','correction_sidecar_present':False}
    assert data['status']=='computed'

    # Eligibility boundaries are exercised even if a fixture receipt pin is rebound.
    invalid_receipts=[('failed_exit','exit',23),('timeout','reason','timeout'),
        ('rss_stop','reason','process_group_rss_exhausted'),('disk_stop','reason','scratch_disk_headroom_exhausted'),
        ('oom_stop','reason','cgroup_oom_event'),('other_validation','validation_error',"ValueError('different error')"),
        ('no_validation_error','validation_error',None),('unverified_cleanup','group_cleanup_verified',False)]
    for name,key,value in invalid_receipts:
        output,source,approval=case('reject-'+name);receipt=json.loads((source/'receipt.json').read_text())
        receipt[key]=value;write(source/'receipt.json',receipt)
        joint.REJECTED_PILOT_RECEIPT_SHA256=sha(source/'receipt.json')
        result=rejected(lambda:correction(output,approval));result['target_absent']=not (source.parent/'attempt-0002').exists()
        results['checks']['eligibility-'+name]=result;assert result['rejected'] and result['target_absent']

    for filename in ('receipt.json','record.json','record.psi4.txt','resources.jsonl','order.json','launch.json'):
        output,source,approval=case('changed-original-'+filename.replace('.','_'))
        path=source/filename;path.write_bytes(path.read_bytes()+b'\n')
        result=rejected(lambda:correction(output,approval));results['checks']['changed-original-'+filename]=result
        assert result['rejected'],filename

    for kind in ('nonfinite','wrong_geometry','unconverged','mixed_failure'):
        output,source,approval=case('invalid-data-'+kind)
        receipt=json.loads((source/'receipt.json').read_text())
        if kind in ('nonfinite','wrong_geometry'):
            data=json.loads((source/'record.json').read_text())
            if kind=='nonfinite':data['gradient_hartree_bohr'][0][0]=float('nan')
            else:data['positions_angstrom'][0][0]+=.1
            write(source/'record.json',data);receipt['record_sha256']=sha(source/'record.json')
        else:
            text=(source/'record.psi4.txt').read_text()
            if kind=='unconverged':text=text.replace('Energy and wave function converged.','SCF iterations incomplete.')
            else:text+='\nSCF failed to converge\n'
            (source/'record.psi4.txt').write_text(text)
            receipt['diagnostic_sha256']['record.psi4.txt']=sha(source/'record.psi4.txt')
        write(source/'receipt.json',receipt);joint.REJECTED_PILOT_RECEIPT_SHA256=sha(source/'receipt.json')
        result=rejected(lambda:correction(output,approval));results['checks']['invalid-data-'+kind]=result;assert result['rejected']

    # Lease, actual harmless process, group identity and ledger checks.
    output,source,approval=case('lease-contention')
    with (output.parent/'queue-lease.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        result=rejected(lambda:correction(output,approval))
    results['checks']['lease_contention']=result;assert result['rejected']
    output,source,approval=case('live-process')
    process=REAL_POPEN([sys.executable,'-c','import time; time.sleep(60)'],cwd=source,start_new_session=True)
    results['harmless_live_processes']+=1
    try:result=rejected(lambda:correction(output,approval))
    finally:process.terminate();process.wait(timeout=5)
    results['checks']['actual_harmless_live_process']=result;assert result['rejected']
    output,source,approval=case('live-group')
    with patch.object(joint.recovery,'group_members',lambda group:[12345]):result=rejected(lambda:correction(output,approval))
    results['checks']['live_group']=result;assert result['rejected']
    for kind in ('running_session','wrong_ledger_identity'):
        output,source,approval=case(kind);state=json.loads((output/'progress.json').read_text())
        if kind=='running_session':state['sessions'][0]['status']='running'
        else:state['identity']['approval_sha256']='0'*64
        write(output/'progress.json',state);result=rejected(lambda:correction(output,approval))
        results['checks'][kind]=result;assert result['rejected']

    # Correction tampering must fail both direct reuse and ordinary source validation.
    for kind in ('wall_seconds','rss_peak','marker_removed','both_markers_removed','wrong_kind','receipt_path',
        'copied_log','copied_identity','original_receipt_copy','correction_statement'):
        output,source,approval=case('changed-correction-'+kind);receipt_path=correction(output,approval)
        target=receipt_path.parent;receipt=json.loads(receipt_path.read_text())
        if kind=='wall_seconds':receipt['wall_seconds']=0.
        elif kind=='rss_peak':receipt['sampled_rss_peak_bytes']=0
        elif kind in ('marker_removed','both_markers_removed'):
            receipt.pop('completion_kind')
            if kind=='both_markers_removed':os.rename(target/'revalidation.json',output.parent/'preserved-revalidation.json')
        elif kind=='wrong_kind':receipt['completion_kind']='ordinary_worker'
        elif kind=='receipt_path':receipt['original_receipt_path']='/tmp/unrelated-receipt.json'
        elif kind in ('copied_log','copied_identity','original_receipt_copy'):
            filename={'copied_log':'record.psi4.txt','copied_identity':'worker-identity.json','original_receipt_copy':'original-receipt.json'}[kind]
            path=target/filename;path.write_bytes(path.read_bytes()+b'\n')
            receipt['diagnostic_sha256'][filename]=sha(path)
        else:
            path=target/'revalidation.json';value=json.loads(path.read_text());value['note']='Altered correction statement'
            write(path,value);receipt['diagnostic_sha256'][path.name]=sha(path)
        write(receipt_path,receipt)
        direct=rejected(lambda:correction(output,approval))
        ordinary=rejected(lambda:joint.validate_joint_record(target/'record.json',order))
        results['checks']['correction-'+kind]={'direct':direct,'ordinary':ordinary}
        assert direct['rejected'] and ordinary['rejected'],kind

    # Simulate loss at every publication boundary; preserve all partial bytes.
    for boundary in ('staging_created','middle_copy','correction_statement','receipt','after_rename','after_parent_sync'):
        output,source,approval=case('crash-'+boundary);staging=source.parent/'.revalidation-staging-v1';target=source.parent/'attempt-0002'
        before=sha(output/'progress.json');real_mkdir=joint.recovery.durable_mkdir;real_fsync=os.fsync
        real_dump=joint.recovery.exclusive_dump;real_rename=os.rename;real_sync=joint.recovery.sync_directory;copy_syncs=0
        def mkdir(path,*args,**kwargs):
            answer=real_mkdir(path,*args,**kwargs)
            if boundary=='staging_created' and Path(path)==staging:raise InjectedCrash(boundary)
            return answer
        def fsync(fd):
            nonlocal copy_syncs
            answer=real_fsync(fd);path=Path(os.readlink('/proc/self/fd/'+str(fd)))
            if boundary=='middle_copy' and path.parent==staging and not path.is_dir():
                copy_syncs+=1
                if copy_syncs==3:raise InjectedCrash(boundary)
            return answer
        def dump(path,data):
            answer=real_dump(path,data)
            if Path(path).parent==staging and ((boundary=='correction_statement' and Path(path).name=='revalidation.json')
                    or (boundary=='receipt' and Path(path).name=='receipt.json')):raise InjectedCrash(boundary)
            return answer
        def rename(a,b):
            answer=real_rename(a,b)
            if boundary=='after_rename' and Path(a)==staging:raise InjectedCrash(boundary)
            return answer
        def sync(path):
            answer=real_sync(path)
            if boundary=='after_parent_sync' and Path(path)==source.parent and target.exists():raise InjectedCrash(boundary)
            return answer
        caught=False
        with patch.object(joint.recovery,'durable_mkdir',mkdir),patch.object(os,'fsync',fsync),patch.object(joint.recovery,'exclusive_dump',dump),patch.object(os,'rename',rename),patch.object(joint.recovery,'sync_directory',sync):
            try:correction(output,approval)
            except InjectedCrash:caught=True
        assert caught,boundary
        partial_hashes={str(p.relative_to(staging)):sha(p) for p in staging.rglob('*') if p.is_file()} if staging.exists() else {}
        if target.exists():
            repeat=correction(output,approval);repeat_status={'accepted_complete_target':repeat==target/'receipt.json'}
        else:
            repeat_status=rejected(lambda:correction(output,approval))
            assert repeat_status['rejected']
            assert partial_hashes=={str(p.relative_to(staging)):sha(p) for p in staging.rglob('*') if p.is_file()}
        results['checks']['crash-'+boundary]={'injected':True,'published_target':target.exists(),'partial_staging_preserved':bool(partial_hashes) or staging.exists(),
            'repeat':repeat_status,'ledger_unchanged':sha(output/'progress.json')==before}
        assert sha(output/'progress.json')==before

    # Independent fsync ordering: every entry is durable before directory rename.
    output,source,approval=case('durability-order');staging=source.parent/'.revalidation-staging-v1';target=source.parent/'attempt-0002'
    real_fsync=os.fsync;real_rename=os.rename;events=[];synced_files={};synced_dirs={};renamed=False
    def trace(fd):
        path=Path(os.readlink('/proc/self/fd/'+str(fd)));sequence=len(events)+1
        real_fsync(fd);events.append({'sequence':sequence,'path':str(path),'directory':path.is_dir()})
        (synced_dirs if path.is_dir() else synced_files)[path]=sequence
    def durable_rename(a,b):
        nonlocal renamed
        assert Path(a)==staging
        files=[p for p in staging.iterdir() if p.is_file()]
        assert all(p in synced_files for p in files),'Unsynced correction file before publication'
        assert synced_dirs.get(staging,0)>max(synced_files[p] for p in files),'Correction entries not durable before publication'
        answer=real_rename(a,b);renamed=True;events.append({'sequence':len(events)+1,'rename_from':str(a),'rename_to':str(b)})
        return answer
    with patch.object(os,'fsync',trace),patch.object(os,'rename',durable_rename):receipt_path=correction(output,approval)
    rename_event=next(e['sequence'] for e in events if 'rename_from' in e)
    assert renamed and synced_dirs[source.parent]>rename_event
    write(output.parent/'fsync-events.json',events)
    results['checks']['durability_order']={'all_files_synced_before_rename':True,'directory_entries_synced_before_rename':True,
        'parent_synced_after_rename':True,'returned_receipt_exists':receipt_path.exists(),'events':len(events)}

    results['actual_original_hashes_unchanged']=canonical_hashes=={p.name:sha(p) for p in original.iterdir() if p.is_file()}
    results['actual_progress_hash_unchanged']=canonical_progress==sha(ACTUAL/'progress.json')
    results['utc_finished']=dt.datetime.now(dt.timezone.utc).isoformat()
    assert results['actual_original_hashes_unchanged'] and results['actual_progress_hash_unchanged'] and results['worker_launch_calls']==0
    write(EVIDENCE/('probe-results-'+options.label+'.json'),results)
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
