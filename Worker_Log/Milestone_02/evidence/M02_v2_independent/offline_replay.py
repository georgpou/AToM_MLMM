import os,pathlib,subprocess,sys,tempfile
with tempfile.TemporaryDirectory(prefix='m02-independent-empty-cache-') as cache:
 assert not list(pathlib.Path(cache).iterdir())
 command=[sys.executable,'-c',"import socket,runpy\ndef deny(*a,**k):raise AssertionError('network forbidden')\nsocket.socket.connect=deny\nsocket.create_connection=deny\nsocket.getaddrinfo=deny\nrunpy.run_path('Worker_Log/Milestone_02/evidence/M02_v1/reproduce_stale_fault.py',run_name='__main__')"]
 print('Fresh subprocess; initially empty XDG_CACHE_HOME; connect/create_connection/getaddrinfo denied. Command:',repr(command),flush=True)
 result=subprocess.run(command,env=dict(os.environ,XDG_CACHE_HOME=cache))
 sys.exit(result.returncode)
