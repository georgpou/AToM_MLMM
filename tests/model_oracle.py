"""G05 test-only cap projection and raw adapter, independent of native graphs."""
import numpy as np
import openmm as mm
from openmm import app, unit


def derived_input(bundle, snapshot):
    """Construct ordered raw coordinates and a full real Jacobian by formula."""
    ids = tuple(a.atom_id for a in bundle.topology.atoms)
    r = np.array([snapshot.positions_nm[snapshot.real_atom_ids.index(a)] for a in ids])
    elements = {a.atom_id: a.element for a in bundle.topology.atoms}
    z = {'H': 1, 'C': 6, 'N': 7, 'O': 8}
    links = {link.cap_id: link for link in bundle.links}
    raw, numbers, projections = [], [], []
    for atom_id in bundle.model_input_ids:
        projection = np.zeros((len(ids), 3, 3))
        if atom_id in links:
            link = links[atom_id]
            a, b = ids.index(link.ml_parent_id), ids.index(link.mm_parent_id)
            vector = r[b] - r[a]
            length = np.linalg.norm(vector)
            direction = vector / length
            cap = r[a] + link.distance_nm * direction
            jac = link.distance_nm / length * (np.eye(3) - np.outer(direction, direction))
            projection[a] = (np.eye(3) - jac).T
            projection[b] = jac.T
            raw.append(cap)
            numbers.append(1)
        else:
            i = ids.index(atom_id)
            raw.append(r[i])
            numbers.append(z[elements[atom_id]])
            projection[i] = np.eye(3)
        projections.append(projection)
    return numbers, np.asarray(raw), np.asarray(projections)


def project(raw_forces, projections):
    return np.einsum('mrij,mj->ri', projections, raw_forces)


def raw_adapter(numbers, positions_nm, platform='Reference'):
    """Actual OpenMM-ML ASE path on all raw coordinates (no virtual sites)."""
    from openmmml import MLPotential
    from atm_mlmm.models.mace import PinnedASECalculator
    topology = app.Topology()
    residue = topology.addResidue('joint', topology.addChain())
    for i, z in enumerate(numbers):
        topology.addAtom(str(i), app.Element.getByAtomicNumber(z), residue)
    system = MLPotential('ase').createSystem(topology, calculator=PinnedASECalculator())
    integrator = mm.VerletIntegrator(.0005)
    context = mm.Context(system, integrator, mm.Platform.getPlatformByName(platform),
                         {'Threads': '2'} if platform == 'CPU' else {})
    try:
        context.setPositions(positions_nm)
        state = context.getState(getEnergy=True, getForces=True)
        return (state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole),
                state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer))
    finally:
        del context, integrator
