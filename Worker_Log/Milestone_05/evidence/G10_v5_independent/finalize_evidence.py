"""Record actual prior commands and verify report-only independent audit output.

This performs no simulation, changes no reviewed module, and stages/commits nothing.
Run under the declared CPU activation from the reviewed repository root.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path('/workspace/AToM_MLMM-g10')
HERE = ROOT / 'Worker_Log/Milestone_05/evidence/G10_v5_independent'
HEAD = 'edd587679aaa110ea687cca29b9e3aee70b7b6f0'
REPORT = ROOT / 'Worker_Log/Milestone_05/Gate_10_v5_audit.md'
STATUS = ROOT / 'docs/project-0/STATUS.md'
PREFIX = ('source /workspace/m05-cpu-setup-v2/activate.sh\n'
          'export OPENBLAS_NUM_THREADS=2 PYTHONPATH="$PWD/src"\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, result):
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


def utc():
    return datetime.now(timezone.utc).isoformat()


def command(arguments, log_name):
    result = subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True)
    (HERE / log_name).write_text(result.stdout + result.stderr)
    return {'argv': arguments, 'cwd': str(ROOT), 'exit_status': result.returncode,
            'finished_utc': utc(), 'stdout_stderr_log': log_name}


def main():
    scientific = []
    probes = [('identity_probe.py', 'identity-probe.log', 'identity-results.json',
               {'source_files': 38, 'submitted_hashes': 24, 'frozen_bundles': 20, 'failed_logs': 4}),
              ('analytic_admission_probe.py', 'analytic-admission-probe.log', 'analytic-admission-results.json',
               {'analytic_cases_passed': 2, 'mathematical_control_passed': 1, 'challenges': 9,
                'violating_challenges': 7, 'correct_rejections': 2}),
              ('transaction_restore_probe.py', 'transaction-restore-probe.log', 'transaction-restore-results.json',
               {'violating_cases': 5}),
              ('molecular_probe.py', 'molecular-probe.log', 'molecular-results.json',
               {'molecular_cases_passed': 2, 'schedule_evaluations': 36, 'pair_matrices': 8,
                'new_integration_steps': 0, 'new_preparation_frames': 0}),
              ('additional_inert_probe.py', 'additional-inert-probe.log', 'additional-inert-results.json',
               {'selection_controls_passed': 16, 'violating_challenges': 5})]
    relative = HERE.relative_to(ROOT).as_posix()
    for script, log, results, counts in probes:
        row = json.loads((HERE / results).read_text())
        scientific.append({'shell': PREFIX + f'python {relative}/{script} >{relative}/{log} 2>&1',
                           'cwd': str(ROOT), 'exit_status': row['exit_status'],
                           'finished_utc': row['finished_utc'],
                           'finished_utc_source': 'complete probe result written at command completion',
                           'counts': counts, 'raw_log': log, 'results': results})
    nodes = [('python -m pytest tests/workflow/test_persistent_exchange.py '
              'tests/workflow/test_replica_exchange.py -k \'multistate or partial_integration\' -q',
              'focused-pytest.log', {'passed': 42, 'skipped': 0, 'deselected': 20, 'seconds': 74.87}),
             ('python -m pytest '
              'tests/workflow/test_persistent_exchange.py::test_round_prefix_resume_preserves_rng_samples_states_and_analysis '
              'tests/workflow/test_replica_exchange.py::test_acceptance_uses_actual_reduced_energies -q',
              'pair-compatibility-pytest.log', {'passed': 5, 'skipped': 0, 'seconds': 7.31})]
    for invocation, log, counts in nodes:
        finished = datetime.fromtimestamp((HERE / log).stat().st_mtime, timezone.utc).isoformat()
        scientific.append({'shell': PREFIX + f'{invocation} >{relative}/{log} 2>&1',
                           'cwd': str(ROOT), 'exit_status': 0, 'counts': counts,
                           'raw_log': log, 'finished_utc': finished,
                           'finished_utc_source': 'raw redirected log final mtime; tool returned exit 0'})
    scientific.sort(key=lambda row: row['finished_utc'])
    commands = {'reviewed_head': HEAD, 'actual_model_effort': 'gpt-6.1-sol / max',
                'scientific_commands': scientific,
                'characterization_nonzero_exits': 'intentional, complete 17 violating cases; see raw results',
                'inspection_methods': ['rg/rg --files', 'sed/cat', 'git diff/show',
                                       'Python stdlib JSON/gzip/hashlib'],
                'incidental_non_scientific_errors':
                    'Exploratory reads used nonexistent test/development/G07 paths, corrected using rg --files; '
                    'a wc glob included the generated __pycache__ directory. These read-only lookup errors '
                    'produced no scientific result, changed no reviewed file, and did not replace failed evidence.',
                'limits': {'memory_max_bytes': int(Path('/sys/fs/cgroup/memory.max').read_text()),
                           'cpu_max': Path('/sys/fs/cgroup/cpu.max').read_text().strip(),
                           'serial_scientific_jobs': True},
                'completion_command': PREFIX + f'python {relative}/finalize_evidence.py'}
    first_attempt = HERE / 'documentation-first-attempt.json'
    if first_attempt.exists():
        commands['report_only_verification_first_attempt'] = json.loads(first_attempt.read_text())
    write(HERE / 'commands.json', commands)
    # These paths must exist when the Markdown link checker sees the index.
    write(HERE / 'completion-results.json', {'state': 'verification_running'})
    write(HERE / 'manifest.json', {'state': 'verification_running'})
    (HERE / 'docs-self-test.log').touch()
    checks = []
    checks.append(command(['python', 'tools/check_docs.py', '--self-test'], 'docs-self-test.log'))
    checks.append(command(['git', 'diff', '--check'], 'diff-check.log'))
    checks.append(command(['git', 'diff', '--cached', '--check'], 'staged-diff-check.log'))
    protected = ['src', 'tests', 'fixtures', 'environment', 'models', 'examples/cloud_engine/README.md',
                 'docs/project-0/specs', 'Worker_Log/Milestone_03',
                 'Worker_Log/Milestone_05/Gate_10_v4_worker.md',
                 'Worker_Log/Milestone_05/Gate_10_v5_worker.md',
                 'Worker_Log/Milestone_05/evidence/G10_v4', 'Worker_Log/Milestone_05/evidence/G10_v5',
                 'Worker_Log/Milestone_05/evidence/G10_v5_review_packet']
    checks.append(command(['git', 'diff', '--exit-code', HEAD, '--', *protected], 'frozen-review-check.log'))
    identity = json.loads((HERE / 'identity-results.json').read_text())
    assert len(identity['source_inventory']) == 38
    actual = {p.relative_to(ROOT).as_posix(): digest(p)
              for p in sorted((ROOT / 'src/atm_mlmm').rglob('*.py'))}
    assert actual == identity['source_inventory'], 'reviewed source inventory changed'
    docs = json.loads((HERE / 'docs-self-test.log').read_text())
    assert docs['errors'] == [], docs
    staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT, text=True).splitlines()
    allowed = ['Worker_Log/Milestone_05/Gate_10_v5_audit.md', 'docs/project-0/STATUS.md']
    assert all(path in allowed or path.startswith(relative + '/') for path in staged), staged
    write(HERE / 'completion-results.json', {
        'reviewed_head': HEAD, 'actual_model_effort': 'gpt-6.1-sol / max',
        'finished_utc': utc(), 'checks': checks,
        'all_checks_passed': all(row['exit_status'] == 0 for row in checks),
        'docs_result': docs, 'source_inventory_files_unchanged': len(actual),
        'staged_scope_check': 'PASS', 'staged_paths': staged,
        'report_only_changes': True, 'implementation_repairs': 0,
        'commit_and_clean_status': 'recorded after committing in the final handoff',
    })
    files = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(HERE.iterdir())
             if p.is_file() and p.name != 'manifest.json'}
    files[REPORT.relative_to(ROOT).as_posix()] = digest(REPORT)
    files[STATUS.relative_to(ROOT).as_posix()] = digest(STATUS)
    write(HERE / 'manifest.json', {'reviewed_head': HEAD, 'sha256': files, 'finished_utc': utc()})
    verified = all(digest(ROOT / path) == sha for path, sha in files.items())
    assert verified
    print(json.dumps({'checks': [(row['argv'], row['exit_status']) for row in checks],
                      'source_files_unchanged': len(actual), 'evidence_report_status_hashes_verified': len(files),
                      'docs_errors': docs['errors'], 'staged_paths': len(staged), 'finished_utc': utc()}, sort_keys=True))
    return 0 if all(row['exit_status'] == 0 for row in checks) else 1


if __name__ == '__main__':
    sys.exit(main())
