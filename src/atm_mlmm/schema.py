"""Version 1 dependency-light records used by the analytic CPU profile.

Own all nested data. Runtime systems and later-gate records are introduced by
their owning gates rather than represented by mutable arbitrary dictionaries.
"""
from collections.abc import Mapping
from dataclasses import dataclass, field, fields
import hashlib
import json
import math
from numbers import Integral, Real
import re
from types import MappingProxyType, UnionType
from typing import Any, get_args, get_origin, get_type_hints, Union

SCHEMA_VERSION = '1.0'
_RECORDS = {}


class MalformedInput(ValueError):
    """A required field, shape, version or unit is malformed."""


class UnsupportedCapability(ValueError):
    """The requested physics or combination is not implemented/admitted."""


class IdentityError(MalformedInput):
    """Real identities, connectivity or ordering are inconsistent."""


class NumericalDomainError(MalformedInput):
    """Nonfinite or inadmissible numerical input, preserved as a failure."""


class QualificationError(ValueError):
    """Evidence cannot establish the requested acceptance."""


def _freeze(value):
    if isinstance(value, Mapping):
        if any(not isinstance(k, str) for k in value):
            raise MalformedInput('metadata keys must be strings')
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, (str, bool)) or value is None:
        return value
    if isinstance(value, Real):
        if not math.isfinite(value):
            raise NumericalDomainError('nonfinite metadata')
        return int(value) if isinstance(value, Integral) else float(value)
    if isinstance(value, Record):
        return value
    try:
        return tuple(_freeze(v) for v in value)
    except TypeError as exc:
        raise MalformedInput(f'unsupported metadata value {type(value).__name__}') from exc


def _coerce(value, annotation, field):
    origin, args = get_origin(annotation), get_args(annotation)
    if annotation is Any:
        return _freeze(value)
    if origin in (Union, UnionType):
        if value is None and type(None) in args:
            return None
        for option in args:
            if option is not type(None):
                return _coerce(value, option, field)
        raise MalformedInput(f'{field}: missing value')
    if origin is tuple:
        if isinstance(value, (str, Mapping)):
            raise MalformedInput(f'{field}: expected sequence')
        try:
            values = tuple(value)
        except TypeError as exc:
            raise MalformedInput(f'{field}: expected sequence') from exc
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(_coerce(v, args[0], field) for v in values)
        if len(values) != len(args):
            raise MalformedInput(f'{field}: expected {len(args)} entries')
        return tuple(_coerce(v, t, field) for v, t in zip(values, args))
    if origin is Mapping:
        if not isinstance(value, Mapping):
            raise MalformedInput(f'{field}: expected mapping')
        return MappingProxyType({_coerce(k, args[0], field): _coerce(v, args[1], field) for k, v in value.items()})
    if annotation is float:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise MalformedInput(f'{field}: expected number')
        if not math.isfinite(value):
            raise NumericalDomainError(f'{field}: nonfinite number')
        return float(value)
    if annotation is int:
        if isinstance(value, bool) or not isinstance(value, Integral):
            raise MalformedInput(f'{field}: expected integer')
        return int(value)
    if not isinstance(value, annotation):
        raise MalformedInput(f'{field}: expected {annotation.__name__}')
    return value


def record(cls):
    cls = dataclass(frozen=True)(cls)
    _RECORDS[cls.__name__] = cls
    return cls


class Record:
    def __post_init__(self):
        annotations = get_type_hints(type(self))
        for field in fields(self):
            object.__setattr__(self, field.name, _coerce(getattr(self, field.name), annotations[field.name], field.name))
        self._validate()

    def _validate(self):
        pass

    @property
    def content_identity(self):
        return hashlib.sha256(to_json(self).encode()).hexdigest()


def _required(*strings):
    if any(not s.strip() for s in strings):
        raise MalformedInput('required identity/description field is empty')


def _ids(ids, *, empty=False):
    if not ids and not empty:
        raise MalformedInput('real atom IDs must not be empty')
    _required(*ids)
    if len(set(ids)) != len(ids):
        raise IdentityError('duplicate real atom ID')


def _coordinates(ids, values, name):
    if len(ids) != len(values):
        raise MalformedInput(f'{name}: one 3-vector required for every real atom')


@record
class Units(Record):
    positions: str = 'nm'
    energy: str = 'kJ/mol'
    forces: str = 'kJ/mol/nm'
    time: str = 'ps'
    temperature: str = 'K'

    def _validate(self):
        if (self.positions, self.energy, self.forces, self.time, self.temperature) != ('nm', 'kJ/mol', 'kJ/mol/nm', 'ps', 'K'):
            raise MalformedInput('incompatible common units')


@record
class AtomIdentity(Record):
    atom_id: str
    element: str
    chain: str
    residue: str
    insertion_code: str
    atom_name: str

    def _validate(self):
        _required(self.atom_id, self.element, self.residue, self.atom_name)


@record
class Bond(Record):
    atom1: str
    atom2: str
    order: float = 1.0
    kind: str = 'ordinary'

    def _validate(self):
        _required(self.atom1, self.atom2, self.kind)
        if self.atom1 == self.atom2 or self.order <= 0:
            raise IdentityError('invalid self bond or bond order')


@record
class MoleculeState(Record):
    molecule_id: str
    atom_ids: tuple[str, ...]
    role: str
    formal_charge: int | None
    multiplicity: int | None

    def _validate(self):
        _required(self.molecule_id, self.role)
        _ids(self.atom_ids)


