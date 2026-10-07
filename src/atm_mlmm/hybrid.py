"""Physical-builder dispatch. Protocols and ATM consume its sealed output."""
from dataclasses import asdict
import numpy as np
from openmm import unit

from .embeddings.mechanical import openmm_topology, original_system, seal_boundary_result
from .models.analytic_boundary import BoundaryProbe, registered_potential
from .schema import IdentityError, UnsupportedCapability


def build_physical(original, partition, model, embedding, *, probe=None, cap_distance_nm, checkpoint=None):
    """Build the shared mechanical Hamiltonian for admitted zero/one/two-cut inputs."""
    if (embedding.kind,embedding.policy_version,embedding.boundary_policy) != ('mechanical','1','protein_c_c') or embedding.periodic_convention not in ('nonperiodic','orthorhombic-pme-v1'):
        raise UnsupportedCapability('unadmitted G04 embedding policy')
    periodic = embedding.periodic_convention == 'orthorhombic-pme-v1'
    if periodic != (original.box_nm is not None):
        raise UnsupportedCapability('embedding convention and input box disagree')
    real_model = model.backend == 'mace-off23-small'
    collection_probe = False
    if real_model:
        from .models.mace import model_spec
        if model != model_spec() or probe is not None:
            raise UnsupportedCapability('unadmitted pinned MACE semantics or analytic probe')
    else:
        if probe is None or checkpoint is not None:
            raise UnsupportedCapability('analytic provider requires its probe and no checkpoint')
        if isinstance(probe, BoundaryProbe):
            if len(partition.boundary_edges) > 1:
                raise UnsupportedCapability('single-cap analytic API cannot describe a cap collection')
            environment_dependent = bool(probe.environment_k)
            backend = 'analytic-environment' if environment_dependent else 'analytic-local'
        else:
            from .models.analytic_caps import CapCollectionProbe
            if not isinstance(probe, CapCollectionProbe):
                raise UnsupportedCapability('unadmitted analytic probe record')
            collection_probe = True
            environment_dependent = probe.environment_dependent
            backend = 'analytic-cap-collection'
            declared_edges = {(term.ml_parent_id, term.mm_parent_id) for term in probe.cap_parameters}
            if declared_edges != set(partition.boundary_edges):
                raise IdentityError('analytic per-edge parameters must bijectively cover resolved boundaries')
        locality = 'environment_dependent' if environment_dependent else 'local'
        if (model.backend,model.locality,model.dtype,model.output_energy_convention,model.chemical_state_support,model.asset_digest) != (backend,locality,'float64','declared_relative_energy','neutral_singlet',None):
            raise UnsupportedCapability('unadmitted G04 analytic model semantics')
    if not {a.element for a in original.topology.atoms if a.atom_id in partition.ml_ids} <= set(model.elements) or 'H' not in model.elements:
        raise UnsupportedCapability('G04 model elements do not cover real atoms and cap')
    ids = tuple(a.atom_id for a in original.topology.atoms)
    if (dict(partition.source_map) != {a:i for i,a in enumerate(ids)} or
            partition.rejected_conditions):
        raise IdentityError('builder needs a resolved original partition for this topology')
    if not partition.boundary_edges and set(partition.ml_ids) != set(ids) and not (real_model or collection_probe):
        raise UnsupportedCapability('uncut reference requires the complete all-ML real-model description')
    # Re-run inherited connectivity/whole-ligand chemistry admission, rejecting
    # forged/stale selections and chemistry declarations rather than inferring
    # formal states from inherited MM partial charges.
    from .partition import resolve_partition
    from .schema import ComponentState, PartitionSpec
    if not partition.component_states:
        raise IdentityError('resolved partition lacks explicit component chemistry declarations')
    spec = PartitionSpec(partition.ml_ids,partition.protein_ml_ids,
                         partition.boundary_edges,partition.component_states)
    if resolve_partition(original.topology,spec) != partition:
        raise IdentityError('resolved partition differs from connectivity/explicit chemistry admission')
    if not np.isfinite(cap_distance_nm) or cap_distance_nm<=0:
        raise IdentityError('cap distance must be positive and finite')
    cap_count = len(partition.boundary_edges)
    boundary_version = 2 if (cap_count > 1 or
                             (cap_count == 0 and set(partition.ml_ids) != set(ids))) else 1
    system = original_system(original, require_inventory_identity=(boundary_version == 2))
    index = {a:i for i,a in enumerate(ids)}
    if real_model:
        from openmmml import MLPotential
        from .models.mace import CHECKPOINT, PinnedASECalculator
        calculator = PinnedASECalculator(CHECKPOINT if checkpoint is None else checkpoint)
        potential = MLPotential('ase')
        adapter_args = {'calculator': calculator}
        if periodic: adapter_args['mlLongRange'] = False
    else:
        if collection_probe:
            for term in probe.cap_parameters:
                if term.ml_parent_id not in partition.ml_ids or term.mm_parent_id in partition.ml_ids:
                    raise IdentityError('collection cap parameters must identify their real ML/MM parents')
                if term.environment_k and (term.environment_id not in index or term.environment_id in partition.ml_ids):
                    raise IdentityError('collection cap environment must be a real MM atom')
            for term in probe.environment_terms:
                if term.model_id not in partition.ml_ids:
                    raise IdentityError('collection environment model atom must be selected ML')
                if term.environment_id not in index or term.environment_id in partition.ml_ids:
                    raise IdentityError('collection environment term must target a real MM atom')
            for term in probe.ligand_terms:
                if term.atom_id not in partition.ml_ids:
                    raise IdentityError('collection ligand term must belong to the selected model input')
            from .models.analytic_caps import registered_potential as collection_potential
            potential = collection_potential(probe, particle_indices=index)
        else:
            partner = index.get(probe.partner_id)
            environment = index.get(probe.environment_id)
            if (probe.pair_k or probe.ligand_k) and probe.partner_id not in partition.ml_ids:
                raise IdentityError('analytic cap partner must be a real model atom')
            if probe.environment_k and (environment is None or probe.environment_id in partition.ml_ids):
                raise IdentityError('analytic environment must be a real MM atom')
            potential = registered_potential(probe,partner_particle=partner,environment_particle=environment)
        adapter_args = {}
        # The periodic ledger substitute is inert. Nonzero coordinate springs
        # are qualified only by their nonperiodic extension-contract probes.
        if periodic:
            if collection_probe:
                active_terms = (any(term.cap_k or term.environment_k for term in probe.cap_parameters)
                                or bool(probe.environment_terms)
                                or any(term.k for term in probe.ligand_terms))
            else:
                active_terms = any((probe.cap_k, probe.pair_k, probe.environment_k, probe.ligand_k))
            if active_terms:
                raise UnsupportedCapability('periodic analytic ledger substitute must be inert')
    distances = [(index[a],index[b],cap_distance_nm*unit.nanometer)
                 for a,b in sorted(partition.boundary_edges)]
    topology = openmm_topology(original.topology)
    if periodic: topology.setPeriodicBoxVectors(original.box_nm)
    info = potential.createMixedSystem(topology,system,
                [index[i] for i in partition.ml_ids],embedding='mechanical',returnInfo=True,
                forceGroup=2,linkAtomDistances=distances, **adapter_args)
    return seal_boundary_result(original,partition,info,manifest={
        'fixture_kind':'pinned_mace_candidate' if real_model else 'analytic_substitute','contract_version':1,
        'model_spec_identity':model.content_identity,'embedding_identity':embedding.content_identity,
        'partition_identity':partition.content_identity,'component_states':partition.component_states,
        'boundary_builder_version':boundary_version,
        'requested_cap_distance_nm':float(cap_distance_nm) if cap_count else None,
        'probe':None if probe is None else asdict(probe)})
