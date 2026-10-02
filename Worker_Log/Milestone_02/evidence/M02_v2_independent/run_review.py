"""Independent exact-snapshot audit command capture, v2; no implementation edits."""
import datetime, gzip, hashlib, json, os, pathlib, shutil, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = pathlib.Path(__file__).resolve().parent
PREFIX = pathlib.Path('/workspace/.onboarding/atom-mlmm-m02-v2')
HEAD = '6015a652c4a9a9c968ab7933c07ac7bbb4573e12'
assert subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip() == HEAD
origin = ROOT/'Worker_Log/Milestone_02/evidence/M02_v1_independent/probe_numerics.py'
copied = OUT/'probe_numerics.py'
assert not copied.exists()
shutil.copyfile(origin, copied)
(OUT/'copy-provenance.json').write_text(json.dumps(dict(source=str(origin.relative_to(ROOT)),destination=str(copied.relative_to(ROOT)),sha256=hashlib.sha256(origin.read_bytes()).hexdigest(),byte_identical=origin.read_bytes()==copied.read_bytes()),indent=2)+'\n')
commands = [
('g02', [sys.executable,'-m','pytest','tests/integration/test_pythonforce_atm.py','tests/contracts/test_transfer_protocols.py','tests/contracts/test_physical_evaluator.py','tests/contracts/test_fault_injection.py','-v'],ROOT),
('g03',[sys.executable,'-m','pytest','tests/workflow/test_atom_force_routing.py','tests/workflow/test_active_force_groups.py','-v'],ROOT),
('admission-regressions',[sys.executable,'-m','pytest','tests/contracts/test_m02_admission.py','-v'],ROOT),
('full',[sys.executable,'-m','pytest','-q'],ROOT),
('analytic',[sys.executable,'-m','pytest','-m','not gpu and not model_assets and not slow','-q'],ROOT),
('strict',[sys.executable,str(PREFIX/'validate.py'),'--repository',str(ROOT)],ROOT),
('upstream',[sys.executable,'-m','pytest','-q','tests/test_uwham.py'],PREFIX/'sources/AToM-OpenMM'),
('docs',[sys.executable,'tools/check_docs.py','--self-test'],ROOT),
('whitespace',['git','diff','--check'],ROOT),
('preserved-admission',[sys.executable,'Worker_Log/Milestone_02/evidence/M02_v1_independent/probe_admission.py','--require-rejection','--output',str(OUT/'admission-results.json')],ROOT),
('independent-v1-numerics',[sys.executable,str(copied)],ROOT),
('offline-stale',[sys.executable,'Worker_Log/Milestone_02/evidence/M02_v1/reproduce_stale_fault.py'],ROOT),
]
records=[]
for name,command,cwd in commands:
    start=datetime.datetime.now(datetime.timezone.utc)
    result=subprocess.run(command,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    records.append(dict(name=name,command=command,cwd=str(cwd),activation=str(PREFIX/'activate.sh'),pythonpath=os.environ.get('PYTHONPATH'),head=HEAD,started_utc=start.isoformat(),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=result.returncode,output=result.stdout))
    with gzip.open(OUT/'command-results.json.gz','wt') as f: json.dump(records,f,indent=2)
    print(name,'exit',result.returncode,result.stdout[-750:].strip(),flush=True)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==HEAD
sys.exit(int(any(r['exit_code'] for r in records)))
