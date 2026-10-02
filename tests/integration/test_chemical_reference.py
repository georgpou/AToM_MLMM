"""Stable G05-T4 checks; missing actual reviewed Q data are explicit failures."""
import json
from pathlib import Path
import numpy as np
import pytest

from atm_mlmm.chemical_reference import force_metrics, load_references, relative_errors
from tests.integration.test_model_adapter import capture

pytestmark=pytest.mark.model_assets
ROOT=Path(__file__).resolve().parents[2]/'fixtures/chemical_reference_v3'
EV_FORCE=1.6021766208e-19*6.022140857e23/1000.*10.


def rows():
    return {p.stem:json.loads(p.read_text()) for p in sorted((ROOT/'structures').glob('*.json'))}


def quantum_numerics(settings,references,structures,label):
    """Validate fine grids and every actual monomer orientation before reuse."""
    records=[]
    for name in settings['convergence_checks']['rows']:
        coarse,fine=references[name],references[name+'-fine-grid']
        energy_error=abs(coarse['energy_kj_mol']-fine['energy_kj_mol'])/4.184
        rms,maximum=force_metrics(coarse['forces_kj_mol_nm']/EV_FORCE,fine['forces_kj_mol_nm']/EV_FORCE)
        records.append({'kind':'fine-grid','name':name,'energy_error_kcal_mol':energy_error,
                        'force_rms_eV_angstrom':rms,'force_max_eV_angstrom':maximum})
    for path in sorted((ROOT/'quadrature_controls').glob('*.json')):
        control=json.loads(path.read_text());actual=references[control['name']];base=references[control['baseline']]
        rotation=np.asarray(control['rotation'])
        energy_error=abs(actual['energy_kj_mol']-base['energy_kj_mol'])/4.184
        rms,maximum=force_metrics(actual['forces_kj_mol_nm']/EV_FORCE,
                                 base['forces_kj_mol_nm']@rotation.T/EV_FORCE)
        records.append({'kind':'monomer-rotation','name':control['name'],'energy_error_kcal_mol':energy_error,
                        'force_rms_eV_angstrom':rms,'force_max_eV_angstrom':maximum})
    capture('quantum-numerical-controls-'+label,{'records':records})
    for record in records:
        assert record['energy_error_kcal_mol']<=.02,record
        assert record['force_rms_eV_angstrom']<=.002,record
        assert record['force_max_eV_angstrom']<=.005,record


def cap_project(row,forces):
    """Independent fixed-length cap Jacobian, including every real parent."""
    if row.get('cap') is None:return np.asarray(forces)
    cap=row['cap'];parent=row['parent'];r=np.asarray(parent['positions_angstrom'])
    a=parent['atom_ids'].index(cap['ml_parent_id']);b=parent['atom_ids'].index(cap['mm_parent_id'])
    n=r[b]-r[a];length=np.linalg.norm(n);n/=length
    jac=cap['distance_angstrom']/length*(np.eye(3)-np.outer(n,n))
    result=np.zeros_like(r)
    result[cap['real_source_indices']]=np.asarray(forces)[:-1]
    result[a]+=(np.eye(3)-jac).T@np.asarray(forces)[-1]
    result[b]+=jac.T@np.asarray(forces)[-1]
    return result


def force_record(row,model,reference):
    mf=np.asarray(model['forces_kj_mol_nm'])/EV_FORCE;qf=reference['forces_kj_mol_nm']/EV_FORCE
    rms,maximum=force_metrics(mf,qf)
    result={'name':row['name'],'force_rms_eV_angstrom':rms,'force_atom_max_eV_angstrom':maximum,
            'model_raw_forces_eV_angstrom':mf.tolist(),'quantum_raw_forces_eV_angstrom':qf.tolist()}
    if row.get('cap') is not None:
        pm,pq=cap_project(row,mf),cap_project(row,qf)
        prms,pmax=force_metrics(pm,pq)
        result.update(projected_rms_eV_angstrom=prms,projected_atom_max_eV_angstrom=pmax,
                      model_parent_forces_eV_angstrom=pm.tolist(),quantum_parent_forces_eV_angstrom=pq.tolist())
    return result


def assert_forces(record,settings):
    assert record['force_rms_eV_angstrom']<=settings['force_component_rms_eV_angstrom'],record['name']
    assert record['force_atom_max_eV_angstrom']<=settings['force_atom_vector_max_eV_angstrom'],record['name']
    if 'projected_rms_eV_angstrom' in record:
        assert record['projected_rms_eV_angstrom']<=settings['force_component_rms_eV_angstrom'],record['name']
        assert record['projected_atom_max_eV_angstrom']<=settings['force_atom_vector_max_eV_angstrom'],record['name']


