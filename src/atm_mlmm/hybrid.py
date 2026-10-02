"""Physical-builder dispatch. Protocols and ATM consume its sealed output."""
from dataclasses import asdict
import numpy as np
from openmm import unit

from .embeddings.mechanical import openmm_topology, original_system, seal_boundary_result
from .models.analytic_boundary import registered_potential
from .schema import IdentityError, UnsupportedCapability


def build_physical(original, partition, model, embedding, *, probe=None, cap_distance_nm, checkpoint=None):
    """Nonperiodic mechanical construction, one admitted C-C cut and provider."""
    if (embedding.kind,embedding.policy_version,embedding.boundary_policy,embedding.periodic_convention) != ('mechanical','1','protein_c_c','nonperiodic'):
        raise UnsupportedCapability('unadmitted G04 embedding policy')
    real_model = model.backend == 'mace-off23-small'
    if real_model:
        from .models.mace import model_spec
        if model != model_spec() or probe is not None:
            raise UnsupportedCapability('unadmitted pinned MACE semantics or analytic probe')
    else:
        if probe is None or checkpoint is not None:
            raise UnsupportedCapability('analytic provider requires its probe and no checkpoint')
        locality = 'environment_dependent' if probe.environment_k else 'local'
        backend = 'analytic-environment' if probe.environment_k else 'analytic-local'
        if (model.backend,model.locality,model.dtype,model.output_energy_convention,model.chemical_state_support,model.asset_digest) != (backend,locality,'float64','declared_relative_energy','neutral_singlet',None):
            raise UnsupportedCapability('unadmitted G04 analytic model semantics')
    if not {a.element for a in original.topology.atoms if a.atom_id in partition.ml_ids} <= set(model.elements) or 'H' not in model.elements:
        raise UnsupportedCapability('G04 model elements do not cover real atoms and cap')
    ids = tuple(a.atom_id for a in original.topology.atoms)
    if dict(partition.source_map) != {a:i for i,a in enumerate(ids)} or len(partition.boundary_edges)!=1 or partition.rejected_conditions:
        raise IdentityError('G04 needs a resolved original partition with one admitted cut')
    # Re-run inherited connectivity/whole-ligand chemistry admission, rejecting
    # forged/stale resolved selections rather than trusting their type alone.
    from .partition import resolve_partition, _components
    from .schema import ComponentState, PartitionSpec
    graph = {a:set() for a in ids}
    for bond in original.topology.bonds:
        graph[bond.atom1].add(bond.atom2);graph[bond.atom2].add(bond.atom1)
    states = tuple(ComponentState(tuple(sorted(c)),0,1) for c in _components(set(partition.ml_ids),graph))
    spec = PartitionSpec(partition.ml_ids,partition.protein_ml_ids,partition.boundary_edges,states)
    if resolve_partition(original.topology,spec) != partition:
        raise IdentityError('G04 resolved partition differs from connectivity/chemistry admission')
    if not np.isfinite(cap_distance_nm) or cap_distance_nm<=0:
        raise IdentityError('cap distance must be positive and finite')
    system = original_system(original)
    index = {a:i for i,a in enumerate(ids)}
    if real_model:
        from openmmml import MLPotential
        from .models.mace import CHECKPOINT, PinnedASECalculator
        calculator = PinnedASECalculator(CHECKPOINT if checkpoint is None else checkpoint)
        potential = MLPotential('ase')
        adapter_args = {'calculator': calculator}
    else:
        partner = index.get(probe.partner_id)
        environment = index.get(probe.environment_id)
        if (probe.pair_k or probe.ligand_k) and probe.partner_id not in partition.ml_ids:
            raise IdentityError('analytic cap partner must be a real model atom')
        if probe.environment_k and (environment is None or probe.environment_id in partition.ml_ids):
            raise IdentityError('analytic environment must be a real MM atom')
        potential = registered_potential(probe,partner_particle=partner,environment_particle=environment)
        adapter_args = {}
    a,b = partition.boundary_edges[0]
    info = potential.createMixedSystem(openmm_topology(original.topology),system,
                [index[i] for i in partition.ml_ids],embedding='mechanical',returnInfo=True,
                forceGroup=2,linkAtomDistances=[(index[a],index[b],cap_distance_nm*unit.nanometer)], **adapter_args)
    return seal_boundary_result(original,partition,info,manifest={
        'fixture_kind':'pinned_mace_candidate' if real_model else 'analytic_substitute','contract_version':1,
        'model_spec_identity':model.content_identity,'embedding_identity':embedding.content_identity,
        'partition_identity':partition.content_identity,'probe':None if probe is None else asdict(probe)})
