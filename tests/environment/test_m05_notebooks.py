"""Notebook orchestration is executable and propagates command failures."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]


def cpu_notebook():
    path = ROOT/'notebooks/m05_colab_cpu.ipynb'
    assert path.is_file(), 'CPU Colab notebook is missing'
    return json.loads(path.read_text())


def test_cpu_notebook_schema_and_immutable_visible_baseline():
    notebook = cpu_notebook()
    assert notebook['nbformat'] == 4 and notebook['nbformat_minor'] == 5
    assert isinstance(notebook['metadata'],dict) and isinstance(notebook['cells'],list)
    assert len({c['id'] for c in notebook['cells']}) == len(notebook['cells'])
    for c in notebook['cells']:
        assert c['cell_type'] in ('markdown','code')
        assert isinstance(c['metadata'],dict) and isinstance(c['source'],(str,list))
    cells = '\n'.join(''.join(c['source']) for c in notebook['cells'])
    assert '7b41213e87bfcc3ce76def7ffb64565110bbafec' in cells
    assert '165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f' in cells
    assert 'Runtime' in cells and 'no accelerator' in cells
    assert 'environment/cloud-cpu/install.sh' in cells and '--trusted' in cells
    assert 'git checkout main' not in cells and 'pip install --upgrade' not in cells
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            assert cell['execution_count'] is None and cell['outputs'] == []
            compile(''.join(cell['source']), '<colab-cell>', 'exec')


def test_cpu_launcher_retains_nonzero_log_and_stops(tmp_path):
    notebook = cpu_notebook()
    helper = next(c for c in notebook['cells'] if c.get('id') == 'command-runner')
    namespace = {'REPO':tmp_path, 'EVIDENCE':tmp_path/'evidence'}
    exec(''.join(helper['source']), namespace)
    with pytest.raises(subprocess.CalledProcessError) as error:
        namespace['run_command']([sys.executable,'-c','print("preserved failure"); raise SystemExit(7)'], 'failed', 10)
    assert error.value.returncode == 7
    assert 'preserved failure' in (tmp_path/'evidence/failed.log').read_text()
    status = json.loads((tmp_path/'evidence/failed-command.json').read_text())
    assert status['exit_code'] == 7


def test_cpu_launcher_timeout_preserves_result(tmp_path):
    helper = next(c for c in cpu_notebook()['cells'] if c.get('id') == 'command-runner')
    namespace = {'REPO':tmp_path, 'EVIDENCE':tmp_path/'evidence'}
    exec(''.join(helper['source']), namespace)
    with pytest.raises(subprocess.TimeoutExpired):
        namespace['run_command']([sys.executable,'-c','import time; print("started",flush=True); time.sleep(2)'], 'bounded', .1)
    status = json.loads((tmp_path/'evidence/bounded-command.json').read_text())
    assert status['timed_out'] and status['exit_code'] != 0
