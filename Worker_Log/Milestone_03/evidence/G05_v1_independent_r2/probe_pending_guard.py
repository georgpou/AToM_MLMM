import importlib.util,json,pathlib
root=pathlib.Path.cwd();output=pathlib.Path(__file__).parent/'pending-guard-results.json'
spec=importlib.util.spec_from_file_location('reviewed_generator',root/'tools/generate_neutral_quantum.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
try:m.validate_plan(root/'fixtures/chemical_reference_v3',root/'Worker_Log/Milestone_00/evidence/M00_v3_decision/decision-pending.json')
except ValueError as e:
 result={'rejected':True,'exception':str(e),'scope':'validate_plan only; coordinator, worker, quantum runtime and model not called'}
else:raise AssertionError('Pending user agreement was admitted')
with output.open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
