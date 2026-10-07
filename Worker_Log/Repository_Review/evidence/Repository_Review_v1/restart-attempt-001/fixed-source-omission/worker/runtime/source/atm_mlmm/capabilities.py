"""Metadata admissibility is distinct from numerical qualification."""
from .schema import UnsupportedCapability, ValidationReport


def validate_request(request, capabilities):
    if request.embedding.kind != 'mechanical':
        raise UnsupportedCapability(f'actual {request.embedding.kind} embedding is unsupported')
    real_model = request.model.backend == 'mace-off23-small'
    if real_model:
        from .models.mace import model_spec
        if request.model != model_spec():
            raise UnsupportedCapability('unadmitted pinned MACE candidate metadata')
    elif request.model.backend not in ('analytic-local', 'analytic-environment'):
        raise UnsupportedCapability(f'backend not admitted to analytic CPU profile: {request.model.backend}')
    if request.embedding.policy_version != '1':
        raise UnsupportedCapability(f'policy_version not reviewed: {request.embedding.policy_version}')
    if request.embedding.boundary_policy != 'protein_c_c':
        raise UnsupportedCapability(f'boundary_policy unsupported: {request.embedding.boundary_policy}')
    if not real_model and request.model.output_energy_convention != 'declared_relative_energy':
        raise UnsupportedCapability(f'output_energy_convention unsupported for analytic providers: {request.model.output_energy_convention}')
    expected_locality = 'local' if real_model else {'analytic-local': 'local', 'analytic-environment': 'environment_dependent'}[request.model.backend]
    if request.model.locality != expected_locality:
        raise UnsupportedCapability(f'locality inconsistent with {request.model.backend}: expected {expected_locality}, got {request.model.locality}')
    for feature, value, declared in (
        ('backend', request.model.backend, capabilities.backends),
        ('embedding', request.embedding.kind, capabilities.embeddings),
        ('protocol', request.protocol.kind, capabilities.protocols),
        ('periodicity', request.embedding.periodic_convention, capabilities.periodicities),
    ):
        if value not in declared:
            raise UnsupportedCapability(f'{feature} not declared: {value}')
    if request.protocol.kind not in ('abfe', 'rbfe'):
        raise UnsupportedCapability(f'unknown protocol: {request.protocol.kind}')
    expected = 1 if request.protocol.kind == 'abfe' else 2
    if len(request.protocol.mobile_groups) != expected:
        raise UnsupportedCapability(f'{request.protocol.kind} requires {expected} mobile groups')
    mobile_ids = {a for group in request.protocol.mobile_groups for a in group.atom_ids}
    if not mobile_ids <= set(request.partition.ml_ids) or mobile_ids & set(request.partition.protein_ml_ids):
        raise UnsupportedCapability('mobile groups must be ML ligands, not protein atoms')
    if capabilities.derivative_scope != 'all_real':
        raise UnsupportedCapability('full real-coordinate derivative coverage required')
    if not set(request.model.elements) <= set(capabilities.elements):
        raise UnsupportedCapability('model elements not declared')
    if request.model.chemical_state_support != 'neutral_singlet':
        raise UnsupportedCapability('only neutral singlet chemistry admitted')
    if request.runtime.ensemble != 'NVT':
        raise UnsupportedCapability(f'ensemble unsupported: {request.runtime.ensemble}')
    if request.runtime.platform not in ('Reference', 'CPU') or request.runtime.device_allocation:
        raise UnsupportedCapability('analytic CPU profile requires Reference/CPU and no GPU allocation')
    if request.runtime.precision != 'double' or request.model.dtype != 'float64':
        raise UnsupportedCapability('analytic reference precision requires double/float64')
    if request.runtime.integrator not in ('LangevinMiddle', 'Verlet'):
        raise UnsupportedCapability(f'integrator requires separate qualification: {request.runtime.integrator}')
    if set(request.protocol.geometry_requests) != {'displacement_nm'}:
        raise UnsupportedCapability('only fixed translation geometry is admitted')
    if request.runtime.timestep_ps > 0.0005:
        raise UnsupportedCapability('timestep above initial 0.5 fs requires separate qualification')
    if request.embedding.periodic_convention != 'nonperiodic':
        raise UnsupportedCapability('periodic physical evaluation belongs to a later gate')
    profile = 'mace-off23-small-cpu-candidate' if real_model else 'core-analytic-cpu'
    return ValidationReport('request-admissibility', ('P0-REQ-023', 'P0-REQ-028'), profile, (),
                            {'qualified': False, 'level': 'metadata_only'}, {}, 'passed', (), ())