@record
class TopologyView(Record):
    atoms: tuple[AtomIdentity, ...]
    bonds: tuple[Bond, ...]
    molecules: tuple[MoleculeState, ...]

    def _validate(self):
        ids = tuple(a.atom_id for a in self.atoms)
        _ids(ids)
        memberships = tuple(a for m in self.molecules for a in m.atom_ids)
        _ids(memberships)
        if set(memberships) != set(ids):
            raise IdentityError('molecule membership must cover all real atom IDs')
        if len({m.molecule_id for m in self.molecules}) != len(self.molecules):
            raise IdentityError('duplicate molecule ID')
        edges = set()
        for bond in self.bonds:
            edge = tuple(sorted((bond.atom1, bond.atom2)))
            if not set(edge) <= set(ids) or edge in edges:
                raise IdentityError(f'unknown atom or duplicate bond: {edge}')
            edges.add(edge)


@record
class ComponentState(Record):
    atom_ids: tuple[str, ...]
    formal_charge: int | None
    multiplicity: int | None

    def _validate(self):
        _ids(self.atom_ids)


@record
class PartitionSpec(Record):
    ml_ids: tuple[str, ...]
    protein_ml_ids: tuple[str, ...]
    permitted_cuts: tuple[tuple[str, str], ...]
    component_states: tuple[ComponentState, ...]

    def _validate(self):
        _ids(self.ml_ids)
        _ids(self.protein_ml_ids, empty=True)
        if not set(self.protein_ml_ids) <= set(self.ml_ids):
            raise IdentityError('protein ML IDs must be selected ML IDs')
        cuts = [frozenset(c) for c in self.permitted_cuts]
        if any(len(c) != 2 for c in cuts) or len(set(cuts)) != len(cuts):
            raise IdentityError('duplicate or invalid permitted cut')


@record
class ResolvedPartition(Record):
    ml_ids: tuple[str, ...]
    protein_ml_ids: tuple[str, ...]
    boundary_edges: tuple[tuple[str, str], ...]
    component_identities: tuple[str, ...]
    rejected_conditions: tuple[str, ...]
    source_map: Mapping[str, int]
    component_states: tuple[ComponentState, ...] = ()

    def _validate(self):
        _ids(self.ml_ids)
        _ids(self.protein_ml_ids, empty=True)
        if self.component_states:
            state_ids = [frozenset(state.atom_ids) for state in self.component_states]
            if len(set(state_ids)) != len(state_ids) or set().union(*state_ids) != set(self.ml_ids):
                raise IdentityError('resolved component chemistry must cover fixed ML membership exactly')
            if any(state.formal_charge != 0 or state.multiplicity != 1 for state in self.component_states):
                raise UnsupportedCapability('resolved components require declared neutral singlet chemistry')


@record
class ModelSpec(Record):
    backend: str
    asset_digest: str | None
    output_energy_convention: str
    elements: tuple[str, ...]
    chemical_state_support: str
    locality: str
    dtype: str

    def _validate(self):
        _required(self.backend, self.output_energy_convention, self.chemical_state_support, self.locality, self.dtype)
        _ids(self.elements)
        if self.asset_digest is not None and (len(self.asset_digest) != 64 or any(c not in '0123456789abcdef' for c in self.asset_digest)):
            raise MalformedInput('asset_digest must be SHA-256')


@record
class EmbeddingSpec(Record):
    kind: str
    policy_version: str
    boundary_policy: str
    periodic_convention: str

    def _validate(self):
        _required(self.kind, self.policy_version, self.boundary_policy, self.periodic_convention)


@record
class MobileGroup(Record):
    group_id: str
    atom_ids: tuple[str, ...]
    roles: tuple[str, ...]
    molecule_id: str

    def _validate(self):
        _required(self.group_id, self.molecule_id)
        _ids(self.atom_ids)
        _ids(self.roles)


@record
class Endpoint(Record):
    state_id: str
    description: str

    def _validate(self):
        _required(self.state_id, self.description)


@record
class ProtocolSpec(Record):
    kind: str
    mobile_groups: tuple[MobileGroup, ...]
    geometry_requests: Mapping[str, Any]
    endpoints: tuple[Endpoint, Endpoint]
    observable: str

    def _validate(self):
        _required(self.kind, self.observable)
        if not self.mobile_groups or not self.geometry_requests:
            raise MalformedInput('protocol requires mobile_groups and geometry_requests')
        _ids(tuple(g.group_id for g in self.mobile_groups))
        all_ids = tuple(a for group in self.mobile_groups for a in group.atom_ids)
        if len(all_ids) != len(set(all_ids)):
            raise IdentityError('overlap between mobile groups')
        if self.endpoints[0].state_id == self.endpoints[1].state_id:
            raise IdentityError('endpoint IDs must be distinct')
        if 'displacement_nm' in self.geometry_requests:
            _coerce(self.geometry_requests['displacement_nm'], tuple[float, float, float], 'displacement_nm')


@record
class CapabilitySet(Record):
    backends: tuple[str, ...]
    embeddings: tuple[str, ...]
    protocols: tuple[str, ...]
    elements: tuple[str, ...]
    periodicities: tuple[str, ...]
    derivative_scope: str
    serialization: tuple[str, ...]

    def _validate(self):
        for values in (self.backends, self.embeddings, self.protocols, self.elements, self.periodicities, self.serialization):
            _ids(values)
        _required(self.derivative_scope)


