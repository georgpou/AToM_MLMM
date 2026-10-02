"""Narrow nonperiodic G04 builder using actual OpenMM-ML boundary construction."""
import copy
import hashlib

import openmm as mm
from openmm import app, unit

from ..ledger import boundary_dispositions, inventory_system
from ..schema import ForceRecord, IdentityError, LinkRecord, PhysicalBundle, UnsupportedCapability


def openmm_topology(view):
    topology = app.Topology()
    membership = {a: m for m in view.molecules for a in m.atom_ids}
    residues, atoms = {}, {}
    for a in view.atoms:
        molecule = membership[a.atom_id]
        if molecule.molecule_id not in residues:
            residues[molecule.molecule_id] = topology.addResidue(molecule.role, topology.addChain(a.chain))
        atoms[a.atom_id] = topology.addAtom(a.atom_name, app.Element.getBySymbol(a.element), residues[molecule.molecule_id])
    for b in view.bonds:
        topology.addBond(atoms[b.atom1], atoms[b.atom2])
    return topology


def original_system(original):
    if hashlib.sha256(original.prepared_mm_artifact.encode()).hexdigest() != original.prepared_mm_sha256:
        raise IdentityError('prepared MM digest mismatch before deserialization')
    system = mm.XmlSerializer.deserialize(original.prepared_mm_artifact)
    if system.getNumParticles() != len(original.topology.atoms) or any(system.isVirtualSite(i) for i in range(system.getNumParticles())):
        raise UnsupportedCapability('G04 original MM must contain real particles only')
    if original.box_nm is not None or system.usesPeriodicBoundaryConditions():
        raise UnsupportedCapability('G04 builder admits nonperiodic coordinates only')
    masses = tuple(system.getParticleMass(i).value_in_unit(unit.dalton) for i in range(system.getNumParticles()))
    ids = tuple(a.atom_id for a in original.topology.atoms)
    constraints = tuple((ids[a], ids[b], d.value_in_unit(unit.nanometer))
                        for a,b,d in (system.getConstraintParameters(i) for i in range(system.getNumConstraints())))
    if masses != original.masses_da or constraints != original.constraints:
        raise IdentityError('prepared MM masses/constraints differ from declared input')
    supported = (mm.HarmonicBondForce, mm.HarmonicAngleForce, mm.PeriodicTorsionForce, mm.RBTorsionForce, mm.NonbondedForce)
    for f in system.getForces():
        if type(f) not in supported:
            raise UnsupportedCapability(f'G04 MM force unsupported: {type(f).__name__}')
        if isinstance(f, mm.NonbondedForce) and (f.getNonbondedMethod() != mm.NonbondedForce.NoCutoff or f.getNumParticleParameterOffsets() or f.getNumExceptionParameterOffsets() or f.getNumGlobalParameters()):
            raise UnsupportedCapability('G04 requires NoCutoff MM without parameter offsets/globals')
    return system


def seal_boundary_result(original, partition, info, *, manifest):
    source = original_system(original)
    system, final_topology = info['system'], info['topology']
    old_to_new = tuple(info['oldToNew'])
    ids = tuple(a.atom_id for a in original.topology.atoms)
    count = system.getNumParticles()
    if len(partition.boundary_edges) != 1 or len(old_to_new) != len(ids) or len(set(old_to_new)) != len(ids) or any(isinstance(i,bool) or not isinstance(i,int) or i<0 or i>=count for i in old_to_new):
        raise IdentityError('G04 requires one boundary and a complete injective oldToNew')
    if count != len(ids)+1 or final_topology.getNumAtoms() != count:
        raise IdentityError('final System/topology must contain every real atom and one cap')
    actual_atoms = list(final_topology.atoms())
    for a, new in zip(original.topology.atoms, old_to_new):
        if actual_atoms[new].element != app.Element.getBySymbol(a.element) or system.isVirtualSite(new):
            raise IdentityError(f'oldToNew changes real identity/element: {a.atom_id}')
    expected_bonds = {frozenset((old_to_new[ids.index(b.atom1)],old_to_new[ids.index(b.atom2)])) for b in original.topology.bonds}
    actual_bonds = {frozenset((b.atom1.index,b.atom2.index)) for b in final_topology.bonds()}
    if actual_bonds != expected_bonds:
        raise IdentityError('final topology changes original connectivity')
    real_to_final = dict(zip(ids,old_to_new))
    extra, = set(range(count))-set(old_to_new)
    if not system.isVirtualSite(extra) or actual_atoms[extra].element != app.element.hydrogen:
        raise IdentityError('derived cap must be an actual hydrogen virtual site')
    site = system.getVirtualSite(extra)
    a,b = partition.boundary_edges[0]
    if not isinstance(site,mm.LocalCoordinatesSite) or site.getNumParticles()!=2 or tuple(site.getParticle(i) for i in range(2)) != (real_to_final[a],real_to_final[b]):
        raise IdentityError('actual cap parents/type differ from the reviewed boundary')
    distance,y,z = site.getLocalPosition().value_in_unit(unit.nanometer)
    if tuple(site.getOriginWeights())!=(1.,0.) or tuple(site.getXWeights())!=(-1.,1.) or tuple(site.getYWeights())!=(0.,0.) or y!=0 or z!=0 or distance<=0:
        raise IdentityError('actual virtual site differs from the fixed-length cap rule')
    cap_id = 'cap:'+hashlib.sha256((a+'\0'+b).encode()).hexdigest()
    link = LinkRecord(cap_id,a,b,extra,len(partition.ml_ids),type(site).__name__,float(distance))
    model_map = {i:real_to_final[i] for i in partition.ml_ids}
    model_map[cap_id] = extra
    # OpenMM-ML preserves the original MM force order and appends model forces.
    retained = copy.deepcopy(system)
    for i in reversed(range(source.getNumForces(),retained.getNumForces())):
        retained.removeForce(i)
    if tuple(type(f) for f in retained.getForces()) != tuple(type(f) for f in source.getForces()):
        raise IdentityError('upstream retained-MM force layout changed')
    ledger = tuple(ForceRecord(i,type(f).__name__,f.getName(),f.getForceGroup(),f.usesPeriodicBoundaryConditions(),
                              {'force_sha256':hashlib.sha256(mm.XmlSerializer.serialize(f).encode()).hexdigest()})
                   for i,f in enumerate(system.getForces()))
    manifest = dict(manifest, boundary_builder_version=1,
                    original_mm_xml=original.prepared_mm_artifact, original_mm_sha256=original.prepared_mm_sha256,
                    retained_mm_xml=mm.XmlSerializer.serialize(retained),
                    boundary_terms=boundary_dispositions(source,retained,old_to_new,ids),
                    original_mm_inventory=inventory_system(source).content_identity,
                    periodicity='nonperiodic',derivative_scope='all_real',model_dtype='float64')
    xml = mm.XmlSerializer.serialize(system)
    masses = tuple(system.getParticleMass(i).value_in_unit(unit.dalton) for i in range(count))
    constraints = tuple((int(a),int(b),d.value_in_unit(unit.nanometer)) for a,b,d in
                        (system.getConstraintParameters(i) for i in range(system.getNumConstraints())))
    return PhysicalBundle(xml,hashlib.sha256(xml.encode()).hexdigest(),original.topology,real_to_final,
                          model_map,old_to_new,partition.ml_ids,masses,constraints,ledger,manifest,links=(link,))
