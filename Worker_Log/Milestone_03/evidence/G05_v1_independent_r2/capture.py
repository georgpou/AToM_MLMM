import datetime,hashlib,json,os,pathlib,subprocess,sys,time
root=pathlib.Path(__file__).parent
name=sys.argv[1];command=sys.argv[2:]
start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
r=subprocess.run(command,text=True,capture_output=True)
d={'command':command,'cwd':os.getcwd(),'reviewed_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'start_utc':start,'elapsed_seconds':time.monotonic()-t,'exit_code':r.returncode,'python':sys.executable,'environment':{k:os.environ.get(k) for k in ('PYTHONPATH','OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','ATOM_G05_CAPTURE_DIR')},'stdout':r.stdout,'stderr':r.stderr}
with (root/(name+'.json')).open('x') as f:json.dump(d,f,indent=2)
print(name,'exit',r.returncode);print(r.stdout[-6000:]);print(r.stderr[-1000:])
sys.exit(r.returncode)
