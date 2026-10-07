"""Deterministic geometry-only construction of the M05 denser local-water input.

No energy-based selection, density equilibration or new physical builder lives
here. The result is a hash-bound SystemInput for the existing common engine.
"""
from dataclasses import replace
import hashlib
import itertools
import json
from pathlib import Path

from .schema import (AtomIdentity,Bond,MoleculeState,Snapshot,TopologyView,
                     MalformedInput,NumericalDomainError,from_json,to_json)

ROOT=Path(__file__).resolve().parents[2]
BOX=((6.4,0.,0.),(0.,6.4,0.),(0.,0.,6.4))


def _water_positions(original, partition):
    import numpy as np
    from .geometry import minimum_image
    x=np.array(original.positions_nm)
    index={a.atom_id:i for i,a in enumerate(original.topology.atoms)}
    radii={'H':.12,'C':.17,'N':.155,'O':.152}
    radius=np.array([radii[a.element] for a in original.topology.atoms])
    mapped=x.copy()
    for sign,m in zip((1.,-1.),[m for m in original.topology.molecules if m.role=='ligand']):
        mapped[[index[a] for a in m.atom_ids]]+=sign*np.array((2.4,0.,0.))
    caps=[]
    for a,b in partition.permitted_cuts:
        delta=x[index[b]]-x[index[a]]
        caps.append(x[index[a]]+.109*delta/np.linalg.norm(delta))
    geometry=np.array(((0.,0.,0.),(.09572,0.,0.),
                       (.09572*np.cos(np.deg2rad(104.52)),.09572*np.sin(np.deg2rad(104.52)),0.)))
    candidates=sorted(itertools.product(range(-3,4),repeat=3),key=lambda p:(sum(v*v for v in p),p))
    waters=[]
    for site in (x[26],x[26]+(2.4,0.,0.)):
        count=0
        for offset in candidates:
            water=site+.32*np.array(offset)+geometry
            # Keep synthetic lattice planes exactly representable. The inherited
            # solute anchor contains ~1e-17-nm roundoff; copying it into all water
            # planes can trigger an unrelated pinned Reference pair-list corner
            # case. This is input formatting only, not a runtime/backend change.
            boundary=np.rint(water/6.4)*6.4
            water=np.where(np.abs(water-boundary)<=8*np.spacing(6.4),boundary,water)
            other=np.vstack(waters) if waters else np.empty((0,3))
            other_radius=np.tile((.152,.12,.12),len(waters))
            scale=np.array((.152,.12,.12))[:,None]+np.concatenate((radius,other_radius))[None,:]
            if any(float((np.linalg.norm(minimum_image(water[:,None,:]-np.vstack((frame,other))[None,:,:],BOX),axis=-1)/scale).min())<.80
                   for frame in (x,mapped)):
                continue
            if caps:
                distance=np.linalg.norm(minimum_image(water[:,None,:]-np.array(caps)[None,:,:],BOX),axis=-1)
                if float((distance/(np.array((.152,.12,.12))[:,None]+.12)).min())<.80:
                    continue
            waters.append(water); count+=1
            if count==32: break
        if count!=32:
            raise NumericalDomainError('predeclared lattice cannot admit 32 waters at each site')
    return np.vstack(waters)


