"""Record the actual independent decision and stable-check command evidence.

Run from the repository root after activation. Refuse to overwrite evidence.
"""
from pathlib import Path
import gzip
import hashlib
import json
import re
import subprocess

from atm_mlmm.schema import AcceptanceRecord, ValidationReport, from_json, to_json

REVIEWED = '6015a652c4a9a9c968ab7933c07ac7bbb4573e12'
HERE = Path(__file__).resolve().parent
WORKER = HERE.parent / 'M02_v2'
INDEPENDENT = HERE.parent / 'M02_v2_independent'
AUDITS = (
    'Worker_Log/Milestone_02/Gate_02_v2_audit.md',
    'Worker_Log/Milestone_02/Gate_03_v2_audit.md',
)
manifest = json.loads((WORKER / 'source-input-manifest.json').read_text())
for name, expected in manifest['sha256'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
assert not subprocess.check_output([
    'git', 'diff', '--name-only', REVIEWED, '--',
    'src', 'tests', 'fixtures', 'environment', 'models', 'examples',
], text=True).strip()
for name in AUDITS:
    text = Path(name).read_text()
    assert REVIEWED in text and 'accepted_for_scope' in text
    assert 'gpt-6-astra' in text and 'high' in text

commands = json.loads(gzip.decompress((INDEPENDENT / 'command-results.json.gz').read_bytes()))
by_name = {row['name']: row for row in commands}
assert all(row['exit_code'] == 0 and row['head'] == REVIEWED for row in commands)
reports = []
for gate, specification in (
    ('g02', 'docs/project-0/gates/G02-analytic-force-in-native-atm.md'),
    ('g03', 'docs/project-0/gates/G03-atom-routing-and-integration.md'),
):
    for line in Path(specification).read_text().splitlines():
        if not re.match(r'\| P0-TEST-G0[23]-\d+ \|', line):
            continue
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        check_id, node = cells[0], cells[1].strip('`')
        requirements = tuple(re.findall(r'P0-REQ-\d+', cells[-1]))
        case_lines = [line for line in by_name[gate]['output'].splitlines()
                      if re.match(re.escape(node) + r'(?:\[|\s)', line)]
        assert case_lines and all(' PASSED ' in line for line in case_lines), node
        inputs = ('fixtures/analytic/transfer-v1.json', 'tests/analytic_oracle.py',
                  node.split('::')[0])
        fixtures = tuple(f'{name}#sha256={manifest["sha256"][name]}' for name in inputs)
        environment = (WORKER / 'environment-manifest.json.gz').relative_to(Path.cwd())
        fixtures += (f'{environment}#sha256={hashlib.sha256(environment.read_bytes()).hexdigest()}',)
        reports.append(ValidationReport(
            check_id=check_id, requirement_ids=requirements, profile='core-analytic-cpu',
            fixture_identities=fixtures,
            measured_values={'pytest_node': node, 'passed_cases': len(case_lines),
                             'applicable_assertions_passed': True},
            thresholds={'minimum_passed_cases': 1, 'applicable_assertions_passed': True,
                        'assertion_contract': f'{specification}: {check_id}'},
            status='passed',
            logs=('Worker_Log/Milestone_02/evidence/M02_v2_independent/command-results.json.gz',
                  'Worker_Log/Milestone_02/evidence/M02_v2_independent/independent-numerics.json'),
            reviewer_references=AUDITS, tested_snapshot=REVIEWED,
        ))
assert len(reports) == 16
acceptance = AcceptanceRecord(
    scope='M02/G02-T1,T2,T3/G03-T1,T2,T3', profile='core-analytic-cpu', snapshot=REVIEWED,
    requirement_ids=tuple(sorted({req for report in reports for req in report.requirement_ids})),
    required_test_ids=tuple(report.check_id for report in reports), reports=tuple(reports),
    reviewer='Codex /root/m02_v2_independent_audit; configured gpt-6-astra, high reasoning',
    verdict='accepted_for_scope', reviewer_decision=AUDITS[1], status='accepted',
)
encoded = to_json(acceptance)
assert from_json(encoded) == acceptance
with (HERE / 'acceptance.json').open('x') as output:
    output.write(json.dumps(json.loads(encoded), indent=2, sort_keys=True) + '\n')
print(json.dumps({'snapshot': REVIEWED, 'status': acceptance.status,
                  'verdict': acceptance.verdict, 'stable_checks': len(reports),
                  'requirements': len(acceptance.requirement_ids),
                  'source_input_hashes_verified': len(manifest['sha256']),
                  'schema_round_trip': True}, indent=2))
