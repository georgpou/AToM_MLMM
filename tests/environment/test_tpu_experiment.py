"""The TPU experiment cannot qualify a host backend or reduced precision."""
import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[2]


def api():
    assert importlib.util.find_spec('atm_mlmm.tpu_experiment'), 'actual-MACE TPU experiment is missing'
    from atm_mlmm import tpu_experiment
    return tpu_experiment


def test_tpu_admission_requires_hardware_arithmetic_and_no_fallback():
    admit=api().admit_tpu
    assert admit('TPU',True,{})
    for device,precision,fallback in [('CPU',True,{}),('TPU',False,{}),('TPU',True,{'aten::_local_scalar_dense':1})]:
        with pytest.raises(ValueError): admit(device,precision,fallback)


def test_tpu_full_real_force_comparison_uses_original_absolute_limits():
    compare=api().compare
    row={'energy_kj_mol':2.,'all_real_ml_forces':[[1.,2.,3.],[4.,5.,6.]]}
    assert compare(row,2.,np.array(row['all_real_ml_forces']))['passed']
    for e,f in [(2.001,row['all_real_ml_forces']),(2.,[[1.,2.,3.],[4.,5.,6.01]])]:
        assert not compare(row,e,np.array(f))['passed']


def test_reference_hash_validation_precedes_any_model_execution(tmp_path):
    path=tmp_path/'reference.json'; path.write_text('{}')
    with pytest.raises(ValueError,match='hash'):
        api().read_reference(path,'0'*64)


def test_separate_tpu_notebook_and_profile_are_pinned_and_clear():
    path=ROOT/'notebooks/m05_colab_tpu_benchmarks.ipynb'
    assert path.is_file(), 'separate TPU notebook is missing'
    doc=json.loads(path.read_text()); text='\n'.join(''.join(c['source']) for c in doc['cells'])
    assert doc['nbformat']==4 and doc['nbformat_minor']==5
    for c in doc['cells']:
        if c['cell_type']=='code':
            assert c['execution_count'] is None and not c['outputs']
            compile(''.join(c['source']),'<tpu-cell>','exec')
    assert 'TPU' in text and 'm05_tpu_probe.py' in text and 'SOURCE_SHA' in text
    lock=(ROOT/'environment/colab-tpu/requirements.lock').read_text()
    assert 'torch-xla==2.8.0' in lock and 'libtpu==0.0.17' in lock
    assert lock.count('--hash=sha256:')==3
    assert 'pip install --upgrade' not in text


@pytest.fixture(scope='module')
def cpu_reference(tmp_path_factory):
    directory=tmp_path_factory.mktemp('tpu-cpu-reference')/'export'
    identity=api().export_cpu_reference(directory)
    return directory,identity,api().read_reference(directory/'reference.json',identity['reference_sha256'])


@pytest.mark.model_assets
def test_actual_cpu_reference_cap_gradients_step_sweeps_and_changed_graphs(cpu_reference):
    directory,identity,reference=cpu_reference
    assert identity['rows']==108
    assert {(r['case'],r['map']) for r in reference['rows']}=={('abfe',0),('abfe',1),('rbfe',0),('rbfe',1)}
    assert len(reference['cpu_steady_timings'])==4
    assert all(len(t['synchronized_end_to_end_s'])==5 for t in reference['cpu_steady_timings'])
    changed_graph=False
    for case,mapping in [('abfe',0),('abfe',1),('rbfe',0),('rbfe',1)]:
        rows=[r for r in reference['rows'] if (r['case'],r['map'])==(case,mapping)]
        base=next(r for r in rows if r['variant']=='base')
        changed=next(r for r in rows if r['variant']=='changed')
        shape=next(r for r in rows if r['variant']=='graph-shape')
        assert not np.array_equal(base['model']['positions_nm'],changed['model']['positions_nm'])
        assert base['energy_kj_mol']!=changed['energy_kj_mol']
        changed_graph |= len(base['model']['directed_edges'])!=len(shape['model']['directed_edges'])
        forces=np.array(base['all_real_ml_forces'])
        descriptor=next(c for c in reference['cases'] if c['kind']==case)
        # Ordinary solvent is outside fixed ML membership, while both cap
        # parents receive their actual energy derivatives.
        solvent=[i for i,a in enumerate(descriptor['real_atom_ids']) if a.startswith('dense-water-')]
        np.testing.assert_array_equal(forces[solvent],0.)
        for atom in {r['fd_atom'] for r in rows if r['variant']=='fd'}:
            errors=[]
            for step in reference['fd_steps_nm']:
                values={r['sign']:r['energy_kj_mol'] for r in rows if r['variant']=='fd' and r['fd_atom']==atom and r['step_nm']==step}
                fd=-(values[1]-values[-1])/(2*step); error=abs(fd-forces[atom,1]);errors.append(error)
            assert errors[-1]<=1e-3+1e-4*abs(forces[atom,1])
            assert errors[-1]<=errors[0]+1e-4
    assert changed_graph, 'changed coordinates must exercise a new graph shape'
    with pytest.raises(FileExistsError): api().export_cpu_reference(directory)


def test_tpu_failure_retains_diagnostics_and_cannot_enter_timings(tmp_path):
    from atm_mlmm.models.mace import CHECKPOINT_SHA256
    reference=tmp_path/'reference.json'
    reference.write_text(json.dumps({'version':1,'model_sha256':CHECKPOINT_SHA256}))
    output=tmp_path/'attempt'
    assert api().run_tpu(reference,'0'*64,output)=='incompatible'
    report=json.loads((output/'report.json').read_text())
    assert 'hash' in report['error'] and not report['rows'] and 'steady_timings' not in report
    assert (output/'exception.txt').is_file()


def test_nonfinite_probe_values_are_preserved_as_inert_failure_evidence(tmp_path):
    path=tmp_path/'report.json'
    api()._save(path,{'energy':float('nan'),'force':[float('inf'),-float('inf')],'status':'incompatible'})
    report=json.loads(path.read_text())
    assert report['energy']=={'nonfinite':'nan'}
    assert report['force']==[{'nonfinite':'inf'},{'nonfinite':'-inf'}]
