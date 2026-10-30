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
relocated=pathlib.Path(sys.argv[1]).resolve()
roots=[pathlib.Path(p).resolve() for p in sys.argv[2:]]
runtime_prefix=pathlib.Path(sys.prefix).resolve()
def within(path,root):
    return path==root or root in path.parents
def denied_path(file,deny_roots,allowed_roots,protected_roots=()):
    path=pathlib.Path(os.fsdecode(file)).resolve()
    if any(within(path,root) for root in protected_roots):
        return True
    if any(within(path,root) for root in allowed_roots):
        return False
    return any(within(path,root) for root in deny_roots)
protected_roots=tuple(roots[1:])
def check_path(file):
    if isinstance(file,(str,bytes,os.PathLike)):
        p=pathlib.Path(os.fsdecode(file)).resolve()
        if denied_path(p,roots,(relocated,runtime_prefix),protected_roots):
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
layout_root=pathlib.Path.cwd()/'.guard-layout-probes'
nested_repo=layout_root/'nested-repository'
nested_bundle=nested_repo/'.tmp'/'relocated'
disjoint_repo=layout_root/'disjoint-repository'
disjoint_bundle=layout_root/'relocated-bundle'
synthetic_prefix=layout_root/'synthetic-prefix'
synthetic_cache=synthetic_prefix/'cache'
assert not denied_path(nested_bundle/'metadata.json',[nested_repo],(nested_bundle,))
assert denied_path(nested_repo/'source.py',[nested_repo],(nested_bundle,))
assert not denied_path(disjoint_bundle/'metadata.json',[disjoint_repo],(disjoint_bundle,))
assert denied_path(disjoint_repo/'source.py',[disjoint_repo],(disjoint_bundle,))
assert denied_path(synthetic_cache/'probe',[layout_root],(synthetic_prefix,),(synthetic_cache,))
def read_with(api,path):
    if api=='os.open':
        descriptor=os.open(path,os.O_RDONLY)
        try:
            return os.read(descriptor,1024*1024)
        finally:
            os.close(descriptor)
    opener=builtins.open if api=='builtins.open' else io.open
    with opener(path,'rb') as stream:
        return stream.read()
open_apis=('builtins.open','io.open','os.open')
denied_targets=[roots[0]/'src/atm_mlmm/workflow.py',
                roots[0]/'tools/resume_neutral_quantum.py',
                roots[0]/'fixtures/chemical_reference_v3/reference-settings.json',
                roots[0]/'.runtime/cosmos-cpu/portability-repair/task-brief.md',
                roots[0]/'.runtime/cosmos-cpu/cache/matplotlib/fontlist-v3.11.0.json.matplotlib-lock',
                pathlib.Path(str(runtime_prefix)+'-sibling')/'probe',
                roots[1]/'metadata.json',
                *(root/'deliberate-deny-probe' for root in roots[2:])]
for api in open_apis:
    for target in denied_targets:
        try:
            read_with(api,target)
        except RuntimeError as error:
            assert 'unavailable' in str(error)
        else:
            raise AssertionError(api+' read a denied original/cache path: '+str(target))
for api in open_apis:
    assert read_with(api,runtime_prefix/'bin/python')
    assert read_with(api,relocated/'metadata.json')
assert within(pathlib.Path(os.environ['MPLCONFIGDIR']).resolve(),relocated)
assert within(pathlib.Path(os.environ['TMPDIR']).resolve(),relocated)
network_probes=(
    ('socket.getaddrinfo',lambda:socket.getaddrinfo('example.invalid',443)),
    ('socket.create_connection',lambda:socket.create_connection(('127.0.0.1',9),timeout=.1)),
    ('socket.socket.connect',lambda:probe_socket('connect')),
    ('socket.socket.connect_ex',lambda:probe_socket('connect_ex')),
)
def probe_socket(method):
    client=socket.socket()
    try:
        getattr(client,method)(('127.0.0.1',9))
    finally:
        client.close()
for label,operation in network_probes:
    try:
        operation()
    except RuntimeError as error:
        assert 'network is unavailable' in str(error)
    else:
        raise AssertionError(label+' unexpectedly succeeded')
import atm_mlmm.workflow
source=pathlib.Path(atm_mlmm.workflow.__file__).resolve()
assert within(source,relocated/'worker/runtime/source')
result=atm_mlmm.workflow.resume_run(relocated,trusted=True)
result.update(network_denied=True,original_paths_denied=True,source_file=str(source))
print(json.dumps(result))
'''
    denied_caches=[tmp_path/name for name in ('empty-xdg','empty-torch','empty-mace')]
    runtime_tmp=relocated/'runtime-tmp'
    runtime_tmp.mkdir()
    env={**os.environ,'PYTHONPATH':str(relocated/'worker/runtime/source'),
         'XDG_CACHE_HOME':str(denied_caches[0]),'TORCH_HOME':str(denied_caches[1]),
     'MACE_CACHE_DIR':str(denied_caches[2]),'MPLCONFIGDIR':str(relocated/'matplotlib-cache'),
     'TMPDIR':str(runtime_tmp),
     'OPENBLAS_NUM_THREADS':'2'}
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
