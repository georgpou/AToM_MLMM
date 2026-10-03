"""Independent arithmetic on frozen records/captures; no model/QM evaluation.

Do not import submitted metric or cap-projection implementation. Form energies
and forces from primitive Hartree/bohr and eV/angstrom arrays, then compare all
saved rows, aggregate statistics and the reviewer replay against those results.
"""
from pathlib import Path
import json
import csv
import datetime

import numpy as np

E = Path(__file__).resolve().parent
ROOT = E.parents[3]
PLAN = ROOT/'fixtures/chemical_reference_v3'
SUBMITTED = ROOT/'Worker_Log/Milestone_03/evidence/G05_v4'
read = lambda p: json.loads(Path(p).read_text())
settings = read(PLAN/'reference-settings.json')
rows = {p.stem: read(p) for p in sorted((PLAN/'structures').glob('*.json'))}
quantum = {p.stem: read(p) for p in (PLAN/'quantum/records').glob('*.json')}
conformers = read(SUBMITTED/'chemical-comparisons/chemical-conformers.json')
contacts = read(SUBMITTED/'chemical-comparisons/chemical-contacts.json')
summary = read(SUBMITTED/'results-summary.json')
captures = {r['name']:r for r in conformers['forces']+contacts['forces']}
native = {}
for group in conformers['families']:
    native.update(zip(group['rows'], group['native_inputs_outputs']))
native.update({r['name']:r['native'] for r in contacts['energies']})
assert set(rows)==set(captures)==set(native) and len(rows)==34

# The admitted ASE convention is CODATA 2014, different from a rounded 96.4853.
EV_KJ = 1.6021766208e-19*6.022140857e23/1000.
EV_FORCE = 10.*EV_KJ
HARTREE_KJ = 2625.4996382852164
BOHR_NM = 0.052917721067
assert settings['hartree_to_kJ_mol']==HARTREE_KJ
assert settings['bohr_to_nm']==BOHR_NM


def same(a,b,tolerance=1e-11):
    aa=np.asarray(a,dtype=float);bb=np.asarray(b,dtype=float)
    assert aa.shape==bb.shape
    assert np.isfinite(aa).all() and np.isfinite(bb).all()
    error=float(np.max(np.abs(aa-bb))) if aa.size else 0.
    assert error<=tolerance,(error,tolerance)
    return error


def statistics(error):
    error=np.asarray(error)
    return float(np.sqrt(np.sum(error*error)/error.size)),float(np.max(np.sqrt(np.sum(error*error,axis=1))))


def project(cap,parent,raw):
    xyz=np.asarray(parent['positions_angstrom'],float)
    ml=parent['atom_ids'].index(cap['ml_parent_id'])
    mm=parent['atom_ids'].index(cap['mm_parent_id'])
    delta=xyz[mm]-xyz[ml];length=float(np.sqrt(delta@delta));direction=delta/length
    tangential=np.eye(3)-direction[:,None]*direction[None,:]
    derivative_mm=cap['distance_angstrom']/length*tangential
    real=np.zeros(xyz.shape)
    for source,force in zip(cap['real_source_indices'],raw[:-1]):real[source]+=force
    real[ml]+=raw[-1]-derivative_mm@raw[-1]
    real[mm]+=derivative_mm@raw[-1]
    same(np.sum(real,axis=0),np.sum(raw,axis=0))
    return real


