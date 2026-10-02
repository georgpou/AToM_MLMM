"""Project-owned physical preparation, separate from reserved-group exports."""
from .atm import PhysicalEvaluator, physical_system, validate_runtime
from .schema import PhysicalBundle, UnsupportedCapability


class PhysicalPreparation(PhysicalEvaluator):
    def __init__(self, physical, runtime):
        if not isinstance(physical, PhysicalBundle):
            raise UnsupportedCapability('preparation requires a physical bundle, not a production export')
        validate_runtime(runtime)
        if runtime.integrator != 'LangevinMiddle':
            raise UnsupportedCapability('preparation qualifies LangevinMiddle explicitly')
        self.bundle = physical
        system = physical_system(physical)
        for force in system.getForces():
            force.setForceGroup(0)
        self._open(system, runtime)
        self.integrator.setIntegrationForceGroups({0})


def build_preparation(physical, runtime):
    return PhysicalPreparation(physical, runtime)
