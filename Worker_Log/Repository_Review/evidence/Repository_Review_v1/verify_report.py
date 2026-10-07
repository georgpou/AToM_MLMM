"""One report-only coverage, whitespace and frozen-input check."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

root = Path.cwd()
evidence = Path(__file__).resolve().parent
inventory = json.loads((evidence / 'inventory.json').read_text())
frozen = json.loads((evidence / 'frozen-input-sha256.json').read_text())
changed = [name for name, digest in frozen.items()
           if not (root / name).is_file() or hashlib.sha256((root / name).read_bytes()).hexdigest() != digest]
canonical = json.loads((evidence / 'provenance.json').read_text())['canonical_read_evidence_sha256']
historical_changed = [name for name, digest in canonical.items()
                      if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest]
coverage = (evidence / 'coverage.md').read_text()
module_table = coverage.split('## Every source module')[1].split('## Gate and milestone claims')[0]
names = re.findall(r'^\| `([^`]+\.py)` \|', module_table, re.M)
expected = [x['path'].removeprefix('src/atm_mlmm/') for x in inventory['source_modules']]
assert len(names) == len(set(names)) == 38 and set(names) == set(expected)
gate_table = coverage.split('## Gate and milestone claims')[1].split('## Fixtures, public entry points')[0]
gates = re.findall(r'^\| (G\d\d) \|', gate_table, re.M)
assert gates == [f'G{i:02d}' for i in range(14)]
report = evidence.parents[1] / 'Repository_Review_v1_audit.md'
line_count = len(report.read_text().splitlines())
assert line_count <= 100
assert not changed and not historical_changed
assert subprocess.check_output(['git', 'diff', '--name-only'], text=True) == ''
untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], text=True).splitlines()
assert untracked and all(name.startswith('Worker_Log/Repository_Review/') for name in untracked)
subprocess.run(['git', 'diff', '--check'], check=True)
whitespace = []
own_text = [report, *(p for p in evidence.iterdir() if p.suffix in ('.md', '.py', '.json'))]
for path in own_text:
    data = path.read_text()
    if not data.endswith('\n') or '\r' in data:
        whitespace.append(str(path))
    for index, line in enumerate(data.splitlines(), 1):
        if line.rstrip(' \t') != line:
            whitespace.append(f'{path}:{index}')
assert not whitespace, whitespace
result = {'frozen_files_verified': len(frozen), 'historical_evidence_verified': len(canonical),
          'changed_frozen_files': changed, 'changed_historical_files': historical_changed,
          'coverage_modules': len(names), 'coverage_gates': len(gates), 'main_report_lines': line_count,
          'tracked_changes': [], 'untracked_report_only_files': len(untracked),
          'whitespace_errors': whitespace, 'git_diff_check_exit': 0, 'source_head_unchanged':
          subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()}
print(json.dumps(result, indent=2))