model_energy={};quantum_energy={};mf={};qf={};metrics={};projections={}
cap_reports={r['name']:r for r in read(SUBMITTED/'cap-parent-force-evidence.json')}
csv_rows={r['name']:r for r in csv.DictReader((SUBMITTED/'chemical-row-metrics.csv').open())}
assert set(csv_rows)==set(rows)
for name,row in rows.items():
    n=native[name];q=quantum[name];captured=captures[name]
    assert n['numbers']==row['atomic_numbers']
    same(n['positions_nm'],np.asarray(row['positions_angstrom'])/10.,1e-14)
    assert n['energy_convention']=='energy' and n['head']=='Default' and n['dtype']=='float64'
    assert n['pbc'] is False and n['box_nm'] is None and n['finite'] is True
    model_energy[name]=n['energy_eV']*EV_KJ
    quantum_energy[name]=q['energy_hartree']*HARTREE_KJ
    same(model_energy[name],n['energy_kj_mol'])
    mf[name]=-np.asarray(n['gradient_eV_angstrom'])
    qf[name]=-np.asarray(q['gradient_hartree_bohr'])*HARTREE_KJ/BOHR_NM/EV_FORCE
    same(mf[name]*EV_FORCE,n['forces_kj_mol_nm'])
    same(mf[name],captured['model_raw_forces_eV_angstrom'])
    same(qf[name],captured['quantum_raw_forces_eV_angstrom'])
    rms,maximum=statistics(mf[name]-qf[name])
    assert rms<=settings['force_component_rms_eV_angstrom']
    assert maximum<=settings['force_atom_vector_max_eV_angstrom']
    item=dict(name=name,family=row['family'],force_rms_eV_angstrom=rms,force_atom_max_eV_angstrom=maximum)
    if 'fragment_count' in row:
        split=row['fragment_count'];cap=row['fragment_cap'];parent=row['g07_controls']['parent']
        pm=np.vstack((project(cap,parent,mf[name][:split]),mf[name][split:]))
        pq=np.vstack((project(cap,parent,qf[name][:split]),qf[name][split:]))
        raw_cap_index=split-1
    elif row.get('cap'):
        cap=row['cap'];parent=row['parent'];pm=project(cap,parent,mf[name]);pq=project(cap,parent,qf[name])
        raw_cap_index=len(mf[name])-1
        same(pm,captured['model_parent_forces_eV_angstrom'])
        same(pq,captured['quantum_parent_forces_eV_angstrom'])
    else:pm=pq=None
    if pm is not None:
        prms,pmax=statistics(pm-pq)
        item.update(projected_rms_eV_angstrom=prms,projected_atom_max_eV_angstrom=pmax,
                    cap_raw_force_error_eV_angstrom=float(np.linalg.norm(mf[name][raw_cap_index]-qf[name][raw_cap_index])))
        assert prms<=settings['force_component_rms_eV_angstrom'] and pmax<=settings['force_atom_vector_max_eV_angstrom']
        cap_report=cap_reports[name]
        same(pm,cap_report['model_full_parent_and_ligand_forces_eV_angstrom'])
        same(pq,cap_report['quantum_full_parent_and_ligand_forces_eV_angstrom'])
        same(mf[name][raw_cap_index],cap_report['raw_cap_model_force_eV_angstrom'])
        same(qf[name][raw_cap_index],cap_report['raw_cap_quantum_force_eV_angstrom'])
        projections[name]=dict(model=pm.tolist(),quantum=pq.tolist())
    for key,value in item.items():
        if key in captured and isinstance(value,float):same(value,captured[key])
        if key in csv_rows[name] and isinstance(value,float):same(value,float(csv_rows[name][key]))
    metrics[name]=item
assert len(projections)==28

conformer_groups=[]
for family in sorted({r['family'] for r in rows.values() if 'fragment_count' not in r}):
    group=[r for r in rows.values() if r['family']==family]
    base=group[0]['baseline']
    errors=[((model_energy[r['name']]-model_energy[base])-(quantum_energy[r['name']]-quantum_energy[base]))/4.184 for r in group]
    rms=float(np.sqrt(np.mean(np.asarray(errors)**2)));maximum=max(abs(x) for x in errors)
    assert rms<=settings['conformer_energy_rms_kcal_mol'] and maximum<=settings['conformer_energy_max_kcal_mol']
    saved=next(f for f in conformers['families'] if f['family']==family)
    same([r['name'] for r in []],[])
    by_name=dict(zip([r['name'] for r in group],errors))
    for name,old in zip(saved['rows'],saved['relative_energy_errors_kcal_mol']):same(by_name[name],old)
    same(rms,saved['energy_rms_kcal_mol']);same(maximum,saved['energy_max_kcal_mol'])
    for name,value in by_name.items():
        metrics[name]['relative_energy_error_kcal_mol']=value
        same(value,float(csv_rows[name]['relative_energy_error_kcal_mol']))
    conformer_groups.append(dict(family=family,rms_kcal_mol=rms,max_kcal_mol=maximum))

