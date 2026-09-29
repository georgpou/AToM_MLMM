#!/usr/bin/env python3
"""Check this documentation edition, not molecular software or later gate progress.

Run from the repository root:
  python Worker_Log/Milestone_00/evidence/Documentation_v1/check_docs.py

This release-specific check expects unexecuted gates. Later real work changes those
expectations; do not erase evidence or reset progress to make this old check pass.
Only Python's standard library is required. External URLs are not fetched.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit


def without_fences(text: str) -> str:
    return re.sub(r'^```[^\n]*\n.*?^```[^\n]*$', '', text, flags=re.M | re.S)


def math_expressions(text: str) -> list[str]:
    return re.findall(r'\$\$.*?\$\$|(?<!\$)\$(?!\$)[^\n$]+\$', without_fences(text), re.S)


def anchors(text: str) -> set[str]:
    found: set[str] = set()
    counts: dict[str, int] = {}
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', without_fences(text), re.M):
        heading = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', heading)
        value = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        n = counts.get(value, 0)
        counts[value] = n + 1
        found.add(value if n == 0 else f'{value}-{n}')
    found.update(re.findall(r'<a\s+(?:id|name)=[\"\x27]([^\"\x27]+)', text))
    return found


def has_cycle(items: list[dict]) -> bool:
    graph = {item['id']: item['depends_on'] for item in items}
    visiting: set[str] = set()
    done: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in done:
            return False
        if node not in graph:
            return True
        visiting.add(node)
        if any(visit(parent) for parent in graph[node]):
            return True
        visiting.remove(node)
        done.add(node)
        return False

    return any(visit(node) for node in graph)


def check(root: Path) -> dict:
    root = root.resolve()
    plan = root / 'docs/project-0'
    evidence = root / 'Worker_Log/Milestone_00/evidence/Documentation_v1'
    baseline = json.loads((evidence / 'baseline-summary.json').read_text())
    data = json.loads((plan / 'plan-index.json').read_text())
    errors: list[str] = []
    count: dict[str, int] = {}

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    markdown = sorted(root.rglob('*.md'))
    text = {p.resolve(): p.read_text(encoding='utf-8') for p in markdown}
    count['markdown_files'] = len(markdown)
    count['internal_link_occurrences'] = 0
    count['external_link_occurrences_not_fetched'] = 0
    for path, body in text.items():
        rel = path.relative_to(root).as_posix()
        require(body.count('\ufffd') == 0, f'{rel}: replacement character')
        require(sum(line.startswith('```') for line in body.splitlines()) % 2 == 0,
                f'{rel}: unbalanced code fences')
        definitions = dict(re.findall(r'^\[([^\]]+)\]:\s*(\S+)', body, re.M))
        targets = re.findall(r'(?<!!)\[[^\]\n]*\]\(([^\s)]+)\)', without_fences(body))
        used_refs = re.findall(r'\[(S\d{2})\](?![:(])', without_fences(body))
        for ref in used_refs:
            require(ref in definitions, f'{rel}: undefined source reference {ref}')
        for target in targets:
            parts = urlsplit(target.strip('<>'))
            if parts.scheme or parts.netloc:
                count['external_link_occurrences_not_fetched'] += 1
                continue
            count['internal_link_occurrences'] += 1
            dest = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            require(dest.is_relative_to(root), f'{rel}: link outside package: {target}')
            require(dest.exists(), f'{rel}: missing target: {target}')
            if dest.exists() and parts.fragment and dest.suffix == '.md':
                require(unquote(parts.fragment) in anchors(dest.read_text()),
                        f'{rel}: missing heading: {target}')

    gates = {x['id']: x for x in data['gates']}
    milestones = {x['id']: x for x in data['milestones']}
    specs = {x['id']: x for x in data['specs']}
    tests = {x['id']: x for x in data['tests']}
    reqs = {x['id']: x for x in data['requirements']}
    require(len(gates) == len(data['gates']) == 14, 'gate count/uniqueness')
    require(len(milestones) == len(data['milestones']) == 9, 'milestone count/uniqueness')
    require(len(specs) == len(data['specs']) == 7, 'specification count/uniqueness')
    require(len(tests) == len(data['tests']) == 82, 'planned test count/uniqueness')
    require(len(reqs) == len(data['requirements']) == 32, 'requirement count/uniqueness')
    require(len({x['nodeid'] for x in tests.values()}) == 82, 'duplicate test node')
    require(not has_cycle(data['gates']), 'gate dependency cycle/missing node')
    require(not has_cycle(data['milestones']), 'milestone dependency cycle/missing node')
    status_text = (plan / 'STATUS.md').read_text()
    for item in list(gates.values()) + list(milestones.values()):
        require((plan / item['path']).is_file(), f"missing task page {item['id']}")
        require(item['status'] == 'not_started', f"false execution status: {item['id']}")
        require(item.get('latest_worker_log') is None and item.get('latest_audit_log') is None,
                f"unexecuted task has log pointer: {item['id']}")
        require(bool(re.search(r'\| \[' + item['id'] + r'\]\([^)]*\) \| not_started \|', status_text)),
                f"STATUS.md and index disagree: {item['id']}")
        task_text = (plan / item['path']).read_text()
        require('## Read for this task' in task_text, f"missing reading route: {item['id']}")
        require(item['log_directory'] in task_text, f"missing log destination: {item['id']}")
    task_ids: set[str] = set()
    for key, gate in gates.items():
        owner = milestones[gate['milestone']]
        expected = 'Worker_Log/Milestone_' + gate['milestone'][1:]
        require(gate['log_directory'] == expected, f'wrong log directory: {key}')
        require(gate['log_stem'] == 'Gate_' + key[1:], f'wrong log stem: {key}')
        require(key in owner['gates'], f'milestone ownership mismatch: {key}')
        require((root / expected / 'README.md').is_file(), f'missing log folder: {key}')
        body = (plan / gate['path']).read_text()
        covered: set[str] = set()
        for task in gate['tasks']:
            require(task['id'] not in task_ids, f"duplicate task: {task['id']}")
            task_ids.add(task['id'])
            require(f"### {task['id']}:" in body, f"missing small task section: {task['id']}")
            for test in task['tests']:
                require(test in tests and tests[test]['gate'] == key, f"wrong task test: {task['id']} / {test}")
                covered.add(test)
        require(covered == set(gate['tests']), f'task/test coverage mismatch: {key}')
        require(set(gate['tests']) == {t for t, value in tests.items() if value['gate'] == key},
                f'gate/test registry mismatch: {key}')
        for test in gate['tests']:
            require(tests[test]['nodeid'] in body, f'missing exact test node: {key}/{test}')
    require(len(task_ids) == 42, 'small task count')
    for key, ms in milestones.items():
        require(ms['log_directory'] == 'Worker_Log/Milestone_' + key[1:], f'wrong milestone log directory: {key}')
    for key, test in tests.items():
        require(test['status'] == 'not_run', f'false test result: {key}')
        require(set(test['requirements']) <= set(reqs), f'unknown test requirement: {key}')
        require(test['nodeid'] in (plan / 'TEST_CATALOG.md').read_text(), f'missing catalog node: {key}')
    for key, req in reqs.items():
        mapped = {t for t, value in tests.items() if key in value['requirements']}
        require(mapped == set(req['tests']) and bool(mapped), f'reverse coverage mismatch: {key}')
        require(req['spec'] in specs and req['primary_gate'] in gates, f'unknown requirement owner: {key}')
        require(any(tests[t]['gate'] == req['primary_gate'] for t in mapped), f'primary gate lacks check: {key}')
        require(req['status'] == 'proposed', f'unsupported requirement status: {key}')
    for old in baseline['tests']:
        require(tests.get(old['id']) == old, f"original test changed: {old['id']}")
    require(set(tests) - {x['id'] for x in baseline['tests']} == {'P0-TEST-G01-07'}, 'unexpected added test')
    for old in baseline['requirements']:
        for field in ('statement', 'spec', 'primary_gate'):
            require(reqs[old['id']][field] == old[field], f"requirement meaning changed: {old['id']}/{field}")
    for kind, actual in (('gates', gates), ('milestones', milestones)):
        for old in baseline[kind]:
            for field in ('depends_on', 'path', 'milestone' if kind == 'gates' else 'gates'):
                require(actual[old['id']][field] == old[field], f"original structure changed: {old['id']}/{field}")
    formula_count = 0
    for rel, expressions in baseline['mathematical_expressions'].items():
        require(math_expressions((root / rel).read_text()) == expressions, f'scientific expression changed: {rel}')
        formula_count += len(expressions)
    archive = 'docs/project-0/reference/original-brainstorming-plan.md'
    require(hashlib.sha256((root / archive).read_bytes()).hexdigest() == baseline['baseline_file_hashes'][archive],
            'original brainstorming archive changed')
    require(data['acceptance_records'] == [] and data['execution_records'] == [], 'fabricated execution/acceptance record')
    require(data['documentation_revision']['counts_as_M00_acceptance'] is False, 'documentation accepted M00')
    require(data['documentation_revision']['audit_log'] is None, 'invented documentation audit')
    require(data['numerical_qualification_performed'] is False, 'false numerical qualification')
    require(not data['remote_changes_made'] and not data['repository_inspected'], 'unsupported remote claim')
    log_pattern = re.compile(r'(?:Gate_\d{2}|Milestone_\d{2}|Documentation)_v[1-9]\d*_(?:worker|audit)\.md')
    logs = [p for p in (root/'Worker_Log').rglob('*.md') if p.name.endswith(('_worker.md', '_audit.md'))]
    for log in logs:
        require(log_pattern.fullmatch(log.name) is not None, f'invalid log filename: {log.name}')
        require(log.parent.name.startswith('Milestone_'), f'wrong log nesting: {log.name}')
    require(not any(p.name.endswith('_audit.md') for p in logs), 'independent audit invented')
    for log in logs:
        body = log.read_text()
        require('**Draft:' not in body, f'worker report still draft: {log.name}')
        for field in ('Model', 'Reasoning setting', 'Finished at', 'Outcome'):
            require(bool(re.search(r'\| ' + field + r' \| .+ \|', body)),
                    f'missing worker metadata {field}: {log.name}')
        match = re.search(r'\| Finished at \| ([^|]+) \|', body)
        if match:
            try:
                timestamp = datetime.fromisoformat(match.group(1).strip().replace('Z', '+00:00'))
                require(timestamp.tzinfo is not None, f'timestamp missing timezone: {log.name}')
            except ValueError:
                require(False, f'invalid completion timestamp: {log.name}')
    require(not (root/'src').exists() and not (root/'tests').exists(), 'unexpected molecular source/test implementation')
    count.update(gates=len(gates), milestones=len(milestones), specifications=len(specs),
                 small_tasks=len(task_ids), requirements=len(reqs), planned_tests=len(tests),
                 preserved_original_tests=len(baseline['tests']), preserved_mathematical_expressions=formula_count,
                 actual_worker_logs=len(logs), actual_audit_logs=0)
    return {'scope': 'edition-2 documentation consistency, not molecular qualification',
            'passed': not errors, 'counts': count, 'errors': errors}


def adversarial_self_tests(root: Path) -> list[dict]:
    """Damage disposable copies, then require the checker to catch each mistake."""
    output = []
    cases = ('broken_link', 'wrong_log_folder', 'changed_formula', 'false_acceptance', 'bad_attempt_name')
    for case in cases:
        with tempfile.TemporaryDirectory(prefix='atm-doc-check-') as directory:
            target = Path(directory) / 'repo'
            shutil.copytree(root, target)
            idx_path = target/'docs/project-0/plan-index.json'
            if case == 'broken_link':
                with (target/'AGENTS.md').open('a') as handle:
                    handle.write('\n[broken](does-not-exist.md)\n')
            elif case in ('wrong_log_folder', 'false_acceptance'):
                index = json.loads(idx_path.read_text())
                if case == 'wrong_log_folder':
                    index['gates'][1]['log_directory'] = 'Worker_Log/Milestone_08'
                else:
                    index['gates'][1]['status'] = 'accepted'
                idx_path.write_text(json.dumps(index))
            elif case == 'changed_formula':
                baseline = json.loads((target/'Worker_Log/Milestone_00/evidence/Documentation_v1/baseline-summary.json').read_text())
                rel, expressions = next((p, x) for p, x in baseline['mathematical_expressions'].items() if x)
                path = target/rel
                path.write_text(path.read_text().replace(expressions[0], '$999$', 1))
            else:
                (target/'Worker_Log/Milestone_01/Gate_01_v0_worker.md').write_text('Invalid test fixture.\n')
            result = check(target)
            output.append({'deliberate_error': case, 'detected': not result['passed'],
                           'reported_errors': result['errors']})
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    try:
        result = check(args.root)
        if args.self_test:
            result['checker_self_tests'] = adversarial_self_tests(args.root)
            result['passed'] = result['passed'] and all(x['detected'] for x in result['checker_self_tests'])
        print(json.dumps(result, indent=2))
        return 0 if result['passed'] else 1
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({'passed': False, 'setup_error': str(exc)}, indent=2))
        return 2


if __name__ == '__main__':
    sys.exit(main())
