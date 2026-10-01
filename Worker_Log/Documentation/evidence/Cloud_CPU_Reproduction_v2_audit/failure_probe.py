"""Controlled failures only in disposable copies; no production artifacts edited."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

repo = Path.cwd()
out = Path(__file__).resolve().parent
base = Path('/workspace/.onboarding/atom-mlmm-audit-v1-submitted-tree')
scratch = Path('/workspace/.onboarding/atom-mlmm-audit-v1-failure-probes')
assert not scratch.exists(), scratch
scratch.mkdir()
results = []
def run_failure(name, target, command):
    prefix = scratch / (name + '-prefix')
    assert not prefix.exists()
    env = dict(os.environ, ATOM_MLMM_SETUP_ROOT=str(prefix), ATOM_MLMM_REPOSITORY=str(target))
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    p = subprocess.run(command, cwd=target, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out/(name+'.log')).write_bytes(p.stdout)
    item = dict(name=name, command=command, cwd=str(target), prefix=str(prefix), started=started,
                finished=datetime.datetime.now(datetime.timezone.utc).isoformat(), exit_code=p.returncode,
                prefix_initially_absent=True, bootstrap_installed=(prefix/'conda').exists(),
                main_env_created=(prefix/'env').exists(), amber_env_created=(prefix/'amber-env').exists())
    (out/(name+'.json')).write_text(json.dumps(item,indent=2)+'\n')
    results.append(item)
    assert p.returncode == 1, item
    assert b'Installer exit code: 1' in p.stdout and b'FAILED' in p.stdout, item
    assert not any(item[k] for k in ['bootstrap_installed','main_env_created','amber_env_created']), item
for kind in ['missing','corrupt']:
    target = scratch / kind
    shutil.copytree(base, target)
    wheel = sorted((target/'environment/cloud-cpu/wheels').glob('*.whl'))[0]
    original_sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
    if kind == 'missing':
        wheel.unlink()
    else:
        with wheel.open('ab') as f: f.write(b'audit-controlled-corruption\n')
    run_failure(kind+'-direct', target, ['bash', str(target/'environment/cloud-cpu/install.sh')])
    run_failure(kind+'-cloud-local', target, ['bash', str(repo/'environment/cloud-cpu/cloud-install.sh')])
    assert hashlib.sha256((base/'environment/cloud-cpu/wheels'/wheel.name).read_bytes()).hexdigest() == original_sha
bad_origin = scratch/'corrupt-origin'
subprocess.run(['git','clone','--shared','--no-checkout',str(repo),str(bad_origin)],check=True)
subprocess.run(['git','-C',str(bad_origin),'switch','--no-track','-c','m01-g00-cloud-environment-setup','28f89cb23bdb7081c3723b9794fbde7d9bb50dca'],check=True)
wheel = sorted((bad_origin/'environment/cloud-cpu/wheels').glob('*.whl'))[0]
with wheel.open('ab') as f: f.write(b'audit-controlled-corruption\n')
subprocess.run(['git','-C',str(bad_origin),'add',str(wheel.relative_to(bad_origin))],check=True)
subprocess.run(['git','-C',str(bad_origin),'-c','user.name=Audit fixture','-c','user.email=audit-fixture@example.invalid',
                'commit','-m','Controlled disposable artifact corruption for audit'],check=True)
fallback = scratch/'missing-setup-checkout'
subprocess.run(['git','clone','--shared','--no-checkout',str(bad_origin),str(fallback)],check=True)
subprocess.run(['git','-C',str(fallback),'checkout','--detach','2d7bcc94f901738e39f536f16de84699d4e8d631'],check=True)
assert not (fallback/'environment/cloud-cpu/install.sh').exists()
def state(path):
    files = subprocess.check_output(['git','-C',str(path),'ls-files'],text=True).splitlines()
    return dict(head=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip(),
                status=subprocess.check_output(['git','-C',str(path),'status','--porcelain'],text=True),
                hashes={p:hashlib.sha256((path/p).read_bytes()).hexdigest() for p in files})
before = state(fallback)
run_failure('corrupt-cloud-fallback',fallback,['bash',str(repo/'environment/cloud-cpu/cloud-install.sh')])
after = state(fallback)
assert before == after and before['status'] == ''
(out/'failure-probe-summary.json').write_text(json.dumps(dict(checks=results, fallback_before=before,
    fallback_after=after, controlled_origin=str(bad_origin),
    original_artifacts_preserved=True, all_five_negative_checks_passed=True),indent=2)+'\n')
print(json.dumps(dict(checks=[dict(name=x['name'],underlying_exit=x['exit_code']) for x in results],
                     fallback_checkout_unchanged=True, no_packages_installed=True),indent=2))
