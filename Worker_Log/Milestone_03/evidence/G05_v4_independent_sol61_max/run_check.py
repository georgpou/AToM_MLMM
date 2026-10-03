from pathlib import Path
import sys,subprocess,datetime,time,json
evidence=Path(__file__).resolve().parent
name=sys.argv[1];command=sys.argv[2:]
start=datetime.datetime.now(datetime.timezone.utc);clock=time.monotonic()
with (evidence/(name+'.log')).open('x') as output:
    result=subprocess.run(command,stdout=output,stderr=subprocess.STDOUT)
record={'command':command,'cwd':str(Path.cwd()),'started_utc':start.isoformat(),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-clock,'exit_code':result.returncode}
with (evidence/(name+'.json')).open('x') as output:json.dump(record,output,indent=2);output.write('\n')
print(json.dumps(record));sys.exit(result.returncode)
