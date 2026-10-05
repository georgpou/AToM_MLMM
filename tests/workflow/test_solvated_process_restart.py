"""Solvated checkpoint/portable-State guarantees and sealed offline processes."""
from contextlib import ExitStack
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
import pytest

from tests.workflow.test_solvated_handover import water_run

ROOT=Path(__file__).resolve().parents[2]


@pytest.mark.model_assets
def test_solvated_checkpoint_exact_continuation_and_portable_observables(water_run):
    import openmm as mm
    from openmm import unit
    from atm_mlmm.adapters.atom import load_worker_run
    from atm_mlmm.workflow import _snapshot
    _,_,output,summary,bundle,rows=water_run
    state_id=rows[0]['state_id']
    checkpoint=(output/'samples/000000/checkpoint.chk').read_bytes()
    portable=(output/'samples/000000/state.xml').read_text()
    with ExitStack() as stack:
        workers=[stack.enter_context(load_worker_run(output/'worker',summary['worker_manifest_sha256'],trusted=True)) for _ in range(2)]
        workers[0].restore_checkpoint(checkpoint,state_id)
        reference=workers[0].evaluate(_snapshot(workers[0]),state_id)
        workers[1].restore_portable_state(portable,state_id)
        copied=workers[1].evaluate(_snapshot(workers[1]),state_id)
        assert copied.raw==reference.raw and copied.parameters==reference.parameters
        np.testing.assert_array_equal(copied.total.forces_kj_mol_nm,reference.total.forces_kj_mol_nm)
        assert _snapshot(workers[0]).box_nm==_snapshot(workers[1]).box_nm
        for worker in workers:
            assert worker.evaluator.system.getNumConstraints()==len(bundle.physical.constraints)
            assert [worker.evaluator.system.getParticleMass(i) for i in range(worker.evaluator.system.getNumParticles())]==list(np.array(bundle.physical.masses_da)*unit.dalton)
            worker.restore_checkpoint(checkpoint,state_id)
            worker.evaluator.integrator.step(2)
        a,b=(_snapshot(w) for w in workers)
        assert a==b
        assert workers[0].evaluate(a,state_id).raw==workers[1].evaluate(b,state_id).raw


OFFLINE_PROBE=r'''
import builtins,io,json,os,pathlib,socket,sys
def denied(*args,**kwargs): raise RuntimeError('network disabled for sealed solvent process')
socket.socket.connect=denied; socket.socket.connect_ex=denied
socket.create_connection=denied; socket.getaddrinfo=denied
roots=[pathlib.Path(p).resolve() for p in sys.argv[2:]]
def guard(file):
    if isinstance(file,(str,bytes,os.PathLike)):
        p=pathlib.Path(os.fsdecode(file)).resolve()
        if any(p==r or r in p.parents for r in roots): raise RuntimeError('original source/run/cache unavailable: '+str(p))
old_open,old_io,old_os=builtins.open,io.open,os.open
def checked_open(file,*a,**k): guard(file); return old_open(file,*a,**k)
def checked_io(file,*a,**k): guard(file); return old_io(file,*a,**k)
def checked_os(file,*a,**k): guard(file); return old_os(file,*a,**k)
builtins.open=checked_open; io.open=checked_io; os.open=checked_os
from atm_mlmm.adapters.atom import load_worker_run
from atm_mlmm.workflow import _snapshot
import atm_mlmm.models.mace as mace
import torch
run=pathlib.Path(sys.argv[1]); metadata=json.loads((run/'metadata.json').read_text())
assert str(pathlib.Path(mace.__file__).resolve()).startswith(str(run/'worker/runtime/source'))
with load_worker_run(run/'worker',metadata['worker_manifest_sha256'],trusted=True) as worker:
    record=json.loads((run/'samples/000000/record.json').read_text())
    worker.restore_checkpoint((run/'samples/000000/checkpoint.chk').read_bytes(),record['state_id'])
    result=worker.evaluate(_snapshot(worker),record['state_id'])
    assert dict(result.parameters)==record['parameters']
    assert result.total.energy_kj_mol==record['raw']['system_total_energy_kJ_mol']
    assert [list(v) for v in result.total.forces_kj_mol_nm]==record['real_forces_kj_mol_nm']
    model=mace.load_model()
    tensors=list(model.parameters())+list(model.buffers())
    assert all(t.device.type=='cpu' for t in tensors)
    assert all(t.dtype==torch.float64 for t in tensors if t.is_floating_point())
    assert worker.evaluator.context.getPlatform().getName()=='Reference'
    from atm_mlmm.workflow import resume_run
result=resume_run(run,trusted=True)
result.update(network_disabled=True,original_paths_denied=True,actual_model_device='cpu',actual_model_dtype='float64',model_sha256=mace.CHECKPOINT_SHA256)
print(json.dumps(result))
'''


@pytest.mark.model_assets
def test_solvated_offline_cache_independent_reload_and_devices(water_run,tmp_path):
    from atm_mlmm.persistence import read_sample_chunks
    _,_,original,_,_,rows=water_run
    relocated=tmp_path/'relocated'; shutil.copytree(original,relocated)
    # Continue an actual committed prefix, not an already-completed no-op.
    for index in (1,2): shutil.rmtree(relocated/'samples'/f'{index:06d}')
    caches=[tmp_path/name for name in ('no-xdg','no-torch','no-mace')]
    env={**os.environ,'PYTHONPATH':str(relocated/'worker/runtime/source'),'OPENBLAS_NUM_THREADS':'2',
         'XDG_CACHE_HOME':str(caches[0]),'TORCH_HOME':str(caches[1]),'MACE_CACHE_DIR':str(caches[2])}
    child=subprocess.run([sys.executable,'-c',OFFLINE_PROBE,str(relocated),str(ROOT),str(original),*(str(p) for p in caches)],
        cwd=tmp_path,env=env,text=True,capture_output=True,timeout=150)
    (tmp_path/'offline-stdout.txt').write_text(child.stdout); (tmp_path/'offline-stderr.txt').write_text(child.stderr)
    assert child.returncode==0,child.stdout+child.stderr
    report=json.loads(child.stdout.splitlines()[-1])
    assert report['status']=='complete' and report['samples']==3
    assert report['network_disabled'] and report['original_paths_denied']
    assert report['actual_model_device']=='cpu' and report['actual_model_dtype']=='float64'
    copied=read_sample_chunks(relocated/'samples')
    assert len(copied)==3 and len({r['sample_id'] for r in copied})==3
    for a,b in zip(rows,copied):
        for key in ('state_id','sequence_number','raw','positions_nm','velocities_nm_ps','real_forces_kj_mol_nm','box_nm'):
            assert a[key]==b[key]
