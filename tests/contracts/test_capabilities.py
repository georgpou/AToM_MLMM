from dataclasses import replace
import pytest


def test_unsupported_combination_fails_closed(partition_spec):
    from atm_mlmm.capabilities import validate_request
    from atm_mlmm.schema import (CalculationRequest, CapabilitySet, EmbeddingSpec,
                                 ModelSpec, MobileGroup, RuntimeSpec, UnsupportedCapability)
    from atm_mlmm.protocols.abfe import make_protocol
    protocol = make_protocol((MobileGroup('A', ('l-a1', 'l-a2'), ('ligand',), 'ligand-a'),), (1, 0, 0))
    model = ModelSpec('analytic-local', None, 'declared_relative_energy', ('H', 'C'), 'neutral_singlet', 'local', 'float64')
    request = CalculationRequest(model, EmbeddingSpec('mechanical', '1', 'protein_c_c', 'nonperiodic'),
                                 partition_spec, protocol, RuntimeSpec('Reference', 'double', (), 0.0005, 300.0, 'NVT'))
    capabilities = CapabilitySet(('analytic-local',), ('mechanical',), ('abfe', 'rbfe'), ('H', 'C'), ('nonperiodic',), 'all_real', ('json-v1',))
    report = validate_request(request, capabilities)
    assert report.status == 'passed'
    assert report.measured_values['qualified'] is False
    with pytest.raises(UnsupportedCapability, match='electrostatic'):
        validate_request(replace(request, embedding=replace(request.embedding, kind='electrostatic')), capabilities)
    # Adding an advertised feature cannot introduce an unimplemented Hamiltonian.
    with pytest.raises(UnsupportedCapability, match='electrostatic'):
        validate_request(replace(request, embedding=replace(request.embedding, kind='electrostatic')),
                         replace(capabilities, embeddings=('mechanical', 'electrostatic')))
    with pytest.raises(UnsupportedCapability, match='NPT'):
        validate_request(replace(request, runtime=replace(request.runtime, ensemble='NPT')), capabilities)
    with pytest.raises(UnsupportedCapability, match='derivative'):
        validate_request(request, replace(capabilities, derivative_scope='ml_only'))
    with pytest.raises(UnsupportedCapability):
        validate_request(replace(request, model=replace(model, backend='unknown')), capabilities)


@pytest.mark.parametrize('field,value', [('precision', 'mixed'), ('integrator', 'MTS'),
                                        ('platform', 'CUDA')])
def test_runtime_metadata_does_not_admit_unqualified_settings(partition_spec, field, value):
    from atm_mlmm.capabilities import validate_request
    from atm_mlmm.schema import CalculationRequest, CapabilitySet, EmbeddingSpec, ModelSpec, MobileGroup, RuntimeSpec, UnsupportedCapability
    from atm_mlmm.protocols.abfe import make_protocol
    request = CalculationRequest(
        ModelSpec('analytic-local', None, 'declared_relative_energy', ('H', 'C'), 'neutral_singlet', 'local', 'float64'),
        EmbeddingSpec('mechanical', '1', 'protein_c_c', 'nonperiodic'), partition_spec,
        make_protocol((MobileGroup('a', ('l-a1', 'l-a2'), ('ligand',), 'ligand-a'),), (1, 0, 0)),
        RuntimeSpec('Reference', 'double', (), 0.0005, 300.0, 'NVT'))
    caps = CapabilitySet(('analytic-local',), ('mechanical',), ('abfe',), ('H', 'C'), ('nonperiodic',), 'all_real', ('json-v1',))
    with pytest.raises(UnsupportedCapability):
        validate_request(replace(request, runtime=replace(request.runtime, **{field: value})), caps)


def test_fixed_translation_description_rejects_wrong_shape_and_nonfinite():
    from atm_mlmm.protocols.abfe import make_protocol
    from atm_mlmm.schema import MobileGroup, MalformedInput
    group = MobileGroup('a', ('id',), ('ligand',), 'ligand')
    for vector in ((1, 2), (float('nan'), 0, 0), ('one', 0, 0)):
        with pytest.raises(MalformedInput):
            make_protocol((group,), vector)
    # Identity-map controls are permitted; no artificial nonzero-map requirement.
    assert make_protocol((group,), (0, 0, 0)).geometry_requests['displacement_nm'] == (0, 0, 0)
