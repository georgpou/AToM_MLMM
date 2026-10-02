"""Independent review command capture; exclusive creation, complete combined output."""
import datetime, gzip, json, os, pathlib, subprocess, sys
root=pathlib.Path(__file__).resolve().parents[4]
output=pathlib.Path(__file__).with_name(sys.argv[1]+'.json.gz')
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with output.open('xb') as raw:
    result=subprocess.run(sys.argv[2:],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    record={'argv':sys.argv[2:],'cwd':str(pathlib.Path.cwd()),'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'exit_code':result.returncode,'activation':'/workspace/atom-mlmm-g04-v2/activate.sh','pythonpath':os.environ.get('PYTHONPATH'),'output':result.stdout}
    with gzip.GzipFile(fileobj=raw,mode='wb') as gz: gz.write(json.dumps(record,indent=2).encode())
print(result.stdout[-4500:])
print('Capture:',output,'exit:',result.returncode)
sys.exit(result.returncode)
