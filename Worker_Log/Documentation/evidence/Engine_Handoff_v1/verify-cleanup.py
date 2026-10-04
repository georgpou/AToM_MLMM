"""Verify the maintenance archive by restoring every byte into a private tree."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone

root = Path('/workspace/AToM_MLMM')
out = root / 'Worker_Log/Documentation/evidence/Engine_Handoff_v1'
probes = root / 'Worker_Log/Milestone_03/evidence/G07_v2_revalidation_independent'
baseline = json.loads((out / 'pre-cleanup-tracked-hashes.json').read_text())
changed_docs = {
    'docs/project-0/STATUS.md',
    'docs/project-0/handoffs/G07-reference-remaining-v2.md',
    'docs/project-0/handoffs/M04-G08-fresh-agent-handoff-v1.md',
}

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

archived = set()
checks = []
for name in ['probes-final', 'probes-durable']:
    manifest = json.loads((probes / (name + '.archive.json')).read_text())
    archive = root / manifest['archive']
    assert sha(archive) == manifest['archive_sha256']
    expected = {x['path']: x for x in manifest['members']}
    assert len(expected) == len(manifest['members'])
    seen = set()
    with tempfile.TemporaryDirectory(prefix='engine-handoff-restore-', dir='/tmp') as text:
        destination = Path(text)
        with tarfile.open(archive, 'r:gz') as tar:
            for member in tar:
                assert member.name in expected and member.name not in seen
                seen.add(member.name)
                rel = Path(member.name)
                assert not rel.is_absolute() and '..' not in rel.parts
                assert not member.issym() and not member.islnk()
                item = expected[member.name]
                restored = destination / rel
                if item['kind'] == 'directory':
                    assert member.isdir()
                    restored.mkdir(parents=True, exist_ok=False)
                else:
                    assert member.isfile() and member.size == item['bytes']
                    assert baseline['sha256'][member.name] == item['sha256']
                    restored.parent.mkdir(parents=True, exist_ok=True)
                    with tar.extractfile(member) as source, restored.open('xb') as target:
                        shutil.copyfileobj(source, target)
                    assert restored.stat().st_size == item['bytes']
                    assert sha(restored) == item['sha256']
                    archived.add(member.name)
                os.chmod(restored, item['mode'])
                assert restored.stat().st_mode & 0o7777 == item['mode']
        assert seen == set(expected)
    assert not destination.exists()
    checks.append({'archive': manifest['archive'], 'sha256': manifest['archive_sha256'],
                   'restored_files': sum(x['kind'] == 'file' for x in expected.values()),
                   'restored_directories': sum(x['kind'] == 'directory' for x in expected.values()),
                   'content_size_mode_and_base_hash_match': True,
                   'private_verification_tree_removed_after_validation': True})

unchanged = []
for rel, expected_sha in baseline['sha256'].items():
    if rel in archived or rel in changed_docs:
        continue
    assert sha(root / rel) == expected_sha, rel
    unchanged.append(rel)
protected = ['src', 'tools', 'tests', 'fixtures', 'models', 'environment']
assert not subprocess.check_output(['git', 'diff', '--name-only', '--', *protected], cwd=root)
branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=root).decode().strip()
assert branch == 'm04-engine-readiness'
subprocess.run(['git', 'merge-base', '--is-ancestor', baseline['base_commit'], 'HEAD'], cwd=root, check=True)
assert subprocess.check_output(['git', 'rev-parse', 'm03-g06-g07'], cwd=root).decode().strip() == baseline['base_commit']
assert subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=root).decode().strip() == '2d7bcc94f901738e39f536f16de84699d4e8d631'
vfs = os.statvfs(root)
result = {'verified_utc': datetime.now(timezone.utc).isoformat(),
          'base_commit': baseline['base_commit'], 'branch': branch,
          'archive_restoration': checks, 'unchanged_base_files_checked': len(unchanged),
          'explicit_reporting_only_edits': sorted(changed_docs),
          'protected_source_tests_fixtures_models_environments_unchanged': True,
          'all_G05_and_canonical_G07_attempts_authorization_assessment_ledger_unchanged': True,
          'local_predecessor_and_main_unchanged': True,
          'disk_free_bytes': vfs.f_bavail * vfs.f_frsize,
          'scope': 'handoff and storage maintenance; no new scientific calculation or gate acceptance'}
(out / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