def test_exact_capped_conformer_reference():
    # This check must fail closed before evaluating any model if data/decisions
    # are missing. A toy or native/adapter agreement cannot satisfy it.
    settings,references=load_references(ROOT)
    structures=rows();quantum_numerics(settings,references,structures,'conformers')
    from atm_mlmm.model_reference import NativeMACE
    native=NativeMACE();records=[];families=[]
    for family in ('ethanol','butane','methanol','acetamide'):
        inputs=[r for r in structures.values() if r['family']==family]
        evaluated=[native.evaluate(r['atomic_numbers'],np.asarray(r['positions_angstrom'])/10.) for r in inputs]
        baseline=next(i for i,r in enumerate(inputs) if r['name']==r['baseline'])
        errors=relative_errors([r['energy_kj_mol'] for r in evaluated],
                               [references[r['name']]['energy_kj_mol'] for r in inputs],baseline)/4.184
        families.append({'family':family,'rows':[r['name'] for r in inputs],
                         'relative_energy_errors_kcal_mol':errors.tolist(),
                         'energy_rms_kcal_mol':float(np.sqrt(np.mean(errors**2))),
                         'energy_max_kcal_mol':float(np.max(np.abs(errors))),
                         'native_inputs_outputs':evaluated})
        records.extend(force_record(r,m,references[r['name']]) for r,m in zip(inputs,evaluated))
    capture('chemical-conformers',{'families':families,'forces':records,'data':'actual reviewed quantum gradients'})
    for family in families:
        assert family['energy_rms_kcal_mol']<=settings['conformer_energy_rms_kcal_mol'],family
        assert family['energy_max_kcal_mol']<=settings['conformer_energy_max_kcal_mol'],family
    for record in records:assert_forces(record,settings)


def test_frozen_contact_reference():
    settings,references=load_references(ROOT)
    structures=rows();quantum_numerics(settings,references,structures,'contacts')
    # Use a separate capture label because both stable checks run these gates.
    from atm_mlmm.model_reference import NativeMACE
    native=NativeMACE();baseline={}
    for r in structures.values():
        if 'fragment_count' not in r and r['name']==r['baseline']:
            baseline[r['name']]=native.evaluate(r['atomic_numbers'],np.asarray(r['positions_angstrom'])/10.)
    records=[];energies=[]
    for row in structures.values():
        if 'fragment_count' not in row:continue
        actual=native.evaluate(row['atomic_numbers'],np.asarray(row['positions_angstrom'])/10.)
        q=references[row['name']];f,l=row['fragment_baseline'],row['ligand_baseline']
        mi=actual['energy_kj_mol']-baseline[f]['energy_kj_mol']-baseline[l]['energy_kj_mol']
        qi=q['energy_kj_mol']-references[f]['energy_kj_mol']-references[l]['energy_kj_mol']
        record=force_record(row,actual,q);n=row['fragment_count'];rot=np.asarray(row['ligand_transform']['rotation'])
        model_net=np.sum(np.asarray(actual['forces_kj_mol_nm'])[n:]-np.asarray(baseline[l]['forces_kj_mol_nm'])@rot.T,axis=0)/EV_FORCE
        quantum_net=np.sum(q['forces_kj_mol_nm'][n:]-references[l]['forces_kj_mol_nm']@rot.T,axis=0)/EV_FORCE
        record.update(model_net_ligand_force_eV_angstrom=model_net.tolist(),
                      quantum_net_ligand_force_eV_angstrom=quantum_net.tolist(),
                      net_ligand_force_error_eV_angstrom=float(np.linalg.norm(model_net-quantum_net)))
        # Include cap-parent errors for the exact transformed parent description.
        fragment={**structures[f],'parent':row['g07_controls']['parent']}
        projected_m=np.vstack([cap_project(fragment,np.asarray(actual['forces_kj_mol_nm'])[:n]/EV_FORCE),
                               np.asarray(actual['forces_kj_mol_nm'])[n:]/EV_FORCE])
        projected_q=np.vstack([cap_project(fragment,q['forces_kj_mol_nm'][:n]/EV_FORCE),q['forces_kj_mol_nm'][n:]/EV_FORCE])
        prms,pmax=force_metrics(projected_m,projected_q)
        record.update(projected_rms_eV_angstrom=prms,projected_atom_max_eV_angstrom=pmax)
        records.append(record)
        energies.append({'name':row['name'],'family':row['family'],'kind':row['kind'],
                         'model_interaction_kcal_mol':mi/4.184,'quantum_interaction_kcal_mol':qi/4.184,
                         'native':actual,'error_kcal_mol':(mi-qi)/4.184})
    families=[]
    for family in sorted({r['family'] for r in energies}):
        group=[r for r in energies if r['family']==family]
        separated=next(r for r in group if r['kind']=='separated')
        errors=np.array([r['error_kcal_mol'] for r in group])
        relative=errors-separated['error_kcal_mol']
        families.append({'family':family,'interaction_rms':float(np.sqrt(np.mean(errors**2))),
                         'interaction_max':float(np.max(np.abs(errors))),
                         'contact_minus_separated_rms':float(np.sqrt(np.mean(relative**2))),
                         'contact_minus_separated_max':float(np.max(np.abs(relative)))})
    capture('chemical-contacts',{'energies':energies,'forces':records,'families':families})
    for family in families:
        for key in ('interaction_rms','contact_minus_separated_rms'):
            assert family[key]<=settings['contact_energy_rms_kcal_mol'],family
        for key in ('interaction_max','contact_minus_separated_max'):
            assert family[key]<=settings['contact_energy_max_kcal_mol'],family
    for record in records:
        assert_forces(record,settings)
        assert record['net_ligand_force_error_eV_angstrom']<=settings['ligand_net_interaction_force_max_eV_angstrom'],record['name']
        energy=next(e for e in energies if e['name']==record['name'])
        if energy['quantum_interaction_kcal_mol']<=-settings['sign_attraction_minimum_kcal_mol']:
            assert energy['model_interaction_kcal_mol']<0.,record['name']
        if record['name'] in settings['compressed_rows'] and record['quantum_net_ligand_force_eV_angstrom'][0]>0.:
            assert record['model_net_ligand_force_eV_angstrom'][0]>0.,record['name']
