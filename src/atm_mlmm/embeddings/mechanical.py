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
    atoms = {}
    last_chain_id, last_residue_key, chain, residue = None, None, None, None
    for a in view.atoms:
        molecule = membership[a.atom_id]
        if a.chain != last_chain_id:
            chain = topology.addChain(a.chain)
            last_chain_id = a.chain
            last_residue_key = None
        residue_key = (molecule.molecule_id, a.chain, a.residue, a.insertion_code)
        if residue_key != last_residue_key:
            residue = topology.addResidue(molecule.role, chain)
            last_residue_key = residue_key
        atoms[a.atom_id] = topology.addAtom(a.atom_name, app.Element.getBySymbol(a.element), residue)
    for b in view.bonds:
        topology.addBond(atoms[b.atom1], atoms[b.atom2])
    return topology


def original_system(original, *, require_inventory_identity=False):
    if hashlib.sha256(original.prepared_mm_artifact.encode()).hexdigest() != original.prepared_mm_sha256:
        raise IdentityError('prepared MM digest mismatch before deserialization')
    if require_inventory_identity and not original.prepared_mm_inventory_identity:
        raise IdentityError('version-2 construction requires a prepared MM inventory identity')
    system = mm.XmlSerializer.deserialize(original.prepared_mm_artifact)
    if system.getNumParticles() != len(original.topology.atoms) or any(system.isVirtualSite(i) for i in range(system.getNumParticles())):
        raise UnsupportedCapability('G04 original MM must contain real particles only')
    periodic = original.box_nm is not None
    if periodic:
        from ..ledger import validate_pme_system
        validate_pme_system(system, original.box_nm)
        box = tuple(tuple(v.value_in_unit(unit.nanometer)) for v in system.getDefaultPeriodicBoxVectors())
        if box != original.box_nm:
            raise IdentityError('prepared MM box differs from declared input')
    elif system.usesPeriodicBoundaryConditions():
        raise UnsupportedCapability('periodic MM requires a declared box')
    masses = tuple(system.getParticleMass(i).value_in_unit(unit.dalton) for i in range(system.getNumParticles()))
    ids = tuple(a.atom_id for a in original.topology.atoms)
    constraints = tuple((ids[a], ids[b], d.value_in_unit(unit.nanometer))
                        for a,b,d in (system.getConstraintParameters(i) for i in range(system.getNumConstraints())))
    if masses != original.masses_da or constraints != original.constraints:
        raise IdentityError('prepared MM masses/constraints differ from declared input')
    if original.prepared_mm_inventory_identity is not None:
        actual_inventory = inventory_system(system).content_identity
        if actual_inventory != original.prepared_mm_inventory_identity:
            raise IdentityError('prepared MM inventory identity mismatch')
    supported = (mm.HarmonicBondForce, mm.HarmonicAngleForce, mm.PeriodicTorsionForce, mm.RBTorsionForce, mm.NonbondedForce)
    for f in system.getForces():
        if type(f) not in supported:
            raise UnsupportedCapability(f'G04 MM force unsupported: {type(f).__name__}')
        if not periodic and isinstance(f, mm.NonbondedForce) and (f.getNonbondedMethod() != mm.NonbondedForce.NoCutoff or f.getNumParticleParameterOffsets() or f.getNumExceptionParameterOffsets() or f.getNumGlobalParameters()):
            raise UnsupportedCapability('G04 requires NoCutoff MM without parameter offsets/globals')
    return system


