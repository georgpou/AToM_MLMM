"""Independent immutable-snapshot command capture; never overwrite evidence."""
import datetime, json, os, subprocess, sys, time
from pathlib import Path
out=Path(sys.argv[1]); argv=sys.argv[2:]
assert not out.exists(), out
started=datetime.datetime.now(datetime.timezone.utc).isoformat(); t=time.monotonic()
def git(*args):return subprocess.check_output(['git',*args],text=True).strip()
head=git('rev-parse','HEAD'); before=git('status','--porcelain')
p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
data=dict(argv=argv,cwd=os.getcwd(),head=head,status_before=before,status_after=git('status','--porcelain'),started_utc=started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-t,exit_code=p.returncode,activation='/workspace/atom-mlmm-g05-v2/activate.sh',python_executable=sys.executable,environment={k:os.environ.get(k) for k in ['PYTHONPATH','OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']},output=p.stdout)
with out.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
print(p.stdout);print('capture:',out,'exit:',p.returncode)
sys.exit(p.returncode)
