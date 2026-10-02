"""Reproduce the small, independent M02 numerical/ownership evidence."""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
from tests.analytic_oracle import (REFERENCE, mapped_positions, physical_answer,
                                   outside_answer, nonlinear_answer, check)
from tests.workflow.test_atom_force_routing import atom_case
from atm_mlmm.atm import build_atm, evaluate_atm
from atm_mlmm.adapters.atom import build_atom, timestep_fs_to_ps
from atm_mlmm.prepare import build_preparation
from atm_mlmm.routing import check_active_forces
from atm_mlmm.schema import to_json

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, default=Path('/tmp/m02-evidence/numerical-results.json'))
args=parser.parse_args()
root=Path.cwd()
rows=[]
identities={}
for platform in ('Reference','CPU'):
    runtime=replace(REFERENCE,platform=platform)
    for environment in (False,True):
        for kind in ('abfe','rbfe'):
            physical, transfer, schedule, restraints, snapshot=atom_case(kind,environment=environment,marker=2000.)
            key=(platform,environment)
            if key in identities:
                assert identities[key]==physical.content_identity, 'protocol changed physical Hamiltonian'
            identities[key]=physical.content_identity
            native=build_atm(physical,transfer,schedule,restraints)
            with build_atom(physical,transfer,schedule,restraints,runtime) as run:
                for state in schedule.states:
                    u0,f0=physical_answer(mapped_positions(snapshot.positions_nm,kind,0),environment=environment,marker=2000.)
                    u1,f1=physical_answer(mapped_positions(snapshot.positions_nm,kind,1),environment=environment,marker=2000.)
                    expression,weights,soft=nonlinear_answer(u0,u1,state.parameters)
                    outside,fk=outside_answer(snapshot.positions_nm)
                    expected=(u0,u1,expression,outside,weights[0]*f0+weights[1]*f1+fk)
                    direct_native=evaluate_atm(native,snapshot,state.state_id,runtime)
                    actual=run.evaluate(snapshot,state.state_id)
                    rows.append(dict(platform=platform,environment=environment,protocol=kind,state_id=state.state_id,
                                     physical_identity=physical.content_identity,transfer_identity=transfer.content_identity,
                                     schedule_identity=schedule.content_identity,restraint_identity=restraints.content_identity,
                                     snapshot=json.loads(to_json(snapshot)),runtime=json.loads(to_json(runtime)),
                                     raw_and_forces=json.loads(to_json(actual)),native_errors=check(direct_native,expected),
                                     upstream_errors=check(actual,expected),softcore_error=abs(actual.raw.delta_u_softcore_kJ_mol-soft),
                                     native_upstream_max_force_error=float(np.max(np.abs(np.asarray(actual.total.forces_kj_mol_nm)-direct_native.total.forces_kj_mol_nm))),
                                     active_forces=check_active_forces(run.evaluator.context,run.evaluator.integrator),
                                     routing_report=[json.loads(to_json(r)) for r in run.bundle.routing_report]))
with build_preparation(physical,REFERENCE) as preparation:
    preparation.evaluate(snapshot)
    preparation_measurement=check_active_forces(preparation.context,preparation.integrator)
report=dict(schema_version='1.0',profile='core-analytic-cpu',code_snapshot=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            fixture_sha256=hashlib.sha256((root/'fixtures/analytic/transfer-v1.json').read_bytes()).hexdigest(),
            scope='seven-real-atom analytic local/environment substitutes; ABFE/RBFE transfer shapes; nonperiodic NVT; no binding claim',
            thresholds=dict(energy_abs_kJ_mol=1e-8,force_component_abs_kJ_mol_nm=1e-7,
                            starting_direct_atm_energy_kJ_mol=1e-4,starting_direct_atm_force_kJ_mol_nm=5e-3,
                            finite_difference_steps_nm=[1e-3,1e-4,1e-5],final_fd_max_component_error_kJ_mol_nm=1e-5),
            precision=dict(Reference='OpenMM Reference double / NumPy float64',CPU='OpenMM CPU platform defaults / NumPy float64; only these analytic terms are qualified'),
            integrator=dict(kind='LangevinMiddle',timestep_ps=timestep_fs_to_ps(.5),temperature_K=300.,ensemble='NVT',friction_per_ps=1.),
            cases=rows,preparation=preparation_measurement,
            maximum_energy_error_kJ_mol=max(v for r in rows for collection in ('native_errors','upstream_errors') for k,v in r[collection].items() if k!='max_force_error_kJ_mol_nm'),
            maximum_force_component_error_kJ_mol_nm=max(r[c]['max_force_error_kJ_mol_nm'] for r in rows for c in ('native_errors','upstream_errors')),
            deferred=['G00-T2 full loader/model qualification','G00-T3/GPU','M00 physical-reference decisions','caps/chemical/protein accuracy','periodic physics','actual electrostatic embedding','molecular binding/sampling/restart/exchange'])
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
print(json.dumps({k:report[k] for k in ('maximum_energy_error_kJ_mol','maximum_force_component_error_kJ_mol_nm')}))