@record
class RuntimeSpec(Record):
    platform: str
    precision: str
    device_allocation: tuple[str, ...]
    timestep_ps: float
    temperature_K: float
    ensemble: str
    integrator: str = 'LangevinMiddle'

    def _validate(self):
        _required(self.platform, self.precision, self.ensemble, self.integrator)
        if self.timestep_ps <= 0 or self.temperature_K <= 0:
            raise MalformedInput('runtime timestep/temperature must be positive')


@record
class CalculationRequest(Record):
    model: ModelSpec
    embedding: EmbeddingSpec
    partition: PartitionSpec
    protocol: ProtocolSpec
    runtime: RuntimeSpec


@record
class Snapshot(Record):
    real_atom_ids: tuple[str, ...]
    positions_nm: tuple[tuple[float, float, float], ...]
    box_nm: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]] | None
    velocities_nm_ps: tuple[tuple[float, float, float], ...] | None = None
    units: Units = Units()

    def _validate(self):
        _ids(self.real_atom_ids)
        _coordinates(self.real_atom_ids, self.positions_nm, 'positions_nm')
        if self.velocities_nm_ps is not None:
            _coordinates(self.real_atom_ids, self.velocities_nm_ps, 'velocities_nm_ps')
        if self.box_nm is not None:
            a, b, c = self.box_nm
            determinant = (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0]))
            if determinant <= 0:
                raise MalformedInput('box_nm must have positive volume; use None for nonperiodic')


@record
class SystemInput(Record):
    prepared_mm_artifact: str
    prepared_mm_sha256: str
    topology: TopologyView
    positions_nm: tuple[tuple[float, float, float], ...]
    box_nm: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]] | None
    masses_da: tuple[float, ...]
    constraints: tuple[tuple[str, str, float], ...]
    force_field_provenance: Mapping[str, Any]
    units: Units = Units()
    prepared_mm_inventory_identity: str | None = None

    def _validate(self):
        _required(self.prepared_mm_artifact)
        if not re.fullmatch('[0-9a-f]{64}', self.prepared_mm_sha256):
            raise MalformedInput('prepared MM identity must be SHA-256')
        if (self.prepared_mm_inventory_identity is not None and
                not re.fullmatch('[0-9a-f]{64}', self.prepared_mm_inventory_identity)):
            raise MalformedInput('prepared MM inventory identity must be SHA-256')
        ids = tuple(a.atom_id for a in self.topology.atoms)
        Snapshot(ids, self.positions_nm, self.box_nm)
        if len(self.masses_da) != len(ids) or any(m <= 0 for m in self.masses_da):
            raise MalformedInput('masses_da must cover every real atom with positive mass')
        edges = set()
        for a, b, distance in self.constraints:
            edge = frozenset((a, b))
            if a not in ids or b not in ids or len(edge) != 2 or edge in edges or distance <= 0:
                raise IdentityError(f'invalid/duplicate constraint: {a}-{b}')
            edges.add(edge)
        if not self.force_field_provenance:
            raise MalformedInput('force_field_provenance is required')


@record
class EnergyForces(Record):
    energy_kj_mol: float
    real_atom_ids: tuple[str, ...]
    forces_kj_mol_nm: tuple[tuple[float, float, float], ...]
    physical_identity: str
    snapshot_identity: str
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
    units: Units = Units()

    def _validate(self):
        _ids(self.real_atom_ids)
        _required(self.physical_identity, self.snapshot_identity)
        _coordinates(self.real_atom_ids, self.forces_kj_mol_nm, 'forces_kj_mol_nm')


@record
class LinkRecord(Record):
    cap_id: str
    ml_parent_id: str
    mm_parent_id: str
    final_particle_index: int
    model_input_index: int
    virtual_site_type: str
    distance_nm: float

    def _validate(self):
        _ids((self.cap_id, self.ml_parent_id, self.mm_parent_id))
        if (self.final_particle_index < 0 or self.model_input_index < 0 or
                not math.isfinite(self.distance_nm) or self.distance_nm <= 0):
            raise MalformedInput('invalid link index/distance')
        if self.virtual_site_type != 'LocalCoordinatesSite':
            raise UnsupportedCapability('only fixed-length LocalCoordinatesSite caps admitted')


