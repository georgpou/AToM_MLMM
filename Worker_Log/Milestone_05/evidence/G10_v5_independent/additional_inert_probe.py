"""Additional bounded argument and recursive-seal/field-identity controls."""
from datetime import datetime, timezone
import itertools
import json
from pathlib import Path
import sys

ROOT=Path('/workspace/AToM_MLMM-g10')
HERE=ROOT/'Worker_Log/Milestone_05/evidence/G10_v5_independent'
sys.path.insert(0,str(HERE))
from analytic_admission_probe import ARTIFACTS,challenge,controller,edit_json,journal


def overflow_gaussian(run,metadata,boundary):
    path=boundary/'rng.json'
    edit_json(path,lambda d:d['python'].__setitem__(2,0.987654321))
    # JSON numbers may overflow to infinity without spelling NaN/Infinity tokens.
    path.write_text(path.read_text().replace('0.987654321','1e309'))


def main():
    cases=[]
    states=tuple(f's-{i}' for i in range(8))
    pairs=tuple(itertools.combinations(range(8),2))
    assert controller._multistate_selection(states,pairs)==(states,pairs)
    cases.append({'name':'eight-state-28-edge-selection','status':'PASS','context_loads':0})
    invalid=(('ids-string','abc',((0,1),(1,2))),
             ('ids-generator',(s for s in ('a','b','c')),((0,1),(1,2))),
             ('ids-nonstrings',('a',True,'c'),((0,1),(1,2))),
             ('ids-blank',('a',' ','c'),((0,1),(1,2))),
             ('ids-two',('a','b'),((0,1),)),
             ('ids-nine',tuple(str(i) for i in range(9)),tuple((i,i+1) for i in range(8))),
             ('pair-bool',('a','b','c'),((False,1),(1,2))),
             ('pair-float',('a','b','c'),((0.,1),(1,2))),
             ('pair-self',('a','b','c'),((0,0),(1,2))),
             ('pair-duplicate',('a','b','c'),((0,1),(1,0),(1,2))),
             ('pair-uncovered',('a','b','c'),((0,1),)),
             ('pair-negative',('a','b','c'),((-1,1),(1,2))),
             ('pair-empty',('a','b','c'),()),
             ('pair-string',('a','b','c'),'01'),
             ('pair-out-of-range',('a','b','c'),((0,3),(1,2))))
    for name,ids,edges in invalid:
        error=None
        try:
            controller._multistate_selection(ids,edges)
        except ValueError as caught:
            error=f'{type(caught).__name__}: {caught}'
        assert error
        cases.append({'name':name,'status':'PASS','inert_rejection':error})
    probes=(
        ('record-inverse-inconsistent',lambda r,m,b:edit_json(b/'record.json',lambda d:d.update(state_to_walker_final=[0,1,2]))),
        ('final-report-step-time-types',lambda r,m,b:edit_json(b/'final-state-reports.json',lambda d:d['workers'][0].update(step=True,time_ps='invalid-time'))),
        ('sample-physical-transfer-identities',lambda r,m,b:edit_json(b/'samples/worker-000.json',lambda d:d.update(physical_identity='0'*64,transfer_identity='0'*64))),
        ('python-gaussian-cache-overflow',overflow_gaussian),
        ('nested-unsealed-manifest',lambda r,m,b:(b/'attempts/0000/manifest.json').write_text('arbitrary unhashed nested bytes\n')),
    )
    for name,change in probes:
        row=challenge(name,change)
        if name=='nested-unsealed-manifest':
            row['top_manifest_unchanged_from_untampered_prefix']=(row['boundary_manifest_sha256']==
                journal.sha(ARTIFACTS/'rbfe-prefix/boundaries/000000/manifest.json'))
            assert row['top_manifest_unchanged_from_untampered_prefix']
        cases.append(row)
        print(json.dumps(row,sort_keys=True),flush=True)
    result={'checks':cases,'positive_controls':16,'negative_challenges':5,
            'violation_count':sum(r['status']=='VIOLATION' for r in cases),
            'finished_utc':datetime.now(timezone.utc).isoformat(),'exit_status':1}
    (HERE/'additional-inert-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'checks':len(cases),'violation_count':result['violation_count'],
                      'exit_status':1,'finished_utc':result['finished_utc']},sort_keys=True))
    return 1


if __name__=='__main__':
    sys.exit(main())
