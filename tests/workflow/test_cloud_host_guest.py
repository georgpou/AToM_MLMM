"""Tiny neutral all-ML vacuum fixture for common-engine execution checks."""
from pathlib import Path
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT/'fixtures/cloud_host_guest/v2'


def test_frozen_host_guest_chemistry_and_maps():
    from atm_mlmm.schema import from_json
    from atm_mlmm.partition import resolve_partition
    manifest = json.loads((FIXTURE/'manifest.json').read_text())
    for name, digest in manifest['files'].items():
        assert hashlib.sha256((FIXTURE/name).read_bytes()).hexdigest() == digest
    original = from_json((FIXTURE/'system-input.json').read_text())
    spec = from_json((FIXTURE/'partition.json').read_text())
    snapshot = from_json((FIXTURE/'snapshot.json').read_text())
    assert len(original.topology.atoms) == 48
    assert [(m.role,len(m.atom_ids),m.formal_charge,m.multiplicity) for m in original.topology.molecules] == [('host',42,0,1),('ligand',6,0,1)]
    assert {a.element for a in original.topology.atoms} == {'C','H','O'}
    partition = resolve_partition(original.topology,spec)
    assert set(partition.ml_ids) == set(snapshot.real_atom_ids)
    assert partition.boundary_edges == () and partition.protein_ml_ids == ()
    x = np.array(snapshot.positions_nm)
    assert np.isfinite(x).all() and snapshot.box_nm is None
    assert manifest['physical_scope'] == 'all-ML vacuum; no MM or binding-accuracy qualification'


def test_cloud_host_guest_actual_model_native_energy_and_forces(tmp_path):
    from dataclasses import replace
    import pytest
    from atm_mlmm.schema import (EmbeddingSpec, MobileGroup, RestraintSpec,
                                 RuntimeSpec, from_json)
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.models.mace import model_spec
    from atm_mlmm.atm import PhysicalEvaluator, AtmEvaluator, build_atm
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.protocols.abfe import make_protocol
    from atm_mlmm.schedule import production_schedule
    from tests.analytic_oracle import production_parameters
    original = from_json((FIXTURE/'system-input.json').read_text())
    spec = from_json((FIXTURE/'partition.json').read_text())
    snapshot = from_json((FIXTURE/'snapshot.json').read_text())
    physical = build_physical(original,resolve_partition(original.topology,spec),model_spec(),
                              EmbeddingSpec('mechanical','1','protein_c_c','nonperiodic'),cap_distance_nm=.109)
    guest = original.topology.molecules[1]
    transfer = resolve_protocol(physical,make_protocol((MobileGroup('guest',guest.atom_ids,('ligand',),guest.molecule_id),),(2.4,0.,0.)))
    schedule = production_schedule(tuple((name,production_parameters(Lambda1=lam,Lambda2=lam,Umax=10000.,Ubcore=500.,Acore=0.,W0=0.,UOffset=0.))
                                         for name,lam in (('contact',0.),('middle',.5),('separated',1.))))
    restraints = RestraintSpec('anchor',('h000',),10.,tuple(snapshot.positions_nm[0]))
    bundle = build_atm(physical,transfer,schedule,restraints)
    runtime = RuntimeSpec('Reference','double',(),.0005,300.,'NVT','LangevinMiddle')
    mapped = np.array(snapshot.positions_nm)
    for a in guest.atom_ids:
        mapped[snapshot.real_atom_ids.index(a)] += (2.4,0.,0.)
    with PhysicalEvaluator(physical,runtime) as direct:
        answers = [direct.evaluate(snapshot),direct.evaluate(replace(snapshot,positions_nm=mapped))]
    (tmp_path/'host-single-points.json').write_text(json.dumps({'energies_kj_mol':[a.energy_kj_mol for a in answers],
        'forces_kj_mol_nm':[a.forces_kj_mol_nm for a in answers],
        'physical_identity':physical.content_identity,'all_real_atoms':48,'model_asset':model_spec().asset_digest}))
    with AtmEvaluator(bundle,runtime) as native:
        for state in schedule.states:
            result = native.evaluate(snapshot,state.state_id)
            lam = state.parameters['Lambda1']
            assert result.raw.u0_raw_kJ_mol == pytest.approx(answers[0].energy_kj_mol,abs=1.e-6)
            assert result.raw.u1_raw_kJ_mol == pytest.approx(answers[1].energy_kj_mol,abs=1.e-6)
            assert result.total.energy_kj_mol == pytest.approx((1-lam)*answers[0].energy_kj_mol+lam*answers[1].energy_kj_mol,abs=1.e-6)
            expected=(1-lam)*np.array(answers[0].forces_kj_mol_nm)+lam*np.array(answers[1].forces_kj_mol_nm)
            assert np.allclose(result.total.forces_kj_mol_nm,expected,rtol=1.e-6,atol=1.e-6)
            assert result.total.real_atom_ids == snapshot.real_atom_ids
            assert np.isfinite(result.total.forces_kj_mol_nm).all()
