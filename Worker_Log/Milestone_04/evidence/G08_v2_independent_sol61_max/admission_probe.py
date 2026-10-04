"""Independent R1 closure, constructed without worker test helpers."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import numpy as np
from atm_mlmm.analysis import combine_free_energies
from atm_mlmm.schema import BindingResult, CorrectionRecord, ThermodynamicSpec, from_json, to_json

out=Path(__file__).resolve().parent
root=out.parents[3]
obligations=('translation_standard_state','bound_release','orientation','conformation','state_counting','midpoint_bridge')
ledger=tuple(CorrectionRecord(name,'computed',value,0.,'Independent deterministic affine fixture: '+name)
             for name,value in zip(obligations,(.23,-.11,.03,.16,-.14,.04)))
spec=ThermodynamicSpec('standard_binding_free_energy',{'bulk':-1.,'bound':1.},'bound_minus_bulk',
                       (('bulk','bound'),),{'bulk':'bulk fixture','bound':'bound fixture'},obligations,ledger,
                       1.6605390671738466,'separable infinite-space fixture','declared analytic restraints',
                       'explicit orientation fixture','one pose, unit symmetry')
covariance=np.array(((.09,.08),(.08,.16)))
def produce(definition,**kwargs):
    return combine_free_energies(('bulk','bound'),(17.,18.5),covariance,definition,**kwargs)
baseline=produce(spec)
report={'rejections':[],'positives':[],'failures':[],'metrics':{}}
def reject(name,call):
    try:
        value=call()
    except ValueError as exc:
        report['rejections'].append({'name':name,'type':type(exc).__name__,'error':str(exc)})
        return
    report['failures'].append({'name':name,'admitted':repr(value)[:500]})
def nested(record):
    value=json.loads(to_json(record));value.pop('schema_version');return value
def negative(name,changes,base=baseline):
    reject(name+'_constructor',lambda:replace(base,**changes))
    payload=json.loads(to_json(base))
    for key,value in changes.items():
        if isinstance(value,ThermodynamicSpec):value=nested(value)
        elif key=='corrections':value=[nested(c) for c in value]
        payload['data'][key]=value
    reject(name+'_json',lambda:from_json(json.dumps(payload)))
def positive(name,result):
    assert from_json(to_json(result))==result
    report['positives'].append(name)

for filename in ('admitted-final-uncomputed.json','admitted-final-empty-ledger.json'):
    path=root/'Worker_Log/Milestone_04/evidence/G08_v1_independent_sol61_max'/filename
    reject('original_v1_'+filename,lambda path=path:from_json(path.read_text()))
positive('complete_deterministic_producer',baseline)
assert abs(baseline.final_kj_mol-1.71)<1.e-12
assert abs(baseline.final_standard_error_kj_mol-.3)<1.e-12
for name,changes in {
    'missing_definition':{'thermodynamics':None},
    'identity_mismatch':{'thermodynamic_identity':'unrelated-definition'},
    'empty_result_ledger':{'corrections':()},
    'reordered_result_ledger':{'corrections':ledger[::-1]},
    'duplicate_result_ledger':{'corrections':ledger+(ledger[0],)},
    'different_result_value':{'corrections':(replace(ledger[0],value_kj_mol=.99),)+ledger[1:]},
    'duplicate_unresolved_ids':{'unresolved_corrections':('orientation','orientation')},
    'unknown_unresolved_id':{'unresolved_corrections':('unknown',)},
    'resolved_status_marked_unresolved':{'unresolved_corrections':('orientation',)},
    'deterministic_covariance_marker':{'unresolved_corrections':('correction_covariance',),'final_kj_mol':None,'final_standard_error_kj_mol':None},
    'wrong_corrected_value':{'final_kj_mol':baseline.final_kj_mol+.0005},
    'missing_final_error':{'final_standard_error_kj_mol':None},
    'missing_final_value':{'final_kj_mol':None},
    'negative_final_error':{'final_standard_error_kj_mol':-.1},
}.items():negative(name,changes)
nonstandard=replace(spec,observable='restrained_free_energy',sign_convention='endpoint_difference')
negative('matching_identity_nonstandard_observable',{'thermodynamics':nonstandard,'thermodynamic_identity':nonstandard.content_identity})
for missing in [*obligations,'ALL']:
    reduced=tuple(c for c in ledger if c.correction_id!=missing) if missing!='ALL' else ()
    partial_spec=replace(spec,corrections=reduced)
    partial=produce(partial_spec)
    positive('partial_missing_'+missing,partial)
    assert partial.final_kj_mol is None
    negative('missing_'+missing,{'thermodynamics':partial_spec,'thermodynamic_identity':partial_spec.content_identity,'corrections':reduced})
for name in obligations:
    uncomputed=tuple(CorrectionRecord(c.correction_id,'required_uncomputed',None,None,'not computed') if c.correction_id==name else c for c in ledger)
    definition=replace(spec,corrections=uncomputed)
    partial=produce(definition)
    positive('uncomputed_partial_'+name,partial)
    negative('hidden_uncomputed_partial_'+name,{'unresolved_corrections':()},base=partial)
    negative('hidden_uncomputed_final_'+name,{'unresolved_corrections':(),'final_kj_mol':1.71,'final_standard_error_kj_mol':.3},base=partial)

# Matching ledger/spec reordering is legitimate; only disagreement must reject.
positive('matching_reordered_definition',produce(replace(spec,corrections=ledger[::-1])))
extra=replace(spec,correction_obligations=obligations+('additional_control',))
with_extra=replace(extra,corrections=ledger+(CorrectionRecord('additional_control','computed',.12,0.,'independent extra control'),))
positive('additional_resolved_obligation',produce(with_extra))
negative('additional_missing_obligation',{'thermodynamics':extra,'thermodynamic_identity':extra.content_identity})
positive('additional_unresolved_obligation',produce(extra))

# Uncertain corrections require producer covariance; verify its complete result independently.
A=np.random.default_rng(80737).normal(0.,.06,(8,5));joint=A@A.T
uncertain=tuple(replace(c,standard_error_kj_mol=float(np.sqrt(joint[i+2,i+2]))) for i,c in enumerate(ledger))
uncertain_spec=replace(spec,corrections=uncertain)
withheld=combine_free_energies(('bulk','bound'),(17.,18.5),joint[:2,:2],uncertain_spec)
assert withheld.unresolved_corrections==('correction_covariance',) and withheld.final_kj_mol is None
positive('uncertain_covariance_withheld',withheld)
final=combine_free_energies(('bulk','bound'),(17.,18.5),joint[:2,:2],uncertain_spec,joint_covariance_kj2_mol2=joint)
w=np.r_[-1.,1.,np.ones(6)]
assert abs(final.final_kj_mol-1.71)<1.e-12
assert abs(final.final_standard_error_kj_mol-np.sqrt(w@joint@w))<1.e-12
positive('complete_joint_covariance_producer',final)
report['metrics']['joint_final_error']=final.final_standard_error_kj_mol

# Actual v1 producer outputs retain exact canonical bytes/content identities.
for seed in (41,73,109):
    payload=(root/'Worker_Log/Milestone_04/evidence/G08_v1/md-focused-attempt'/f'seed-{seed}'/'result.json').read_text().strip()
    old=from_json(payload)
    assert old.final_kj_mol is None and old.thermodynamics is None
    assert to_json(old)==payload
    assert old.content_identity==hashlib.sha256(payload.encode()).hexdigest()
    report['positives'].append('legacy_v1_seed_'+str(seed))
    report['metrics']['legacy_identity_'+str(seed)]=old.content_identity
legacy=BindingResult(1.5,.2,(),('orientation',),None,None,'legacy-unresolved-definition')
positive('legacy_partial_without_definition',legacy)
assert 'thermodynamics' not in json.loads(to_json(legacy))['data']

(out/'admission-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'correct_rejections':len(report['rejections']),'positive_round_trips':len(report['positives']),
                  'failures':report['failures'],'metrics':report['metrics']},indent=2))
raise SystemExit(1 if report['failures'] else 0)
