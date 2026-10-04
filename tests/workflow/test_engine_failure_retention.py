"""Actual advanced-worker failures must retain state without energy reentry."""
import json
import openmm as mm
import pytest
from atm_mlmm.schema import NumericalDomainError
from tests.workflow.test_atom_force_routing import atom_case
from tests.analytic_oracle import REFERENCE


@pytest.mark.parametrize('origin',('integration','final_state'))
def test_advanced_actual_worker_failure_is_archived(tmp_path,monkeypatch,origin):
    import atm_mlmm.adapters.atom as adapter
    from atm_mlmm.workflow import _execute
    physical,transfer,schedule,restraints,snapshot=atom_case('abfe')
    out=tmp_path/'attempt'
    with adapter.build_atom(physical,transfer,schedule,restraints,REFERENCE) as source:
        _,digest=adapter.export_worker_run(source,out/'worker',snapshot,'first')
    owners,fault={},{}
    normal_load=adapter.load_worker_run
    normal_step=mm.LangevinMiddleIntegrator.step
    normal_state=mm.Context.getState
    normal_evaluate=adapter.WorkerRun.evaluate
    def track_load(*args,**kwargs):
        worker=normal_load(*args,**kwargs)
        owners[id(worker.evaluator.integrator)]=worker
        return worker
    def capture(worker):
        from atom_openmm.ommworker import OMMWorkerATMSync
        assert type(worker.worker) is OMMWorkerATMSync
        context=worker.evaluator.context
        state=normal_state(context,getPositions=True,getVelocities=True,getParameters=True)
        fault.update(xml=mm.XmlSerializer.serialize(state),checkpoint=context.createCheckpoint(),
                     actual_step=context.getStepCount(),triggered=True)
    def step(integrator,steps):
        assert steps==1
        normal_step(integrator,1)
        if origin=='integration':
            capture(owners[id(integrator)])
            raise NumericalDomainError('injected integration failure')
    def evaluate(worker,*args,**kwargs):
        result=normal_evaluate(worker,*args,**kwargs)
        if origin=='final_state':
            capture(worker)
            fault['next_state_fails']=True
        return result
    def state(context,*args,**kwargs):
        if fault.get('next_state_fails') and kwargs.get('getPositions'):
            fault['next_state_fails']=False
            raise NumericalDomainError('injected final_state failure')
        if fault.get('triggered') and (kwargs.get('getEnergy') or kwargs.get('getForces')):
            raise RuntimeError('archiving must not retrigger failed energy')
        return normal_state(context,*args,**kwargs)
    monkeypatch.setattr(adapter,'load_worker_run',track_load)
    monkeypatch.setattr(mm.LangevinMiddleIntegrator,'step',step)
    monkeypatch.setattr(adapter.WorkerRun,'evaluate',evaluate)
    monkeypatch.setattr(mm.Context,'getState',state)
    # This test targets exception boundaries, without a molecular domain claim.
    import atm_mlmm.workflow as workflow
    monkeypatch.setattr(workflow,'_domain',lambda *args:[])
    metadata={'settings':{'frames_per_state':1,'steps_per_frame':1,'seed':41,
                        'displacement_nm':[.3,0.,0.],'protocol_kind':'abfe'},
              'worker_manifest_sha256':digest,'run_id':'R1',
              'runtime_identity':REFERENCE.content_identity,'profile':{}}
    with pytest.raises(NumericalDomainError,match=f'injected {origin} failure'):
        _execute(out,metadata)
    failed=out/'failure-000000'
    assert (failed/'state.xml').read_text()==fault['xml']
    assert (failed/'checkpoint.chk').read_bytes()==fault['checkpoint']
    error=json.loads((failed/'error.json').read_text())
    assert error['actual_step']==fault['actual_step']==1
    assert error['attempted_sample_id']=='R1:first:1'
    assert error['walker_id']=='R1:first' and error['state_id']=='first'
    assert error['error_type']=='NumericalDomainError'
    assert not (out/'samples').exists()
