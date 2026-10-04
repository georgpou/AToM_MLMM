"""Recheck frozen repaired execution source without QM or model launches."""
from argparse import Namespace
from pathlib import Path
import datetime as dt
import fcntl
import hashlib
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time

EVIDENCE=Path(__file__).resolve().parent
REPO=EVIDENCE.parents[3]
SOURCE=EVIDENCE/'reviewed-source-repaired'
PLAN=REPO/'fixtures/chemical_reference_v3'
MATRIX=REPO/'fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json'
AUTH=REPO/'Worker_Log/Milestone_03/evidence/G07_v2/authorization.json'
PILOT='ethanol-methanol-d3-r0--full-parent'


def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


HARNESS='''
from argparse import Namespace
from pathlib import Path
import hashlib,json,os,sys
config=json.loads(Path(sys.argv[1]).read_text())
sys.path[:0]=[config['source_tools'],config['src']]
import resume_joint_quantum as joint
# Test-process fixture substitution only; production source remains unmodified.
joint.APPROVAL_PATH=Path(config['approval']).resolve()
joint.APPROVAL_SHA256=hashlib.sha256(joint.APPROVAL_PATH.read_bytes()).hexdigest()
if config.get('trace_durability'):
    actual=os.fsync; synced=set(); seen=[]
    def trace(fd):
        path=Path(os.readlink('/proc/self/fd/'+str(fd)))
        if path.name=='progress.json.tmp':
            state=json.loads(path.read_text())
            for name in state['record_hashes']:
                source=Path(state['provenance'][name]['source'])
                receipt=json.loads(source.with_name('receipt.json').read_text())
                required=[source,source.with_name('receipt.json'),source.with_name('order.json'),source.with_name('launch.json')]
                required += [source.parent/filename for filename in receipt['diagnostic_sha256']]
                assert all(p in synced for p in required), ('checkpoint references unsynced evidence',required,synced)
                assert source.with_suffix('.psi4.txt') in synced
                seen.append(name)
        actual(fd);synced.add(path)
    os.fsync=trace
try:
    code=joint.run(Namespace(**config['args']))
    if config.get('trace_durability'):
        Path(config['trace_durability']).write_text(json.dumps(dict(checkpointed_names=seen,synced_paths=sorted(map(str,synced))),indent=2))
    raise SystemExit(code)
except (ValueError,KeyError,OSError,TypeError) as error:
    print('Synthetic fixture rejected:',repr(error),file=sys.stderr)
    raise SystemExit(2)
'''


def members(group):
    result=[]
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():continue
        try:
            fields=(path/'stat').read_text().rsplit(')',1)[1].split()
            if fields[0]!='Z' and int(fields[2])==group:result.append(int(path.name))
        except (OSError,IndexError,ValueError):pass
    return result


