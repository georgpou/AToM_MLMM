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

    def _validate(self):
        _ids(self.ml_ids)
        _ids(self.protein_ml_ids, empty=True)


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

    def _validate(self):
        _required(self.prepared_mm_artifact)
        if not re.fullmatch('[0-9a-f]{64}', self.prepared_mm_sha256):
            raise MalformedInput('prepared MM identity must be SHA-256')
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
        return dict(record_type=type(value).__name__, data={f.name: _encode(getattr(value, f.name)) for f in fields(value)})
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
