"""Fetch one declared upstream tag and compare every supplied archive entry."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile

setup = Path.cwd() / 'environment/cloud-cpu'
name = sys.argv[1]
source = next(s for s in json.loads((setup/'upstream-sources.json').read_text()) if s['directory'] == name)
scratch = Path('/workspace/.onboarding/atom-mlmm-audit-v1-upstream') / name
bare = scratch / 'git'
if '--reuse-fetched-tag' not in sys.argv:
    assert not scratch.exists(), scratch
    scratch.mkdir(parents=True)
    subprocess.run(['git', 'init', '--bare', str(bare)], check=True)
    subprocess.run(['git', '-C', str(bare), 'fetch', '--depth=1', source['url'], 'refs/tags/' + source['tag']], check=True)
commit = subprocess.check_output(['git', '-C', str(bare), 'rev-parse', 'FETCH_HEAD^{commit}'], text=True).strip()
assert commit == source['commit'], (commit, source['commit'])
# Versioneer uses export-subst for ref decorations. Preserve the fetched tag
# and detached HEAD so its exported keyword is comparable with the delivery.
subprocess.run(['git', '-C', str(bare), 'update-ref', 'refs/tags/' + source['tag'], 'FETCH_HEAD'], check=True)
subprocess.run(['git', '-C', str(bare), 'update-ref', '--no-deref', 'HEAD', commit], check=True)
fresh = scratch / 'upstream.tar'
subprocess.run(['git', '-C', str(bare), 'archive', '--format=tar', '--output', str(fresh), commit], check=True)
def entries(path):
    with tarfile.open(path) as archive:
        return {p.name: (p.type.decode(), p.mode, p.linkname, hashlib.sha256(archive.extractfile(p).read()).hexdigest() if p.isfile() else None) for p in archive.getmembers()}
supplied = setup / source['archive']
observed, expected = entries(supplied), entries(fresh)
assert observed == expected, sorted(k for k in observed.keys() | expected.keys() if observed.get(k) != expected.get(k))
result = dict(**source, fetched_commit=commit, entries=len(observed), all_names_types_modes_links_and_file_hashes_match=True,
              supplied_archive_sha256=hashlib.sha256(supplied.read_bytes()).hexdigest(),
              uncompressed_bytes_match=gzip.decompress(supplied.read_bytes()) == fresh.read_bytes())
(Path(__file__).resolve().parent / ('upstream-' + name + '-comparison.json')).write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
