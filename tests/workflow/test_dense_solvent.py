"""Independent dense-control geometry, classical coupling and full derivatives."""
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT/'fixtures/solvated_fragment/v2'


def control(kind):
    from atm_mlmm.workflow import load_configuration
    assert (FIXTURE/kind/'config.json').is_file(), 'denser v2 control is missing'
    return load_configuration(FIXTURE/kind/'config.json')


@pytest.mark.parametrize('kind', ('abfe','rbfe'))
def test_dense_control_preserves_solute_and_sixty_four_rigid_waters(kind):
    import openmm as mm
    from atm_mlmm.schema import from_json
    config=control(kind)
    original=from_json((ROOT/'fixtures/cloud_fragment_controls/v1'/kind/'system-input.json').read_text())
    actual=config.original
    n=len(original.topology.atoms)
    assert len(actual.topology.atoms)==n+192
    assert actual.topology.atoms[:n]==original.topology.atoms
    assert actual.positions_nm[:n]==original.positions_nm
    assert actual.masses_da[:n]==original.masses_da
    assert actual.topology.bonds[:len(original.topology.bonds)]==original.topology.bonds
    assert actual.topology.molecules[:len(original.topology.molecules)]==original.topology.molecules
    assert config.partition==from_json((ROOT/'fixtures/cloud_fragment_controls/v1'/kind/'partition.json').read_text())
    before,after=(mm.XmlSerializer.deserialize(s.prepared_mm_artifact) for s in (original,actual))
    old,new=(next(f for f in s.getForces() if isinstance(f,mm.NonbondedForce)) for s in (before,after))
    for i in range(n): assert old.getParticleParameters(i)==new.getParticleParameters(i)
    for i in range(old.getNumExceptions()): assert old.getExceptionParameters(i)==new.getExceptionParameters(i)
    assert after.getNumConstraints()==before.getNumConstraints()+192
    assert tuple(new.getPMEParameters())==(4.4/mm.unit.nanometer,64,64,64)
    assert not new.getUseDispersionCorrection()
    waters=[m for m in actual.topology.molecules if m.role=='solvent']
    assert len(waters)==64 and all(len(m.atom_ids)==3 and m.formal_charge==0 for m in waters)
    assert all(a not in config.partition.ml_ids for m in waters for a in m.atom_ids)


@pytest.mark.parametrize('kind', ('abfe','rbfe'))
def test_dense_geometry_agrees_with_explicit_twenty_seven_image_oracle(kind):
    from itertools import product
    from atm_mlmm.workflow import _domain
    config=control(kind)
    topology=config.original.topology
    radii={'H':.12,'C':.17,'N':.155,'O':.152}
    index={a.atom_id:i for i,a in enumerate(topology.atoms)}
    images=np.asarray(list(product((-6.4,0.,6.4),repeat=3)))
    positions=np.asarray(config.snapshot.positions_nm)
    mapped=positions.copy()
    for sign,m in zip((1.,-1.),[m for m in topology.molecules if m.role=='ligand']):
        mapped[[index[a] for a in m.atom_ids]]+=sign*np.array((2.4,0.,0.))
    for frame in (positions,mapped):
        minimum=float('inf')
        for i,m in enumerate(topology.molecules):
            for other in topology.molecules[i+1:]:
                a,b=[index[v] for v in m.atom_ids],[index[v] for v in other.atom_ids]
                # Independent finite image enumeration, no production minimum_image.
                delta=frame[a,None,None,:]-frame[None,b,None,:]+images[None,None,:,:]
                distance=np.linalg.norm(delta,axis=-1).min(axis=-1)
                scale=np.array([radii[topology.atoms[j].element] for j in a])[:,None]+np.array([radii[topology.atoms[j].element] for j in b])[None,:]
                minimum=min(minimum,float((distance/scale).min()))
        assert minimum>=.65
    diagnostics=_domain(topology,config.snapshot,(2.4,0.,0.),kind,config.partition.permitted_cuts)
    assert all(row['minimum_intermolecular_Bondi_ratio']>=.65 for row in diagnostics[:2])
    from atm_mlmm.schema import NumericalDomainError
    for map_index in (0,1):
        x=positions.copy(); x[-3]=x[26]+(6.4+2.4*map_index,0.,0.)
        with pytest.raises(NumericalDomainError):
            _domain(topology,replace(config.snapshot,positions_nm=x),(2.4,0.,0.),kind,config.partition.permitted_cuts)


def test_dense_builder_reproduces_exact_fixture_without_overwrite(tmp_path):
    assert importlib.util.find_spec('atm_mlmm.solvent'), 'dense builder is missing'
    from atm_mlmm.solvent import build_dense_control
    for kind in ('abfe','rbfe'):
        destination=tmp_path/kind
        build_dense_control(kind,destination)
        for name in ('system-input.json','partition.json','snapshot.json','manifest.json','config.json'):
            assert (destination/name).read_bytes()==(FIXTURE/kind/name).read_bytes()
        with pytest.raises(FileExistsError): build_dense_control(kind,destination)


