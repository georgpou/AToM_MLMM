"""Check the pinned UWHAM objective derivatives without MBAR initialization."""
import json
from pathlib import Path

import numpy as np
from scipy.special import logsumexp
from atom_openmm.uwham import _obj_fcn

out=Path(__file__).resolve().parent
rng=np.random.default_rng(218591)
counts=np.array((19,31,23,37,29))
N=int(counts.sum())
log_density=rng.normal(0.,2.1,(5,N))
log_density-=log_density[0]
point=np.array((-.3,.7,-1.2,.5))
rho=counts/N

def oracle(z):
    full=np.r_[0.,z]
    return float(np.mean(logsumexp(log_density-full[:,None]+np.log(rho[:,None]),axis=0))+rho@full)

value,gradient,hessian=_obj_fcn(point,log_density,counts,0)
assert abs(value-oracle(point)) < 1.e-13
rows=[]
for h in (1.e-3,1.e-4,1.e-5):
    fd_gradient=np.zeros(4)
    fd_hessian=np.zeros((4,4))
    for i in range(4):
        delta=np.zeros(4);delta[i]=h
        fd_gradient[i]=(oracle(point+delta)-oracle(point-delta))/(2*h)
        fd_hessian[:,i]=(_obj_fcn(point+delta,log_density,counts,0)[1]-_obj_fcn(point-delta,log_density,counts,0)[1])/(2*h)
    rows.append(dict(step=h,max_gradient_error=float(np.max(np.abs(fd_gradient-gradient))),
                     max_hessian_error=float(np.max(np.abs(fd_hessian-hessian)))))
assert rows[-1]['max_gradient_error'] < 1.e-8
assert rows[-1]['max_hessian_error'] < 1.e-8
assert np.linalg.eigvalsh(hessian).min() > 0
result=dict(counts=counts.tolist(),objective_error=abs(value-oracle(point)),step_sweep=rows,
            smallest_hessian_eigenvalue=float(np.linalg.eigvalsh(hessian).min()),
            initialization='explicit independent point; no MBAR call')
(out/'uwham-objective-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
