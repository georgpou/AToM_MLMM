"""Exercise the additional force that stock AToM preparation can omit."""
import logging

import numpy as np
import openmm as mm
from openmm import unit
import pytest


def test_benchmark_preparation_integrates_every_physical_force():
    from atm_mlmm.adapters import atom
    factory = getattr(atom, 'benchmark_preparation_class', None)
    assert factory is not None, 'the stock preparation mask needs a hybrid adapter'
    cls = factory()
    preparation = cls('probe', {'FRICTION_COEFF': 1., 'TIME_STEP': .0005,
                              'INTEGRATOR': 'langevinmiddle'}, None, None,
                      logging.getLogger('benchmark-test'))
    system = mm.System()
    system.addParticle(12.)
    for group, expression in [(1, '-3*x'), (7, '-2*y')]:
        force = mm.CustomExternalForce(expression)
        force.addParticle(0, [])
        force.setForceGroup(group)
        system.addForce(force)
    preparation.system = system
    preparation.atmforcegroup = 31
    preparation.set_integrator(300.*unit.kelvin, 1./unit.picosecond,
                               .0005*unit.picosecond)
    context = mm.Context(system, preparation.integrator,
                         mm.Platform.getPlatformByName('Reference'))
    context.setPositions([[.1, .2, .3]])
    active = context.getState(getForces=True,
        groups=preparation.integrator.getIntegrationForceGroups()).getForces(asNumpy=True)
    np.testing.assert_allclose(active.value_in_unit(unit.kilojoule_per_mole/unit.nanometer),
                               [[3., 2., 0.]], atol=1e-12)
    del context


def test_upstream_npt_requests_cannot_change_fixed_volume():
    from atm_mlmm.adapters.atom import benchmark_preparation_class
    preparation = benchmark_preparation_class()('probe',
        {'FRICTION_COEFF': 1., 'TIME_STEP': .0005}, None, None, logging.getLogger('test'))
    preparation.system = mm.System()
    preparation.set_barostat(300.*unit.kelvin, 1.*unit.bar, 25)
    preparation.barostat.setFrequency(25)
    assert preparation.barostat.getFrequency() == 0


def test_preparation_hook_restores_upstream_on_failure():
    import importlib
    from atm_mlmm.adapters.atom import benchmark_preparation_hooks
    upstream = importlib.import_module('atom_openmm.abfe_structprep')
    original = upstream.OMMSystemABFEnoATM
    original_massage = upstream.massage_keywords
    with pytest.raises(RuntimeError, match='probe failure'):
        with benchmark_preparation_hooks():
            assert upstream.OMMSystemABFEnoATM is not original
            raise RuntimeError('probe failure')
    assert upstream.OMMSystemABFEnoATM is original
    assert upstream.massage_keywords is original_massage


def test_preparation_preserves_the_declared_timestep():
    from atm_mlmm.adapters.atom import benchmark_preparation_hooks
    options = {'TIME_STEP': .0005}
    with benchmark_preparation_hooks() as upstream:
        upstream.massage_keywords(options, restrain_solutes=False)
    assert options['TIME_STEP'] == .0005


@pytest.mark.parametrize('allocation', ['localhost,0:0,1,CUDA,,/tmp',
    'localhost,0:0,0,CPU,,/tmp', 'localhost,0:0,1,CPU,,', '',
    'localhost,0:0,1,CPU,,/tmp\nlocalhost,0:0,1,CPU,,/tmp'])
def test_nodefile_rejects_unsupported_or_ambiguous_workers_before_start(tmp_path, allocation):
    from atm_mlmm.adapters import atom
    validator = getattr(atom, 'validate_benchmark_nodefile', None)
    assert validator is not None
    path = tmp_path / 'nodes'
    path.write_text(allocation)
    with pytest.raises(ValueError):
        validator(path)


