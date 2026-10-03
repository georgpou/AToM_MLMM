import datetime,hashlib,importlib.metadata,json,pathlib,subprocess,sys
ROOT=pathlib.Path.cwd();OUT=pathlib.Path(__file__).parent
EXPECTED='a7768e375476667139db374dc0091999263a37de';BASE='bc788aeeedb4dc45026ac1bff44bd4fb533b325a';M00='a825f5f1c2d8cf4146133c2049ef1c4eca550e93'
def git(*args):return subprocess.check_output(['git',*args],text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
head=git('rev-parse','HEAD');status=git('status','--porcelain');assert head==EXPECTED and not status
manifest=json.loads((ROOT/'Worker_Log/Milestone_03/evidence/G05_v1/source-input-manifest-partial.json').read_text())
checked={p:sha(ROOT/p) for p in manifest['files']};assert checked==manifest['files']
protected=git('ls-tree','-r','--name-only',BASE,'--','environment/cloud-cpu','models','docs/project-0/specs','Worker_Log').splitlines()
changes=[]
for p in protected:
 old=subprocess.check_output(['git','show',BASE+':'+p]);new=(ROOT/p).read_bytes()
 if old!=new:changes.append(p)
# G05 adds new reports only. No old evidence, model, lock or scientific spec changed.
assert not changes,changes
plan_paths=git('ls-tree','-r','--name-only',M00,'--','fixtures/chemical_reference_v3','docs/project-0/reference/M00-neutral-reference-plan-v3.md','Worker_Log/Milestone_00/Milestone_00_v3_audit.md').splitlines()
for p in plan_paths:assert subprocess.check_output(['git','show',M00+':'+p])==(ROOT/p).read_bytes(),p
old=OUT.parent/'G05_v1_independent';prior={}
for name in ('frozen-full.json','frozen-analytic.json','strict-environment.json'):
 j=json.loads((old/name).read_text());assert j['reviewed_commit']==EXPECTED
 prior[name]={'sha256':sha(old/name),'command':j['command'],'exit_code':j['exit_code'],'reviewed_commit':j['reviewed_commit'],'elapsed_seconds':j['elapsed_seconds']}
# Preserve exact runtime source hashes and source commits for the evaluated adapter.
import openmmml.models.asepotential as asepotential
versions={n:importlib.metadata.version(n) for n in ('torch','mace-torch','ase','numpy','OpenMM','openmmml','AToM-OpenMM')}
report={'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':head,'status':status,'base':BASE,'source_input_hashes':checked,'protected_inherited_files_unchanged':len(protected),'m00_exact_files_unchanged':len(plan_paths),'m00_reviewed_snapshot':M00,'prior_interrupted_reviewer_captures':prior,'versions':versions,'python':sys.version,'executable':sys.executable,'actual_ase_adapter':{'path':asepotential.__file__,'sha256':sha(pathlib.Path(asepotential.__file__))},'decision':json.loads((ROOT/'Worker_Log/Milestone_00/evidence/M00_v3_decision/decision-pending.json').read_text())}
with (OUT/'snapshot-results.json').open('x') as f:json.dump(report,f,indent=2)
print(len(checked),'source/input hashes;',len(protected),'inherited protected files;',len(plan_paths),'M00 exact files; all match; clean immutable HEAD')
