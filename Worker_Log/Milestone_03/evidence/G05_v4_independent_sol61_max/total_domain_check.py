"""Replay every captured domain geometry through the complete physical system."""
from pathlib import Path
from dataclasses import replace
import json
import numpy as np

from tests.integration.test_model_adapter import real_case
from tests.link_oracle import REFERENCE
from atm_mlmm.atm import PhysicalEvaluator

E=Path(__file__).resolve().parent
samples=json.loads((E/'fresh-g05-captures/domain-scans.json').read_text())['raw_records']
bundle,snapshot=real_case()
records=[]
with PhysicalEvaluator(bundle,REFERENCE) as evaluator:
    for sample in samples:
        row={key:sample[key] for key in ('kind','parameter','map','admitted','real_positions_nm')}
        try:
            actual=evaluator.evaluate(replace(snapshot,positions_nm=sample['real_positions_nm']))
            forces=np.asarray(actual.forces_kj_mol_nm)
            row.update(total_energy_kj_mol=actual.energy_kj_mol,total_real_forces_kj_mol_nm=forces.tolist(),
                       finite=bool(np.isfinite(actual.energy_kj_mol) and np.isfinite(forces).all()))
        except Exception as error:row.update(exception=repr(error),finite=False)
        records.append(row)
def clean(value):
    if isinstance(value,float) and not np.isfinite(value):return str(value)
    if isinstance(value,list):return [clean(x) for x in value]
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
    return value
with (E/'total-domain-results.json').open('x') as stream:json.dump(clean(records),stream,indent=2,allow_nan=False);stream.write('\n')
assert len(records)==36
assert sum(x['admitted'] for x in records)==34
assert all(x['finite'] for x in records if x['admitted'])
print('36 preserved physical-system rows; all 34 admitted rows finite in energy and full-real forces')
