import hashlib,json,pathlib
root=pathlib.Path.cwd();out=pathlib.Path(__file__).parent
sources={
 'inherited_numerics.py':'Worker_Log/Milestone_02/evidence/M02_v1_independent/probe_numerics.py',
 'inherited_closure.py':'Worker_Log/Milestone_02/evidence/M02_v2_independent/probe_closure.py',
 'nested_diagnostic.py':'Worker_Log/Milestone_03/evidence/G04_v1/diagnose_nested.py'}
records=[]
for name,source in sources.items():
 data=(root/source).read_bytes()
 with (out/name).open('xb') as f:f.write(data)
 assert (out/name).read_bytes()==data
 records.append({'source':source,'destination':str(out/name),'sha256':hashlib.sha256(data).hexdigest()})
with (out/'copy-provenance.json').open('x') as f:json.dump(records,f,indent=2)
print(records)
