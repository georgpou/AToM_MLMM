"""Independent read-only identities for the exact G10 v5 combined submission."""
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/AToM_MLMM-g10')
HERE = ROOT / 'Worker_Log/Milestone_05/evidence/G10_v5_independent'
SUBMISSION = 'ecace38b34e15fae65508b2ee9cd2f535a1b85c4'
DESIGN = 'bd44b2c93a5cba40225dba632f0277e535467be9'
HEAD = 'edd587679aaa110ea687cca29b9e3aee70b7b6f0'


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    assert git('rev-parse', 'HEAD').decode().strip() == HEAD
    assert git('branch', '--show-current').decode().strip() == 'g10-engine-next'
    unchanged = ['src', 'tests', 'fixtures', 'environment', 'models', 'examples/cloud_engine/README.md']
    assert git('diff', '--name-only', SUBMISSION, HEAD, '--', *unchanged) == b''
    production_changed = git('diff', '--name-only', DESIGN, SUBMISSION, '--', 'src').decode().splitlines()
    assert production_changed == ['src/atm_mlmm/exchange.py', 'src/atm_mlmm/exchange_journal.py']
    protected = ['fixtures', 'environment', 'models', 'docs/project-0/specs', 'Worker_Log/Milestone_03']
    assert git('diff', '--name-only', DESIGN, HEAD, '--', *protected) == b''
    inventory = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes())
                 for p in sorted((ROOT / 'src/atm_mlmm').rglob('*.py'))}
    packet = ROOT / 'Worker_Log/Milestone_05/evidence/G10_v5_review_packet'
    runtime_paths = json.loads((packet / 'orchestrator-verification.json').read_text())['combined_diff']['paths']
    raw_diff = gzip.decompress((packet / 'combined-runtime.diff.gz').read_bytes())
    assert raw_diff == git('diff', DESIGN, SUBMISSION, '--', *runtime_paths)
    assert digest(raw_diff) == '9fc744b7d305dbaf3797e9bd28e2664b2550a00fbf99e56c1ace6067bffe9bd6'
    submitted_hashes = {}
    evidence = ROOT / 'Worker_Log/Milestone_05/evidence/G10_v5'
    for line in (evidence / 'artifact-hashes.txt').read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        expected, path = line.split(None, 1)
        actual = digest(git('show', f'{SUBMISSION}:{path.strip()}'))
        assert actual == expected, path
        submitted_hashes[path.strip()] = actual
    failed_logs = {}
    for attempt in ('focused', 'repaired', 'repair2', 'final-focused'):
        raw = gzip.decompress((evidence / f'pilot-{attempt}.log.gz').read_bytes())
        original = Path('/workspace/G10_v5_artifacts/raw-logs') / f'pilot-{attempt}.log'
        assert raw == original.read_bytes()
        failed_logs[attempt] = {'raw_sha256': digest(raw), 'raw_bytes': len(raw),
                               'result_line': raw.decode().splitlines()[-1]}
    old_sources = json.loads((evidence / 'source-inventory.json').read_text())
    preserved = []
    for attempt, cases in old_sources['attempts'].items():
        for case, expected in cases.items():
            case_root = Path('/workspace/G10_v5_artifacts') / attempt / case
            for role in ('prepared-run', 'multistate-run'):
                worker = case_root / role / 'worker'
                manifest = json.loads((worker / 'manifest.json').read_text())
                source = {p: h for p, h in manifest['files'].items()
                          if p.startswith('runtime/source/atm_mlmm/') and p.endswith('.py')}
                assert source == expected['source_files'], (attempt, case, role)
                actual_paths = {p.relative_to(worker).as_posix()
                                for p in (worker / 'runtime/source/atm_mlmm').rglob('*.py')}
                assert actual_paths == set(source)
                for name, sha256 in source.items():
                    assert digest((worker / name).read_bytes()) == sha256
                # Verify all manifest entries, including the unchanged local model and locks.
                for name, sha256 in manifest['files'].items():
                    assert digest((worker / name).read_bytes()) == sha256
                preserved.append({'attempt': attempt, 'case': case, 'role': role,
                                  'source_file_count': len(source),
                                  'worker_manifest_sha256': digest((worker / 'manifest.json').read_bytes()),
                                  'exchange_sha256': source['runtime/source/atm_mlmm/exchange.py']})
    from atm_mlmm.workflow import _profile
    important = runtime_paths + ['docs/project-0/specs/g10-multistate-runtime-amendment.md',
                                'environment/cloud-cpu/core-conda-linux-64.lock',
                                'environment/cloud-cpu/amber-conda-linux-64.lock']
    result = {'reviewed_head': HEAD, 'submission': SUBMISSION, 'design': DESIGN,
              'actual_reviewer_assignment': 'gpt-6.1-sol / max; root-dispatched sole auditor',
              'source_test_fixture_environment_model_usage_equal_to_submission': True,
              'protected_specs_fixtures_environment_models_m03_evidence_unchanged': True,
              'production_changed': production_changed, 'source_inventory': inventory,
              'source_inventory_count': len(inventory), 'runtime_diff_bytes': len(raw_diff),
              'runtime_diff_sha256': digest(raw_diff), 'submitted_hashes_verified': submitted_hashes,
              'frozen_worker_bundles_verified': preserved, 'failed_logs_verified': failed_logs,
              'important_hashes': {p: digest((ROOT / p).read_bytes()) for p in important},
              'profile': _profile(), 'activation_sha256': digest(Path('/workspace/m05-cpu-setup-v2/activate.sh').read_bytes()),
              'finished_utc': datetime.now(timezone.utc).isoformat(), 'exit_status': 0}
    (HERE / 'identity-results.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'source_files': len(inventory), 'submitted_hashes': len(submitted_hashes),
                      'frozen_bundles': len(preserved), 'failed_raw_logs': len(failed_logs),
                      'exit_status': 0, 'finished_utc': result['finished_utc']}, sort_keys=True))


if __name__ == '__main__':
    main()
