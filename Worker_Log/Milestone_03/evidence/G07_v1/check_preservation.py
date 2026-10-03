"""Verify the accepted base and all newly declared fixture hashes, without QM."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BASE = '08ccee74d0da900ffb1bd98d076e6e87e9df1b0c'
ALLOWED = {
    'src/atm_mlmm/adapters/atom.py', 'src/atm_mlmm/atm.py',
    'src/atm_mlmm/embeddings/mechanical.py', 'src/atm_mlmm/geometry.py',
    'src/atm_mlmm/hybrid.py', 'src/atm_mlmm/ledger.py',
    'src/atm_mlmm/model_reference.py', 'docs/project-0/STATUS.md',
}


def hashes(path, mode):
    size = len(os.readlink(path).encode()) if mode == '120000' else path.stat().st_size
    git_hash = hashlib.sha1(f'blob {size}\0'.encode())
    sha256 = hashlib.sha256()
    if mode == '120000':
        data = os.readlink(path).encode()
        git_hash.update(data); sha256.update(data)
    else:
        with path.open('rb') as stream:
            for data in iter(lambda:stream.read(1048576), b''):
                git_hash.update(data); sha256.update(data)
    return git_hash.hexdigest(), sha256.hexdigest()


def main():
    tree = subprocess.check_output(['git','ls-tree','-r','-z',BASE],cwd=ROOT)
    unchanged, changed = {}, {}
    for item in tree.split(b'\0'):
        if not item:continue
        metadata, name = item.decode().split('\t',1)
        mode, kind, expected = metadata.split()
        if kind != 'blob':raise ValueError('unhandled base tree entry')
        actual, sha256 = hashes(ROOT/name, mode)
        if actual != expected:
            if name not in ALLOWED:raise ValueError('unapproved accepted-file change: '+name)
            changed[name] = dict(base_git_blob=expected,current_git_blob=actual,sha256=sha256)
        else:
            unchanged[name] = dict(base_git_blob=expected,sha256=sha256)
    new_fixture_hashes = {}
    for directory in ('fixtures/periodic_ledger','fixtures/fragment_ligand/prepared-mm-v1'):
        parent = ROOT/directory
        manifest = json.loads((parent/'manifest.json').read_text())
        for name, expected in manifest['files'].items():
            if name == 'manifest.json':raise ValueError('invalid self hash')
            actual = hashlib.sha256((parent/name).read_bytes()).hexdigest()
            if actual != expected:raise ValueError('new fixture digest mismatch: '+name)
            new_fixture_hashes[str(Path(directory)/name)] = actual
    parent = ROOT/'fixtures/fragment_ligand/descriptions-v1'
    for row in json.loads((parent/'manifest.json').read_text())['rows']:
        actual = hashlib.sha256((parent/row['artifact']).read_bytes()).hexdigest()
        if actual != row['artifact_sha256']:raise ValueError('changed sealed description')
        new_fixture_hashes[str(parent.relative_to(ROOT)/row['artifact'])] = actual
    quantum = json.loads((ROOT/'fixtures/chemical_reference_v3/quantum/manifest.json').read_text())
    record_count = sum(name.startswith('records/') for name in quantum['files'])
    if record_count != 46:raise ValueError('accepted reference count changed')
    report = dict(base_commit=BASE,accepted_base_file_count=len(unchanged)+len(changed),
        unchanged_base_file_count=len(unchanged),allowed_changed_files=changed,
        accepted_quantum_records=record_count,unchanged_base_files=unchanged,
        verified_new_fixture_files=new_fixture_hashes,
        acceptance='preservation only; no independent scientific approval')
    output = Path(__file__).resolve().parent/'reference-preservation.json'
    with output.open('x') as stream:
        json.dump(report,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({key:report[key] for key in ('base_commit','accepted_base_file_count',
        'unchanged_base_file_count','accepted_quantum_records')},indent=2))
    print('All',len(new_fixture_hashes),'new fixture file hashes verified; allowed existing changes:',sorted(changed))


if __name__ == '__main__':main()
