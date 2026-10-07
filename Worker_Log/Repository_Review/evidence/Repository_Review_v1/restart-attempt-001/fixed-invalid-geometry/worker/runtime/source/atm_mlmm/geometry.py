"""Fixed identity-based full-particle translations, independent of physics."""
from .identity import validate_mobile_groups
from .schema import IdentityError, TransferDefinition, UnsupportedCapability


def resolve_protocol(bundle, protocol):
    if protocol.kind not in ('abfe', 'rbfe'):
        raise UnsupportedCapability(f'unknown transfer protocol: {protocol.kind}')
    expected = 1 if protocol.kind == 'abfe' else 2
    if len(protocol.mobile_groups) != expected:
        raise UnsupportedCapability(f'{protocol.kind} requires {expected} complete mobile groups')
    if set(protocol.geometry_requests) != {'displacement_nm'}:
        raise UnsupportedCapability('only fixed translation geometry requests admitted')
    validate_mobile_groups(bundle.topology, protocol)
    mobile = {a for g in protocol.mobile_groups for a in g.atom_ids}
    if not mobile <= set(bundle.ml_atom_ids):
        raise UnsupportedCapability('all mobile ligand atoms must belong to fixed ML membership')
    count = len(bundle.masses_da)
    map0 = ((0., 0., 0.),)*count
    map1 = list(map0)
    displacement = protocol.geometry_requests['displacement_nm']
    # Presets specify signs; the shared assembler consumes the resulting maps.
    for group, sign in zip(protocol.mobile_groups, (1., -1.)):
        for atom_id in group.atom_ids:
            map1[bundle.real_to_final[atom_id]] = tuple(sign*x for x in displacement)
    return TransferDefinition(bundle.content_identity, protocol, map0, map1, count)


def final_positions(bundle, snapshot):
    expected = tuple(a.atom_id for a in bundle.topology.atoms)
    if snapshot.real_atom_ids != expected:
        raise IdentityError('snapshot real-atom order/coverage differs from physical topology')
    coordinates = snapshot.positions_nm
    periodic = bundle.manifest.get('periodicity') == 'orthorhombic-pme-v1'
    if periodic:
        if snapshot.box_nm is None:
            raise UnsupportedCapability('periodic physical evaluation requires a box')
        from .ledger import validate_pme_system
        # The immutable retained artifact has all of the actual MM settings.
        import openmm as mm
        validate_pme_system(mm.XmlSerializer.deserialize(bundle.manifest['retained_mm_xml']), snapshot.box_nm)
        coordinates = unwrap_molecules(bundle.topology, coordinates, snapshot.box_nm)
    elif snapshot.box_nm is not None:
        raise UnsupportedCapability('nonperiodic physical evaluation cannot acquire a box')
    # Derived entries are placeholders only. The Context reconstructs them
    # with its validated virtual-site machinery after every setPositions.
    positions = [(0., 0., 0.)]*len(bundle.masses_da)
    for atom_id, coordinate in zip(expected, coordinates):
        positions[bundle.real_to_final[atom_id]] = tuple(coordinate)
    for link in bundle.links:
        a, b = (positions[bundle.real_to_final[parent]] for parent in (link.ml_parent_id, link.mm_parent_id))
        if a == b:
            raise IdentityError(f'coincident link parents: {link.ml_parent_id}-{link.mm_parent_id}')
    return tuple(positions)


def orthorhombic_lengths(box_nm):
    """Admit positive axis-aligned orthorhombic cells only."""
    import numpy as np
    b = np.asarray(box_nm, dtype=float)
    if b.shape != (3, 3) or not np.isfinite(b).all() or np.any(np.diag(b) <= 0) or np.any(b != np.diag(np.diag(b))):
        raise UnsupportedCapability('only positive orthorhombic boxes admitted')
    return np.diag(b).copy()


def minimum_image(delta, box_nm):
    import numpy as np
    lengths = orthorhombic_lengths(box_nm)
    d = np.asarray(delta, dtype=float)
    if d.shape[-1:] != (3,) or not np.isfinite(d).all():
        raise IdentityError('image displacement requires finite Cartesian vectors')
    return d - lengths*np.floor(d/lengths + .5)


def unwrap_molecules(topology, positions_nm, box_nm):
    """Reconstruct bonded molecules before native fixed-length cap construction.

    Anchor each complete molecule in the primary cell. Reject ambiguous bond
    images and nonzero winding rather than creating a cap across a box.
    """
    import numpy as np
    from .schema import NumericalDomainError
    lengths = orthorhombic_lengths(box_nm)
    x = np.asarray(positions_nm, dtype=float)
    ids = tuple(a.atom_id for a in topology.atoms)
    if x.shape != (len(ids), 3) or not np.isfinite(x).all():
        raise IdentityError('unwrapping requires every finite real coordinate')
    index = {a:i for i,a in enumerate(ids)}
    graph = {a:[] for a in ids}
    for bond in topology.bonds:
        graph[bond.atom1].append(bond.atom2); graph[bond.atom2].append(bond.atom1)
    result = np.empty_like(x)
    for molecule in topology.molecules:
        anchor = molecule.atom_ids[0]
        result[index[anchor]] = np.mod(x[index[anchor]], lengths)
        seen, queue = {anchor}, [anchor]
        for a in queue:
            for b in graph[a]:
                d = minimum_image(x[index[b]]-x[index[a]], box_nm)
                if np.any(np.isclose(np.abs(d), lengths*.5, rtol=0, atol=1e-10)):
                    raise NumericalDomainError('ambiguous half-box bonded image')
                value = result[index[a]] + d
                if b in seen:
                    if not np.allclose(value, result[index[b]], rtol=0, atol=1e-9):
                        raise NumericalDomainError('bonded molecule has nonzero periodic winding')
                else:
                    result[index[b]] = value; seen.add(b); queue.append(b)
        if seen != set(molecule.atom_ids):
            raise IdentityError('molecule connectivity differs from declared complete component')
    return result


