import datetime,hashlib,json,os,pathlib,subprocess,sys,time
root=pathlib.Path(__file__).parent
name=sys.argv[1]; cmd=sys.argv[2:]
t=time.time();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run(cmd,text=True,capture_output=True)
data={'command':cmd,'cwd':os.getcwd(),'reviewed_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'start_utc':start,'elapsed_seconds':time.time()-t,'exit_code':r.returncode,'python':sys.executable,'profile':{'OMP_NUM_THREADS':os.environ.get('OMP_NUM_THREADS'),'PYTHONPATH':os.environ.get('PYTHONPATH'),'ATOM_G05_CAPTURE_DIR':os.environ.get('ATOM_G05_CAPTURE_DIR')},'stdout':r.stdout,'stderr':r.stderr}
(root/(name+'.json')).write_text(json.dumps(data,indent=2)); print(name, 'exit',r.returncode);print(r.stdout[-6000:]);print(r.stderr[-2000:])
