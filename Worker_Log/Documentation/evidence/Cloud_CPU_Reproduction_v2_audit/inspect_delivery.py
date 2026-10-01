"""Independent static audit; reads every lock, wheel and recorded amendment hash."""
import ast
import email
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile
import zipfile

repo = Path.cwd()
out = Path(__file__).resolve().parent
submitted = Path('/workspace/.onboarding/atom-mlmm-audit-v1-submitted-tree')
setup = repo / 'environment/cloud-cpu'
sha = lambda data: hashlib.sha256(data).hexdigest()
normalize = lambda name: re.sub(r'[-_.]+', '-', name).lower()
result = {'snapshots': {}, 'locks': {}, 'wheels': [], 'sources': [], 'documentation_v4': {}}
for root, label in [(repo, 'inherited'), (submitted, 'submitted')]:
    directory = root / 'environment/cloud-cpu'
    for name in ['bundle.sha256', 'wheels.sha256']:
        check = subprocess.run(['sha256sum', '-c', name], cwd=directory, capture_output=True, text=True)
        (out / f'{label}-{name}.log').write_text(check.stdout + check.stderr)
        result['snapshots'][label + '-' + name] = {'exit_code': check.returncode, 'entries': len((directory / name).read_text().splitlines())}
        assert check.returncode == 0
    for file in directory.glob('*.py'):
        ast.parse(file.read_text(), filename=str(file))
    for file in directory.glob('*.sh'):
        subprocess.run(['bash', '-n', str(file)], check=True)
runtime_differences = []
for file in sorted(setup.rglob('*')):
    if file.is_file():
        relative = file.relative_to(repo)
        original = submitted / relative
        if not original.exists() or file.read_bytes() != original.read_bytes():
            runtime_differences.append(relative.as_posix())
result['snapshots']['setup_differences'] = runtime_differences
assert runtime_differences == ['environment/cloud-cpu/CLOUD_START.md', 'environment/cloud-cpu/README.md', 'environment/cloud-cpu/bundle.sha256']
for label in ['core', 'amber']:
    urls = [line for line in (setup / f'{label}-conda-linux-64.lock').read_text().splitlines() if line.startswith('https://')]
    assert len(urls) == len(set(urls))
    assert all(re.fullmatch(r'https://conda\.anaconda\.org/conda-forge/(linux-64|noarch)/[^#]+#[a-f0-9]{64}', u) for u in urls)
    python_inventory = dict(line.split('==', 1) for line in (setup / f'{label}-pip-inventory.txt').read_text().splitlines())
    package_records = json.loads((setup / f'{label}-packages.json').read_text())
    # These committed inventories are `conda list` output, not conda-meta records.
    # Core includes the 51 PyPI records as well as the locked Conda packages.
    conda_records = [p for p in package_records if p['channel'] == 'conda-forge']
    locked_names = {re.sub(r'\.(conda|tar\.bz2)$', '', u.split('#')[0].rsplit('/', 1)[1]) for u in urls}
    assert {p['dist_name'] for p in conda_records} == locked_names
    result['locks'][label] = dict(conda_count=len(urls), python_count=len(python_inventory),
        selected_conda={p['name']: dict(version=p['version'], build=p['build_string']) for p in package_records if p['name'] in ['python','numpy','pytorch','openmm','ambertools','e3nn','mdtraj']},
        selected_python={k:v for k,v in python_inventory.items() if normalize(k) in ['numpy','torch','openmm','atom-openmm','mace-torch','e3nn','openmmml','torchani']})
locks = {}
for line in (setup / 'pip-wheels.lock').read_text().splitlines():
    match = re.fullmatch(r'(\S+)==(\S+) --hash=sha256:([a-f0-9]{64})', line)
    assert match, line
    name, version, digest = match.groups()
    locks[normalize(name)] = (version, digest)
assert len(locks) == 51
for wheel in sorted((setup / 'wheels').glob('*.whl')):
    data = wheel.read_bytes()
    with zipfile.ZipFile(wheel) as z:
        assert z.testzip() is None
        metadata_name = next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))
        meta = email.message_from_bytes(z.read(metadata_name))
        name, version = normalize(meta['Name']), meta['Version']
        assert locks[name] == (version, sha(data)), wheel.name
        result['wheels'].append(dict(file=wheel.name, name=name, version=version, sha256=sha(data)))