signs=[]
for name,row in rows.items():
    if 'fragment_count' not in row:continue
    fragment=row['fragment_baseline'];ligand=row['ligand_baseline'];split=row['fragment_count']
    rr=np.asarray(row['positions_angstrom'])
    frag_t=row['fragment_transform'];lig_t=row['ligand_transform']
    frag_rr=(np.asarray(rows[fragment]['positions_angstrom'])-frag_t['source_anchor_angstrom'])@np.asarray(frag_t['rotation']).T
    lig_rr=(np.asarray(rows[ligand]['positions_angstrom'])-lig_t['source_anchor_angstrom'])@np.asarray(lig_t['rotation']).T+lig_t['translation_angstrom']
    same(rr[:split],frag_rr,2e-14);same(rr[split:],lig_rr,2e-14)
    distances=np.linalg.norm(rr[:split,None,:]-rr[None,split:,:],axis=2)
    interedges=[edge for edge in native[name]['directed_edges'] if (edge[0]<split)!=(edge[1]<split)]
    if row['kind']=='separated':assert np.min(distances)>=15. and not interedges
    else:assert interedges
    mi=(model_energy[name]-model_energy[fragment]-model_energy[ligand])/4.184
    qi=(quantum_energy[name]-quantum_energy[fragment]-quantum_energy[ligand])/4.184
    rotation=np.asarray(lig_t['rotation'])
    model_net=np.sum(mf[name][split:]-mf[ligand]@rotation.T,axis=0)
    quantum_net=np.sum(qf[name][split:]-qf[ligand]@rotation.T,axis=0)
    net_error=float(np.linalg.norm(model_net-quantum_net))
    assert net_error<=settings['ligand_net_interaction_force_max_eV_angstrom']
    same(model_net,captures[name]['model_net_ligand_force_eV_angstrom'])
    same(quantum_net,captures[name]['quantum_net_ligand_force_eV_angstrom'])
    same(net_error,captures[name]['net_ligand_force_error_eV_angstrom'])
    metrics[name].update(model_interaction_kcal_mol=mi,quantum_interaction_kcal_mol=qi,
                         interaction_error_kcal_mol=mi-qi,net_ligand_force_error_eV_angstrom=net_error)
    attraction=qi<=-settings['sign_attraction_minimum_kcal_mol']
    repulsion=bool(name in settings['compressed_rows'] and quantum_net[0]>0.)
    assert not attraction or mi<0.
    assert not repulsion or model_net[0]>0.
    signs.append(dict(name=name,attraction_required=attraction,repulsion_required=repulsion,
                      model_interaction_kcal_mol=mi,quantum_interaction_kcal_mol=qi,
                      model_approach_force_eV_angstrom=float(model_net[0]),quantum_approach_force_eV_angstrom=float(quantum_net[0])))

contact_groups=[]
for family in sorted({r['family'] for r in rows.values() if 'fragment_count' in r}):
    group=[metrics[r['name']] for r in rows.values() if r['family']==family]
    separated=next(metrics[r['name']] for r in rows.values() if r['family']==family and r['kind']=='separated')
    error=np.array([r['interaction_error_kcal_mol'] for r in group]);relative=error-separated['interaction_error_kcal_mol']
    entry=dict(family=family,interaction_rms=float(np.sqrt(np.mean(error**2))),interaction_max=float(np.max(np.abs(error))),
               contact_minus_separated_rms=float(np.sqrt(np.mean(relative**2))),contact_minus_separated_max=float(np.max(np.abs(relative))))
    for key in ('interaction_rms','contact_minus_separated_rms'):assert entry[key]<=settings['contact_energy_rms_kcal_mol']
    for key in ('interaction_max','contact_minus_separated_max'):assert entry[key]<=settings['contact_energy_max_kcal_mol']
    saved=next(f for f in contacts['families'] if f['family']==family)
    for key in entry:
        if key!='family':same(entry[key],saved[key])
    for item,rel in zip(group,relative):item['contact_minus_separated_error_kcal_mol']=float(rel)
    contact_groups.append(entry)