def test_initial_offset_matches_stock_mass_weighted_centroid_restraint():
    from atm_mlmm.adapters import atom
    from atom_openmm.utils.AtomUtils import AtomUtils
    offset_function = getattr(atom, '_benchmark_centroid_offset', None)
    assert offset_function is not None
    system = mm.System()
    for mass in (12., 16., 12.):
        system.addParticle(mass)
    xyz = np.array([[0., 0., 0.], [.2, 0., 0.], [2., 0., 0.]])
    offset = offset_function(system, xyz, [0, 1], [2])
    AtomUtils(system).addVsiteRestraintForceCMCM([0, 1], [2],
        2.*unit.kilojoule_per_mole/unit.nanometer**2, 0.*unit.nanometer,
        offset*unit.nanometer)
    integrator = mm.VerletIntegrator(.001)
    context = mm.Context(system, integrator, mm.Platform.getPlatformByName('Reference'))
    context.setPositions(xyz)
    energy = context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    assert energy == pytest.approx(0., abs=1.e-15)
    del context


def test_stock_production_counts_physical_forces_once_and_keeps_cap_parents_mobile(tmp_path):
    """Independent polynomial oracle, including a virtual site's parent forces."""
    from openmm import app
    from atom_openmm.ommsystem import OMMSystemABFE
    system = mm.System()
    for mass in (12., 12., 12., 0.):
        system.addParticle(mass)
    system.setVirtualSite(3, mm.TwoParticleAverageSite(1, 2, .8, .2))
    for index, expression in [(0, 'x*x+y*y'), (3, 'x*x+5*z')]:
        force = mm.CustomExternalForce(expression)
        force.addParticle(index, [])
        force.setForceGroup(1)
        system.addForce(force)
    periodic = mm.CustomBondForce('0')
    periodic.addBond(0, 1, [])
    periodic.setUsesPeriodicBoundaryConditions(True)
    periodic.setForceGroup(1)
    system.addForce(periodic)
    topology = app.Topology()
    for name, element in [('L1', app.element.carbon), ('P1', app.element.carbon),
                          ('P2', app.element.carbon), ('CAP', app.element.hydrogen)]:
        residue = topology.addResidue(name, topology.addChain())
        topology.addAtom('C' if element == app.element.carbon else 'H', element, residue)
    xyz = np.array([[.1, .2, .3], [1., 0., 0.], [1.15, 0., 0.], [1.03, 0., 0.]])
    pdb, xml = tmp_path/'probe.pdb', tmp_path/'probe.xml'
    with pdb.open('w') as handle:
        app.PDBFile.writeFile(topology, xyz*unit.nanometer, handle)
    xml.write_text(mm.XmlSerializer.serialize(system))
    options = dict(LIGAND_ATOMS=[0], DISPLACEMENT=[2., 0., 0.], VARIABLE_FORCE_GROUP=1,
                   FRICTION_COEFF=1., TIME_STEP=.0005, INTEGRATOR='langevinmiddle',
                   UMAX=200., UBCORE=100., ACORE=.0625)
    production = OMMSystemABFE('probe', options, str(pdb), str(xml), logging.getLogger('test'))
    production.create_system()
    assert production.atmforce.getNumForces() == 3
    assert not any(f.getForceGroup() == 1 for f in production.system.getForces())
    assert production.barostat.getFrequency() == 0
    context = mm.Context(production.system, production.integrator,
                         mm.Platform.getPlatformByName('Reference'))
    context.setPositions(xyz)
    context.computeVirtualSites()
    for lam in (0., .5):
        context.setParameter('Lambda1', lam)
        context.setParameter('Lambda2', lam)
        state = context.getState(getEnergy=True, getForces=True,
            groups=production.integrator.getIntegrationForceGroups())
        expected = (1-lam)*(.1**2+.2**2) + lam*(.3**2+.2**2) + 1.03**2
        assert state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole) == pytest.approx(expected)
        forces = state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer)
        np.testing.assert_allclose(forces[:3], [[-2*(.1+.2*lam), -.4, 0.],
                                                [-2*1.03*.8, 0., -4.],
                                                [-2*1.03*.2, 0., -1.]], atol=1e-12)
    del context
