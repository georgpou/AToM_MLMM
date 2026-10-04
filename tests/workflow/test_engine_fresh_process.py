"""Actual worker continuation from only a relocated, locally sealed bundle."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tests.workflow.test_cloud_host_guest import FIXTURE,ROOT


def test_offline_actual_worker_resume_with_original_checkout_and_caches_denied(tmp_path):
    from atm_mlmm.workflow import run_configuration
    from atm_mlmm.persistence import read_sample_chunks
    base=json.loads((FIXTURE/'config.json').read_text())
    base['input_manifest']=str(FIXTURE/'manifest.json')
    base['settings'].update(frames_per_state=1,steps_per_frame=1,minimization_iterations=3)
    config=tmp_path/'config.json'
    config.write_text(json.dumps(base))
    original=tmp_path/'original-run'
    run_configuration(config,original,trusted=True,stop_after_samples=1)
    relocated=tmp_path/'relocated-run'
    shutil.copytree(original,relocated)
    probe=r'''
import builtins,io,json,os,pathlib,socket,sys
def deny_network(*args,**kwargs):
    raise RuntimeError('network is unavailable in relocated worker test')
socket.socket.connect=deny_network
socket.socket.connect_ex=deny_network
socket.create_connection=deny_network
socket.getaddrinfo=deny_network
roots=[pathlib.Path(p).resolve() for p in sys.argv[2:]]
def check_path(file):
    if isinstance(file,(str,bytes,os.PathLike)):
        p=pathlib.Path(os.fsdecode(file)).resolve()
        if any(p==r or r in p.parents for r in roots):
            raise RuntimeError('original checkout, run or caches are unavailable: '+str(p))
normal_open,normal_io_open,normal_os_open=builtins.open,io.open,os.open
def guarded_open(file,*args,**kwargs):
    check_path(file)
    return normal_open(file,*args,**kwargs)
def guarded_io_open(file,*args,**kwargs):
    check_path(file)
    return normal_io_open(file,*args,**kwargs)
def guarded_os_open(file,*args,**kwargs):
    check_path(file)
    return normal_os_open(file,*args,**kwargs)
builtins.open,io.open,os.open=guarded_open,guarded_io_open,guarded_os_open
import atm_mlmm.workflow
assert str(pathlib.Path(atm_mlmm.workflow.__file__).resolve()).startswith(sys.argv[1])
result=atm_mlmm.workflow.resume_run(sys.argv[1],trusted=True)
result.update(network_denied=True,original_paths_denied=True,source_file=atm_mlmm.workflow.__file__)
print(json.dumps(result))
'''
    denied_caches=[tmp_path/name for name in ('empty-xdg','empty-torch','empty-mace')]
    env={**os.environ,'PYTHONPATH':str(relocated/'worker/runtime/source'),
         'XDG_CACHE_HOME':str(denied_caches[0]),'TORCH_HOME':str(denied_caches[1]),
         'MACE_CACHE_DIR':str(denied_caches[2]),'OPENBLAS_NUM_THREADS':'2'}
    child=subprocess.run([sys.executable,'-c',probe,str(relocated),str(ROOT),str(original),
                          *(str(p) for p in denied_caches)],cwd=tmp_path,env=env,text=True,
                         capture_output=True,timeout=90)
    (tmp_path/'child-stdout.txt').write_text(child.stdout)
    (tmp_path/'child-stderr.txt').write_text(child.stderr)
    assert child.returncode==0,child.stdout+child.stderr
    result=json.loads(child.stdout.splitlines()[-1])
    assert result['status']=='complete' and result['samples']==3
    assert result['profile']['model_device']=='CPU'
    assert result['profile']['openmm_platform']=='Reference'
    assert result['network_denied'] and result['original_paths_denied']
    rows=read_sample_chunks(relocated/'samples')
    assert len(rows)==3 and len({r['sample_id'] for r in rows})==3
    assert read_sample_chunks(original/'samples')==rows[:1]