@record
class PhysicalBundle(Record):
    """Sealed, trusted physical artifact; XML can contain executable callbacks.

    JSON decoding is inert. Use the explicit trusted/hash-checked loader for
    external artifacts. Runtime Systems/Contexts are separate mutable copies.
    """
    system_xml: str
    system_sha256: str
    topology: TopologyView
    real_to_final: Mapping[str, int]
    model_to_final: Mapping[str, int]
    old_to_new: tuple[int, ...]
    ml_atom_ids: tuple[str, ...]
    masses_da: tuple[float, ...]
    constraints: tuple[tuple[int, int, float], ...]
    ledger: tuple['ForceRecord', ...]
    manifest: Mapping[str, Any]
    units: Units = Units()
    links: tuple[LinkRecord, ...] = ()
    chemistry_states: tuple[ComponentState, ...] = ()

    @property
    def model_input_ids(self):
        return self.ml_atom_ids + tuple(link.cap_id for link in self.links)

    def _validate(self):
        if hashlib.sha256(self.system_xml.encode()).hexdigest() != self.system_sha256:
            raise IdentityError('physical System digest mismatch')
        ids = tuple(a.atom_id for a in self.topology.atoms)
        _ids(self.ml_atom_ids)
        if set(self.real_to_final) != set(ids):
            raise IdentityError('real/final map must cover all real IDs')
        indices = tuple(self.real_to_final[a] for a in ids)
        if len(set(indices)) != len(indices) or any(i < 0 or i >= len(self.masses_da) for i in indices):
            raise IdentityError('real/final map has duplicate or out-of-range index')
        if indices != self.old_to_new:
            raise IdentityError('real/final map must consume oldToNew explicitly')
        if not set(self.ml_atom_ids) <= set(ids) or set(self.model_to_final) != set(self.model_input_ids):
            raise IdentityError('model map must cover fixed real ML membership')
        if any(self.model_to_final[a] != self.real_to_final[a] for a in self.ml_atom_ids):
            raise IdentityError('model/final index map mismatch')
        if not self.masses_da or any(m < 0 for m in self.masses_da):
            raise MalformedInput('invalid final particle masses')
        if any(self.masses_da[i] <= 0 for i in indices):
            raise MalformedInput('real particle mass must be positive')
        states = self.chemistry_states
        if states:
            state_ids = [frozenset(state.atom_ids) for state in states]
            if len(set(state_ids)) != len(state_ids) or set().union(*state_ids) != set(self.ml_atom_ids):
                raise IdentityError('sealed component chemistry must cover fixed ML membership exactly')
            if any(state.formal_charge != 0 or state.multiplicity != 1 for state in states):
                raise UnsupportedCapability('sealed components require declared neutral singlet chemistry')
        version = self.manifest.get('boundary_builder_version')
        if version is not None and (type(version) is not int or version not in (1, 2)):
            raise UnsupportedCapability(f'unsupported boundary builder version: {version}')
        if version == 1 and (len(self.links) > 1 or (not self.links and set(self.ml_atom_ids) != set(ids))):
            raise UnsupportedCapability('boundary builder version 1 retains zero/one-cut all-ML semantics')
        if version == 2:
            if not (len(self.links) >= 2 or (not self.links and set(self.ml_atom_ids) < set(ids))):
                raise UnsupportedCapability('boundary builder version 2 requires a cap collection or mixed zero-cut input')
            if not states:
                raise IdentityError('boundary builder version 2 requires explicit component chemistry')
            if any(name not in self.manifest for name in
                   ('boundary_edges', 'cap_distances_nm', 'cap_force_ownership')):
                raise IdentityError('boundary builder version 2 requires complete edge, distance, and ownership records')
        declared_edges = self.manifest.get('boundary_edges')
        if declared_edges is not None:
            if (not isinstance(declared_edges, (tuple, list)) or
                    any(not isinstance(edge, (tuple, list)) or len(edge) != 2
                        or any(not isinstance(atom_id, str) or not atom_id for atom_id in edge)
                        for edge in declared_edges)):
                raise IdentityError('declared boundary edges must be ordered atom-ID pairs')
            if (len(declared_edges) != len(self.links) or
                    set(map(tuple, declared_edges)) != {
                        (link.ml_parent_id, link.mm_parent_id) for link in self.links
                    }):
                raise IdentityError('sealed cap collection differs from declared boundary edges')
        distance_rows = self.manifest.get('cap_distances_nm')
        if distance_rows is not None:
            if (not isinstance(distance_rows, (tuple, list)) or
                    any(not isinstance(row, (tuple, list)) or len(row) != 2
                        for row in distance_rows)):
                raise IdentityError('cap distances must be cap-ID/distance pairs')
            distance_ids = tuple(row[0] for row in distance_rows)
            if (any(not isinstance(cap_id, str) or not cap_id for cap_id in distance_ids) or
                    len(distance_ids) != len(self.links) or len(set(distance_ids)) != len(distance_ids) or
                    any(isinstance(row[1], bool) or not isinstance(row[1], Real) or
                        not math.isfinite(row[1]) for row in distance_rows) or
                    {row[0]: float(row[1]) for row in distance_rows} !=
                    {link.cap_id: link.distance_nm for link in self.links}):
                raise IdentityError('manifest cap distances disagree with actual sealed links')
        if self.links:
            cap_ids = tuple(link.cap_id for link in self.links)
            cap_particles = tuple(link.final_particle_index for link in self.links)
            cap_inputs = tuple(link.model_input_index for link in self.links)
            mm_parents = tuple(link.mm_parent_id for link in self.links)
            ml_parents = tuple(link.ml_parent_id for link in self.links)
            edges = tuple((link.ml_parent_id, link.mm_parent_id) for link in self.links)
            if (len(set(cap_ids)) != len(cap_ids) or len(set(cap_particles)) != len(cap_particles)
                    or len(set(cap_inputs)) != len(cap_inputs) or len(set(mm_parents)) != len(mm_parents)
                    or len(set(ml_parents)) != len(ml_parents) or len(set(edges)) != len(edges)):
                raise IdentityError('duplicate cap identity, parent, model input, final particle, or edge')
            _ids(self.model_input_ids)
            for link in self.links:
                if link.cap_id in ids:
                    raise IdentityError('cap identity must not alias a real atom ID')
                if link.ml_parent_id not in self.ml_atom_ids or link.mm_parent_id not in ids or link.mm_parent_id in self.ml_atom_ids:
                    raise IdentityError('link parents must be real ML/MM atoms')
                if link.final_particle_index in indices or not 0 <= link.final_particle_index < len(self.masses_da):
                    raise IdentityError('link/final map overlaps real particles or is out of range')
                if self.masses_da[link.final_particle_index] != 0.:
                    raise IdentityError('cap has independent mass')
                if link.model_input_index != self.model_input_ids.index(link.cap_id) or self.model_to_final[link.cap_id] != link.final_particle_index:
                    raise IdentityError('link/model map mismatch')
                expected_id = 'cap:'+hashlib.sha256((link.ml_parent_id+'\0'+link.mm_parent_id).encode()).hexdigest()
                if link.cap_id != expected_id:
                    raise IdentityError('cap identity is not stable for its declared parents')
            ownership = self.manifest.get('cap_force_ownership')
            if ownership is not None:
                if (not isinstance(ownership, (tuple, list)) or
                        any(not isinstance(entry, Mapping) for entry in ownership) or
                        len(ownership) != len(cap_ids) or
                        {entry.get('cap_id') for entry in ownership} != set(cap_ids) or
                        any(entry.get('raw_force_group') != 2 or
                            entry.get('raw_force_owner') != 'mechanical-model' or
                            entry.get('projection_owner') != 'native LocalCoordinatesSite exactly once'
                            for entry in ownership)):
                    raise IdentityError('cap force ownership must name every cap exactly once')
        elif version == 2 and any(self.manifest[name] for name in
                                  ('boundary_edges', 'cap_distances_nm', 'cap_force_ownership')):
            raise IdentityError('mixed zero-cut v2 inputs cannot declare cap metadata')
        if set(indices) | {l.final_particle_index for l in self.links} != set(range(len(self.masses_da))):
            raise IdentityError('real/link maps must cover every final particle')
        if not self.ledger or not self.manifest:
            raise MalformedInput('physical ledger and manifest required')


