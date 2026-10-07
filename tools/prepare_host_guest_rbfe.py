#!/usr/bin/env python
"""Freeze a deterministic geometry-only methanol-to-ethanol RBFE preflight."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import openmm as mm
from openmm import unit
from rdkit import Chem, rdBase
from rdkit.Chem import rdMolDescriptors

_TOOL_DIR = Path(__file__).resolve().parent
if str(_TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOL_DIR))
from prepare_cloud_host_guest import molecule as _embed_molecule

from atm_mlmm.ledger import inventory_system
from atm_mlmm.schedule import production_schedule
from atm_mlmm.schema import (AtomIdentity, Bond, ComponentState, CorrectionRecord,
                             MoleculeState, PartitionSpec, Snapshot, SystemInput,
                             ThermodynamicSpec, TopologyView, to_json)


_RADII = {'H': .12, 'C': .17, 'O': .152}
_HOST_SMILES = 'O1CCOCCOCCOCCOCCOCC1'
_SMILES = {'A': 'CO', 'B': 'CCO'}


def _bound_pose(host, host_atoms, mol, coords):
    oxygen_ids = [a.GetIdx() for a in host.GetAtoms() if a.GetSymbol() == 'O']
    guest_oxygen = next(a.GetIdx() for a in mol.GetAtoms() if a.GetSymbol() == 'O')
    donor_hydrogen = next(a.GetIdx() for a in mol.GetAtomWithIdx(guest_oxygen).GetNeighbors()
                          if a.GetSymbol() == 'H')
    direction = coords[donor_hydrogen] - coords[guest_oxygen]
    direction /= np.linalg.norm(direction)
    helper = np.array((1., 0., 0.)) if abs(direction[0]) < .9 else np.array((0., 1., 0.))
    side = helper - direction * np.dot(helper, direction)
    side /= np.linalg.norm(side)
    local_basis = np.array((side, np.cross(direction, side), direction))
    local = (coords - coords[guest_oxygen]) @ local_basis.T
    limits = np.array([[_RADII[a.GetSymbol()] + _RADII[b.GetSymbol()]
                        for b in host_atoms] for a in mol.GetAtoms()])
    # Fixed geometry-only ordering: every host oxygen, then radial/+z/-z.
    for oxygen_id in oxygen_ids:
        radial = host.GetConformer().GetPositions()[oxygen_id]
        radial = radial - np.dot(radial, (0., 0., 1.)) * np.array((0., 0., 1.))
        if np.linalg.norm(radial) < 1.e-10:
            radial = np.array((1., 0., 0.))
        radial /= np.linalg.norm(radial)
        for approach in (radial, np.array((0., 0., 1.)), np.array((0., 0., -1.))):
            desired = -approach
            helper = np.array((1., 0., 0.)) if abs(desired[0]) < .9 else np.array((0., 1., 0.))
            side = helper - desired * np.dot(helper, desired)
            side /= np.linalg.norm(side)
            basis = np.array((side, np.cross(desired, side), desired))
            target = host.GetConformer().GetPositions()[oxygen_id] / 10.
            candidate = local @ basis + target + .30 * approach
            distance = np.linalg.norm(candidate[:, None, :] - host_coords(host)[None, :, :], axis=2)
            ratios = distance / limits
            if float(np.min(ratios)) >= .65:
                return candidate, oxygen_id, tuple(float(v) for v in approach), float(np.min(ratios))
    raise RuntimeError('no whole-host-admitted pose in the fixed geometry-only ordering')


def host_coords(host):
    return np.asarray(host.GetConformer().GetPositions(), dtype=float) / 10.


def _atom_ids(prefix, mol):
    return tuple(f'{prefix}{i:03d}' for i in range(mol.GetNumAtoms()))


def _typed_thermodynamics():
    ids = ('translation_standard_state', 'bound_release', 'orientation',
           'conformation', 'state_counting', 'midpoint_bridge')
    corrections = tuple(CorrectionRecord(key, 'required_uncomputed', None, None,
        'No adequate molecular sampling or documented, applicable correction calculation is present.')
        for key in ids)
    return ThermodynamicSpec(
        observable='relative_standard_binding_free_energy',
        endpoint_weights={'endpoint-A': -1., 'endpoint-B': 1.},
        sign_convention='B_minus_A',
        state_connections=(('endpoint-A', 'midpoint-bridge'), ('midpoint-bridge', 'endpoint-B')),
        endpoint_descriptions={
            'endpoint-A': 'Bound methanol minus bulk methanol in the declared host and spectator domains; physical parameters are missing.',
            'endpoint-B': 'Bound ethanol minus bulk ethanol in the same declared host and spectator domains; physical parameters are missing.'},
        correction_obligations=ids, corrections=corrections,
        standard_volume_nm3=1.6605390671738467,
        domain_description='Nonperiodic geometry-only host plus explicit bound/bulk atom groups; no physical solvent or endpoint domain claim.',
        restraint_description='No restraint-release calculation is defined; restraint atoms/domain remain unresolved.',
        orientation_description='No orientation integral or correction procedure is computed.',
        state_counting_description='One molecule per endpoint; nonduplicated state counting has not been established for a physical route.')


def _write(path, value, *, typed=False):
    text = to_json(value) if typed else json.dumps(value, sort_keys=True, indent=2, allow_nan=False)
    Path(path).write_text(text + '\n')
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    host, host_xyz = _embed_molecule(_HOST_SMILES, 61709)
    guest_a, a_xyz = _embed_molecule(_SMILES['A'], 61710)
    guest_b, b_xyz = _embed_molecule(_SMILES['B'], 61711)
    # The crown is centered and placed in a deterministic canonical orientation.
    host_oxygen = [a.GetIdx() for a in host.GetAtoms() if a.GetSymbol() == 'O']
    host_xyz -= host_xyz[host_oxygen].mean(axis=0)
    _, _, basis = np.linalg.svd(host_xyz[host_oxygen], full_matrices=False)
    normal = basis[-1]
    if normal[2] < 0:
        normal = -normal
    axis = host_xyz[host_oxygen[0]] - np.dot(host_xyz[host_oxygen[0]], normal) * normal
    axis /= np.linalg.norm(axis)
    rotation = np.array((axis, np.cross(normal, axis), normal))
    host_xyz = host_xyz @ rotation.T
    for i, position in enumerate(host_xyz * 10.):
        host.GetConformer().SetAtomPosition(i, position)

    # Use a declarative molecule-relative geometry order; no energy or model score.
    a_bound, a_oxygen, a_approach, a_ratio = _bound_pose(host, host.GetAtoms(), guest_a, a_xyz)
    # _bound_pose uses the conformer in angstrom, now aligned with canonical host coords.
    b_bound, b_oxygen, b_approach, b_ratio = _bound_pose(host, host.GetAtoms(), guest_b, b_xyz)
    displacement = np.array((2.4, 0., 0.))
    a_bulk, b_bulk = a_bound + displacement, b_bound + displacement
    all_host = host_xyz
    all_guests = (guest_a, guest_b)
    bound = (a_bound, b_bound)
    for mol, coords in zip(all_guests, bound):
        radii = np.array([_RADII[a.GetSymbol()] for a in mol.GetAtoms()])[:, None]
        host_radii = np.array([_RADII[a.GetSymbol()] for a in host.GetAtoms()])[None, :]
        if float(np.min(np.linalg.norm(coords[:, None, :] - all_host[None, :, :], axis=2) /
                        (radii + host_radii))) < .65:
            raise RuntimeError('bound pose failed complete host contact admission')
    # For the opposite map, ligand B occupies its bound pose and ligand A goes to bulk.
    if (float(np.min(np.linalg.norm(a_bound[:, None, :] - b_bulk[None, :, :], axis=2))) < .65 or
            float(np.min(np.linalg.norm(a_bulk[:, None, :] - b_bound[None, :, :], axis=2))) < .65):
        raise RuntimeError('one of the two mapped guest/guest clearances failed')
    # Check full-host contacts and both bulk placements as actually mapped.
    for bulk in (a_bulk, b_bulk):
        if float(np.min(np.linalg.norm(bulk[:, None, :] - all_host[None, :, :], axis=2))) < .65:
            raise RuntimeError('bulk placement is not clear of the complete host')

    atoms, bonds, molecules, positions, components = [], [], [], [], []
    for mol, xyz, prefix, molecule_id, role, chain in (
            (host, host_xyz, 'h', 'host-18-crown-6', 'host', 'H'),
            (guest_a, a_bound, 'a', 'ligand-methanol-A', 'ligand', 'A'),
            (guest_b, b_bulk, 'b', 'ligand-ethanol-B', 'ligand', 'B')):
        ids = _atom_ids(prefix, mol)
        atoms.extend(AtomIdentity(atom_id, atom.GetSymbol(), chain, '1', '', atom.GetSymbol() + str(i))
                     for i, (atom_id, atom) in enumerate(zip(ids, mol.GetAtoms())))
        bonds.extend(Bond(ids[b.GetBeginAtomIdx()], ids[b.GetEndAtomIdx()],
                          b.GetBondTypeAsDouble()) for b in mol.GetBonds())
        molecules.append(MoleculeState(molecule_id, ids, role, 0, 1))
        components.append(ComponentState(ids, 0, 1))
        positions.extend(tuple(float(v) for v in row) for row in xyz)
    ids = tuple(a.atom_id for a in atoms)
    topology = TopologyView(tuple(atoms), tuple(bonds), tuple(molecules))

    # This all-ML vacuum fixture carries an explicitly inert original-MM ledger.
    system = mm.System()
    nonbonded = mm.NonbondedForce()
    for atom in atoms:
        system.addParticle(Chem.GetPeriodicTable().GetAtomicWeight(atom.element))
        nonbonded.addParticle(0., .3, 0.)
    nonbonded.setName('inert ledger; no physical parameter route')
    system.addForce(nonbonded)
    xml = mm.XmlSerializer.serialize(system)
    provenance = {
        'physical_scope': 'all-ML vacuum plumbing only; original MM is explicitly inert',
        'geometry': 'RDKit ETKDGv3/MMFF94s conformers with canonical deterministic orientation',
        'selection': 'fixed geometry ordering only; no model, quantum, experimental, docking, or energy pose score',
        'host_smiles': _HOST_SMILES,
        'ligand_smiles': _SMILES,
        'seeds': {'host': 61709, 'methanol_A': 61710, 'ethanol_B': 61711},
        'host_oxygen_order': host_oxygen,
        'bound_geometry': {
            'methanol_A': {'host_oxygen': a_oxygen, 'approach': a_approach,
                           'O_O_distance_nm': .30, 'whole_host_minimum_Bondi_ratio': a_ratio},
            'ethanol_B': {'host_oxygen': b_oxygen, 'approach': b_approach,
                          'O_O_distance_nm': .30, 'whole_host_minimum_Bondi_ratio': b_ratio},
        },
        'displacement_nm': displacement.tolist(),
        'bulk_ligands': {'methanol_A': 'map1 + displacement', 'ethanol_B': 'map0; map1 - displacement'},
        'parameter_route': 'blocked: prepared-mm-v1 supplies complete methanol/ethanol GAFF 2.2.20 / AM1-BCC ligand artifacts but no 18-crown-6 host parameters; its manifest records G07 quantum launch budget/review pending, and no crown charge/parameter calculation is authorized here',
        'parameter_route_source': {
            'path': 'fixtures/fragment_ligand/prepared-mm-v1/manifest.json',
            'sha256': 'b956f580c233ca84cf1c88c855f13bb060e14f4178a479177ba535d153b81c08',
            'state': 'prepared; G07 quantum launch budget/review pending',
            'software': {'gaff': '2.2.20', 'ambertools': '26.0',
                         'openmm': '8.6.1', 'openff_toolkit': '0.18.0'},
        },
        'rdkit': rdBase.rdkitVersion,
        'openmm': mm.version.version,
    }
    original = SystemInput(
        xml, hashlib.sha256(xml.encode()).hexdigest(), topology, tuple(positions), None,
        tuple(system.getParticleMass(i).value_in_unit(unit.dalton)
              for i in range(system.getNumParticles())), (), provenance,
        prepared_mm_inventory_identity=inventory_system(system).content_identity)
    partition = PartitionSpec(ids, (), (), tuple(components))
    snapshot = Snapshot(ids, tuple(positions), None)
    geometry = {
        'schema': 'host-guest-geometry-admission-v1', 'geometry_only': True,
        'maps': ['map0', 'map1'], 'periodic_images': 'not_applicable_nonperiodic_input',
        'selection': 'fixed candidate ordering; no scored pose choice',
        'complete_static_host': True, 'guest_guest_contact_check': 'complete_all_atom_pairs_both_maps',
        'required_bondi_ratio': .65, 'required_bulk_static_clearance_nm': .65,
        'displacement_nm': displacement.tolist(), 'checks': [
            {'map': 'map0', 'bound': 'methanol_A', 'bulk': 'ethanol_B', 'whole_host': True},
            {'map': 'map1', 'bound': 'ethanol_B', 'bulk': 'methanol_A', 'whole_host': True}],
        'status': 'geometry_admitted_only; not a physical parameter or affinity result',
    }
    run_definitions = {
        'schema': 'host-guest-rbfe-run-definitions-v1', 'binding_result': 'not_evaluated',
        'scope': 'frozen proposals only; no adequate sampling authorized or performed',
        'shared_conventions': {
            'host': 'same complete 18-crown-6 atoms and coordinates',
            'spectator': 'none in this plumbing fixture; physical solvent remains undefined',
            'model': 'same all-ML selected real atoms; B common builder zero-cut path',
            'caps': 'none', 'box': 'nonperiodic', 'constraints': [],
            'restraints': 'static host anchor for mechanics only; no correction interpretation',
            'physical_parameter_route': 'blocked_missing_host_parameters',
        },
        'runs': [
            {'run_id': 'A_to_A_identity', 'direction': 'methanol_A_to_methanol_A',
             'initialization': 'independent deterministic start from frozen geometry', 'seed': 19001,
             'status': 'proposed_not_run',
             'retention': {'retain_all_declared_frames_and_raw_state_energies': True,
                           'frame_count_and_sampling_ceiling': 'predeclare only after physical input and resource profile are admitted'},
             'correlation': 'estimate per-state integrated autocorrelation and effective sample count',
             'overlap': 'report adjacent-state overlap and endpoint support',
             'uncertainty': 'block resampling or independent-run resampling after adequate sampling; report standard error separately from replicate spread and include covariance when combining legs',
             'resource_estimate': {'status': 'wall_time_blocked_until_physical_rate_and_retention_are_defined',
                                   'schedule_states': 3, 'workers': 3, 'cpu_threads_per_worker': 2,
                                   'memory_limit_gib': 8,
                                   'operation_count_formula': 'schedule_states * retained_frames_per_state * integration_steps_per_frame'}},
            {'run_id': 'forward_A_to_B', 'direction': 'methanol_A_to_ethanol_B',
             'initialization': 'frozen map0 geometry', 'seed': 19002, 'status': 'proposed_not_run',
             'retention': {'retain_all_declared_frames_and_raw_state_energies': True,
                           'frame_count_and_sampling_ceiling': 'predeclare only after physical input and resource profile are admitted'},
             'correlation': 'estimate per-state integrated autocorrelation and effective sample count',
             'overlap': 'report adjacent-state overlap and endpoint support',
             'uncertainty': 'block resampling or independent-run resampling after adequate sampling; report standard error separately from replicate spread and include covariance when combining legs',
             'resource_estimate': {'status': 'wall_time_blocked_until_physical_rate_and_retention_are_defined',
                                   'schedule_states': 3, 'workers': 3, 'cpu_threads_per_worker': 2,
                                   'memory_limit_gib': 8,
                                   'operation_count_formula': 'schedule_states * retained_frames_per_state * integration_steps_per_frame'}},
            {'run_id': 'independent_reverse_B_to_A', 'direction': 'ethanol_B_to_methanol_A',
             'initialization': 'independently initialize from frozen map1 geometry', 'seed': 19003,
             'status': 'proposed_not_run',
             'retention': {'retain_all_declared_frames_and_raw_state_energies': True,
                           'frame_count_and_sampling_ceiling': 'predeclare only after physical input and resource profile are admitted'},
             'correlation': 'estimate separately from forward trajectory',
             'overlap': 'report reverse adjacent-state overlap and endpoint support',
             'uncertainty': 'block resampling or independent-run resampling; compare with forward estimate, report replicate spread separately and include covariance when combining legs',
             'resource_estimate': {'status': 'wall_time_blocked_until_physical_rate_and_retention_are_defined',
                                   'schedule_states': 3, 'workers': 3, 'cpu_threads_per_worker': 2,
                                   'memory_limit_gib': 8,
                                   'operation_count_formula': 'schedule_states * retained_frames_per_state * integration_steps_per_frame'}},
            {'run_id': 'matched_cycle_closure', 'direction': 'A_to_B_to_A cycle',
             'initialization': 'independent cycle controls with matched host, spectator, model, caps, box, constraints and restraints',
             'seed': 19004, 'status': 'blocked_unmatched_physical_terms',
             'unmatched_terms': ['physical solvent/host parameters', 'domain/restraint correction definitions'],
             'retention': {'retain_all_declared_frames_and_raw_state_energies': True,
                           'frame_count_and_sampling_ceiling': 'predeclare only after every physical closure term and resource profile are admitted'},
             'correlation': 'estimate by window after physical route is admitted',
             'overlap': 'report state-wise overlap after physical route is admitted',
             'uncertainty': 'block/independent-run resampling and covariance after physical route is admitted; S06 effective-support flags trigger investigation only',
             'resource_estimate': {'status': 'blocked_unmatched_physical_terms',
                                   'schedule_states': 6, 'workers': 6, 'cpu_threads_per_worker': 2,
                                   'memory_limit_gib': 8,
                                   'operation_count_formula': 'schedule_states * retained_frames_per_state * integration_steps_per_frame'}},
        ],
        'cross_protocol_closure_definition': {
            'run_id': 'matched_ABFE_RBFE_closure',
            'status': 'blocked_unmatched_physical_terms_and_uncovered_C3_refusal_contract',
            'member_run_ids': ['ABFE_A_bound_to_bulk', 'ABFE_B_bound_to_bulk',
                               'RBFE_bound_A_to_B', 'RBFE_bulk_A_to_B'],
            'member_run_seeds': {'ABFE_A_bound_to_bulk': 19005,
                                 'ABFE_B_bound_to_bulk': 19006,
                                 'RBFE_bound_A_to_B': 19007,
                                 'RBFE_bulk_A_to_B': 19008},
            'matched_conventions_to_freeze': ['host', 'spectator', 'model', 'caps',
                                              'box', 'constraints', 'restraints',
                                              'endpoint domain and reference atoms'],
            'currently_unmatched': ['physical host parameters', 'physical solvent definition',
                                    'bound/bulk domains and restraint references',
                                    'applicable correction procedure'],
            'closure_expression': None,
            'hold': 'C3 general unmatched-physical-state closure refusal contract remains uncovered; no closure equation or molecular result is inferred.',
            'sampling': 'no member run is executed; each retention ceiling and resource budget requires predeclaration after the physical route is admitted',
            'resource_estimate': {'status': 'blocked_until_member_protocols_and_sampling_ceilings_are_defined',
                                  'cpu_threads_per_worker': 2, 'memory_limit_gib': 8,
                                  'operation_count_formula': 'sum(member_schedule_states * member_retained_frames * member_steps_per_frame)'},
        },
        'S06_uncertainty_needs': {
            'report': ['connected overlap support (necessary, not sufficient)',
                       'effective contribution counts', 'correlation', 'independent seeds',
                       'estimate stability versus retained time', 'full/last-half comparisons',
                       'covariance for combined differences'],
            'investigation_triggers_only': ['fewer than 100 effectively contributing samples',
                                            'incompatible full/last-half estimates'],
            'convergence_claim': 'none; S06 flags are not universal convergence laws and no readiness uncertainty target is adopted here',
        },
        'resource_scope': 'Known worker/thread/memory shape and operation-count formula are recorded. Wall-time estimation is blocked until a physical parameter route, production retention, and a measured admitted profile exist.',
        'performance_separation': 'Predictive Pearson r/Kendall tau are dataset metrics; they do not establish convergence of individual endpoint energies.',
        'sampling_ceiling': 'future runs use predeclared ceilings; current tiny worker proof is plumbing-only.',
    }
    thermodynamics = _typed_thermodynamics()
    accounting = {
        'schema': 'correction-accounting-v1', 'binding_result': 'not_evaluated',
        'interpretation': 'Applicability and computation are separate. No numerical correction is authorized from this preflight.',
        'domain_atoms': {'bound': None, 'bulk': None, 'host': ids[:len(host.GetAtoms())],
                         'restraint_atoms': None},
        'source_procedure': {
            'U15': 'AToM-OpenMM v8.5.0 abfe_structprep.py; preparation sets positional/orientation restraint machinery; file does not define a postprocessing correction equation.',
            'installed_distribution': 'atom-openmm==8.5.0b0',
            'source_release_tag': 'v8.5.0',
            'method_status': 'not_claimed: U37 guide retrieval returned HTTP 403; applicability and correction equations remain a hold',
        },
        'obligations': [
            {'id': 'translation_standard_state', 'status': 'required_uncomputed', 'applicability': 'unresolved_for_physical_protocol', 'accounting_classification': 'not_yet_computed', 'additive_calculation_authorized': False},
            {'id': 'bound_release', 'status': 'required_uncomputed', 'applicability': 'unresolved_without_domain_and_restraint_definitions', 'accounting_classification': 'not_yet_computed', 'additive_calculation_authorized': False},
            {'id': 'orientation', 'status': 'required_uncomputed', 'applicability': 'unresolved_without_reference_atoms_and_restraint_definition', 'accounting_classification': 'not_yet_computed', 'additive_calculation_authorized': False},
            {'id': 'conformation', 'status': 'required_uncomputed', 'applicability': 'unresolved_without_adequate_sampling', 'accounting_classification': 'not_yet_computed', 'additive_calculation_authorized': False},
            {'id': 'state_counting', 'status': 'required_uncomputed', 'applicability': 'unresolved_without_physical_state_definition', 'accounting_classification': 'not_yet_computed', 'additive_calculation_authorized': False},
            {'id': 'midpoint_bridge', 'status': 'required_uncomputed', 'applicability': 'present_as_an_explicit_intermediate_state_in_the_proposed_schedule', 'accounting_classification': 'already_in_path', 'additive_calculation_authorized': False},
        ],
    }
    files = {}
    for name, record in (('system-input.json', original), ('partition.json', partition),
                         ('snapshot.json', snapshot)):
        files[name] = _write(directory / name, record, typed=True)
    files['geometry-admission.json'] = _write(directory / 'geometry-admission.json', geometry)
    files['run-definitions.json'] = _write(directory / 'run-definitions.json', run_definitions)
    files['thermodynamic-ledger.json'] = _write(directory / 'thermodynamic-ledger.json', thermodynamics, typed=True)
    files['correction-accounting.json'] = _write(directory / 'correction-accounting.json', accounting)
    manifest = {
        'fixture_kind': 'development_host_guest_rbfe', 'version': 1, 'status': 'preflight_only',
        'host_formula': rdMolDescriptors.CalcMolFormula(host),
        'ligand_formulas': {key: rdMolDescriptors.CalcMolFormula(mol)
                            for key, mol in zip(('A', 'B'), (guest_a, guest_b))},
        'real_atoms': len(atoms), 'physical_scope': 'all-ML vacuum plumbing only',
        'parameter_route': {'status': 'blocked_missing_host_parameters',
                            'detail': provenance['parameter_route']},
        'preparation': provenance, 'files': files,
    }
    manifest_sha = _write(directory / 'manifest.json', manifest)
    config = {
        'version': 1, 'input_manifest': 'manifest.json', 'input_manifest_sha256': manifest_sha,
        'settings': {
            'temperature_K': 300., 'timestep_ps': .0005, 'platform': 'Reference', 'seed': 41,
            'temperatures_K': [10., 100., 300.], 'steps_per_phase': 2,
            'minimization_iterations': 10, 'frames_per_state': 3, 'steps_per_frame': 2,
            'displacement_nm': displacement.tolist(), 'outside_spring_kj_mol_nm2': 10.,
            'protocol_kind': 'rbfe',
        },
        'schedule': json.loads(to_json(production_schedule(tuple(
            (name, {'Alpha': .1, 'Uh': 0., 'W0': 0., 'Umax': 10000., 'Ubcore': 500.,
                   'Acore': 0., 'Direction': 1., 'UOffset': 0., 'Lambda1': lam, 'Lambda2': lam})
            for name, lam in (('contact', 0.), ('middle', .5), ('separated', 1.))), temperature_K=300.)))
    }
    _write(directory / 'config.json', config)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.output), indent=2, sort_keys=True))
