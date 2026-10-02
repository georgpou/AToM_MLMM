"""Metadata candidate admission never supplies numerical/chemical acceptance."""
from dataclasses import replace
import pytest


def test_pinned_mace_candidate_metadata(partition_spec):
    from atm_mlmm.capabilities import validate_request
    from atm_mlmm.models.mace import model_spec
    from atm_mlmm.protocols.abfe import make_protocol
    from atm_mlmm.schema import (CalculationRequest, CapabilitySet, EmbeddingSpec,
                                 MobileGroup, RuntimeSpec, UnsupportedCapability)
    model=model_spec()
    request=CalculationRequest(model,EmbeddingSpec('mechanical','1','protein_c_c','nonperiodic'),
          partition_spec,make_protocol((MobileGroup('A',('l-a1','l-a2'),('ligand',),'ligand-a'),),(1,0,0)),
          RuntimeSpec('Reference','double',(),.0005,300.,'NVT'))
    caps=CapabilitySet(('mace-off23-small',),('mechanical',),('abfe','rbfe'),('H','C','N','O'),
                       ('nonperiodic',),'all_real',('json-v1',))
    report=validate_request(request,caps)
    assert report.status=='passed' and report.measured_values['qualified'] is False
    for field,value in (('asset_digest','0'*64),('output_energy_convention','interaction_energy'),
                        ('chemical_state_support','charged'),('locality','environment_dependent'),
                        ('dtype','float32')):
        with pytest.raises(UnsupportedCapability):
            validate_request(replace(request,model=replace(model,**{field:value})),caps)