def periodic_edges(positions_nm, box_nm, cutoff_nm):
    """Unique short-range directed edges and integer shifts in the safe cell."""
    import numpy as np
    lengths = orthorhombic_lengths(box_nm)
    x = np.asarray(positions_nm, dtype=float)
    if not np.isfinite(cutoff_nm) or cutoff_nm <= 0 or np.any(lengths <= 2*cutoff_nm):
        raise UnsupportedCapability('model cutoff needs a unique image and no self-image edges')
    if x.ndim != 2 or x.shape[1] != 3 or not np.isfinite(x).all():
        raise IdentityError('graph needs finite Cartesian coordinates')
    edges = []
    for i in range(len(x)):
        for j in range(len(x)):
            if i == j: continue
            d = x[j]-x[i]
            shift = -np.floor(d/lengths + .5).astype(int)
            if np.linalg.norm(d+lengths*shift) < cutoff_nm:
                edges.append((i, j, tuple(int(v) for v in shift)))
    return tuple(edges)


def validate_bulk_clearance(ligand_nm, protein_nm, caps_nm, box_nm, *, cutoff_nm, margin_nm=.2, other_ligands_nm=()):
    """Setup diagnostic over the full protein, caps and other complete ligands.

    This initial margin is not a trajectory guarantee or a restraint/correction.
    """
    import numpy as np
    from .schema import NumericalDomainError
    orthorhombic_lengths(box_nm)
    arrays = [np.asarray(v, dtype=float).reshape((-1,3)) for v in (protein_nm,caps_nm,other_ligands_nm)]
    ligand = np.asarray(ligand_nm,dtype=float)
    obstacles = np.vstack(arrays)
    if ligand.ndim != 2 or ligand.shape[1] != 3 or not len(ligand) or not len(obstacles) or not np.isfinite(ligand).all() or not np.isfinite(obstacles).all():
        raise IdentityError('clearance needs finite complete ligand and protein coordinates')
    if not np.isfinite(cutoff_nm) or cutoff_nm <= 0 or not np.isfinite(margin_nm) or margin_nm < 0:
        raise IdentityError('clearance cutoff/margin must be finite and nonnegative')
    distances = np.linalg.norm(minimum_image(ligand[:,None,:]-obstacles[None,:,:],box_nm),axis=2)
    distance = float(np.min(distances))
    if distance < cutoff_nm + margin_nm:
        raise NumericalDomainError(f'periodic bulk clearance {distance} nm below {cutoff_nm+margin_nm} nm')
    return {'minimum_distance_nm':distance,'required_distance_nm':cutoff_nm+margin_nm,
            'scope':'initial geometry diagnostic, not a free-energy correction'}


def validate_transfer(bundle, transfer):
    if transfer != resolve_protocol(bundle, transfer.protocol):
        raise IdentityError('fixed full-particle maps or physical membership differ from the protocol')


def validate_sites(system, bundle):
    """Verify executable derived sites against sealed identity-based records."""
    import openmm as mm
    from openmm import unit
    declared={link.final_particle_index for link in bundle.links}
    actual={i for i in range(system.getNumParticles()) if system.isVirtualSite(i)}
    if actual != declared:
        raise IdentityError('actual derived particles differ from sealed link records')
    for link in bundle.links:
        site=system.getVirtualSite(link.final_particle_index)
        if not isinstance(site,mm.LocalCoordinatesSite) or site.getNumParticles()!=2:
            raise IdentityError('link virtual-site type/parent count mismatch')
        parents=tuple(site.getParticle(i) for i in range(2))
        if parents != (bundle.real_to_final[link.ml_parent_id],bundle.real_to_final[link.mm_parent_id]):
            raise IdentityError('link parent identities differ from actual virtual site')
        if (tuple(site.getOriginWeights()),tuple(site.getXWeights()),tuple(site.getYWeights()),
            tuple(site.getLocalPosition().value_in_unit(unit.nanometer))) != ((1.,0.),(-1.,1.),(0.,0.),(link.distance_nm,0.,0.)):
            raise IdentityError('link distance/weights differ from the fixed-length rule')
        if any(link.final_particle_index in system.getConstraintParameters(i)[:2] for i in range(system.getNumConstraints())):
            raise IdentityError('derived cap cannot have a Cartesian constraint')
        for force in system.getForces():
            if isinstance(force,mm.NonbondedForce):
                q,_,e=force.getParticleParameters(link.final_particle_index)
                if q.value_in_unit(unit.elementary_charge)!=0 or e.value_in_unit(unit.kilojoule_per_mole)!=0:
                    raise IdentityError('cap has unintended classical charge/LJ interaction')