@record
class TransferDefinition(Record):
    physical_identity: str
    protocol: ProtocolSpec
    displacement0_nm: tuple[tuple[float, float, float], ...]
    displacement1_nm: tuple[tuple[float, float, float], ...]
    final_particle_count: int
    convention: str = 'fixed_translation'

    def _validate(self):
        _required(self.physical_identity)
        if self.convention != 'fixed_translation':
            raise UnsupportedCapability('only fixed translation maps admitted')
        if self.final_particle_count <= 0 or len(self.displacement0_nm) != self.final_particle_count or len(self.displacement1_nm) != self.final_particle_count:
            raise IdentityError('both maps must cover every final particle')


@record
class ScheduleState(Record):
    state_id: str
    parameters: Mapping[str, float]

    def _validate(self):
        _required(self.state_id)
        if not self.parameters:
            raise MalformedInput('complete schedule parameters required')


@record
class ScheduleSpec(Record):
    kind: str
    expression: str
    states: tuple[ScheduleState, ...]
    parameter_units: Mapping[str, str]
    temperature_K: float

    def _validate(self):
        _required(self.kind, self.expression)
        _ids(tuple(s.state_id for s in self.states))
        if self.temperature_K <= 0:
            raise MalformedInput('schedule temperature must be positive')
        if any(set(s.parameters) != set(self.parameter_units) for s in self.states):
            raise MalformedInput('schedule parameters/units must be complete')


@record
class RestraintSpec(Record):
    restraint_id: str
    atom_ids: tuple[str, ...]
    spring_kj_mol_nm2: float
    center_nm: tuple[float, float, float]
    ownership: str = 'outside'
    domain: str = 'analytic_unbounded'
    orientation_convention: str = 'lab_frame'
    correction_obligations: tuple[str, ...] = ()

    def _validate(self):
        _required(self.restraint_id, self.domain, self.orientation_convention)
        _ids(self.atom_ids)
        if self.ownership != 'outside' or self.domain != 'analytic_unbounded' or self.orientation_convention != 'lab_frame':
            raise UnsupportedCapability('only declared outside analytic harmonic restraints admitted')
        if self.spring_kj_mol_nm2 < 0 or self.correction_obligations:
            raise UnsupportedCapability('analytic restraint is not a binding/correction definition')


@record
class EvaluationRecords(Record):
    """Raw NVT observations; walker sequence is explicit for correlation analysis."""
    schedule: ScheduleSpec
    sample_ids: tuple[str, ...]
    sampled_state_ids: tuple[str, ...]
    walker_ids: tuple[str, ...]
    sequence_numbers: tuple[int, ...]
    u0_raw_kJ_mol: tuple[float, ...]
    u1_raw_kJ_mol: tuple[float, ...]
    outside_energy_kJ_mol: tuple[float, ...]
    observed_total_kJ_mol: tuple[float, ...]
    physical_identity: str
    transfer_identity: str
    restraint_identity: str
    provenance: Mapping[str, str]
    sampling_mode: str

    def _validate(self):
        _ids(self.sample_ids)
        count = len(self.sample_ids)
        arrays = (self.sampled_state_ids, self.walker_ids, self.sequence_numbers,
                  self.u0_raw_kJ_mol, self.u1_raw_kJ_mol, self.outside_energy_kJ_mol,
                  self.observed_total_kJ_mol)
        if any(len(array) != count for array in arrays):
            raise MalformedInput('raw observation fields must cover every sample')
        known = {s.state_id for s in self.schedule.states}
        if not set(self.sampled_state_ids) <= known:
            raise IdentityError('observation references unknown sampled state')
        _required(*self.walker_ids, self.physical_identity, self.transfer_identity, self.restraint_identity)
        if not self.provenance:
            raise MalformedInput('observation provenance required')
        _required(*self.provenance.keys(), *self.provenance.values())
        if self.sampling_mode not in ('independent', 'correlated'):
            raise MalformedInput('explicit observation sampling_mode required')
        previous = {}
        for walker, number in zip(self.walker_ids, self.sequence_numbers):
            if number < 0 or number <= previous.get(walker, -1):
                raise IdentityError('walker sequence_numbers must increase without duplicates')
            previous[walker] = number


