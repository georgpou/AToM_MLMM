"""Independent fault inside a real worker integrator: retain failed coordinates.

The fault advances the actual integrator once, then raises a domain exception.
This exercises the controller's integration boundary, distinct from its
post-step domain/evaluation handler. Auditor captures are explicitly separate
from production archives.
"""
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

import openmm as mm
from openmm import unit

from atm_mlmm.adapters.atom import build_atom,export_worker_run,load_worker_run
from atm_mlmm.schema import NumericalDomainError
from atm_mlmm.workflow import _execute
from tests.workflow.test_atom_force_routing import atom_case
from tests.analytic_oracle import REFERENCE

OUT=Path(__file__).resolve().parent
work=Path(tempfile.mkdtemp(prefix='g09-independent-integration-failure-',dir='/tmp'))
physical,transfer,schedule,restraints,snapshot=atom_case('abfe')
with build_atom(physical,transfer,schedule,restraints,REFERENCE) as source:
    _,digest=export_worker_run(source,work/'worker',snapshot,'first')
active={}
load_original=load_worker_run
def tracked_load(*args,**kwargs):
    worker=load_original(*args,**kwargs)
    active[id(worker.evaluator.integrator)]=worker
    return worker

step_original=mm.LangevinMiddleIntegrator.step
fault={}
def failing_step(integrator,steps):
    step_original(integrator,1)
    worker=active[id(integrator)]
    state=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
    # Auditor capture: it does not make the production retention assertion pass.
    (OUT/'integration-failure-auditor-state.xml').write_text(mm.XmlSerializer.serialize(state))
    (OUT/'integration-failure-auditor-checkpoint.chk').write_bytes(worker.evaluator.context.createCheckpoint())
    fault.update(step=worker.evaluator.context.getStepCount(),
                 positions_nm=state.getPositions(asNumpy=True).value_in_unit(unit.nanometer).tolist(),
                 parameters=dict(state.getParameters()))
    raise NumericalDomainError('independent injected domain failure inside integrator.step')

metadata={'settings':{'frames_per_state':1,'steps_per_frame':1,'seed':41,
                     'displacement_nm':[.3,0.,0.],'protocol_kind':'abfe'},
          'worker_manifest_sha256':digest,'run_id':'independent-integration-failure',
          'runtime_identity':REFERENCE.content_identity,'profile':{}}
with patch('atm_mlmm.adapters.atom.load_worker_run',tracked_load),patch.object(mm.LangevinMiddleIntegrator,'step',failing_step):
    try:
        _execute(work,metadata)
    except NumericalDomainError as error:
        assert str(error)=='independent injected domain failure inside integrator.step'
        caught=str(error)
    else:
        raise AssertionError('fault must propagate')
archives=list(work.glob('failure-*'))
report=dict(error=caught,actual_integrator='LangevinMiddleIntegrator',actual_worker='OMMWorkerATMSync',
            advanced_step=fault['step'],production_failure_archives=[p.name for p in archives],
            committed_sample_directories=[p.name for p in (work/'samples').glob('*')] if (work/'samples').exists() else [],
            work_directory=str(work),auditor_capture='integration-failure-auditor-state.xml',
            retained_by_production=bool(archives))
(OUT/'integration-failure-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert archives,'integration exception escaped the retention handler; failed coordinates/checkpoint were not archived'
