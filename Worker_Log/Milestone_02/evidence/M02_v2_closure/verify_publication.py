"""Verify report-only publication and protected refs; write new evidence once."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

from atm_mlmm.schema import AcceptanceRecord, from_json

REVIEWED = '6015a652c4a9a9c968ab7933c07ac7bbb4573e12'
HANDOFF = 'a8098a43d46df76b981861aa8dec0522d31be966'
HERE = Path(__file__).resolve().parent
WORKER = HERE.parent / 'M02_v2'


def git(*arguments):
    return subprocess.check_output(['git', *arguments], text=True).rstrip('\n')


def sha(data):
    return hashlib.sha256(data).hexdigest()


assert git('branch', '--show-current') == 'm02-analytic-atm'
assert git('rev-parse', 'HEAD') == REVIEWED
for ancestor in (HANDOFF, '87146b4cc7fbd0b58d6688903a5ba081b813ac13'):
    subprocess.run(['git', 'merge-base', '--is-ancestor', ancestor, 'HEAD'], check=True)
assert not git('diff', '--name-only', REVIEWED, '--',
               'src', 'tests', 'fixtures', 'environment', 'models', 'examples')
source = json.loads((WORKER / 'source-input-manifest.json').read_text())
assert len(source['sha256']) == 127
for name, expected in source['sha256'].items():
    assert sha(Path(name).read_bytes()) == expected, name
baseline = json.loads((WORKER / 'baseline-input-check.json').read_text())
assert len(baseline['preserved_v1_sha256']) == 28
for name, expected in baseline['preserved_v1_sha256'].items():
    assert sha(Path(name).read_bytes()) == expected, name
submitted = {}
for name in git('ls-tree', '-r', '--name-only', REVIEWED, '--', 'Worker_Log/Milestone_02').splitlines():
    expected = sha(subprocess.check_output(['git', 'show', f'{REVIEWED}:{name}']))
    assert sha(Path(name).read_bytes()) == expected, name
    submitted[name] = expected

allowed_files = {'docs/project-0/STATUS.md',
                 'Worker_Log/Milestone_02/Gate_02_v2_audit.md',
                 'Worker_Log/Milestone_02/Gate_03_v2_audit.md'}
allowed_folders = ('Worker_Log/Milestone_02/evidence/M02_v2_independent/',
                   'Worker_Log/Milestone_02/evidence/M02_v2_closure/')
changed = []
for line in git('status', '--porcelain', '--untracked-files=all').splitlines():
    name = line[3:]
    assert name in allowed_files or name.startswith(allowed_folders), line
    changed.append(name)

expected_refs = {
    'refs/heads/main': '2d7bcc94f901738e39f536f16de84699d4e8d631',
    'refs/heads/m00-audit-m01-development': '87146b4cc7fbd0b58d6688903a5ba081b813ac13',
    'refs/heads/m02-analytic-atm': HANDOFF,
}
remote = {ref: commit for commit, ref in
          (line.split() for line in git('ls-remote', 'origin', *expected_refs).splitlines())}
assert remote == expected_refs, remote
assert git('rev-parse', 'refs/remotes/origin/main') == expected_refs['refs/heads/main']
record = from_json((HERE / 'acceptance.json').read_text())
assert isinstance(record, AcceptanceRecord)
assert record.status == 'accepted' and record.verdict == 'accepted_for_scope'
assert record.snapshot == REVIEWED and len(record.required_test_ids) == 16
decision_files = [Path(name) for name in allowed_files if name.endswith('_audit.md')]
evidence_files = sorted((HERE.parent / 'M02_v2_independent').rglob('*'))
independent_hashes = {str(path.resolve().relative_to(Path.cwd())): sha(path.read_bytes())
                      for path in decision_files + evidence_files if path.is_file()}
result = {
    'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'branch': git('branch', '--show-current'), 'reviewed_snapshot': REVIEWED,
    'repaired_source_snapshot': source['code_snapshot'], 'handoff': HANDOFF,
    'handoff_and_predecessor_are_ancestors': True,
    'source_test_fixture_environment_model_example_diff': [],
    'all_127_source_inputs_match': True,
    'all_28_handoff_milestone_files_unchanged': True,
    'all_submitted_milestone_files_unchanged': submitted,
    'report_only_changes': sorted(changed), 'remote_tips_before_push': remote,
    'independent_audit_and_evidence_sha256': independent_hashes,
    'acceptance_schema_valid': True, 'stable_checks': 16, 'requirements': 11,
    'intended_push_refspec': 'HEAD:refs/heads/m02-analytic-atm',
}
with (HERE / 'publication-verification.json').open('x') as output:
    json.dump(result, output, indent=2, sort_keys=True)
    output.write('\n')
print(json.dumps({key: result[key] for key in (
    'branch', 'reviewed_snapshot', 'repaired_source_snapshot',
    'all_127_source_inputs_match', 'all_28_handoff_milestone_files_unchanged',
    'acceptance_schema_valid', 'remote_tips_before_push',
)}, indent=2))
