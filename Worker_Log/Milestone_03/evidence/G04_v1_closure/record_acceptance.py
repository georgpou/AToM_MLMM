"""Record the actual Astra decision and all seven independent stable checks.

Run after activation from the repository root. Existing evidence is immutable.
"""
from pathlib import Path
import gzip
import hashlib
import json
import re
import subprocess

from atm_mlmm.schema import AcceptanceRecord, ValidationReport, from_json, to_json

REVIEWED = '35b48dbe0ac00e2f2270c0fb983b5e10bac9e86a'
HERE = Path(__file__).resolve().parent
WORKER = HERE.parent / 'G04_v1'
INDEPENDENT = HERE.parent / 'G04_v1_independent_r2'
AUDIT = 'Worker_Log/Milestone_03/Gate_04_v1_audit.md'
GATE = 'docs/project-0/gates/G04-link-boundary-and-derivatives.md'

manifest = json.loads((WORKER / 'source-input-manifest.json').read_text())
for name, expected in manifest['sha256'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
assert not subprocess.check_output([
    'git', 'diff', '--name-only', REVIEWED, '--',
    'src', 'tests', 'fixtures', 'environment', 'models', 'examples',
], text=True).strip()
decision = Path(AUDIT).read_text()
assert '**Decision:** **accepted_for_scope** for **all G04-T1/T2/T3' in decision
assert REVIEWED in decision and 'gpt-6-astra' in decision
assert 'reasoning_effort="high"' in decision and 'fork_turns="none"' in decision

captures = {}
for name in ('g04', 'full', 'analytic', 'g02', 'g03', 'admission', 'strict', 'upstream',
             'cap-independent', 'cap-admission', 'offline-cap', 'docs', 'whitespace',
             'inherited-numerics', 'inherited-admission', 'inherited-closure',
             'stale-offline', 'final-snapshot'):
    row = json.loads(gzip.decompress((INDEPENDENT / (name + '.json.gz')).read_bytes()))
    assert row['exit_code'] == 0 and row['head'] == REVIEWED, name
    captures[name] = row
assert re.search(r'\b24 passed\b', captures['g04']['output'])

minimum_cases = dict(zip(range(1, 8), (1, 2, 1, 1, 4, 2, 2)))
reports = []
for line in Path(GATE).read_text().splitlines():
    if not re.match(r'\| P0-TEST-G04-\d+ \|', line):
        continue
    cells = [cell.strip() for cell in line.split('|')[1:-1]]
    check_id, node = cells[0], cells[1].strip('`')
    requirements = tuple(re.findall(r'P0-REQ-\d+', cells[-1]))
    cases = [row for row in captures['g04']['output'].splitlines()
             if re.match(re.escape(node) + r'(?:\[|\s)', row)]
    required = minimum_cases[int(check_id[-2:])]
    assert len(cases) >= required and all(' PASSED ' in row for row in cases), node
    inputs = ('fixtures/one_cut_alkane/input.json', 'fixtures/one_cut_alkane/original-mm.xml',
              'tests/link_oracle.py', 'tests/link_permutation.py', node.split('::')[0])
    identities = tuple(f'{name}#sha256={manifest["sha256"][name]}' for name in inputs)
    environment = (WORKER / 'environment-manifest.json.gz').relative_to(Path.cwd())
    identities += (f'{environment}#sha256={hashlib.sha256(environment.read_bytes()).hexdigest()}',)
    evidence = 'Worker_Log/Milestone_03/evidence/G04_v1_independent_r2/'
    reports.append(ValidationReport(
        check_id=check_id, requirement_ids=requirements, profile='core-analytic-cpu',
        fixture_identities=identities,
        measured_values={'pytest_node': node, 'passed_cases': len(cases),
                         'applicable_assertions_passed': True},
        thresholds={'minimum_passed_cases': required, 'applicable_assertions_passed': True,
                    'assertion_contract': f'{GATE}: {check_id}'},
        status='passed', logs=(evidence + 'g04.json.gz', evidence + 'cap-independent-results.json',
                               evidence + 'structure.json'),
        reviewer_references=(AUDIT,), tested_snapshot=REVIEWED,
    ))
assert len(reports) == 7 and sum(r.measured_values['passed_cases'] for r in reports) == 13
acceptance = AcceptanceRecord(
    scope='G04/G04-T1,T2,T3', profile='core-analytic-cpu', snapshot=REVIEWED,
    requirement_ids=tuple(sorted({req for report in reports for req in report.requirement_ids})),
    required_test_ids=tuple(report.check_id for report in reports), reports=tuple(reports),
    reviewer='Codex /root/g04_v1_astra_audit_resume; actual gpt-6-astra, high reasoning, fresh context',
    verdict='accepted_for_scope', reviewer_decision=AUDIT, status='accepted',
)
encoded = to_json(acceptance)
assert from_json(encoded) == acceptance
with (HERE / 'acceptance.json').open('x') as output:
    output.write(json.dumps(json.loads(encoded), indent=2, sort_keys=True) + '\n')
print(json.dumps({'snapshot': REVIEWED, 'status': acceptance.status, 'verdict': acceptance.verdict,
                  'stable_checks': len(reports), 'stable_parameter_cases': 13,
                  'requirements': len(acceptance.requirement_ids),
                  'source_input_hashes_verified': len(manifest['sha256']),
                  'required_independent_captures_verified': len(captures),
                  'schema_round_trip': True}, indent=2))
