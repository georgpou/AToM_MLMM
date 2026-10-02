"""Verify report-only closure, immutable evidence and protected remote refs.

Run from the repository root after activation, before the publication commit.
"""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

from atm_mlmm.schema import AcceptanceRecord, from_json

REVIEWED = '35b48dbe0ac00e2f2270c0fb983b5e10bac9e86a'
SOURCE = '55df6a7d25e7a4de607a13b7d87c327feddecb34'
HANDOFF = 'c63634ca7567428e294a73fa432d42026f9fd38a'
HERE = Path(__file__).resolve().parent
WORKER = HERE.parent / 'G04_v1'


def git(*args, cwd=None):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).rstrip('\n')


def sha(data):
    return hashlib.sha256(data).hexdigest()


assert git('branch', '--show-current') == 'm03-link-boundary'
assert git('rev-parse', 'HEAD') == REVIEWED
for ancestor in (HANDOFF, SOURCE, '8dcb75c4e720c0da3179e06d40ccc13c9f23f16f'):
    subprocess.run(['git', 'merge-base', '--is-ancestor', ancestor, 'HEAD'], check=True)
assert not git('diff', '--name-only', REVIEWED, '--',
               'src', 'tests', 'fixtures', 'environment', 'models', 'examples')
inputs = json.loads((WORKER / 'source-input-manifest.json').read_text())
assert inputs['source_commit'] == SOURCE and len(inputs['sha256']) == 151
for name, expected in inputs['sha256'].items():
    assert sha(Path(name).read_bytes()) == expected, name
preservation = json.loads((WORKER / 'preservation.json').read_text())
assert preservation['base'] == HANDOFF and len(preservation['unchanged_inherited_files']) == 212
for name, expected in preservation['unchanged_inherited_files'].items():
    assert sha(Path(name).read_bytes()) == expected, name
    assert sha(subprocess.check_output(['git', 'show', f'{HANDOFF}:{name}'])) == expected, name

frozen_worker = {}
for name in git('ls-tree', '-r', '--name-only', REVIEWED, '--', 'Worker_Log/Milestone_03').splitlines():
    expected = sha(subprocess.check_output(['git', 'show', f'{REVIEWED}:{name}']))
    assert sha(Path(name).read_bytes()) == expected, name
    frozen_worker[name] = expected
copied = json.loads((HERE / 'independent-copy-manifest.json').read_text())
assert copied['reviewed_snapshot'] == REVIEWED and len(copied['sha256']) == 66
for name, expected in copied['sha256'].items():
    assert sha(Path(name).read_bytes()) == expected, name
    original = Path(copied['source_review_worktree']) / name
    assert sha(original.read_bytes()) == expected, name
interrupted = json.loads((HERE / 'interrupted-review-preservation.json').read_text())
for name, expected in interrupted['sha256'].items():
    assert sha((HERE.parent / 'G04_v1_independent' / name).read_bytes()) == expected, name

allowed_files = {
    'docs/project-0/STATUS.md', 'docs/project-0/handoffs/M03-after-G04.md',
    'Worker_Log/Milestone_03/Gate_04_v1_audit.md',
}
allowed_folders = tuple('Worker_Log/Milestone_03/evidence/' + name + '/' for name in
                        ('G04_v1_independent', 'G04_v1_independent_r2', 'G04_v1_closure'))
changed = []
for line in git('status', '--porcelain', '--untracked-files=all').splitlines():
    name = line[3:]
    assert name in allowed_files or name.startswith(allowed_folders), line
    changed.append(name)

protected = {
    'refs/heads/main': '2d7bcc94f901738e39f536f16de84699d4e8d631',
    'refs/heads/m00-audit-m01-development': '87146b4cc7fbd0b58d6688903a5ba081b813ac13',
    'refs/heads/m02-analytic-atm': HANDOFF,
}
expected_refs = dict(protected, **{'refs/heads/m03-link-boundary': REVIEWED})
remote = {ref: commit for commit, ref in
          (line.split() for line in git('ls-remote', '--heads', 'origin', *expected_refs).splitlines())}
assert remote == expected_refs, remote
original_repo = Path('/workspace/AToM_MLMM')
assert git('rev-parse', 'HEAD', cwd=original_repo) == protected['refs/heads/main']
assert git('branch', '--show-current', cwd=original_repo) == 'work'
assert not git('status', '--porcelain', cwd=original_repo)

acceptance = from_json((HERE / 'acceptance.json').read_text())
assert isinstance(acceptance, AcceptanceRecord)
assert acceptance.status == 'accepted' and acceptance.verdict == 'accepted_for_scope'
assert acceptance.snapshot == REVIEWED and len(acceptance.required_test_ids) == 7
assert len(acceptance.requirement_ids) == 7
result = {
    'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'branch': 'm03-link-boundary', 'reviewed_snapshot': REVIEWED,
    'source_input_commit': SOURCE, 'handoff': HANDOFF,
    'required_ancestry_verified': True, 'source_test_fixture_environment_model_example_diff': [],
    'source_input_hashes_verified': 151, 'inherited_hashes_verified': 212,
    'frozen_worker_files_unchanged': frozen_worker,
    'independent_copied_file_count': len(copied['sha256']),
    'interrupted_review_file_count': len(interrupted['sha256']),
    'all_copied_review_files_match_reviewer_originals': True,
    'report_only_changes': sorted(changed), 'remote_tips_before_push': remote,
    'original_work_checkout_clean_and_unchanged': True,
    'acceptance_schema_valid': True, 'stable_checks': 7, 'requirements': 7,
    'actual_review_configuration': {'model': 'gpt-6-astra', 'reasoning_effort': 'high',
                                    'fork_turns': 'none', 'deployed_version_exposed': False},
    'intended_push_refspec': 'HEAD:refs/heads/m03-link-boundary',
}
with (HERE / 'publication-verification.json').open('x') as output:
    json.dump(result, output, indent=2, sort_keys=True)
    output.write('\n')
print(json.dumps({key: result[key] for key in (
    'branch', 'reviewed_snapshot', 'source_input_hashes_verified', 'inherited_hashes_verified',
    'independent_copied_file_count', 'acceptance_schema_valid', 'remote_tips_before_push',
    'original_work_checkout_clean_and_unchanged',
)}, indent=2))
