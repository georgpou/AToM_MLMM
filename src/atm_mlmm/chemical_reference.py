"""Frozen quantum data integrity and explicit chemical metrics; no quantum runtime."""
import hashlib
import json
from pathlib import Path
import numpy as np

from .schema import IdentityError


def relative_errors(model, reference, baseline):
    model=np.asarray(model,dtype=float);reference=np.asarray(reference,dtype=float)
    if model.shape!=reference.shape or model.ndim!=1 or not np.isfinite([model,reference]).all():
        raise IdentityError('relative energies require finite compatible compositions/family arrays')
    return (model-model[baseline])-(reference-reference[baseline])


def force_metrics(model, reference):
    model=np.asarray(model,dtype=float);reference=np.asarray(reference,dtype=float)
    if model.shape!=reference.shape or model.ndim!=2 or model.shape[1]!=3 or not len(model):
        raise IdentityError('force metrics require matching nonempty Cartesian arrays')
    error=model-reference
    if not np.isfinite(error).all():
        raise IdentityError('force metrics require finite Cartesian arrays')
    return float(np.sqrt(np.mean(error**2))),float(np.max(np.linalg.norm(error,axis=1)))


def load_references(root):
    """Missing/failed data raise before a learned-model comparison can run."""
    root=Path(root)
    try:
        inputs=json.loads((root/'input-manifest.json').read_text())
        manifest=json.loads((root/'quantum/manifest.json').read_text())
        settings=json.loads((root/'reference-settings.json').read_text())
    except (OSError,ValueError) as exc:
        raise IdentityError('reviewed quantum reference data are absent or malformed; G05-T4 pending') from exc
    approval=manifest.get('approval',{})
    if (manifest.get('ready_for_comparison') is not True or approval.get('user_agreed') is not True
            or approval.get('design_verdict')!='accepted_for_scope' or approval.get('reviewer_model')!='gpt-6-astra'
            or approval.get('reasoning_effort')!='high' or approval.get('fresh_context') is not True):
        raise IdentityError('quantum references lack complete reviewed/agreed generation provenance')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    if (sha(root/'input-manifest.json')!=manifest.get('input_manifest_sha256')
            or sha(root/'reference-settings.json')!=manifest.get('reference_settings_sha256')):
        raise IdentityError('quantum reference plan/settings identity differs')
    for name,expected in inputs['files'].items():
        if sha(root/name)!=expected:raise IdentityError('changed quantum reference input: '+name)
    records={}
    for name,expected in manifest['files'].items():
        path=(root/'quantum'/name).resolve()
        if not path.is_relative_to((root/'quantum').resolve()) or sha(path)!=expected:
            raise IdentityError('quantum reference record digest/path differs')
        data=json.loads(path.read_text())
        if data.get('status')!='computed' or data.get('network_denied') is not True:
            raise IdentityError('failed or unauditable quantum reference attempt')
        key=path.stem
        source_key=key.removesuffix('-fine-grid')
        source=(root/'structures'/(source_key+'.json'))
        if not source.exists():source=root/'quadrature_controls'/(source_key+'.json')
        if sha(source)!=data.get('source_input_sha256'):
            raise IdentityError('quantum reference geometry identity differs')
        geometry=json.loads(source.read_text())
        if (data['positions_angstrom']!=geometry['positions_angstrom'] or data['atomic_numbers']!=geometry['atomic_numbers']
                or data['formal_charge']!=0 or data['multiplicity']!=1
                or data['method']!='wb97m-d3bj/def2-tzvppd' or data['psi4_version']!='1.10.2'
                or data['basis_file_sha256']!=settings['basis_file_sha256']):
            raise IdentityError('quantum reference convention/structure differs')
        expected_settings=dict(settings['settings'])
        if key.endswith('-fine-grid'):expected_settings.update(settings['convergence_checks']['settings'])
        if data['settings']!=expected_settings:raise IdentityError('quantum reference convergence settings differ')
        e=float(data['energy_hartree']);g=np.asarray(data['gradient_hartree_bohr'],dtype=float)
        if not np.isfinite(e) or not np.isfinite(g).all() or g.shape!=(len(data['atomic_numbers']),3):
            raise IdentityError('nonfinite/malformed quantum reference output')
        data={**data,'energy_kj_mol':e*settings['hartree_to_kJ_mol'],
              'forces_kj_mol_nm':-g*settings['hartree_to_kJ_mol']/settings['bohr_to_nm']}
        records[key]=data
    expected={p.stem for p in (root/'structures').glob('*.json')}|{p.stem for p in (root/'quadrature_controls').glob('*.json')}
    expected|={name+'-fine-grid' for name in settings['convergence_checks']['rows']}
    if set(records)!=expected:raise IdentityError('missing or extra quantum reference rows')
    return settings,records
