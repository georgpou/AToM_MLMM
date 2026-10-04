"""Independent map/physical-force oracle for saved cloud/control frames."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import numpy as np
from atm_mlmm.adapters.atom import load_worker_run
from atm_mlmm.atm import PhysicalEvaluator
from atm_mlmm.persistence import read_sample_chunks
from atm_mlmm.schema import Snapshot,from_json
from atm_mlmm.schedule import reduced_potentials

OUT=Path(__file__).resolve().parent
ROOT=Path('/tmp/atm-mlmm-g09-independent-readonly')
PILOT=Path('/workspace/cloud-engine-pilots/host-v1')
CAPTURE=ROOT/'Worker_Log/Milestone_05/evidence/G09_v1/host-pilot-capture'
diagnostics=json.loads((ROOT/'Worker_Log/Milestone_05/evidence/G09_v1/host-pilot-diagnostics.json').read_text())
for name,digest in diagnostics['capture_files'].items():
    assert hashlib.sha256((CAPTURE/name).read_bytes()).hexdigest()==digest,name
    assert (PILOT/name).read_bytes()==(CAPTURE/name).read_bytes(),name
pilotrows=json.loads((PILOT/'observations.json').read_text())
assert len(pilotrows)==60 and pilotrows==read_sample_chunks(PILOT/'samples')
assert len({r['sample_id'] for r in pilotrows})==60

attempts=[('crown48',PILOT,[0,19,20,39,40,59]),
          ('cappedABFE32',Path('/tmp/g09-independent-focused/test_same_runner_preserves_cap0/control'),[0,1,2]),
          ('cappedRBFE41',Path('/tmp/g09-independent-focused/test_same_runner_preserves_cap1/control'),[0,1,2])]
report=[]
for label,directory,selected in attempts:
    rows=json.loads((directory/'observations.json').read_text())
    metadata=json.loads((directory/'metadata.json').read_text())
    bundle=from_json((directory/'worker/bundle.json').read_text())
    runtime=from_json((directory/'worker/runtime.json').read_text())
    records=from_json((directory/'records.json').read_text())
    matrix=reduced_potentials(records)
    ids=tuple(a.atom_id for a in bundle.physical.topology.atoms)
    index={a:i for i,a in enumerate(ids)}
    ligands=[m for m in bundle.physical.topology.molecules if m.role=='ligand']
    obstacles=[index[a] for m in bundle.physical.topology.molecules if m.role in ('host','protein') for a in m.atom_ids]
    displacement=np.asarray(metadata['settings']['displacement_nm'])
    radii=np.array([{'H':.12,'C':.17,'N':.155,'O':.152}[a.element] for a in bundle.physical.topology.atoms])
    ratio_min=float('inf');bulk_min=float('inf')
    for row in rows:
        assert tuple(row['real_atom_ids'])==ids
        assert row['physical_identity']==bundle.physical.content_identity
        assert row['transfer_identity']==bundle.transfer.content_identity
        for key in ('positions_nm','velocities_nm_ps','real_forces_kj_mol_nm'):
            assert np.asarray(row[key]).shape==(len(ids),3) and np.isfinite(row[key]).all()
        x=np.asarray(row['positions_nm']);mapped=x.copy()
        for sign,molecule in zip((1.,-1.),ligands):
            mapped[[index[a] for a in molecule.atom_ids]]+=sign*displacement
        for geometry in (x,mapped):
            for i,molecule in enumerate(bundle.physical.topology.molecules):
                a=[index[v] for v in molecule.atom_ids]
                for other in bundle.physical.topology.molecules[i+1:]:
                    b=[index[v] for v in other.atom_ids]
                    distances=np.linalg.norm(geometry[a,None,:]-geometry[None,b,:],axis=2)
                    ratio_min=min(ratio_min,float(np.min(distances/(radii[a,None]+radii[None,b]))))
        for j,molecule in enumerate(ligands):
            geometry=mapped if j==0 else x
            distances=np.linalg.norm(geometry[[index[a] for a in molecule.atom_ids],None,:]-geometry[None,obstacles,:],axis=2)
            bulk_min=min(bulk_min,float(np.min(distances)))
    assert ratio_min>=.65 and bulk_min>=.65
    errors=dict(raw_energy=0.,total_energy=0.,full_real_force=0.,cross_state_energy=0.,constructor_energy=0.)
    comparisons=[]
    with PhysicalEvaluator(bundle.physical,runtime) as direct:
        with load_worker_run(directory/'worker',metadata['worker_manifest_sha256'],trusted=True) as worker:
            assert worker.worker.context is worker.evaluator.context
            initial=from_json((directory/'worker/snapshot.json').read_text())
            handover=worker.evaluate(initial,worker.manifest['state_id'])
            declared=json.loads((directory/'handover-parity.json').read_text())
            errors['constructor_energy']=abs(handover.total.energy_kj_mol-declared['energy_kj_mol'])
            np.testing.assert_allclose(handover.total.forces_kj_mol_nm,declared['all_real_forces_kj_mol_nm'],atol=1e-7,rtol=0)
            for i in selected:
                row=rows[i];x=np.asarray(row['positions_nm']);mapped=x.copy()
                for sign,molecule in zip((1.,-1.),ligands):
                    mapped[[index[a] for a in molecule.atom_ids]]+=sign*displacement
                snapshot=Snapshot(ids,x,None)
                first=direct.evaluate(snapshot)
                second=direct.evaluate(replace(snapshot,positions_nm=mapped))
                f0=np.asarray(first.forces_kj_mol_nm);f1=np.asarray(second.forces_kj_mol_nm)
                outside=0.;outside_forces=np.zeros_like(x)
                for atom in bundle.restraints.atom_ids:
                    j=index[atom];delta=x[j]-bundle.restraints.center_nm
                    outside+=.5*bundle.restraints.spring_constant*float(delta@delta)
                    outside_forces[j]-=bundle.restraints.spring_constant*delta
                raw_error=max(abs(first.energy_kj_mol-row['raw']['u0_raw_kJ_mol']),abs(second.energy_kj_mol-row['raw']['u1_raw_kJ_mol']))
                assert raw_error<=1e-8
                errors['raw_energy']=max(errors['raw_energy'],raw_error)
                assert abs(outside-row['raw']['outside_energy_kJ_mol'])<=1e-8
                for j,state in enumerate(bundle.schedule.states):
                    p=state.parameters
                    assert p['Lambda1']==p['Lambda2'] and p['Direction']==1. and p['UOffset']==p['W0']==p['Acore']==0.
                    lam=p['Lambda1']
                    expected=(1-lam)*first.energy_kj_mol+lam*second.energy_kj_mol+outside
                    expected_forces=(1-lam)*f0+lam*f1+outside_forces
                    actual=worker.evaluate(snapshot,state.state_id)
                    error=abs(expected-actual.total.energy_kj_mol)
                    force_error=float(np.max(np.abs(expected_forces-np.asarray(actual.total.forces_kj_mol_nm))))
                    cross_error=abs(expected-matrix[j,i]*.00831446261815324*runtime.temperature_K)
                    assert error<=1e-8 and cross_error<=1e-8 and force_error<=1e-7
                    errors['total_energy']=max(errors['total_energy'],error)
                    errors['full_real_force']=max(errors['full_real_force'],force_error)
                    errors['cross_state_energy']=max(errors['cross_state_energy'],cross_error)
                    if state.state_id==row['state_id']:
                        np.testing.assert_allclose(row['real_forces_kj_mol_nm'],actual.total.forces_kj_mol_nm,atol=1e-7,rtol=0)
                        assert actual.parameters==row['parameters'] and actual.raw.system_total_energy_kJ_mol==row['raw']['system_total_energy_kJ_mol']
                comparisons.append(dict(sample_id=row['sample_id'],u0=first.energy_kj_mol,u1=second.energy_kj_mol,
                                        raw_energy_error=raw_error))
    report.append(dict(fixture=label,atoms=len(ids),all_frames_checked=len(rows),independent_frames=len(selected),
                       state_evaluations=len(selected)*len(bundle.schedule.states),
                       minimum_Bondi_ratio=ratio_min,minimum_bulk_distance_nm=bulk_min,
                       errors=errors,comparisons=comparisons,
                       worker_manifest_sha256=metadata['worker_manifest_sha256'],
                       physical_identity=bundle.physical.content_identity,
                       observations_sha256=hashlib.sha256((directory/'observations.json').read_bytes()).hexdigest()))
(OUT/'numerical-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps([{k:v for k,v in r.items() if k!='comparisons'} for r in report],indent=2))