def build_dense_control(kind, destination):
    """Freeze the predeclared 64-water input into an unused directory."""
    import openmm as mm
    from openmm import app,unit
    if kind not in ('abfe','rbfe'):
        raise MalformedInput('denser solvent control kind must be abfe or rbfe')
    destination=Path(destination)
    if destination.exists(): raise FileExistsError(destination)
    source=ROOT/'fixtures/cloud_fragment_controls/v1'/kind
    original=from_json((source/'system-input.json').read_text())
    partition=from_json((source/'partition.json').read_text())
    positions=_water_positions(original,partition)
    system=mm.XmlSerializer.deserialize(original.prepared_mm_artifact)
    nb=next(f for f in system.getForces() if isinstance(f,mm.NonbondedForce))
    system.setDefaultPeriodicBoxVectors(*BOX)
    nb.setNonbondedMethod(mm.NonbondedForce.PME); nb.setCutoffDistance(.9)
    nb.setUseSwitchingFunction(True); nb.setSwitchingDistance(.75)
    nb.setUseDispersionCorrection(False); nb.setEwaldErrorTolerance(1e-7)
    nb.setPMEParameters(4.4,64,64,64)
    atoms,bonds,molecules=list(original.topology.atoms),list(original.topology.bonds),list(original.topology.molecules)
    topology=app.Topology(); chain=topology.addChain()
    for number in range(64):
        ids=tuple(f'dense-water-{number}:{name}' for name in ('O','H1','H2'))
        residue=topology.addResidue('HOH',chain)
        water_atoms=[topology.addAtom(name,app.Element.getBySymbol(element),residue)
                     for name,element in (('O','O'),('H1','H'),('H2','H'))]
        for h in water_atoms[1:]: topology.addBond(water_atoms[0],h)
        atoms.extend(AtomIdentity(atom,element,'W',str(number+1),'',name)
                     for atom,element,name in zip(ids,('O','H','H'),('O','H1','H2')))
        bonds.extend(Bond(ids[0],h) for h in ids[1:])
        molecules.append(MoleculeState(f'dense-water-{number}',ids,'solvent',0,1))
    water=app.ForceField('tip3p.xml').createSystem(topology,nonbondedMethod=app.NoCutoff,rigidWater=True,removeCMMotion=False)
    water_nb=next(f for f in water.getForces() if isinstance(f,mm.NonbondedForce))
    for force in water.getForces():
        if isinstance(force,mm.HarmonicBondForce) and force.getNumBonds()!=0:
            raise NumericalDomainError('rigid TIP3P unexpectedly contains bonded terms')
        if isinstance(force,mm.HarmonicAngleForce) and force.getNumAngles()!=0:
            raise NumericalDomainError('rigid TIP3P unexpectedly contains angle terms')
        if not isinstance(force,(mm.NonbondedForce,mm.HarmonicBondForce,mm.HarmonicAngleForce)):
            raise NumericalDomainError('unexpected rigid water force ownership')
    offset=system.getNumParticles()
    for i in range(water.getNumParticles()):
        system.addParticle(water.getParticleMass(i)); nb.addParticle(*water_nb.getParticleParameters(i))
    for i in range(water_nb.getNumExceptions()):
        a,b,q,sigma,epsilon=water_nb.getExceptionParameters(i)
        nb.addException(offset+a,offset+b,q,sigma,epsilon)
    constraints=list(original.constraints)
    for i in range(water.getNumConstraints()):
        a,b,distance=water.getConstraintParameters(i)
        system.addConstraint(offset+a,offset+b,distance)
        constraints.append((atoms[offset+a].atom_id,atoms[offset+b].atom_id,distance.value_in_unit(unit.nanometer)))
    xml=mm.XmlSerializer.serialize(system)
    ff=Path(app.__file__).parent/'data/tip3p.xml'
    provenance={**original.force_field_provenance,'solvent':'OpenMM rigid TIP3P; 64 denser local-water controls',
        'tip3p_xml_sha256':hashlib.sha256(ff.read_bytes()).hexdigest(),'solute_input_identity':original.content_identity,
        'periodic_convention':'orthorhombic-pme-v1','density_equilibration':'not performed; no liquid-density qualification',
        'construction':{'waters_per_site':32,'lattice_spacing_nm':.32,'integer_offsets':[-3,3],
                        'candidate_order':'squared distance then integer coordinates','minimum_water_Bondi_ratio':.80}}
    provenance['construction']['box_face_input_roundoff_ulp']=8
    solvated=replace(original,prepared_mm_artifact=xml,prepared_mm_sha256=hashlib.sha256(xml.encode()).hexdigest(),
        topology=TopologyView(tuple(atoms),tuple(bonds),tuple(molecules)),
        positions_nm=tuple(original.positions_nm)+tuple(map(tuple,positions)),box_nm=BOX,constraints=constraints,
        force_field_provenance=provenance,
        masses_da=tuple(system.getParticleMass(i).value_in_unit(unit.dalton) for i in range(system.getNumParticles())))
    snapshot=Snapshot(tuple(a.atom_id for a in atoms),solvated.positions_nm,BOX)
    from .workflow import _domain
    _domain(solvated.topology,snapshot,(2.4,0.,0.),kind,partition.permitted_cuts)
    destination.mkdir(parents=True,exist_ok=False)
    files={}
    for name,record in (('system-input.json',solvated),('partition.json',partition),('snapshot.json',snapshot)):
        payload=(to_json(record)+'\n').encode(); (destination/name).write_bytes(payload)
        files[name]=hashlib.sha256(payload).hexdigest()
    manifest=destination/'manifest.json'
    manifest.write_text(json.dumps({'files':files,'physical_scope':'64 denser local TIP3P waters; no liquid density/equilibrium qualification',
        'source_files':{name:hashlib.sha256((source/name).read_bytes()).hexdigest() for name in files}},indent=2)+'\n')
    config=json.loads((source/'config.json').read_text())
    config.update(input_manifest='manifest.json',input_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest())
    (destination/'config.json').write_text(json.dumps(config,indent=2)+'\n')