@record
class CorrectionRecord(Record):
    """Additive S05 correction; missing computations never acquire zero values."""
    correction_id: str
    status: str
    value_kj_mol: float | None
    standard_error_kj_mol: float | None
    evidence: str

    def _validate(self):
        _required(self.correction_id)
        if self.status not in ('required_uncomputed', 'computed', 'zero_demonstrated', 'not_applicable'):
            raise MalformedInput('unknown correction status')
        if self.status == 'required_uncomputed':
            if self.value_kj_mol is not None or self.standard_error_kj_mol is not None:
                raise MalformedInput('uncomputed correction cannot have a value/error')
        else:
            if not self.evidence.strip():
                raise MalformedInput('resolved correction needs evidence')
            if self.value_kj_mol is None or self.standard_error_kj_mol is None or self.standard_error_kj_mol < 0:
                raise MalformedInput('resolved correction needs value and nonnegative error')
            if self.status in ('zero_demonstrated', 'not_applicable') and (self.value_kj_mol != 0 or self.standard_error_kj_mol != 0):
                raise MalformedInput('evidence-backed zero/not-applicable correction must be zero')


STANDARD_CORRECTION_OBLIGATIONS = ('translation_standard_state', 'bound_release', 'orientation',
                                   'conformation', 'state_counting', 'midpoint_bridge')


@record
class ThermodynamicSpec(Record):
    observable: str
    endpoint_weights: Mapping[str, float]
    sign_convention: str
    state_connections: tuple[tuple[str, str], ...]
    endpoint_descriptions: Mapping[str, str]
    correction_obligations: tuple[str, ...]
    corrections: tuple[CorrectionRecord, ...]
    standard_volume_nm3: float | None
    domain_description: str
    restraint_description: str
    orientation_description: str
    state_counting_description: str

    def _validate(self):
        if self.observable not in ('restrained_free_energy', 'standard_binding_free_energy'):
            raise UnsupportedCapability('unadmitted thermodynamic observable')
        _required(self.sign_convention, self.domain_description, self.restraint_description,
                  self.orientation_description, self.state_counting_description)
        if self.sign_convention not in ('endpoint_difference', 'bound_minus_bulk', 'B_minus_A'):
            raise UnsupportedCapability('unknown thermodynamic sign convention')
        if not self.endpoint_weights or not any(self.endpoint_weights.values()) or abs(sum(self.endpoint_weights.values())) > 1.e-12:
            raise MalformedInput('endpoint weights must define a nonzero gauge-invariant difference')
        _ids(tuple(self.endpoint_weights))
        if not set(self.endpoint_weights) <= set(self.endpoint_descriptions):
            raise MalformedInput('weighted endpoints need descriptions')
        _required(*self.endpoint_descriptions.values())
        if not self.state_connections or any(a == b or not a.strip() or not b.strip() for a, b in self.state_connections):
            raise MalformedInput('explicit state graph connections required')
        _ids(self.correction_obligations, empty=True)
        _ids(tuple(c.correction_id for c in self.corrections), empty=True)
        if not {c.correction_id for c in self.corrections} <= set(self.correction_obligations):
            raise MalformedInput('corrections must correspond to declared obligations')
        if self.standard_volume_nm3 is not None and self.standard_volume_nm3 <= 0:
            raise MalformedInput('standard volume must be positive')
        if self.observable == 'standard_binding_free_energy':
            if self.sign_convention != 'bound_minus_bulk' or self.standard_volume_nm3 is None:
                raise MalformedInput('standard binding requires bound-minus-bulk and standard volume')
            if not set(STANDARD_CORRECTION_OBLIGATIONS) <= set(self.correction_obligations):
                raise MalformedInput('standard binding requires explicit correction obligations')