def main():
    root=EVIDENCE/'probes-repaired';root.mkdir()
    # Reuse only the independently authored stand-in implementation.
    spec=importlib.util.spec_from_file_location('initial_probes',EVIDENCE/'independent_execution_probes.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    exe=root/'synthetic-reference/bin/python';exe.parent.mkdir(parents=True)
    exe.write_text('#!'+sys.executable+'\n'+helper.FAKE);exe.chmod(0o755)
    for index,line in enumerate((PLAN/'reference-explicit.lock').read_text().splitlines()):
        if line.startswith('https://'):
            url,digest=line.rsplit('#',1);write(exe.parents[1]/'conda-meta'/f'{index}.json',dict(url=url,sha256=digest))
    harness=root/'harness.py';harness.write_text(HARNESS)
    approved=json.loads(AUTH.read_text());environment={**os.environ,'PYTHONPATH':str(REPO/'src')}
    outcomes={'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'source_hashes':{str(p.relative_to(SOURCE)):sha(p) for p in SOURCE.glob('tools/*.py')},'notice':'SYNTHETIC EXECUTION SOFTWARE EVIDENCE ONLY','checks':{}}

    def case(name):
        folder=root/name;folder.mkdir();output=folder/'output';auth=folder/'authorization.json'
        write(auth,{**approved,'attempt_path':str(output)})
        return output,auth

    def fixture_command(output,auth,mode='',changes=None,durability=False):
        args=dict(plan_root=str(PLAN),matrix=str(MATRIX),approval=str(auth),output=str(output),reference_python=str(exe),
            check_resume=False,memory_gib=3.,wall_limit_seconds=None,continue_batch=False,pilot_assessment=None)
        args.update(changes or {})
        config=output.parent/'fixture-config.json';write(config,dict(source_tools=str(SOURCE/'tools'),src=str(REPO/'src'),approval=str(auth),args=args,
            trace_durability=str(output.parent/'durability-events.json') if durability else None))
        return [sys.executable,str(harness),str(config)]

    def run(output,auth,mode='',changes=None,durability=False):
        command=fixture_command(output,auth,mode,changes,durability)
        result=subprocess.run(command,env={**environment,'G07_INDEPENDENT_MODE':mode},capture_output=True,text=True,timeout=50)
        with (output.parent/'commands.jsonl').open('a') as stream:stream.write(json.dumps(dict(command=command,mode=mode,args=changes,exit=result.returncode,stdout=result.stdout,stderr=result.stderr))+'\n')
        return result

    # Production CLI uses exact real authorization, but is read-only.
    production=[sys.executable,str(REPO/'tools/resume_joint_quantum.py'),'--plan-root',str(PLAN),'--matrix',str(MATRIX),
        '--approval',str(AUTH),'--output',approved['attempt_path'],'--check-resume']
    checked=subprocess.run(production,env=environment,capture_output=True,text=True,timeout=15)
    outcomes['checks']['production_read_only']={'command':production,'exit':checked.returncode,'reported':json.loads(checked.stdout),'stderr':checked.stderr}
    assert checked.returncode==0 and outcomes['checks']['production_read_only']['reported']['expected_count']==30
    out,auth=case('copied-authorization-rejected')
    copied=list(production);copied[copied.index('--approval')+1]=str(auth);copied[copied.index('--output')+1]=str(out)
    rejected=subprocess.run(copied,env=environment,capture_output=True,text=True,timeout=15)
    outcomes['checks']['copied_authorization']={'exit':rejected.returncode,'stderr':rejected.stderr,'output_exists':out.exists()}
    assert rejected.returncode==2 and not out.exists()
    wrong=list(production);wrong[wrong.index('--output')+1]=str(out)
    rejected=subprocess.run(wrong,env=environment,capture_output=True,text=True,timeout=15)
    outcomes['checks']['wrong_output_canonical_authorization']={'exit':rejected.returncode,'stderr':rejected.stderr,'output_exists':out.exists()}
    assert rejected.returncode==2 and not out.exists()

    # Pilot pause, durability ordering, diagnostic/hash protection and restoration.
    out,auth=case('durable-pilot-and-diagnostic-recovery')
    result=run(out,auth,durability=True);assert result.returncode==1,result.stderr
    state=json.loads((out/'progress.json').read_text());assert len(state['record_hashes'])==1
    source=Path(state['provenance'][PILOT]['source']);receipt_path=source.with_name('receipt.json')
    receipt=json.loads(receipt_path.read_text())
    outcomes['checks']['durable_pilot_pause']={'exit':result.returncode,'records':len(state['record_hashes']),'stop_reason':state['sessions'][-1]['stop_reason'],
        'trace_assertions_passed':(out.parent/'durability-events.json').exists(),'receipt_diagnostic_files':sorted(receipt['diagnostic_sha256'])}
    mutations={}
    for label,path in [('missing_source_log',source.with_suffix('.psi4.txt')),('changed_source_log',source.with_suffix('.psi4.txt')),
        ('changed_published_log',out/'records'/(PILOT+'.psi4.txt')),('changed_receipt',receipt_path),
        ('changed_resources',source.with_name('resources.jsonl')),('changed_order',source.with_name('order.json')),
        ('changed_launch',source.with_name('launch.json'))]:
        data=path.read_bytes()
        if label.startswith('missing_'):path.unlink()
        else:path.write_bytes(data+b'\n')
        result=run(out,auth);mutations[label]={'exit':result.returncode,'stderr':result.stderr};assert result.returncode==2,(label,result.stderr)
        path.write_bytes(data)
    outcomes['checks']['reused_diagnostic_mutations_rejected']=mutations
    target=out/'records'/(PILOT+'.json');target_log=target.with_suffix('.psi4.txt');target.unlink();target_log.unlink()
    restored=run(out,auth);assert restored.returncode==1,restored.stderr
    outcomes['checks']['lost_promoted_record_restored']={'exit':restored.returncode,'record_hash_matches':sha(target)==state['record_hashes'][PILOT],
        'log_hash_matches':sha(target_log)==sha(source.with_suffix('.psi4.txt')),'pilot_attempt_count':len(list(out.glob('jobs/*/attempt-*')))}

    sys.path[:0]=[str(SOURCE/'tools'),str(REPO/'src')]
    import resume_joint_quantum as joint
    matrix=json.loads(MATRIX.read_text());approval=json.loads(auth.read_text());measured=joint.pilot_evidence(out)
    assessment=dict(measured,continue_authorized=True,matrix_sha256=approved['matrix_sha256'],
        projected_remaining_worker_seconds=1000.,projected_max_rss_bytes=2**30,projected_scratch_bytes=measured['pilot_scratch_peak_bytes']*4)
    assessment_path=out.parent/'measured-assessment.json';write(assessment_path,assessment)
    joint.validate_assessment(assessment_path,out,approval,matrix)
    assessment_checks={}
    for field,value in [('pilot_resources_sha256','0'*64),('pilot_receipt_sha256','0'*64),('pilot_record_sha256','0'*64),
        ('matrix_sha256','0'*64),('pilot_wall_seconds',measured['pilot_wall_seconds']+1),
        ('projected_remaining_worker_seconds',0.),('projected_max_rss_bytes',6*2**30+1),
        ('projected_scratch_bytes',100*2**30),('projected_remaining_worker_seconds',float('inf'))]:
        changed={**assessment,field:value};name=field+('-nonfinite' if value==float('inf') else '')
        path=out.parent/('wrong-'+name+'.json');path.write_text(json.dumps(changed)+'\n')
        try:joint.validate_assessment(path,out,approval,matrix);assessment_checks[name]={'rejected':False}
        except (ValueError,KeyError,OSError,TypeError) as error:assessment_checks[name]={'rejected':True,'error':repr(error)}
        assert assessment_checks[name]['rejected'],name
    outcomes['checks']['measured_assessment_mutations']=assessment_checks
    # Continue synthetic exact30 queue and then resume it without new attempts.
    continuation=run(out,auth,changes={'continue_batch':True,'pilot_assessment':str(assessment_path)});assert continuation.returncode==0,continuation.stderr
    state=json.loads((out/'progress.json').read_text());count=len(list(out.glob('jobs/*/attempt-*')));prior=state['wall_seconds_debited']
    repeated=run(out,auth,changes={'continue_batch':True,'pilot_assessment':str(assessment_path)});assert repeated.returncode==0,repeated.stderr
    final=json.loads((out/'progress.json').read_text())
    outcomes['checks']['exact_matrix_continuation_and_reuse']={'exit':continuation.returncode,'repeat_exit':repeated.returncode,'record_count':len(final['record_hashes']),
        'ready_for_comparison':final['ready_for_comparison'],'attempts_before_repeat':count,'attempts_after_repeat':len(list(out.glob('jobs/*/attempt-*'))),
        'debit_before_repeat':prior,'debit_after_repeat':final['wall_seconds_debited']}
    assert count==30 and len(final['record_hashes'])==30 and len(list(out.glob('jobs/*/attempt-*')))==30

    # Known computed failure, cumulative pilot ceiling and totalbatch ceiling.
    out,auth=case('cumulative-ceilings');failed=run(out,auth,'computed_fail');assert failed.returncode==1
    state=json.loads((out/'progress.json').read_text());assert not state['record_hashes']
    path=out/'progress.json';state['sessions'][0]['wall_seconds']=3600.5;write(path,state)
    stopped=run(out,auth);pilot_state=json.loads(path.read_text());assert stopped.returncode==1
    assert len(list(out.glob('jobs/*/attempt-*')))==1 and pilot_state['sessions'][-1]['stop_reason']=='pilot_budget_exhausted'
    pilot_state['sessions'][0]['wall_seconds']=86400.5;write(path,pilot_state)
    stopped=run(out,auth);batch_state=json.loads(path.read_text());assert stopped.returncode==1
    assert len(list(out.glob('jobs/*/attempt-*')))==1 and batch_state['sessions'][-1]['stop_reason']=='budget_exhausted'
    outcomes['checks']['pilot_and_batch_cumulative_ceilings']={'no_extra_launch':True,'pilot_stop':'pilot_budget_exhausted','batch_stop':'budget_exhausted','batch_debit':batch_state['wall_seconds_debited']}

    # Coordinator loss retains the canonical fixture lease while cleanup runs.
    out,auth=case('coordinator-loss');started=out.parent/'worker-started.pid'
    process=subprocess.Popen(fixture_command(out,auth),env={**environment,'G07_INDEPENDENT_MODE':'stubborn','G07_INDEPENDENT_STARTED':str(started)},
        stdout=(out.parent/'coordinator.txt').open('w'),stderr=subprocess.STDOUT)
    deadline=time.monotonic()+15
    while not started.exists() and process.poll() is None and time.monotonic()<deadline:time.sleep(.02)
    assert started.exists(),'stand-in worker never started'
    state=json.loads((out/'progress.json').read_text());group=state['sessions'][-1]['active_worker']['pid'];process.kill();process.wait(timeout=5)
    retained=False
    with (out.parent/'queue-lease.lock').open('a') as stream:
        try:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(stream,fcntl.LOCK_UN)
        except BlockingIOError:retained=True
    deadline=time.monotonic()+12
    while members(group) and time.monotonic()<deadline:time.sleep(.03)
    remaining=members(group)
    if remaining:os.killpg(group,signal.SIGKILL)
    recovered=run(out,auth);state=json.loads((out/'progress.json').read_text())
    outcomes['checks']['coordinator_loss_retained_lease']={'coordinator_exit':process.returncode,'lease_retained':retained,'remaining_group':remaining,'recovery_exit':recovered.returncode,
        'interrupted_status':state['sessions'][0]['status'],'interrupted_seconds':state['sessions'][0]['wall_seconds'],'total_debit':state['wall_seconds_debited']}
    assert retained and not remaining and recovered.returncode==1 and state['sessions'][0]['status']=='interrupted'
    write(EVIDENCE/'independent-probes-repaired.json',outcomes)
    print(json.dumps(outcomes,indent=2))


if __name__=='__main__':main()