def seal_boundary_result(original, partition, info, *, manifest):
    ids = tuple(a.atom_id for a in original.topology.atoms)
    system, final_topology = info['system'], info['topology']
    old_to_new = tuple(info['oldToNew'])
    cap_count = len(partition.boundary_edges)
    version = 2 if (cap_count > 1 or
                    (cap_count == 0 and set(partition.ml_ids) != set(ids))) else 1
    requested_version = manifest.get('boundary_builder_version')
    if requested_version is not None and requested_version != version:
        raise UnsupportedCapability('boundary manifest version disagrees with zero/one/collection input semantics')
    if dict(partition.source_map) != {a: i for i, a in enumerate(ids)} or partition.rejected_conditions:
        raise IdentityError('sealer needs a resolved original partition')
    source = original_system(original, require_inventory_identity=(version == 2))
    count = system.getNumParticles()
    if (len(old_to_new) != len(ids) or len(set(old_to_new)) != len(ids)
            or any(isinstance(i, bool) or not isinstance(i, int) or i < 0 or i >= count for i in old_to_new)):
        raise IdentityError('builder requires a complete injective oldToNew map')
    if count != len(ids)+cap_count or final_topology.getNumAtoms() != count:
        raise IdentityError('final System/topology must contain every real atom and declared cap')
    actual_atoms = list(final_topology.atoms())
    for a, new in zip(original.topology.atoms, old_to_new):
        if actual_atoms[new].element != app.Element.getBySymbol(a.element) or system.isVirtualSite(new):
            raise IdentityError(f'oldToNew changes real identity/element: {a.atom_id}')
    expected_bonds = {frozenset((old_to_new[ids.index(b.atom1)],old_to_new[ids.index(b.atom2)])) for b in original.topology.bonds}
    actual_bonds = {frozenset((b.atom1.index,b.atom2.index)) for b in final_topology.bonds()}
    if actual_bonds != expected_bonds:
        raise IdentityError('final topology changes original connectivity')
    real_to_final = dict(zip(ids,old_to_new))
    model_map = {i:real_to_final[i] for i in partition.ml_ids}
    links = ()
    if cap_count:
        extras = set(range(count))-set(old_to_new)
        if len(extras) != cap_count:
            raise IdentityError('native virtual-site count differs from declared boundary collection')
        inverse = {new: old for old, new in zip(ids, old_to_new)}
        edge_order = tuple(sorted(partition.boundary_edges))
        edge_rank = {edge: rank for rank, edge in enumerate(edge_order)}
        expected_edges = set(edge_order)
        sites_by_edge = {}
        for extra in sorted(extras):
            if (not system.isVirtualSite(extra) or
                    actual_atoms[extra].element != app.element.hydrogen):
                raise IdentityError('every declared cap must be an actual hydrogen virtual site')
            site = system.getVirtualSite(extra)
            if not isinstance(site, mm.LocalCoordinatesSite) or site.getNumParticles() != 2:
                raise IdentityError('actual cap type differs from the fixed-length boundary rule')
            mapped_parents = tuple(site.getParticle(i) for i in range(2))
            try:
                edge = tuple(inverse[parent] for parent in mapped_parents)
            except KeyError as exc:
                raise IdentityError('actual cap parent is not a mapped real atom') from exc
            if edge not in expected_edges or edge in sites_by_edge:
                raise IdentityError(f'actual cap parent identity is undeclared or duplicated: {edge}')
            distance, y, z = site.getLocalPosition().value_in_unit(unit.nanometer)
            if (tuple(site.getOriginWeights()) != (1., 0.) or
                    tuple(site.getXWeights()) != (-1., 1.) or
                    tuple(site.getYWeights()) != (0., 0.) or y != 0. or z != 0. or distance <= 0.):
                raise IdentityError('actual virtual site differs from the fixed-length cap rule')
            requested_distance = manifest.get('requested_cap_distance_nm')
            if requested_distance is not None and float(distance) != float(requested_distance):
                raise IdentityError(f'actual cap distance differs from requested value for {edge}')
            sites_by_edge[edge] = (extra, site, float(distance))
        if set(sites_by_edge) != expected_edges:
            raise IdentityError('native virtual sites are not a bijection with declared boundary edges')
        rows = []
        nonbonded_forces = [f for f in system.getForces() if isinstance(f, mm.NonbondedForce)]
        for edge in edge_order:
            extra, site, distance = sites_by_edge[edge]
            a, b = edge
            cap_id = 'cap:' + hashlib.sha256((a + '\0' + b).encode()).hexdigest()
            input_index = len(partition.ml_ids) + edge_rank[edge]
            rows.append(LinkRecord(cap_id, a, b, extra, input_index,
                                   type(site).__name__, distance))
            model_map[cap_id] = extra
            if system.getParticleMass(extra).value_in_unit(unit.dalton) != 0.:
                raise IdentityError(f'cap has independent mass: {cap_id}')
            for force in nonbonded_forces:
                charge, sigma, epsilon = force.getParticleParameters(extra)
                if (charge.value_in_unit(unit.elementary_charge) != 0. or
                        epsilon.value_in_unit(unit.kilojoule_per_mole) != 0.):
                    raise IdentityError(f'cap has classical charge/LJ parameters: {cap_id}')
        links = tuple(rows)
    # OpenMM-ML preserves the original MM force order and appends model forces.
    retained = copy.deepcopy(system)
    for i in reversed(range(source.getNumForces(),retained.getNumForces())):
        retained.removeForce(i)
    if tuple(type(f) for f in retained.getForces()) != tuple(type(f) for f in source.getForces()):
        raise IdentityError('upstream retained-MM force layout changed')
    ledger = tuple(ForceRecord(i,type(f).__name__,f.getName(),f.getForceGroup(),f.usesPeriodicBoundaryConditions(),
                              {'force_sha256':hashlib.sha256(mm.XmlSerializer.serialize(f).encode()).hexdigest()})
                   for i,f in enumerate(system.getForces()))
    ownership = tuple(dict(cap_id=link.cap_id, raw_force_group=2,
                           raw_force_owner='mechanical-model',
                           projection_owner='native LocalCoordinatesSite exactly once')
                      for link in links)
    manifest = dict(manifest, boundary_builder_version=version,
                    boundary_edges=tuple(tuple(edge) for edge in sorted(partition.boundary_edges)),
                    cap_distances_nm=tuple((link.cap_id, link.distance_nm) for link in links),
                    cap_force_ownership=ownership,
                    original_mm_xml=original.prepared_mm_artifact, original_mm_sha256=original.prepared_mm_sha256,
                    retained_mm_xml=mm.XmlSerializer.serialize(retained),
                    boundary_terms=boundary_dispositions(source,retained,old_to_new,ids),
                    original_mm_inventory=inventory_system(source).content_identity,
                    periodicity='orthorhombic-pme-v1' if original.box_nm is not None else 'nonperiodic',
                    derivative_scope='all_real',model_dtype='float64')
    if original.box_nm is not None:
        manifest.update(box_nm=original.box_nm, periodic_geometry='bonded-molecule-unwrapping-before-native-sites',
                        electrostatic_background='openmm-uniform-neutralizing-background',
                        model_pbc=True, model_long_range=False,
                        periodic_scope='small fixed-volume CPU single points; no dynamics qualification')
    xml = mm.XmlSerializer.serialize(system)
    masses = tuple(system.getParticleMass(i).value_in_unit(unit.dalton) for i in range(count))
    constraints = tuple((int(a),int(b),d.value_in_unit(unit.nanometer)) for a,b,d in
                        (system.getConstraintParameters(i) for i in range(system.getNumConstraints())))
    return PhysicalBundle(xml,hashlib.sha256(xml.encode()).hexdigest(),original.topology,real_to_final,
                          model_map,old_to_new,partition.ml_ids,masses,constraints,ledger,manifest,
                          links=links, chemistry_states=partition.component_states)