for name,item in metrics.items():
    for key,value in item.items():
        if isinstance(value,float) and key in csv_rows[name]:same(value,float(csv_rows[name][key]))

controls=[]
def qforces(name):return -np.asarray(quantum[name]['gradient_hartree_bohr'])*HARTREE_KJ/BOHR_NM/EV_FORCE
def control(name,other,rotation,kind):
    diff=qforces(name)-qforces(other)@np.asarray(rotation).T
    rms,maximum=statistics(diff)
    energy=abs((quantum[name]['energy_hartree']-quantum[other]['energy_hartree'])*HARTREE_KJ)/4.184
    assert energy<=.02 and rms<=.002 and maximum<=.005
    controls.append(dict(name=other if kind=='fine-grid' else name,kind=kind,energy_error_kcal_mol=energy,force_rms_eV_angstrom=rms,force_max_eV_angstrom=maximum))
for name in settings['convergence_checks']['rows']:control(name+'-fine-grid',name,np.eye(3),'fine-grid')
for p in sorted((PLAN/'quadrature_controls').glob('*.json')):
    row=read(p);control(row['name'],row['baseline'],row['rotation'],'monomer-rotation')
assert len(controls)==12
submitted_controls={r['name']:r for r in read(SUBMITTED/'quantum-numerical-validation/quantum-numerical-controls-prebundle.json')['records']}
for item in controls:
    for key,value in item.items():
        if isinstance(value,float):same(value,submitted_controls[item['name']][key],5e-11)

maxima={key:max(item[key] for item in metrics.values() if key in item) for key in summary['maxima']}
for key,value in maxima.items():same(value,summary['maxima'][key])
control_maxima={key:max(item[key] for item in controls) for key in summary['numerical_control_maxima']}
for key,value in control_maxima.items():same(value,summary['numerical_control_maxima'][key],5e-11)
assert sum(x['attraction_required'] for x in signs)==7
assert sum(x['repulsion_required'] for x in signs)==4
sign_csv={r['name']:r for r in csv.DictReader((SUBMITTED/'contact-sign-checks.csv').open())}
assert set(sign_csv)=={r['name'] for r in signs}
for item in signs:
    saved=sign_csv[item['name']]
    for key in ('attraction_required','repulsion_required'):assert str(item[key])==saved[key]

# Compare fresh independent test-run captures with the submitted model captures.
fresh_c=read(E/'fresh-g05-captures/chemical-conformers.json')
fresh_t=read(E/'fresh-g05-captures/chemical-contacts.json')
fresh_forces={r['name']:r for r in fresh_c['forces']+fresh_t['forces']}
assert set(fresh_forces)==set(rows)
for name,cap in fresh_forces.items():
    same(cap['model_raw_forces_eV_angstrom'],mf[name])
    same(cap['quantum_raw_forces_eV_angstrom'],qf[name])
domain=read(E/'fresh-g05-captures/domain-scans.json')['raw_records']
assert len(domain)==36 and sum(r['admitted'] for r in domain)==34
for row in domain:
    if row['admitted']:assert row['native']['finite'] and 'exception' not in row

result=dict(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            scope='independent arithmetic only; no quantum generation, no model reevaluation in this script',
            chemical_rows=34,cap_parent_projections=28,conformer_families=conformer_groups,
            contact_families=contact_groups,numerical_controls=controls,maxima=maxima,numerical_control_maxima=control_maxima,
            attraction_signs_required=7,compressed_repulsion_signs_required=4,sign_rows=signs,
            per_row_metrics=list(metrics.values()),full_parent_and_ligand_projections=projections,
            fresh_model_captures_match=True,domain_samples=36,admitted_domain_samples=34)
with (E/'scientific-results-v2.json').open('x') as stream:json.dump(result,stream,indent=2,allow_nan=False);stream.write('\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['full_parent_and_ligand_projections','per_row_metrics','sign_rows','numerical_controls']},indent=2))
