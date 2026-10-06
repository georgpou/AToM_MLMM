source /workspace/m05-cpu-setup-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"
python - <<'PY'
from datetime import datetime,timezone
from decimal import Decimal,localcontext
import json,math,sys
from pathlib import Path
from atm_mlmm.exchange_journal import _validate_expected_clock
here=Path('Worker_Log/Milestone_05/evidence/G10_v8_independent')
prior=json.loads(Path('Worker_Log/Milestone_05/evidence/G10_v7_independent/repair-continuation-results.json').read_text())
saved=next(p for p in prior['probes'] if p['name']=='gamma-n-valid-repeated-additions')['controls']
nonzero=next(p for p in saved if p['origin_ps']==123.25)
cases=[('negative-origin',-1.,-.9995,1),('huge-stagnant-origin',1e308,1e308,1),
       ('finite-stagnant-origin',1e14,1e14,1),
       ('saved-nonzero-repeated-additions',123.25,nonzero['repeated_time_ps'],nonzero['steps'])]
rows=[]
for name,origin,current,n in cases:
    captured={}
    def trace(frame,event,arg):
        if frame.f_code is _validate_expected_clock.__code__ and event=='return':
            captured.update(frame.f_locals)
        return trace
    previous=sys.gettrace(); sys.settrace(trace)
    try: _validate_expected_clock(n,current,{'step':0,'time_ps':origin},n,.0005)
    finally: sys.settrace(previous)
    actual=captured['bound']; residual=captured['residual_magnitude']
    with localcontext() as context:
        context.prec=120
        u=Decimal(2)**-53; gamma=(n*u)/(1-n*u); single=u/(1-u)
        t0=Decimal.from_float(origin); t=Decimal.from_float(current); dt=Decimal.from_float(.0005)
        exact_scale=n*abs(dt)
        expected=Decimal.from_float(n*.0005); observed=Decimal.from_float(current-origin)
        exact_bound=gamma*(abs(t0)+exact_scale)+single*(exact_scale+abs(t)+abs(t0)+abs(expected)+abs(observed))
        exact_residual=abs(observed-expected)
        assert math.isfinite(actual) and Decimal.from_float(actual)>=exact_bound
        assert math.isfinite(residual) and Decimal.from_float(residual)>=exact_residual
    rows.append(dict(name=name,status='PASS',origin_ps=origin,current_time_ps=current,steps=n,
                     actual_finite_bound_ps=actual,independent_decimal_bound_ps=str(exact_bound),
                     bound_and_residual_round_outward=True))
result=dict(controls=rows,pass_count=4,decimal_precision=120,long_addition_loops_run=0,
            reused_recorded_nonzero_addition_control=True,auditor_model='gpt-6.1-sol',reasoning_effort='max',
            finite_admitted_timestep_max_ps=.0005,admitted_step_max=999999,
            gamma_n_and_positive_addition_monotonicity_reviewed=True,
            finished_utc=datetime.now(timezone.utc).isoformat(),exit_status=0)
(here/'arithmetic-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,sort_keys=True))
PY
