"""G06-02: four masks, independent Ewald and LJ checks, fixed mesh/scaling."""
import copy
import numpy as np
import openmm as mm
from openmm import unit
import pytest
from tests.periodic_oracle import BOX, CAVITY, LIGAND, periodic_input, ewald_energy, direct_lj_cross


def nb_only():
    original, _, snapshot = periodic_input()
    source = mm.XmlSerializer.deserialize(original.prepared_mm_artifact)
    system = mm.System()
    for _ in range(13): system.addParticle(12.)
    system.setDefaultPeriodicBoxVectors(*BOX)
    nb = next(f for f in source.getForces() if isinstance(f, mm.NonbondedForce))
    system.addForce(copy.deepcopy(nb))
    return system, snapshot


def test_pme_charge_mask_cross_identity():
    from atm_mlmm.ledger import charge_mask_diagnostic
    system, snapshot = nb_only()
    nb = system.getForce(0)
    report = charge_mask_diagnostic(system, snapshot.positions_nm, BOX, CAVITY, LIGAND)
    assert report['realized_pme'] == (4.4, 64, 64, 64)
    assert report['background_convention'] == 'openmm-uniform-neutralizing-background'
    q = np.array([p[0].value_in_unit(unit.elementary_charge) for p in
                  (nb.getParticleParameters(i) for i in range(13))])
    oracle = {}
    for name, selected in (('union', CAVITY+LIGAND), ('cavity', CAVITY), ('ligand', LIGAND), ('empty', ())):
        charges = np.zeros(13); charges[list(selected)] = q[list(selected)]
        expected = ewald_energy(charges, snapshot.positions_nm, BOX, 4.4)
        # Original exceptions replace only the zero-image Coulomb interaction.
        for i in range(nb.getNumExceptions()):
            a, b, product, _, _ = nb.getExceptionParameters(i)
            r = np.linalg.norm(np.array(snapshot.positions_nm)[b]-snapshot.positions_nm[a])
            qp = product.value_in_unit(unit.elementary_charge**2) if a in selected and b in selected else 0.
            from tests.periodic_oracle import COULOMB
            expected += COULOMB * (qp - charges[a]*charges[b]) / r
        oracle[name] = expected
        assert abs(report['energies_kj_mol'][name] - expected) <= 1e-4, (name, report, expected)
    cross = oracle['union']-oracle['cavity']-oracle['ligand']+oracle['empty']
    assert abs(report['cross_kj_mol']-cross) <= 1e-4
    # A missing background changes a nonneutral cross contribution substantially.
    correction = -138.93545764438198*np.pi*q[list(CAVITY)].sum()*q[list(LIGAND)].sum()/(4.4**2*np.linalg.det(BOX))
    assert abs(correction) > .001
    scaled = charge_mask_diagnostic(system, snapshot.positions_nm, BOX, CAVITY, LIGAND, scale=-1.7)
    assert abs(scaled['cross_kj_mol']-1.7**2*report['cross_kj_mol']) <= 1e-7
    assert mm.XmlSerializer.serialize(system) == mm.XmlSerializer.serialize(nb_only()[0])


def test_lj_mask_cross_and_switching():
    from atm_mlmm.ledger import lj_mask_diagnostic
    system, snapshot = nb_only()
    for displacement in (0., .35, .48, .6):
        x = np.array(snapshot.positions_nm); x[list(LIGAND)] += (0., displacement, 0.)
        report = lj_mask_diagnostic(system, x, BOX, CAVITY, LIGAND)
        assert abs(report['cross_kj_mol']-direct_lj_cross(system.getForce(0), x, CAVITY, LIGAND)) <= 1e-4


@pytest.mark.parametrize('sets', (((0, 0), (8,)), ((0,), (0,)), ((-1,), (8,)), ((13,), (8,))))
def test_invalid_mask_sets_reject(sets):
    from atm_mlmm.ledger import charge_mask_diagnostic
    from atm_mlmm.schema import IdentityError
    system, snapshot = nb_only()
    with pytest.raises(IdentityError):
        charge_mask_diagnostic(system, snapshot.positions_nm, BOX, *sets)
