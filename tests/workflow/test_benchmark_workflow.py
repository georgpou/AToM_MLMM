"""Benchmark input/stage admission stays independent of model weights and GPUs."""
import importlib.util
import json
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'benchmarks/fkbp/benchmark.json'


def test_benchmark_workflow_is_available():
    assert importlib.util.find_spec('atm_mlmm.benchmark_workflow') is not None, \
        'the reproducible AToM benchmark workflow is missing'


def test_selected_ligands_are_complete_neutral_and_hash_bound(tmp_path):
    from atm_mlmm.benchmark_workflow import load_benchmark, plan_jobs
    data = load_benchmark(INPUT)
    assert [(l['id'], l['atom_count']) for l in data['ligands']] == [
        ('but', 14), ('prp', 11), ('dap', 27)]
    assert all(l['formal_charge'] == 0 and l['multiplicity'] == 1 for l in data['ligands'])
    jobs = plan_jobs(INPUT, tmp_path / 'runs', mode='cavity')
    assert [job['ligand_id'] for job in jobs] == ['but', 'prp', 'dap']
    assert all(job['mode'] == 'cavity' for job in jobs)
    assert not (tmp_path / 'runs').exists()


def test_tampered_source_is_rejected_before_a_run_directory_exists(tmp_path):
    from atm_mlmm.benchmark_workflow import load_benchmark
    copied = tmp_path / 'benchmark'
    shutil.copytree(INPUT.parent, copied)
    ligand = copied / 'inputs/ligands/but.sdf'
    ligand.write_text(ligand.read_text().replace('32.0260', '33.0260'))
    with pytest.raises(ValueError, match='SHA-256'):
        load_benchmark(copied / 'benchmark.json')


@pytest.mark.parametrize('change', ['charge', 'escape', 'unknown_mode'])
def test_unsupported_inputs_fail_early(tmp_path, change):
    from atm_mlmm.benchmark_workflow import load_benchmark, plan_jobs
    copied = tmp_path / 'benchmark'
    shutil.copytree(INPUT.parent, copied)
    path = copied / 'benchmark.json'
    data = json.loads(path.read_text())
    if change == 'charge':
        data['ligands'][0]['formal_charge'] = 1
    elif change == 'escape':
        data['ligands'][0]['path'] = '../outside.sdf'
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        if change == 'unknown_mode':
            plan_jobs(path, tmp_path / 'runs', mode='unknown')
        else:
            load_benchmark(path)


def test_production_requires_verified_preparation(tmp_path):
    from atm_mlmm.benchmark_workflow import run_stage
    with pytest.raises(ValueError, match='setup'):
        run_stage(INPUT, tmp_path / 'runs', 'but', 'cavity', 'run')
    assert not (tmp_path / 'runs').exists()


@pytest.mark.parametrize('mutation', ['unsafe_target', 'internal_symlink'])
def test_job_paths_and_input_aliases_are_rejected(tmp_path, mutation):
    from atm_mlmm.benchmark_workflow import plan_jobs
    copied = tmp_path / 'benchmark'
    shutil.copytree(INPUT.parent, copied)
    path = copied / 'benchmark.json'
    if mutation == 'unsafe_target':
        data = json.loads(path.read_text())
        data['target_id'] = '../../other-directory'
        path.write_text(json.dumps(data))
    else:
        ligand = copied / 'inputs/ligands/but.sdf'
        ligand.rename(ligand.with_name('alias.sdf'))
        ligand.symlink_to('alias.sdf')
    with pytest.raises(ValueError):
        plan_jobs(path, tmp_path / 'runs')
    assert not (tmp_path / 'runs').exists()


def test_missing_nodefile_can_be_corrected_without_poisoning_the_job(tmp_path, monkeypatch):
    import sys
    from types import SimpleNamespace
    from atm_mlmm.benchmark_workflow import run_stage
    calls = []
    def setup(manifest, directory, job, **kwargs):
        (directory / 'options.json').write_text('{}')
    def prepare(directory):
        (directory / 'fkbp12-but-mm_0.xml').write_text('synthetic state')
    def produce(directory, nodefile):
        calls.append(nodefile)
    monkeypatch.setitem(sys.modules, 'atm_mlmm.adapters.atom', SimpleNamespace(
        setup_benchmark_job=setup, prepare_benchmark_job=prepare, produce_benchmark_job=produce,
        validate_benchmark_nodefile=lambda p: None))
    output = tmp_path / 'runs'
    run_stage(INPUT, output, 'but', 'mm', 'setup')
    run_stage(INPUT, output, 'but', 'mm', 'prepare')
    with pytest.raises(ValueError, match='nodefile'):
        run_stage(INPUT, output, 'but', 'mm', 'run')
    directory = output / 'fkbp12-but-mm'
    assert not (directory / 'failure-run.json').exists()
    nodefile = tmp_path / 'nodes'
    nodefile.write_text('synthetic allocation')
    run_stage(INPUT, output, 'but', 'mm', 'run', nodefile=nodefile)
    assert calls == [nodefile]


def test_interrupted_preparation_cannot_overwrite_partial_outputs(tmp_path, monkeypatch):
    import sys
    from types import SimpleNamespace
    from atm_mlmm.benchmark_workflow import run_stage
    calls = []
    def setup(manifest, directory, job, **kwargs):
        (directory / 'options.json').write_text('{}')
    def prepare(directory):
        calls.append(directory)
        (directory / 'partial.xml').write_text('preserve interrupted preparation')
        raise KeyboardInterrupt('interruption probe')
    monkeypatch.setitem(sys.modules, 'atm_mlmm.adapters.atom', SimpleNamespace(
        setup_benchmark_job=setup, prepare_benchmark_job=prepare))
    output = tmp_path / 'runs'
    run_stage(INPUT, output, 'but', 'mm', 'setup')
    with pytest.raises(KeyboardInterrupt):
        run_stage(INPUT, output, 'but', 'mm', 'prepare')
    with pytest.raises(ValueError, match='fresh setup'):
        run_stage(INPUT, output, 'but', 'mm', 'prepare')
    assert len(calls) == 1
    assert (output / 'fkbp12-but-mm/partial.xml').read_text() == 'preserve interrupted preparation'