def test_synthetic_water_input_uses_exact_box_faces_for_roundoff_coordinates():
    config=control('abfe')
    x=np.array(config.snapshot.positions_nm)[32:]
    boundary=np.rint(x/6.4)*6.4
    near=np.abs(x-boundary)<=8*np.spacing(6.4)
    assert np.any(near)
    np.testing.assert_array_equal(x[near],boundary[near])


@pytest.fixture(scope='module',params=('abfe','rbfe'))
def dense_physical(request):
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.partition import resolve_partition
    from atm_mlmm.models.mace import model_spec
    from atm_mlmm.schema import EmbeddingSpec
    config=control(request.param)
    physical=build_physical(config.original,resolve_partition(config.original.topology,config.partition),model_spec(),
        EmbeddingSpec('mechanical','1','protein_c_c','orthorhombic-pme-v1'),cap_distance_nm=.109)
    return config,physical


@pytest.mark.model_assets
def test_dense_both_map_full_forces_coupling_and_parent_solvent_step_sweeps(dense_physical,tmp_path):
    import openmm as mm
    from atm_mlmm.atm import PhysicalEvaluator
    from atm_mlmm.model_reference import NativeMACE
    from atm_mlmm.geometry import final_positions
    from tests.joint_oracle import mapped_snapshot,independent_answer
    from tests.periodic_oracle import plain_periodic
    config,physical=dense_physical
    native=NativeMACE()
    masked=mm.XmlSerializer.deserialize(physical.manifest['retained_mm_xml'])
    retained=mm.XmlSerializer.deserialize(physical.manifest['retained_mm_xml'])
    nb=next(f for f in masked.getForces() if isinstance(f,mm.NonbondedForce))
    ligand={physical.real_to_final[a] for m in physical.topology.molecules if m.role=='ligand' for a in m.atom_ids}
    solvent=[i for i,a in enumerate(config.snapshot.real_atom_ids) if a.startswith('dense-water-')]
    for i in ligand:
        _,sigma,_=nb.getParticleParameters(i); nb.setParticleParameters(i,0.,sigma,0.)
    for i in range(nb.getNumExceptions()):
        a,b,_,sigma,_=nb.getExceptionParameters(i)
        if a in ligand or b in ligand: nb.setExceptionParameters(i,a,b,0.,sigma,0.)
    link=physical.links[0]
    selected=[config.snapshot.real_atom_ids.index(a) for a in (link.ml_parent_id,link.mm_parent_id)]
    selected+=[26,solvent[0],solvent[96]]
    evidence=[]
    with PhysicalEvaluator(physical,config.runtime) as direct:
        for mapping in (0,1):
            frame=mapped_snapshot(physical,config.snapshot,mapping)
            actual=direct.evaluate(frame)
            e,f,_=independent_answer(physical,frame,native)
            assert abs(actual.energy_kj_mol-e)<=1e-4
            np.testing.assert_allclose(actual.forces_kj_mol_nm,f,atol=5e-3,rtol=0)
            positions=final_positions(physical,frame)
            _,coupled=plain_periodic(retained,positions,frame.box_nm)
            _,uncoupled=plain_periodic(masked,positions,frame.box_nm)
            s=[physical.real_to_final[config.snapshot.real_atom_ids[i]] for i in solvent]
            assert np.max(np.abs(coupled[s]-uncoupled[s]))>1e-3
            for atom in selected:
                values=[]
                energy_pairs=[]
                for step in (1e-3,1e-4,1e-5):
                    energies=[]
                    for sign in (1.,-1.):
                        x=np.array(frame.positions_nm); x[atom,1]+=sign*step
                        energies.append(direct.evaluate(replace(frame,positions_nm=x)).energy_kj_mol)
                    values.append(-(energies[0]-energies[1])/(2*step))
                    energy_pairs.append(energies)
                force=actual.forces_kj_mol_nm[atom][1]
                evidence.append({'map':mapping,'atom_id':frame.real_atom_ids[atom],'force_y':force,'fd_y':values,
                    'energies_plus_minus':energy_pairs,'positions_nm':frame.positions_nm})
                (tmp_path/'dense-numerical-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
                assert abs(values[-1]-force)<=1e-3+1e-4*abs(force)
                assert abs(values[-1]-force)<=abs(values[0]-force)+1e-4
            evidence.append({'map':mapping,'energy_kj_mol':actual.energy_kj_mol,'energy_error':actual.energy_kj_mol-e,
                'full_real_forces':actual.forces_kj_mol_nm,'max_force_error':float(np.max(np.abs(np.asarray(actual.forces_kj_mol_nm)-f)))})
    (tmp_path/'dense-numerical-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