@record
class BindingResult(Record):
    restrained_kj_mol: float
    restrained_standard_error_kj_mol: float
    corrections: tuple[CorrectionRecord, ...]
    unresolved_corrections: tuple[str, ...]
    final_kj_mol: float | None
    final_standard_error_kj_mol: float | None
    thermodynamic_identity: str
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
    thermodynamics: ThermodynamicSpec | None = None

    def _validate(self):
        _required(self.thermodynamic_identity)
        _ids(tuple(c.correction_id for c in self.corrections), empty=True)
        _ids(self.unresolved_corrections, empty=True)
        by_id = {c.correction_id: c for c in self.corrections}
        unresolved = set(self.unresolved_corrections)
        uncomputed = {c.correction_id for c in self.corrections if c.status == 'required_uncomputed'}
        if not uncomputed <= unresolved:
            raise MalformedInput('uncomputed ledger status must remain unresolved')
        if self.thermodynamics is not None:
            spec = self.thermodynamics
            if spec.content_identity != self.thermodynamic_identity:
                raise IdentityError('binding result thermodynamic identity mismatch')
            if self.corrections != spec.corrections:
                raise IdentityError('binding result correction ledger differs from its definition')
            missing = set(spec.correction_obligations)-set(by_id)
            expected = missing | uncomputed
            if not expected <= unresolved or unresolved-expected-{'correction_covariance'}:
                raise MalformedInput('binding result unresolved entries differ from declared obligations')
            if 'correction_covariance' in unresolved and not any(
                    c.standard_error_kj_mol for c in self.corrections):
                raise MalformedInput('unresolved correction covariance needs an uncertain correction')
        if self.restrained_standard_error_kj_mol < 0:
            raise MalformedInput('negative restrained error')
        if (self.final_kj_mol is None) != (self.final_standard_error_kj_mol is None):
            raise MalformedInput('final value and covariance-aware error must coexist')
        if self.final_kj_mol is not None and (self.unresolved_corrections or self.final_standard_error_kj_mol < 0):
            raise MalformedInput('unresolved correction prevents a final binding result')
        if self.final_kj_mol is not None:
            if self.thermodynamics is None or self.thermodynamics.observable != 'standard_binding_free_energy':
                raise MalformedInput('final binding result requires its standard thermodynamic definition')
            if not set(self.thermodynamics.correction_obligations) <= set(by_id) or uncomputed:
                raise MalformedInput('final binding result requires a complete resolved correction ledger')
            corrected = self.restrained_kj_mol+sum(c.value_kj_mol for c in self.corrections)
            if not math.isclose(self.final_kj_mol, corrected, rel_tol=1.e-12, abs_tol=1.e-12):
                raise MalformedInput('final binding value differs from restrained value plus corrections')


@record
class ForceOwnership(Record):
    force_id: str
    class_name: str
    name: str
    disposition: str
    force_group: int
    path: tuple[int, ...]
    force_sha256: str

    def _validate(self):
        _required(self.force_id, self.class_name, self.name)
        if self.disposition not in ('physical_child', 'outside') or not 0 <= self.force_group <= 31 or not self.path:
            raise MalformedInput('invalid force ownership/disposition/path')


RAW_ATM_FIELDS = ('u0_raw_kJ_mol', 'u1_raw_kJ_mol', 'delta_u_raw_kJ_mol',
                  'delta_u_softcore_kJ_mol', 'atm_expression_energy_kJ_mol',
                  'outside_energy_kJ_mol', 'system_total_energy_kJ_mol')


@record
class AlchemicalBundle(Record):
    physical: PhysicalBundle
    transfer: TransferDefinition
    schedule: ScheduleSpec
    restraints: RestraintSpec
    system_xml: str
    system_sha256: str
    routing_report: tuple[ForceOwnership, ...]
    construction: str = 'native'
    raw_observable_schema: tuple[str, ...] = RAW_ATM_FIELDS

    def _validate(self):
        if hashlib.sha256(self.system_xml.encode()).hexdigest() != self.system_sha256:
            raise IdentityError('ATM System digest mismatch')
        if self.transfer.physical_identity != self.physical.content_identity:
            raise IdentityError('transfer belongs to a different physical identity')
        if self.transfer.final_particle_count != len(self.physical.masses_da):
            raise IdentityError('transfer/final particle count mismatch')
        if not self.routing_report or self.raw_observable_schema != RAW_ATM_FIELDS:
            raise MalformedInput('complete routing/raw-observable schema required')


@record
class RawAtmEnergies(Record):
    u0_raw_kJ_mol: float
    u1_raw_kJ_mol: float
    delta_u_raw_kJ_mol: float
    delta_u_softcore_kJ_mol: float
    atm_expression_energy_kJ_mol: float
    outside_energy_kJ_mol: float
    system_total_energy_kJ_mol: float

    def _validate(self):
        if not math.isclose(self.delta_u_raw_kJ_mol, self.u1_raw_kJ_mol-self.u0_raw_kJ_mol, rel_tol=0, abs_tol=1e-8):
            raise IdentityError('raw perturbation is u1-u0')
        if not math.isclose(self.system_total_energy_kJ_mol, self.atm_expression_energy_kJ_mol+self.outside_energy_kJ_mol, rel_tol=0, abs_tol=1e-8):
            raise IdentityError('total must include the outside energy exactly once')


@record
class AtmEvaluation(Record):
    total: EnergyForces
    raw: RawAtmEnergies
    state_id: str
    transfer_identity: str
    schedule_identity: str
    restraint_identity: str
    parameters: Mapping[str, float]

    def _validate(self):
        _required(self.state_id, self.transfer_identity, self.schedule_identity, self.restraint_identity)
        if self.total.energy_kj_mol != self.raw.system_total_energy_kJ_mol:
            raise IdentityError('ATM total/raw result mismatch')


@record
class ValidationReport(Record):
    check_id: str
    requirement_ids: tuple[str, ...]
    profile: str
    fixture_identities: tuple[str, ...]
    measured_values: Mapping[str, Any]
    thresholds: Mapping[str, Any]
    status: str
    logs: tuple[str, ...]
    reviewer_references: tuple[str, ...]
    tested_snapshot: str = ''

    def _validate(self):
        _required(self.check_id, self.profile)
        _ids(self.requirement_ids)
        if self.status not in ('not_run', 'failed', 'passed', 'skipped'):
            raise MalformedInput('unknown test status')


@record
class ForceRecord(Record):
    index: int
    class_name: str
    name: str
    force_group: int
    uses_periodic: bool
    parameters: Mapping[str, Any]

    def _validate(self):
        _required(self.class_name, self.name)
        if self.index < 0 or not 0 <= self.force_group <= 31:
            raise MalformedInput('invalid force index/group')


