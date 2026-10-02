"""Distinctive MM terms pin actual central-atom/connectivity boundary rules."""
import openmm as mm
from openmm import app,unit
import pytest


def predicate_fixture():
    topology=app.Topology();residue=topology.addResidue('predicate-graph',topology.addChain())
    atoms=[topology.addAtom(str(i),app.element.carbon,residue) for i in range(8)]
    for a,b in ((0,1),(1,2),(2,3),(1,4),(2,5),(0,6),(3,7)):topology.addBond(atoms[a],atoms[b])
    system=mm.System()
    for _ in atoms:system.addParticle(12.)
    bond=mm.HarmonicBondForce()
    for i,(a,b) in enumerate(((0,1),(1,2),(2,3))):bond.addBond(a,b,.14+i*.01,101.+i)
    angle=mm.HarmonicAngleForce()
    for i,t in enumerate(((0,1,4),(0,1,2),(1,2,3),(1,0,5))):angle.addAngle(*t,1.+i*.1,201.+i)
    torsion=mm.PeriodicTorsionForce()
    # Internal proper; proper with MM end and ML centers; crossing proper;
    # improper with ML center and MM endpoint; improper with MM center.
    for i,t in enumerate(((4,1,0,6),(2,1,0,6),(0,1,2,3),(0,1,2,4),(1,2,3,5))):torsion.addTorsion(*t,i+1,.2+i*.1,301.+i)
    nb=mm.NonbondedForce();nb.setNonbondedMethod(mm.NonbondedForce.NoCutoff);nb.setUseDispersionCorrection(False)
    for i in range(8):nb.addParticle((i+1)*.01,.2+i*.001,.3+i*.01)
    for i,t in enumerate(((0,4),(1,2),(2,3))):nb.addException(*t,.04+i*.01,.25+i*.01,.09+i*.01)
    for f in (bond,angle,torsion,nb):system.addForce(f)
    for a,b,d in ((0,1,.14),(1,2,.15),(2,3,.16)):system.addConstraint(a,b,d)
    return topology,system,[0,1,4,6]


def test_each_boundary_term_disposition():
    from atm_mlmm.ledger import boundary_dispositions
    from openmmml import MLPotential
    from tests.link_oracle import upstream_info
    upstream_info() # register only the analytic substitute, retaining actual embedding
    topology,original,ml=predicate_fixture()
    original_xml=mm.XmlSerializer.serialize(original)
    info=MLPotential('g04-diagnostic').createMixedSystem(topology,original,ml,returnInfo=True,forceGroup=2)
    retained=info['system']
    retained.removeForce(retained.getNumForces()-1) # diagnostic model, not MM
    rows=boundary_dispositions(original,retained,info['oldToNew'],tuple(f's{i}' for i in range(8)))
    assert mm.XmlSerializer.serialize(original)==original_xml
    expected={'bond':('removed','retained','retained'),
              'angle':('removed','removed','retained','retained'),
              'torsion':('removed','removed','retained','removed','retained'),
              'exception':('replaced_by_exclusion','retained','retained'),
              'constraint':('removed','retained','retained')}
    for kind,dispositions in expected.items():
        matching=[r for r in rows if r['kind']==kind and r['original_index'] is not None]
        assert tuple(r['disposition'] for r in matching)==dispositions,matching
        assert all(r['original_parameters'] for r in matching)
        for row in matching:
            if row['disposition']=='retained':assert row['original_parameters']==row['retained_parameters']
    # Assert distinctive actual parameters, beyond counts and ledger labels.
    assert [float(retained.getForce(0).getBondParameters(i)[-1].value_in_unit(unit.kilojoule_per_mole/unit.nanometer**2)) for i in range(2)]==[102.,103.]
    assert [float(retained.getForce(1).getAngleParameters(i)[-1].value_in_unit(unit.kilojoule_per_mole/unit.radian**2)) for i in range(2)]==[203.,204.]
    assert [float(retained.getForce(2).getTorsionParameters(i)[-1].value_in_unit(unit.kilojoule_per_mole)) for i in range(2)]==[303.,305.]
    nb=retained.getForce(3)
    for i in range(8):assert nb.getParticleParameters(i)==original.getForce(3).getParticleParameters(i)
    assert float(nb.getParticleParameters(8)[0].value_in_unit(unit.elementary_charge))==0.
    assert float(nb.getParticleParameters(8)[2].value_in_unit(unit.kilojoule_per_mole))==0.
    added=[r for r in rows if r['disposition']=='added_exclusion']
    assert len(added)==5 # six ML pairs, one existing ML exception


def test_saved_original_retained_hybrid_identity():
    from tests.integration.test_link_geometry import case,model_result
    from tests.link_permutation import plain_result
    bundle,snapshot=case()
    original=mm.XmlSerializer.deserialize(bundle.manifest['original_mm_xml'])
    retained=mm.XmlSerializer.deserialize(bundle.manifest['retained_mm_xml'])
    from atm_mlmm.atm import evaluate_physical
    from tests.link_oracle import REFERENCE
    full=plain_result(original,snapshot.positions_nm)[0]
    keep=plain_result(retained,snapshot.positions_nm)[0]
    model=model_result(bundle,snapshot)[0]
    hybrid=evaluate_physical(bundle,snapshot,REFERENCE).energy_kj_mol
    assert abs(hybrid-(full-(full-keep)+model))<=1e-8
    assert abs(hybrid-(keep+model))<=1e-8
    assert bundle.manifest['boundary_terms']
