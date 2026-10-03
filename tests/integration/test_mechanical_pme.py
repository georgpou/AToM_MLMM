"""G06-01/06: actual mechanical builder, retained MM and early rejections."""
from dataclasses import replace
import hashlib
import numpy as np
import openmm as mm
from openmm import unit
import pytest
from tests.periodic_oracle import (BOX, CAVITY, ENVIRONMENT, LIGAND,
    periodic_case, periodic_input, plain_periodic, direct_lj_cross)


def test_periodic_builder_admits_standard_pme():
    bundle, snapshot = periodic_case()
    assert bundle.manifest['periodicity'] == 'orthorhombic-pme-v1'
    assert bundle.manifest['boundary_terms']


def test_ml_mm_cross_interactions_retained():
    from atm_mlmm.atm import PhysicalEvaluator
    from atm_mlmm.ledger import charge_mask_diagnostic, lj_mask_diagnostic
    from tests.link_oracle import REFERENCE
    bundle, snapshot = periodic_case()
    original = mm.XmlSerializer.deserialize(bundle.manifest['original_mm_xml'])
    retained = mm.XmlSerializer.deserialize(bundle.manifest['retained_mm_xml'])
    before = next(f for f in original.getForces() if isinstance(f, mm.NonbondedForce))
    after = next(f for f in retained.getForces() if isinstance(f, mm.NonbondedForce))
    assert after.getNumParticles() == 14
    assert all(after.getParticleParameters(i) == before.getParticleParameters(i) for i in range(13))
    assert after.getParticleParameters(13)[0].value_in_unit(unit.elementary_charge) == 0.
    assert after.getParticleParameters(13)[2].value_in_unit(unit.kilojoule_per_mole) == 0.
    assert after.getExceptionsUsePeriodicBoundaryConditions()
    rows = bundle.manifest['boundary_terms']
    assert any(r['disposition'] == 'replaced_by_exclusion' for r in rows)
    assert sum(r['disposition'] == 'added_inert_cap' for r in rows) == 1
    assert sum(r['disposition'] == 'changed_periodic_exception_convention' for r in rows) == 1
    x = np.vstack([snapshot.positions_nm, [0., 0., 0.]])
    with PhysicalEvaluator(bundle, REFERENCE) as evaluator:
        for shift in ((0., 0., 0.), (.017, -.012, .021)):
            moved = x.copy(); moved[ENVIRONMENT[1]] += shift
            expected = plain_periodic(retained, moved)[0]
            actual = evaluator.evaluate(replace(snapshot, positions_nm=moved[:13]))
            assert abs(actual.energy_kj_mol - expected) <= 1e-4
            for diagnostic in (charge_mask_diagnostic, lj_mask_diagnostic):
                keep = diagnostic(retained, moved, BOX, CAVITY+LIGAND, ENVIRONMENT)
                full = diagnostic(original, moved[:13], BOX, CAVITY+LIGAND, ENVIRONMENT)
                assert abs(keep['cross_kj_mol'] - full['cross_kj_mol']) <= 1e-4
            lj = lj_mask_diagnostic(retained, moved, BOX, CAVITY+LIGAND, ENVIRONMENT)
            assert abs(lj['cross_kj_mol'] - direct_lj_cross(after, moved, CAVITY+LIGAND, ENVIRONMENT)) <= 1e-4
            assert abs(lj['cross_kj_mol']) > .001
    # Excluded ML pairs still have a periodic electrostatic image contribution.
    images = charge_mask_diagnostic(retained, x, BOX, CAVITY, LIGAND)
    assert abs(images['cross_kj_mol']) > .001


@pytest.mark.parametrize('fault', ('offset', 'exception-offset', 'ljpme', 'custom', 'triclinic', 'dispersion', 'two-nb'))
def test_nonstandard_forces_and_box_rejected(fault):
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.models.analytic_boundary import BoundaryProbe
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.schema import EmbeddingSpec, ModelSpec, UnsupportedCapability
    original, spec, _ = periodic_input()
    system = mm.XmlSerializer.deserialize(original.prepared_mm_artifact)
    nb = next(f for f in system.getForces() if isinstance(f, mm.NonbondedForce))
    box = BOX
    if fault == 'offset':
        nb.addGlobalParameter('qshift', 0.); nb.addParticleParameterOffset('qshift', 0, 1., 0., 0.)
    elif fault == 'exception-offset':
        nb.addGlobalParameter('qshift', 0.); nb.addExceptionParameterOffset('qshift', 0, 1., 0., 0.)
    elif fault == 'ljpme': nb.setNonbondedMethod(mm.NonbondedForce.LJPME)
    elif fault == 'custom': system.addForce(mm.CustomNonbondedForce('0'))
    elif fault == 'triclinic':
        box = ((3.2, 0., 0.), (.2, 3.4, 0.), (0., 0., 3.6)); system.setDefaultPeriodicBoxVectors(*box)
    elif fault == 'dispersion': nb.setUseDispersionCorrection(True)
    else: system.addForce(mm.NonbondedForce())
    xml = mm.XmlSerializer.serialize(system)
    original = replace(original, prepared_mm_artifact=xml,
                       prepared_mm_sha256=hashlib.sha256(xml.encode()).hexdigest(), box_nm=box)
    with pytest.raises(UnsupportedCapability):
        build_physical(original, resolve_partition(original.topology, spec),
            ModelSpec('analytic-local', None, 'declared_relative_energy', ('H','C'), 'neutral_singlet','local','float64'),
            EmbeddingSpec('mechanical','1','protein_c_c','orthorhombic-pme-v1'),
            probe=BoundaryProbe(cap_k=0.,ligand_k=0.), cap_distance_nm=.117)
