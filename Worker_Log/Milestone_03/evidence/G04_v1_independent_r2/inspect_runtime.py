import hashlib,importlib,json,pathlib,tarfile
import openmm,openmmml,numpy
out=pathlib.Path(__file__).parent
archive=pathlib.Path('environment/cloud-cpu/sources/openmm-ml-a7fb40ebecd031db3a5d1da08202cad6819c366f.tar.gz')
rows=[]
with tarfile.open(archive) as tar:
 for name in ('openmmml.mlpotential','openmmml.embeddings.mechanicalembedding','openmmml.embeddings.utilities'):
  module=importlib.import_module(name);path=pathlib.Path(module.__file__);relative='/'+name.replace('.','/')+'.py'
  members=[m for m in tar.getmembers() if m.name.endswith(relative)];assert len(members)==1
  data=tar.extractfile(members[0]).read();installed=path.read_bytes()
  row={'module':name,'installed_path':str(path),'installed_sha256':hashlib.sha256(installed).hexdigest(),'archive_member':members[0].name,'archive_sha256':hashlib.sha256(data).hexdigest(),'match':installed==data};rows.append(row);assert row['match']
result={'numpy':numpy.__version__,'openmm':openmm.__version__,'modules':rows}
with (out/'runtime-source.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
