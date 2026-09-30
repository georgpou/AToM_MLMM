#!/usr/bin/env python3
"""Check local Markdown links/headings; never infer scientific progress.

Run from the repository root: python tools/check_docs.py --self-test
Uses only the standard library. External links are counted, not fetched.
Historical ZIP contents are deliberately not treated as active documentation.
"""
from __future__ import annotations
import argparse
import json
import re
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit


def without_fences(text: str) -> str:
    return re.sub(r'^(`{3,}|~{3,})[^\n]*\n.*?^\1\s*$', '', text, flags=re.M | re.S)


def anchors(text: str) -> set[str]:
    found: set[str] = set()
    counts: dict[str, int] = {}
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', without_fences(text), re.M):
        heading = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', heading)
        value = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        n = counts.get(value, 0)
        counts[value] = n + 1
        found.add(value if n == 0 else f'{value}-{n}')
    found.update(re.findall(r'<a\s+(?:id|name)=["\x27]([^"\x27]+)', text))
    return found


def check(root: Path) -> dict:
    root = root.resolve()
    errors: list[str] = []
    counts = {'markdown_files': 0, 'local_links': 0, 'external_links_not_fetched': 0}
    paths = [p for p in sorted(root.rglob('*.md')) if '.git' not in p.parts]
    texts = {p.resolve(): p.read_text(encoding='utf-8') for p in paths}
    for path, text in texts.items():
        rel = path.relative_to(root).as_posix()
        counts['markdown_files'] += 1
        body = without_fences(text)
        if re.search(r'^(`{3,}|~{3,})', body, re.M):
            errors.append(f'{rel}: unclosed code fence')
        if '\ufffd' in text:
            errors.append(f'{rel}: Unicode replacement character')
        definitions = {key.casefold(): value for key, value in re.findall(r'^\[([^\]]+)\]:\s*<?([^\s>]+)>?', body, re.M)}
        targets = re.findall(r'!?\[[^\]\n]*\]\(<?([^\s)>]+)>?(?:\s+["\x27][^\n]*?["\x27])?\)', body)
        for label, key in re.findall(r'!?\[([^\]\n]+)\]\[([^\]\n]*)\]', body):
            key = (key or label).casefold()
            if key not in definitions:
                errors.append(f'{rel}: undefined reference {key}')
            else:
                targets.append(definitions[key])
        # These source identifiers also occur as shortcut reference links.
        for key in re.findall(r'\[((?:S|U)\d{2})\](?![:(\[])', body):
            if key.casefold() not in definitions:
                errors.append(f'{rel}: undefined source reference {key}')
            else:
                targets.append(definitions[key.casefold()])
        for target in targets:
            parts = urlsplit(target)
            if parts.scheme or parts.netloc:
                counts['external_links_not_fetched'] += 1
                continue
            counts['local_links'] += 1
            dest = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            if not dest.is_relative_to(root):
                errors.append(f'{rel}: link leaves repository: {target}')
            elif not dest.exists():
                errors.append(f'{rel}: missing target: {target}')
            elif parts.fragment and dest.suffix.lower() == '.md':
                if unquote(parts.fragment) not in anchors(texts.get(dest, dest.read_text(encoding='utf-8'))):
                    errors.append(f'{rel}: missing heading: {target}')
    return {'errors': errors, 'counts': counts, 'scope': 'local documentation only; no external-link or scientific qualification'}


def self_test() -> dict[str, bool]:
    """Mutation checks, including permission for real development to advance."""
    results: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix='atm-doc-check-') as tmp:
        root = Path(tmp)
        readme = root / 'README.md'
        target = root / 'notes.md'
        target.write_text('# Good heading\n\n## Repeated\n## Repeated\n', encoding='utf-8')
        good = '# Test\n[valid](notes.md#good-heading)\n[repeat](notes.md#repeated-1)\n'
        readme.write_text(good, encoding='utf-8')
        results['valid_links_and_duplicate_heading'] = not check(root)['errors']
        cases = {
            'broken_file_detected': good + '[bad](absent.md)\n',
            'broken_anchor_detected': good + '[bad](notes.md#absent)\n',
            'undefined_reference_detected': good + '[bad][missing]\n',
            'escape_detected': good + '[bad](../outside.md)\n',
            'unclosed_fence_detected': good + '```python\nunclosed\n',
        }
        for name, value in cases.items():
            readme.write_text(value, encoding='utf-8')
            results[name] = bool(check(root)['errors'])
        readme.write_text(good + '\n```text\n[fake](absent.md)\n```\n', encoding='utf-8')
        results['code_examples_are_not_live_links'] = not check(root)['errors']
        (root / 'src').mkdir()
        (root / 'src' / 'example.py').write_text('x = 1\n', encoding='utf-8')
        (root / 'Gate_01_v1_audit.md').write_text('# Audit\naccepted_for_scope\n', encoding='utf-8')
        (root / 'STATUS.md').write_text('# Status\nin_progress\n', encoding='utf-8')
        results['implementation_audits_and_progress_are_allowed'] = not check(root)['errors']
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = check(args.root)
    if args.self_test:
        result['self_tests'] = self_test()
        for name, passed in result['self_tests'].items():
            if not passed:
                result['errors'].append('self-test failed: ' + name)
    payload = json.dumps(result, indent=2) + '\n'
    print(payload, end='')
    if args.output:
        args.output.write_text(payload, encoding='utf-8')
    return int(bool(result['errors']))


if __name__ == '__main__':
    raise SystemExit(main())
