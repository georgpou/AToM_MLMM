import json,sys
from pathlib import Path
from dataclasses import replace
import numpy as np
sys.path.insert(0,str(Path.cwd()))
from tests.integration.test_model_adapter import real_case
from tests.link_oracle import REFERENCE
from atm_mlmm.atm import PhysicalEvaluator
OUT=Path(__file__).parent
samples=json.loads((OUT/'software-numerics/domain-scans.json').read_text())['raw_records']
bundle,snapshot=real_case();records=[]
with PhysicalEvaluator(bundle,REFERENCE) as evaluator:
 for sample in samples:
  r={'kind':sample['kind'],'parameter':sample['parameter'],'map':sample['map'],'admitted':sample['admitted'],'real_positions_nm':sample['real_positions_nm'],'ml_energy_kj_mol':sample.get('adapter_energy'),'graph_edges':sample.get('native',{}).get('directed_edges')}
  try:
   actual=evaluator.evaluate(replace(snapshot,positions_nm=sample['real_positions_nm']))
   f=np.asarray(actual.forces_kj_mol_nm)
   r.update(total_energy_kj_mol=actual.energy_kj_mol,total_forces_kj_mol_nm=f.tolist(),total_max_atom_force=float(np.max(np.linalg.norm(f,axis=1))),finite=bool(np.isfinite(actual.energy_kj_mol) and np.isfinite(f).all()))
  except Exception as e:r.update(exception=repr(e),finite=False)
  records.append(r)
def clean(x):
 if isinstance(x,float) and not np.isfinite(x):return str(x)
 if isinstance(x,list):return [clean(v) for v in x]
 if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
 return x
with (OUT/'domain-total-results.json').open('x') as f:json.dump(clean(records),f,indent=2,allow_nan=False)
assert all(r['finite'] for r in records if r['admitted'])
print(len(records),'preserved rows;',sum(r['admitted'] for r in records),'admitted finite total-energy/full-real-force rows')
