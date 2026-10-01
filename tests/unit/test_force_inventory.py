import hashlib
import json
from pathlib import Path
import pytest

FIXTURE = Path(__file__).resolve().parents[2] / 'fixtures/contracts/original-mm.xml'


def build_original():
    import openmm as mm
    system = mm.System()
    for mass in (12.01, 1.02, 14.03, 16.04):
        system.addParticle(mass)
    system.addConstraint(0, 1, 0.109)
    system.setDefaultPeriodicBoxVectors(mm.Vec3(2.1, 0, 0), mm.Vec3(0, 2.2, 0), mm.Vec3(0, 0, 2.3))
    bonds = mm.HarmonicBondForce()
    bonds.setName('distinct-bonds'); bonds.setForceGroup(3)
    bonds.addBond(0, 1, 0.123, 456.0); bonds.addBond(1, 2, 0.234, 789.0)
    bonds.setUsesPeriodicBoundaryConditions(True)
    system.addForce(bonds)
    angles = mm.HarmonicAngleForce()
    angles.addAngle(0, 1, 2, 1.234, 2.345)
    system.addForce(angles)
    torsions = mm.PeriodicTorsionForce()
    torsions.addTorsion(0, 1, 2, 3, 3, 0.456, 5.678)
    system.addForce(torsions)
    rb = mm.RBTorsionForce()
    rb.addTorsion(0, 1, 2, 3, 1.1, 1.4, 1.7, 2.0, 2.3, 2.6)
    system.addForce(rb)
    nb = mm.NonbondedForce()
    nb.setName('distinct-nonbonded'); nb.setForceGroup(5)
    nb.setNonbondedMethod(mm.NonbondedForce.PME)
    nb.setCutoffDistance(0.9); nb.setUseSwitchingFunction(True); nb.setSwitchingDistance(0.65)
    nb.setUseDispersionCorrection(False); nb.setEwaldErrorTolerance(1e-5)
    nb.setReactionFieldDielectric(45.5); nb.setReciprocalSpaceForceGroup(6)
    nb.setExceptionsUsePeriodicBoundaryConditions(True)
    nb.setPMEParameters(3.2, 12, 14, 16)
    nb.setLJPMEParameters(3.3, 18, 20, 22)
    for q, sigma, epsilon in ((0.11, 0.21, 0.31), (-0.22, 0.22, 0.32), (0.33, 0.23, 0.33), (-0.22, 0.24, 0.34)):
        nb.addParticle(q, sigma, epsilon)
    nb.addException(0, 3, -0.045, 0.246, 0.357)
    nb.addGlobalParameter('scale', 0.4)
    nb.addParticleParameterOffset('scale', 1, 0.012, 0.003, 0.004)
    nb.addExceptionParameterOffset('scale', 0, 0.015, 0.005, 0.006)
    system.addForce(nb)
    cm = mm.CMMotionRemover(7)
    system.addForce(cm)
    return system


def test_original_mm_inventory_and_unknown_force():
    import openmm as mm
    from atm_mlmm.ledger import inventory_system
    from atm_mlmm.schema import UnsupportedCapability, from_json, to_json
    # The immutable XML is generated once from this hand-written independent input.
    xml = FIXTURE.read_text()
    assert mm.XmlSerializer.serialize(build_original()) == xml
    system = mm.XmlSerializer.deserialize(xml)
    before = mm.XmlSerializer.serialize(system)
    record = inventory_system(system)
    assert mm.XmlSerializer.serialize(system) == before
    assert record.artifact_sha256 == hashlib.sha256(xml.encode()).hexdigest()
    assert record.particle_masses_da == (12.01, 1.02, 14.03, 16.04)
    assert record.constraints == ((0, 1, 0.109),)
    assert record.box_vectors_nm == ((2.1, 0, 0), (0, 2.2, 0), (0, 0, 2.3))
    assert record.virtual_sites == {}
    assert [f.class_name for f in record.forces] == ['HarmonicBondForce', 'HarmonicAngleForce', 'PeriodicTorsionForce', 'RBTorsionForce', 'NonbondedForce', 'CMMotionRemover']
    assert record.forces[0].name == 'distinct-bonds'
    assert record.forces[0].force_group == 3
    assert record.forces[0].uses_periodic is True
    assert record.forces[0].parameters['terms'] == ((0, 1, 0.123, 456), (1, 2, 0.234, 789))
    assert record.forces[1].parameters['terms'] == ((0, 1, 2, 1.234, 2.345),)
    assert record.forces[2].parameters['terms'] == ((0, 1, 2, 3, 3, 0.456, 5.678),)
    assert record.forces[3].parameters['terms'] == ((0, 1, 2, 3, 1.1, 1.4, 1.7, 2.0, 2.3, 2.6),)
    nb = record.forces[4]
    assert nb.name == 'distinct-nonbonded' and nb.force_group == 5
    assert nb.parameters == {
        'method': 4, 'cutoff_nm': 0.9, 'switching': True, 'switching_distance_nm': 0.65,
        'dispersion_correction': False, 'ewald_tolerance': 1e-5, 'reaction_field_dielectric': 45.5,
        'reciprocal_force_group': 6, 'include_direct_space': True, 'exceptions_periodic': True,
        'pme': (3.2, 12, 14, 16), 'ljpme': (3.3, 18, 20, 22),
        'particles': ((0.11, 0.21, 0.31), (-0.22, 0.22, 0.32), (0.33, 0.23, 0.33), (-0.22, 0.24, 0.34)),
        'exceptions': ((0, 3, -0.045, 0.246, 0.357),),
        'global_parameters': (('scale', 0.4),),
        'particle_offsets': (('scale', 1, 0.012, 0.003, 0.004),),
        'exception_offsets': (('scale', 0, 0.015, 0.005, 0.006),),
    }
    assert record.forces[5].parameters == {'frequency': 7}
    assert from_json(to_json(record)) == record
    with pytest.raises(TypeError):
        nb.parameters['exceptions'] = ()
    system.addForce(mm.CustomExternalForce('x*x'))
    with pytest.raises(UnsupportedCapability, match='CustomExternalForce'):
        inventory_system(system)


def test_inventory_virtual_sites_have_explicit_parents_and_weights():
    import openmm as mm
    from atm_mlmm.ledger import inventory_system
    system = mm.System()
    for mass in (1, 2, 0):
        system.addParticle(mass)
    system.setVirtualSite(2, mm.TwoParticleAverageSite(0, 1, 0.25, 0.75))
    inventory = inventory_system(system)
    assert inventory.virtual_sites == {'2': {'class_name': 'TwoParticleAverageSite', 'parents': (0, 1), 'weights': (0.25, 0.75)}}
