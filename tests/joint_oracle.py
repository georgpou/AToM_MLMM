"""G07 fixed whole-ligand fixtures and independently assembled full forces."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import numpy as np
import openmm as mm
from openmm import unit
from atm_mlmm.schema import (AtomIdentity,Bond,MoleculeState,TopologyView,SystemInput,
    Snapshot,PartitionSpec,ComponentState,EmbeddingSpec,MobileGroup,RestraintSpec,RuntimeSpec)

ROOT = Path(__file__).resolve().parents[1]
PREPARED = ROOT/'fixtures/fragment_ligand/prepared-mm-v1'
STRUCTURES = ROOT/'fixtures/chemical_reference_v3/structures'
DISPLACEMENT = (2.4,0.,0.)
JOINT_BOX = ((6.4,0.,0.),(0.,6.4,0.),(0.,0.,6.4))
RUNTIME = RuntimeSpec('Reference','double',(),.0005,300.,'NVT','LangevinMiddle')


def joint_input(*, two_ligands=False, choice='baseline', periodic=False, row_name='ethanol-methanol-d3-r0'):
    data = json.loads((STRUCTURES/(row_name+'.json')).read_text())
    parent = data['g07_controls']['parent']
    family = 'butane' if row_name.startswith('butane') else 'ethanol'
    ligand_name = 'acetamide' if 'acetamide' in data['family'] else 'methanol'
    ligand_record = json.loads((STRUCTURES/('acetamide-0.json' if ligand_name=='acetamide' else 'methanol-baseline.json')).read_text())
    records = [(parent,parent['positions_angstrom'],'', 'protein','protein'),
               (ligand_record,data['g07_controls']['ligand_positions_angstrom'],'a:',ligand_name,'ligand')]
    names = [family,ligand_name]
    if two_ligands:
        assert ligand_name == 'methanol'
        second = json.loads((STRUCTURES/(family+'-acetamide-d3'+('.8' if family=='butane' else '')+'-r0.json')).read_text())
        ligand_b = json.loads((STRUCTURES/'acetamide-0.json').read_text())
        x = np.asarray(second['g07_controls']['ligand_positions_angstrom'])+10*np.asarray(DISPLACEMENT)
        records.append((ligand_b,x,'b:','acetamide','ligand'));names.append('acetamide')
    key = '-'.join(names)
    manifest = json.loads((PREPARED/'manifest.json').read_text())
    path = PREPARED/(key+'.xml')
    xml = path.read_text()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest['files'][path.name]
    system = mm.XmlSerializer.deserialize(xml)
    atoms,bonds,molecules,positions = [],[],[],[]
    for record,x,prefix,molecule,role in records:
        ids = tuple(prefix+a for a in record['atom_ids'])
        atoms.extend(AtomIdentity(a,e,molecule,'1','',a) for a,e in zip(ids,record['elements']))
        bonds.extend(Bond(ids[a],ids[b],order) for a,b,order in record['bonds'])
        molecules.append(MoleculeState(molecule,ids,role,0,1))
        positions.extend(np.asarray(x)/10.)
    topology = TopologyView(tuple(atoms),tuple(bonds),tuple(molecules))
    description = next(c for c in data['g07_controls']['choices'] if c['name']==choice)
    protein = tuple(description['protein_ml_ids'])
    cuts = () if choice=='uncut' else ((description['cut_ml_parent_id'],description['cut_mm_parent_id']),)
    ligand_ids = tuple(a for m in molecules[1:] for a in m.atom_ids)
    spec = PartitionSpec(protein+ligand_ids,protein,cuts,
                         tuple(ComponentState(ids,0,1) for ids in (protein,)+tuple(m.atom_ids for m in molecules[1:])))
    box = JOINT_BOX if periodic else None
    if periodic:
        system.setDefaultPeriodicBoxVectors(*box)
        nb = next(f for f in system.getForces() if isinstance(f,mm.NonbondedForce))
        nb.setNonbondedMethod(mm.NonbondedForce.PME);nb.setCutoffDistance(.9)
        nb.setUseSwitchingFunction(True);nb.setSwitchingDistance(.75)
        nb.setEwaldErrorTolerance(1e-7);nb.setPMEParameters(4.4,128,128,128)
        xml = mm.XmlSerializer.serialize(system)
    original = SystemInput(xml,hashlib.sha256(xml.encode()).hexdigest(),topology,tuple(positions),box,
        tuple(system.getParticleMass(i).value_in_unit(unit.dalton) for i in range(system.getNumParticles())),(),
        {'forcefield':'GAFF 2.2.20 / actual AM1-BCC','prepared_manifest':hashlib.sha256((PREPARED/'manifest.json').read_bytes()).hexdigest()})
    snapshot = Snapshot(tuple(a.atom_id for a in atoms),tuple(positions),box)
    return original,spec,snapshot


def joint_case(*, two_ligands=False, choice='baseline', periodic=False, environment=False, real_model=True, row_name='ethanol-methanol-d3-r0'):
    from atm_mlmm.hybrid import build_physical
    from atm_mlmm.partition import resolve_partition
    original,spec,snapshot = joint_input(two_ligands=two_ligands,choice=choice,periodic=periodic,row_name=row_name)
    probe = None
    if real_model:
        from atm_mlmm.models.mace import model_spec
        model = model_spec()
    else:
        from atm_mlmm.models.analytic_boundary import BoundaryProbe
        from atm_mlmm.schema import ModelSpec
        model = ModelSpec('analytic-environment' if environment else 'analytic-local',None,
                         'declared_relative_energy',('H','C','N','O'),'neutral_singlet',
                         'environment_dependent' if environment else 'local','float64')
        probe = BoundaryProbe(cap_k=0.,pair_k=4.,partner_id='a:l0',environment_k=10. if environment else 0.,
                              environment_id='p0',ligand_k=0.)
    bundle = build_physical(original,resolve_partition(original.topology,spec),model,
        EmbeddingSpec('mechanical','1','protein_c_c','orthorhombic-pme-v1' if periodic else 'nonperiodic'),
        cap_distance_nm=.109,probe=probe)
    return bundle,snapshot


def protocol_case(bundle,two_ligands=False):
    from atm_mlmm.protocols import abfe,rbfe
    from atm_mlmm.geometry import resolve_protocol
    from atm_mlmm.schedule import production_schedule
    from tests.analytic_oracle import production_parameters
    groups = tuple(MobileGroup('mobile-'+m.molecule_id,m.atom_ids,('ligand',),m.molecule_id)
                   for m in bundle.topology.molecules if m.role=='ligand')
    transfer = resolve_protocol(bundle,(rbfe if two_ligands else abfe).make_protocol(groups,DISPLACEMENT))
    fixed = dict(Umax=10000.,Ubcore=500.,Acore=0.,W0=0.,UOffset=0.)
    schedule = production_schedule((('map0',production_parameters(**fixed,Lambda1=0.,Lambda2=0.)),
        ('middle',production_parameters(**fixed,Lambda1=.2,Lambda2=.7,Alpha=.01,Uh=0.)),
        ('map1',production_parameters(**fixed,Lambda1=1.,Lambda2=1.))))
    return transfer,schedule,RestraintSpec('outside',('p0',),0.,(0.,0.,0.))


def mapped_snapshot(bundle,snapshot,mapping):
    x = np.array(snapshot.positions_nm)
    # Hand map complete ligand components; never use the production resolver.
    if mapping:
        for index,a in enumerate(snapshot.real_atom_ids):
            if a.startswith('a:'): x[index] += DISPLACEMENT
            elif a.startswith('b:'): x[index] -= DISPLACEMENT
    return replace(snapshot,positions_nm=x)


def independent_answer(bundle,snapshot,native=None,probe=None):
    from tests.model_oracle import derived_input,project
    from tests.periodic_oracle import plain_periodic
    from tests.link_permutation import plain_result
    if snapshot.box_nm is not None:
        # Independent bonded-image search, anchored on the same molecules.
        from tests.periodic_oracle import enumerated_displacement
        x = np.array(snapshot.positions_nm)
        indices = {a:i for i,a in enumerate(snapshot.real_atom_ids)}
        graph = {a:[] for a in indices}
        for bond in bundle.topology.bonds:
            graph[bond.atom1].append(bond.atom2);graph[bond.atom2].append(bond.atom1)
        raw = x.copy()
        for molecule in bundle.topology.molecules:
            anchor = molecule.atom_ids[0];raw[indices[anchor]] = np.mod(x[indices[anchor]],np.diag(snapshot.box_nm))
            seen,queue={anchor},[anchor]
            for a in queue:
                for b in graph[a]:
                    if b not in seen:
                        raw[indices[b]]=raw[indices[a]]+enumerated_displacement(x[indices[b]]-x[indices[a]],snapshot.box_nm)[0]
                        seen.add(b);queue.append(b)
        snapshot = replace(snapshot,positions_nm=raw)
    numbers,x,jac = derived_input(bundle,snapshot)
    if native is not None:
        output = native.evaluate(numbers,x,box_nm=snapshot.box_nm)
        energy,forces = output['energy_kj_mol'],project(output['forces_kj_mol_nm'],jac)
    else:
        # Cap spring to a model ligand and optional MM environment; independently
        # construct the raw cap force then apply the generic Jacobian once.
        ids = snapshot.real_atom_ids
        cap = x[-1];real = np.asarray(snapshot.positions_nm)
        forces = np.zeros_like(real);cap_force = np.zeros(3);energy=0.
        for partner,k in ((ids.index('a:l0'),4.),(ids.index('p0'),10. if probe else 0.)):
            d = cap-real[partner];energy += .5*k*np.dot(d,d)
            cap_force -= k*d;forces[partner] += k*d
        forces += np.einsum('rij,j->ri',jac[-1],cap_force)
        output = {'raw_cap_force':cap_force.tolist()}
    retained = mm.XmlSerializer.deserialize(bundle.manifest['retained_mm_xml'])
    if snapshot.box_nm is None: mm_e,mm_f = plain_result(retained,snapshot.positions_nm)
    else: mm_e,mm_f = plain_periodic(retained,np.vstack([snapshot.positions_nm,[0.,0.,0.]]),snapshot.box_nm)
    return energy+mm_e,forces+mm_f[list(bundle.old_to_new)],output
