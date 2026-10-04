"""Trace crash-after-rename recovery on isolated copies; no actual writes or workers."""
from pathlib import Path
from argparse import Namespace
from unittest.mock import patch
import hashlib,json,os,shutil,sys
E=Path(__file__).resolve().parent;REPO=E.parents[3]
sys.path[:0]=[str(E/'source-final/tools'),str(REPO/'src')]
import resume_joint_quantum as j
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ACTUAL=REPO/'Worker_Log/Milestone_03/evidence/G07_v2/quantum-attempt-v1'
folder=E/'rename-recovery-durability-case';folder.mkdir()
output=folder/'output';source=output/'jobs'/j.PILOT/'attempt-0001'
actualsource=ACTUAL/'jobs'/j.PILOT/'attempt-0001'
original={p.name:sha(p) for p in actualsource.iterdir() if p.is_file()};progresspin=sha(ACTUAL/'progress.json')
shutil.copytree(actualsource,source);(output/'records').mkdir()
auth=json.loads((REPO/'Worker_Log/Milestone_03/evidence/G07_v2/authorization.json').read_text());auth['attempt_path']=str(output)
authpath=folder/'authorization.json';authpath.write_text(json.dumps(auth,indent=2)+'\n');j.APPROVAL_PATH=authpath;j.APPROVAL_SHA256=sha(authpath)
state=json.loads((ACTUAL/'progress.json').read_text());state['identity']['approval_sha256']=sha(authpath)
(output/'progress.json').write_text(json.dumps(state,indent=2)+'\n')
plan=REPO/'fixtures/chemical_reference_v3';matrixpath=REPO/'fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json'
matrix=json.loads(matrixpath.read_text());reference='/workspace/atom-mlmm-g07/reference-env/bin/python'
launches=0

def forbidden(*a,**k):
 global launches
 launches+=1
 raise AssertionError('worker prohibited')
j.recovery.subprocess.Popen=forbidden
staging=source.parent/'.revalidation-staging-v1';target=source.parent/'attempt-0002';rename=os.rename
class Crash(Exception):pass

def interrupted(a,b):
 answer=rename(a,b)
 if Path(a)==staging:raise Crash('after rename before parent fsync')
 return answer
with patch.object(os,'rename',interrupted):
 try:j.revalidate_pilot(output,plan,auth,matrix,reference)
 except Crash:pass
assert target.exists() and not staging.exists()
fsync=os.fsync;events=[];dump=j.recovery.atomic_dump

def trace(fd):
 path=Path(os.readlink('/proc/self/fd/'+str(fd)))
 answer=fsync(fd);events.append({'fsync':str(path),'directory':path.is_dir()});return answer

def checkpoint(path,data):
 if Path(path)==output/'progress.json' and data['record_hashes']:
  events.append({'checkpoint_with_record':j.PILOT,'parent_synced_before':any(e.get('fsync')==str(source.parent) for e in events)})
 return dump(path,data)
args=Namespace(plan_root=str(plan),approval=str(authpath),matrix=str(matrixpath),output=str(output),reference_python=reference,
 check_resume=False,memory_gib=3.,wall_limit_seconds=None,continue_batch=False,pilot_assessment=None,revalidate_pilot=True)
with patch.object(os,'fsync',trace),patch.object(j.recovery,'atomic_dump',checkpoint):exitcode=j.run(args)
checkpoints=[e for e in events if 'checkpoint_with_record' in e]
result={'source_sha256':sha(E/'source-final/tools/resume_joint_quantum.py'),'injected_after_rename':True,'exit':exitcode,
 'record_admitted':len(json.loads((output/'progress.json').read_text())['record_hashes'])==1,
 'parent_synced_before_admitted_checkpoint':checkpoints[0]['parent_synced_before'],
 'parent_synced_at_all_on_resume':any(e.get('fsync')==str(source.parent) for e in events),
 'worker_launch_calls':launches,'actual_original_unchanged':original=={p.name:sha(p) for p in actualsource.iterdir() if p.is_file()},
 'actual_progress_unchanged':progresspin==sha(ACTUAL/'progress.json'),'events':events}
(folder/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='events'},indent=2))
assert result['actual_original_unchanged'] and result['actual_progress_unchanged'] and not launches