@record
class ForceInventory(Record):
    artifact_sha256: str
    particle_masses_da: tuple[float, ...]
    constraints: tuple[tuple[int, int, float], ...]
    box_vectors_nm: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
    virtual_sites: Mapping[str, Any]
    forces: tuple[ForceRecord, ...]
    units: Units = Units()

    def _validate(self):
        if not re.fullmatch('[0-9a-f]{64}', self.artifact_sha256):
            raise MalformedInput('MM artifact digest must be SHA-256')
        if not self.particle_masses_da or any(m < 0 for m in self.particle_masses_da):
            raise MalformedInput('invalid original-MM masses')


@record
class AcceptanceRecord(Record):
    scope: str
    profile: str
    snapshot: str
    requirement_ids: tuple[str, ...]
    required_test_ids: tuple[str, ...]
    reports: tuple[ValidationReport, ...]
    reviewer: str
    verdict: str
    reviewer_decision: str
    status: str

    def _validate(self):
        _required(self.scope, self.profile)
        if self.status not in ('not_started', 'in_progress', 'blocked', 'ready_for_review',
                               'changes_requested', 'accepted', 'invalidated'):
            raise MalformedInput('unknown acceptance status')
        if self.status != 'accepted':
            return
        if not re.fullmatch('[0-9a-f]{40}', self.snapshot):
            raise QualificationError('acceptance needs an immutable code snapshot')
        if not self.reviewer.strip() or not self.reviewer_decision.strip() or self.verdict != 'accepted_for_scope':
            raise QualificationError('acceptance requires an independent reviewer and decision')
        if not self.reports or not self.requirement_ids or not self.required_test_ids:
            raise QualificationError('acceptance requires requirement/test evidence')
        ids = [r.check_id for r in self.reports]
        if len(ids) != len(set(ids)) or set(ids) != set(self.required_test_ids):
            raise QualificationError('required tests must have unique complete evidence')
        coverage = {requirement for r in self.reports for requirement in r.requirement_ids}
        if not set(self.requirement_ids) <= coverage:
            raise QualificationError('acceptance lacks requirement coverage')
        for report in self.reports:
            if report.tested_snapshot != self.snapshot:
                raise QualificationError('test evidence belongs to a different snapshot')
            if report.profile != self.profile or report.status != 'passed':
                raise QualificationError('applicable test missing a passed result on the requested profile')
            references = (report.logs, report.fixture_identities, report.reviewer_references)
            if any(not entries or any(not entry.strip() for entry in entries) for entries in references):
                raise QualificationError('test evidence references must identify nonblank inputs/logs/reviewers')
            if not report.measured_values or not report.thresholds:
                raise QualificationError('test evidence needs inputs/results/limits/logs/reviewer references')


def _encode(value):
    if isinstance(value, Record):
        # Additive G04 links are omitted when absent: old real-only artifact
        # bytes/content identities and their nested transfer IDs stay unchanged.
        return dict(record_type=type(value).__name__, data={f.name: _encode(getattr(value, f.name)) for f in fields(value)
                    if not ((isinstance(value, PhysicalBundle) and f.name == 'links' and not value.links)
                            or (isinstance(value, PhysicalBundle) and f.name == 'chemistry_states' and not value.chemistry_states)
                            or (isinstance(value, ResolvedPartition) and f.name == 'component_states' and not value.component_states)
                            or (isinstance(value, SystemInput) and f.name == 'prepared_mm_inventory_identity'
                                and value.prepared_mm_inventory_identity is None)
                            or (isinstance(value, BindingResult) and f.name == 'thermodynamics'
                                and value.thermodynamics is None))})
    if isinstance(value, Mapping):
        return {k: _encode(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_encode(v) for v in value]
    return value


def _decode(value):
    if isinstance(value, dict):
        if 'record_type' in value:
            if set(value) != {'record_type', 'data'} or value['record_type'] not in _RECORDS:
                raise MalformedInput('unknown record_type or incompatible required fields')
            cls = _RECORDS[value['record_type']]
            if not isinstance(value['data'], dict):
                raise MalformedInput('record data must be a mapping')
            unknown = set(value['data']) - {f.name for f in fields(cls)}
            if unknown:
                raise MalformedInput(f'unknown mandatory fields: {sorted(unknown)}')
            try:
                return cls(**{k: _decode(v) for k, v in value['data'].items()})
            except TypeError as exc:
                raise MalformedInput(str(exc)) from exc
        return {k: _decode(v) for k, v in value.items()}
    if isinstance(value, list):
        return tuple(_decode(v) for v in value)
    return value


def to_json(value):
    if not isinstance(value, Record):
        raise MalformedInput('a reviewed record is required')
    return json.dumps(dict(schema_version=SCHEMA_VERSION, **_encode(value)), sort_keys=True, allow_nan=False)


def from_json(text):
    def reject_constant(value):
        raise NumericalDomainError(f'nonfinite JSON: {value}')
    try:
        envelope = json.loads(text, parse_constant=reject_constant)
    except json.JSONDecodeError as exc:
        raise MalformedInput(str(exc)) from exc
    if not isinstance(envelope, dict) or envelope.get('schema_version') != SCHEMA_VERSION:
        raise MalformedInput('unsupported or missing schema_version')
    if set(envelope) != {'schema_version', 'record_type', 'data'}:
        raise MalformedInput('incompatible schema envelope fields')
    return _decode({k: v for k, v in envelope.items() if k != 'schema_version'})
