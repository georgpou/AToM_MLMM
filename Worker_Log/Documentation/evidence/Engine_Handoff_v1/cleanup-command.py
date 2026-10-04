"""One-off, bounded cleanup for the 2026-10-04 engine handoff.

This is a recorded maintenance command, not an ML/MM or QM execution tool.
Only the explicitly listed closed probe copies and verified downloads qualify.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tarfile
from datetime import datetime, timezone

ROOT = Path('/workspace/AToM_MLMM')
SETUP = Path('/workspace/atom-mlmm-g07')
OUT = ROOT / 'Worker_Log/Documentation/evidence/Engine_Handoff_v1'
BASE = 'fc6dbe3dfbb33906f85c0756d6c6ba6b44f1dd86'
PROBES = ROOT / 'Worker_Log/Milestone_03/evidence/G07_v2_revalidation_independent'
TREES = [PROBES / 'probes-final', PROBES / 'probes-durable']

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

def resources():
    cg = Path('/sys/fs/cgroup')
    names = ['cpu.max', 'memory.max', 'memory.current', 'memory.events', 'memory.stat']
    return {
        'utc': datetime.now(timezone.utc).isoformat(),
        'disk_free_bytes': os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize,
        'cgroup': {n: (cg / n).read_text() for n in names if (cg / n).exists()},
        'swaps': Path('/proc/swaps').read_text(),
    }

def process_use(paths):
    targets = {str(p.resolve()) for p in paths}
    used = []
    unreadable = []
    workers = []
    names = {'resume_joint_quantum.py', 'resume_neutral_quantum.py',
             'generate_neutral_quantum.py', 'quantum_worker_guard.py',
             'pytest', 'conda', 'mamba', 'micromamba'}
    for proc in Path('/proc').iterdir():
        if not proc.name.isdecimal():
            continue
        try:
            args = (proc / 'cmdline').read_bytes().split(b'\0')
            if any(Path(a.decode(errors='replace')).name in names for a in args):
                workers.append(int(proc.name))
            for entry in [proc / 'exe', proc / 'cwd', *list((proc / 'fd').iterdir())]:
                try:
                    target = os.readlink(entry)
                except (OSError, PermissionError):
                    continue
                if target in targets:
                    used.append({'pid': int(proc.name), 'target': target})
        except (OSError, PermissionError):
            unreadable.append(int(proc.name))
    assert not used and not workers, (used, workers)
    return {'used_candidates': used, 'active_workers_or_installers': workers,
            'unreadable_or_exited_pids': unreadable}

assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip() == BASE
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT).decode().strip() == 'm04-engine-readiness'
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT)
OUT.mkdir(parents=True, exist_ok=False)
before = resources()
tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
baseline = {p: digest(ROOT / p) for p in tracked if p and (ROOT / p).is_file()}
save(OUT / 'pre-cleanup-tracked-hashes.json', {'base_commit': BASE, 'sha256': baseline})

inventory = json.loads((ROOT / 'Worker_Log/Milestone_03/evidence/G07_v2/cleanup-candidate-inventory.json').read_text())
metadata = {}
for prefix in ['conda', 'env', 'amber-env', 'reference-env']:
    for path in (SETUP / prefix / 'conda-meta').glob('*.json'):
        item = json.loads(path.read_text())
        if item.get('fn') and item.get('sha256'):
            metadata.setdefault(item['fn'], []).append((path, item))
downloads = []
for text in inventory['installation_archives']['paths']:
    path = Path(text)
    path.relative_to(SETUP)
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and not path.is_symlink()
    sha = digest(path)
    matches = [(p, m) for p, m in metadata.get(path.name, []) if m['sha256'] == sha]
    assert matches, path
    downloads.append({'path': str(path), 'bytes': info.st_size, 'sha256': sha,
                      'installed_metadata': [str(p) for p, _ in matches],
                      'urls': sorted({m['url'] for _, m in matches}),
                      'reason': 'verified compressed package download; installed files and extracted cache retained'})
installer = Path(inventory['bootstrap_installer']['path'])
assert installer.is_file() and not installer.is_symlink() and installer.stat().st_nlink == 1
sha = digest(installer)
assert sha == '281b0ac7d550802efc81af633225a5e6116d29ae72f3ab4eae7168c3931a4c05'
downloads.append({'path': str(installer), 'bytes': installer.stat().st_size, 'sha256': sha,
                  'url': 'https://github.com/conda-forge/miniforge/releases/download/26.7.2-0/Miniforge3-26.7.2-0-Linux-x86_64.sh',
                  'reason': 'verified reproducible installer; bootstrap logs and active conda retained'})

ignored = subprocess.check_output(['git', 'ls-files', '--others', '--ignored', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
bytecode = []
for text in ignored:
    if not text:
        continue
    path = ROOT / text
    if any(path.is_relative_to(tree) for tree in TREES):
        continue
    if (path.suffix == '.pyc' and '__pycache__' in path.parts) or text.startswith('.pytest_cache/'):
        assert path.is_file() and not path.is_symlink()
        bytecode.append({'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path),
                         'reason': 'ignored, regenerable Python bytecode or pytest cache'})

deletion_paths = [Path(x['path']) for x in downloads + bytecode]
probe_files = [p for tree in TREES for p in tree.rglob('*') if p.is_file()]
processes = process_use(deletion_paths + probe_files)
target_names = {str(p.resolve()) for p in deletion_paths}
symlink_uses = []
for prefix in ['conda', 'env', 'amber-env', 'reference-env']:
    for path in (SETUP / prefix).rglob('*'):
        if path.is_symlink() and str(path.resolve()) in target_names:
            symlink_uses.append(str(path))
assert not symlink_uses, symlink_uses
save(OUT / 'deletion-plan.json', {'before': before, 'process_use': processes,
     'active_prefix_symlink_uses': symlink_uses, 'downloads': downloads, 'ignored_cache_files': bytecode,
     'retain': ['all active environments', 'extracted package caches', 'abandoned bootstrap prefix',
                'all source, tests, fixtures, models, locks', 'all G05 records',
                'canonical G07 attempts, logs, receipts and ledger', 'independent scripts/logs/results']})

archives = []
for tree in TREES:
    archive = PROBES / (tree.name + '.tar.gz')
    nodes = [tree, *sorted(tree.rglob('*'))]
    members = []
    for path in nodes:
        info = path.lstat()
        assert not path.is_symlink() and (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode))
        item = {'path': str(path.relative_to(ROOT)), 'kind': 'file' if path.is_file() else 'directory',
                'mode': stat.S_IMODE(info.st_mode), 'original_mtime_ns': info.st_mtime_ns}
        if path.is_file():
            item.update(bytes=info.st_size, sha256=digest(path))
        members.append(item)
    with archive.open('xb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0, filename='', compresslevel=6) as zipped:
            with tarfile.open(fileobj=zipped, mode='w', format=tarfile.PAX_FORMAT) as tar:
                for path in nodes:
                    info = tar.gettarinfo(str(path), arcname=str(path.relative_to(ROOT)))
                    info.uid = info.gid = 0
                    info.uname = info.gname = ''
                    info.mtime = 0
                    if path.is_file():
                        with path.open('rb') as stream:
                            tar.addfile(info, stream)
                    else:
                        tar.addfile(info)
        raw.flush()
        os.fsync(raw.fileno())
    actual = {}
    with tarfile.open(archive, 'r:gz') as tar:
        for member in tar:
            assert member.name not in actual and not member.issym() and not member.islnk()
            if member.isfile():
                with tar.extractfile(member) as stream:
                    actual[member.name] = {'bytes': member.size, 'sha256': hashlib.file_digest(stream, 'sha256').hexdigest()}
            else:
                assert member.isdir()
                actual[member.name] = None
    assert set(actual) == {item['path'] for item in members}
    for item in members:
        if item['kind'] == 'file':
            assert actual[item['path']] == {k: item[k] for k in ['bytes', 'sha256']}
            assert digest(ROOT / item['path']) == item['sha256']
    entry = {'archive': str(archive.relative_to(ROOT)), 'archive_bytes': archive.stat().st_size,
             'archive_sha256': digest(archive), 'tree': str(tree.relative_to(ROOT)),
             'original_bytes': sum(x.get('bytes', 0) for x in members), 'members': members,
             'round_trip': 'every archive member read and compared against original SHA-256 and size before removal'}
    save(PROBES / (tree.name + '.archive.json'), entry)
    archives.append(entry)
    # Both archive data and manifest were fsynced before removing closed copies.
    for path in sorted(nodes, key=lambda p: len(p.parts), reverse=True):
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink()

for item in downloads + bytecode:
    path = Path(item['path'])
    assert digest(path) == item['sha256'] and path.stat().st_size == item['bytes']
    path.unlink()
for path in sorted({Path(x['path']).parent for x in bytecode}, key=lambda p: len(p.parts), reverse=True):
    if path.is_dir() and not any(path.iterdir()):
        path.rmdir()

after = resources()
removed_members = {item['path'] for entry in archives for item in entry['members'] if item['kind'] == 'file'}
unexpected = [p for p, sha in baseline.items() if p not in removed_members and digest(ROOT / p) != sha]
assert not unexpected, unexpected
report = {'base_commit': BASE, 'branch': 'm04-engine-readiness', 'before': before, 'after': after,
          'downloads_removed': len(downloads), 'download_bytes_removed': sum(x['bytes'] for x in downloads),
          'ignored_cache_files_removed': len(bytecode), 'ignored_cache_bytes_removed': sum(x['bytes'] for x in bytecode),
          'archives': [{k:v for k,v in entry.items() if k != 'members'} for entry in archives],
          'tracked_files_archived': len(removed_members), 'other_base_tracked_files_hash_unchanged': True,
          'other_base_tracked_files_checked': len(baseline) - len(removed_members),
          'observed_disk_free_increase_bytes': after['disk_free_bytes'] - before['disk_free_bytes'],
          'quantum_launched': False, 'budget_changed': False}
save(OUT / 'cleanup-result.json', report)
print(json.dumps(report, indent=2))
