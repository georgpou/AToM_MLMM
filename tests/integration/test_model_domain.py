"""Save every domain sample, including diagnostic coincidences and ATM maps."""
from dataclasses import replace
import numpy as np
import pytest

from tests.integration.test_model_adapter import real_case, assert_agree, capture
from tests.model_oracle import derived_input, project
from tests.link_oracle import IDS, REFERENCE

pytestmark = pytest.mark.model_assets


def test_contact_cutoff_and_counterfactual_scans():
    from atm_mlmm.model_reference import NativeMACE
    from tests.integration.test_link_geometry import model_result
    native = NativeMACE()
    bundle, snapshot = real_case()
    original = np.array(snapshot.positions_nm)
    rows = []
    for distance in (.65, .50, .45, .40, .36, .30, .26, .20):
        r = original.copy(); r[8:] += (0., distance-.4, 0.)
        rows.append(('approach', distance, r, True))
    # Rotate around the real parent axis while moving the cap's MM parent;
    # native expected geometry and actual sites must both be recomputed.
    for angle in (-60., 0., 60., 120.):
        t = np.deg2rad(angle)
        q = np.array([[np.cos(t), -np.sin(t), 0.], [np.sin(t), np.cos(t), 0.], [0., 0., 1.]])
        r = original.copy(); r[1] = r[0] + q @ (r[1]-r[0])
        rows.append(('cap-parent-rotation', angle, r, True))
    def nearest(distance):
        r=original.copy();r[8:] += (0.,distance-.4,0.)
        _,x,_=derived_input(bundle,replace(snapshot,positions_nm=r))
        return np.min(np.linalg.norm(x[:5,None,:]-x[None,5:,:],axis=2))
    low, high = .4, .9
    for _ in range(60):
        mid=(low+high)/2
        if nearest(mid)<.45:low=mid
        else:high=mid
    crossing=(low+high)/2
    for delta in (-1e-4, -1e-6, 1e-6, 1e-4):
        r=original.copy();r[8:] += (0.,crossing+delta-.4,0.)
        rows.append(('last-intercomponent-edge-crossing', delta, r, True))
    for offset in ((0.,2.,0.), (0.,-.4,0.)):
        r=original.copy();r[8:]+=offset
        rows.append(('separated' if offset[1]>0 else 'extreme-coincident-diagnostic', offset[1], r, offset[1]>0))
    records=[]
    for kind, parameter, r, admitted in rows:
        for mapping in (0,1):
            mapped=r.copy()
            if mapping:mapped[8:]+=(.3,.1,-.2)
            frame=replace(snapshot,positions_nm=mapped)
            n,x,jac=derived_input(bundle,frame)
            try:
                out=native.evaluate(n,x)
                energy,forces,final=model_result(bundle,frame)
                record={'kind':kind,'parameter':parameter,'map':mapping,'admitted':admitted,
                        'real_positions_nm':mapped.tolist(),'native':out,'adapter_energy':energy,
                        'adapter_real_forces':forces.tolist(),'final_positions_nm':final.tolist(),
                        'max_real_force_kj_mol_nm':float(np.max(np.linalg.norm(forces,axis=1))),
                        'projected_forces':project(out['forces_kj_mol_nm'],jac).tolist()}
            except Exception as error:
                record={'kind':kind,'parameter':parameter,'map':mapping,'admitted':admitted,
                        'real_positions_nm':mapped.tolist(),'exception':repr(error)}
            records.append(record)
    # Preserve nonfinite samples as explicit strings, never drop the sample.
    def finite_json(value):
        if isinstance(value,float) and not np.isfinite(value):return str(value)
        if isinstance(value,dict):return {k:finite_json(v) for k,v in value.items()}
        if isinstance(value,(list,tuple)):return [finite_json(v) for v in value]
        return value
    capture('domain-scans',finite_json({'raw_records':records,'extremes_are_diagnostic_only':True}))
    for record in records:
        if record['admitted']:
            assert 'exception' not in record,record
            assert record['native']['finite'],record
            assert_agree(record['adapter_energy'], record['adapter_real_forces'],
                         record['native']['energy_kj_mol'], record['projected_forces'])
    # Compressing the contacting CH4 pair to 3.0 A must cost ML energy and
    # produce an outward ligand force; no retained-MM repulsion can mask it.
    approach={r['parameter']:r for r in records if r['kind']=='approach' and r['map']==0}
    assert approach[.30]['native']['energy_kj_mol'] > approach[.40]['native']['energy_kj_mol']
    assert sum(f[1] for f in approach[.30]['projected_forces'][8:]) > 0.
    edges={r['parameter']:r for r in records if r['kind']=='last-intercomponent-edge-crossing' and r['map']==0}
    assert any((i<5)!=(j<5) for i,j in edges[-1e-6]['native']['directed_edges'])
    assert not any((i<5)!=(j<5) for i,j in edges[1e-6]['native']['directed_edges'])
    assert abs(edges[-1e-6]['native']['energy_kj_mol']-edges[1e-6]['native']['energy_kj_mol'])<=1e-4
    np.testing.assert_allclose(edges[-1e-6]['native']['forces_kj_mol_nm'],
                               edges[1e-6]['native']['forces_kj_mol_nm'],atol=5e-3,rtol=0)