assert len(result['wheels']) == 51
wheel_modules = {'AToM-OpenMM': ('atom_openmm', 'atom_openmm-8.5.0b0-py3-none-any.whl'),
                 'openmm-ml': ('openmmml', 'openmmml-1.8-py3-none-any.whl'),
                 'openmmforcefields': ('openmmforcefields', 'openmmforcefields-0.16.0-py3-none-any.whl')}
for source in json.loads((setup / 'upstream-sources.json').read_text()):
    with tarfile.open(setup / source['archive'], 'r:gz') as archive:
        assert archive.pax_headers['comment'] == source['commit']
        entries = {p.name: archive.extractfile(p).read() for p in archive.getmembers() if p.isfile()}
        module, wheelname = wheel_modules[source['directory']]
        matched, different, missing = [], [], []
        with zipfile.ZipFile(setup / 'wheels' / wheelname) as wheel:
            for name in wheel.namelist():
                if name.startswith(module + '/') and not name.endswith('/'):
                    if name not in entries:
                        missing.append(name)
                    elif entries[name] != wheel.read(name):
                        different.append(name)
                    else:
                        matched.append(name)
        # Generated version metadata is identified separately, never counted as source equivalence.
        generated = [module + '/_version.py'] if source['directory'] in ['openmm-ml', 'openmmforcefields'] else []
        unexpected = [p for p in different + missing if p not in generated]
        assert not unexpected, unexpected
        result['sources'].append(dict(**source, archive_sha256=sha((setup/source['archive']).read_bytes()),
            pax_commit=archive.pax_headers['comment'], file_count=len(entries), wheel_matching_files=len(matched),
            generated_or_different=different, wheel_files_absent_from_source=missing,
            license_files=[p for p in entries if 'license' in p.lower() or 'copying' in p.lower()]))
        if source['directory'] == 'AToM-OpenMM':
            (out/'atom-test-source.txt').write_bytes(entries['tests/test_uwham.py'] + b'\n' + entries['pyproject.toml'])
record = json.loads((repo/'Worker_Log/Milestone_00/evidence/Documentation_v4/verification.json').read_text())
for root, label in [(repo, 'inherited'), (submitted, 'submitted')]:
    changed = []
    for item in record['changes']:
        if item['action'] != 'replace':
            continue
        actual = sha((root / item['path']).read_bytes())
        changed.append(dict(path=item['path'], before=item['before_sha256'], claimed_after=item['after_sha256'],
                            actual=actual, matches_before=actual == item['before_sha256'], matches_after=actual == item['after_sha256']))
    manifest = []
    for line in (root/'Worker_Log/Milestone_00/evidence/Documentation_v4/file-manifest.sha256').read_text().splitlines():
        digest, file = line.split('  ', 1)
        path = root / file
        actual = sha(path.read_bytes()) if path.exists() else None
        manifest.append(dict(path=file, recorded=digest, actual=actual, matches=actual==digest))
    result['documentation_v4'][label] = dict(changed_files=changed, full_manifest=manifest,
        missing_delivery=[p['path'] for p in changed if p['matches_before']],
        source_register_actual=sha((root/'docs/project-0/reference/sources.md').read_bytes()))
history = subprocess.check_output(['git', 'log', '--all', '--format=%H %s', '--', 'docs/project-0/reference/sources.md'], text=True)
result['documentation_v4']['source_history'] = history
for name in ['cloud-entrypoint-first', 'cloud-entrypoint-repeat']:
    data = gzip.decompress((repo/f'Worker_Log/Documentation/evidence/Cloud_CPU_Reproduction_v2/{name}.log.gz').read_bytes()).decode()
    lines = data.splitlines()
    selected = [{'line':i+1,'text':s} for i,s in enumerate(lines) if re.search(r'Installer exit|entrypoint.*status|File exists|OpenCL|Environment checks|exit [1-9]',s)]
    result[name] = dict(line_count=len(lines), selected=selected, tail=lines[-12:])
(out/'static-inspection.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(dict(locks=result['locks'], setup_differences=runtime_differences,
                     wheels=len(result['wheels']), sources=result['sources'],
                     documentation_v4_missing_delivery=result['documentation_v4']['inherited']['missing_delivery']), indent=2))
