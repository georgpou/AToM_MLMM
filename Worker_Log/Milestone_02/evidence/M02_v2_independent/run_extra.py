import datetime,gzip,json,pathlib,subprocess,sys
out=pathlib.Path(__file__).parent
name=sys.argv[1];command=sys.argv[2:];target=out/(name+'.json.gz')
assert not target.exists()
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
record=dict(command=command,cwd=str(pathlib.Path.cwd()),activation='/workspace/.onboarding/atom-mlmm-m02-v2/activate.sh',pythonpath='src:.',head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),started_utc=start,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=r.returncode,output=r.stdout)
with gzip.open(target,'wt') as f:json.dump(record,f,indent=2)
print(r.stdout);sys.exit(r.returncode)
