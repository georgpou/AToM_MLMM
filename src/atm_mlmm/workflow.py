"""Manifest-driven, bounded CPU engine preflight and same-profile continuation.

This controller samples fixed windows. It does not equilibrate a system, perform
replica exchange, or infer a binding free energy from a short pilot.
"""
from dataclasses import asdict, dataclass
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import resource
import time
import uuid

from .persistence import commit_sample_chunk, read_json, read_sample_chunks, write_json
from .runtime_validation import (portable_state_clock, validate_restored_state,
                                 verify_source_inventory)
from .schema import (EvaluationRecords, IdentityError, MalformedInput, MobileGroup,
                     NumericalDomainError, PartitionSpec, RestraintSpec, RuntimeSpec,
                     ScheduleSpec, Snapshot, SystemInput, ThermodynamicSpec,
                     UnsupportedCapability, from_json, to_json)

SCOPE = 'bounded engine preflight; no equilibrium or physical-accuracy claim'
_SETTINGS = {'temperature_K','timestep_ps','platform','seed','temperatures_K',
             'steps_per_phase','minimization_iterations','frames_per_state',
             'steps_per_frame','displacement_nm','outside_spring_kj_mol_nm2',
             'protocol_kind'}


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _number(value, name, *, positive=True):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise MalformedInput(f'{name} must be a finite number')
    if value < 0 or (positive and value == 0):
        raise MalformedInput(f'{name} must be {"positive" if positive else "nonnegative"}')
    return float(value)


def _integer(value, name, limit=1000000):
    if isinstance(value,bool) or not isinstance(value,int) or not 0 < value < limit:
        raise MalformedInput(f'{name} must be an integer between 1 and {limit-1}')
    return value


@dataclass(frozen=True)
class Configuration:
    document: dict
    original: SystemInput
    partition: PartitionSpec
    snapshot: Snapshot
    runtime: RuntimeSpec
    schedule: ScheduleSpec
    settings: dict
    input_manifest: dict


def load_configuration(path):
    """Validate declarative inputs without deserializing executable MM/ML code."""
    from .partition import resolve_partition
    from .schedule import production_schedule, validate_schedule
    path = Path(path).resolve()
    document = read_json(path)
    required = {'version','input_manifest','input_manifest_sha256','settings'}
    if not isinstance(document,dict) or not required <= set(document) or set(document)-required-{'schedule'}:
        raise MalformedInput('configuration requires version, input_manifest, input_manifest_sha256 and settings')
    if type(document['version']) is not int or document['version'] != 1:
        raise UnsupportedCapability('configuration version must be 1')
    settings = dict(document['settings'])
    if set(settings)-_SETTINGS:
        raise UnsupportedCapability(f'unsupported settings: {sorted(set(settings)-_SETTINGS)}')
    mandatory = _SETTINGS-{'protocol_kind'}
    if not mandatory <= set(settings):
        raise MalformedInput(f'missing settings: {sorted(mandatory-set(settings))}')
    if settings['platform'] != 'Reference':
        raise UnsupportedCapability('bounded worker preflight admits Reference double on CPU')
    temperature = _number(settings['temperature_K'],'temperature_K')
    dt = _number(settings['timestep_ps'],'timestep_ps')
    if dt > .0005:
        raise UnsupportedCapability('qualified timestep is at most 0.0005 ps; larger steps need separate evidence')
    _integer(settings['seed'],'seed',2**31-10000)
    for key in ('steps_per_phase','minimization_iterations','frames_per_state','steps_per_frame'):
        _integer(settings[key],key)
    temperatures = settings['temperatures_K']
    if not isinstance(temperatures,list) or not 1 <= len(temperatures) <= 100:
        raise MalformedInput('temperatures_K requires 1 to 100 explicit phases')
    temperatures = [_number(t,'temperatures_K') for t in temperatures]
    if any(a >= b for a,b in zip(temperatures,temperatures[1:])) or temperatures[-1] != temperature:
        raise MalformedInput('temperatures_K must increase to temperature_K')
    displacement = settings['displacement_nm']
    if not isinstance(displacement,list) or len(displacement) != 3:
        raise MalformedInput('displacement_nm requires three finite numbers')
    if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in displacement):
        raise MalformedInput('displacement_nm requires three finite numbers')
    if sum(x*x for x in displacement) == 0:
        raise MalformedInput('displacement_nm must be nonzero')
    _number(settings['outside_spring_kj_mol_nm2'],'outside_spring_kj_mol_nm2',positive=False)
    settings.setdefault('protocol_kind','abfe')
    if settings['protocol_kind'] not in ('abfe','rbfe'):
        raise UnsupportedCapability('protocol_kind must be abfe or rbfe')
    runtime = RuntimeSpec('Reference','double',(),dt,temperature,'NVT','LangevinMiddle')
    if 'schedule' in document:
        schedule = from_json(json.dumps(document['schedule'],allow_nan=False))
        if not isinstance(schedule,ScheduleSpec):
            raise MalformedInput('schedule must be a typed ScheduleSpec')
        validate_schedule(schedule)
        if schedule.kind != 'softplus' or schedule.temperature_K != temperature:
            raise UnsupportedCapability('worker requires softplus schedule at declared temperature')
    else:
        parameters = dict(Alpha=.1,Uh=0.,W0=0.,Umax=10000.,Ubcore=500.,
                          Acore=0.,Direction=1.,UOffset=0.)
        schedule = production_schedule(tuple((name,{**parameters,'Lambda1':lam,'Lambda2':lam})
            for name,lam in (('contact',0.),('middle',.5),('separated',1.))),temperature_K=temperature)
    if len(schedule.states) < 2 or len(schedule.states) >= 10000:
        raise MalformedInput('preflight requires 2 to 9999 explicit schedule states')
    if len(schedule.states)*settings['frames_per_state'] >= 1000000:
        raise MalformedInput('bounded journal permits fewer than one million samples')
    manifest_path = (path.parent/document['input_manifest']).resolve()
    if _sha(manifest_path) != document['input_manifest_sha256']:
        raise IdentityError('input manifest digest mismatch')
    manifest = read_json(manifest_path)
    files = manifest.get('files',{})
    if not {'system-input.json','partition.json','snapshot.json'} <= set(files):
        raise IdentityError('input manifest must bind system-input, partition and snapshot')
    for name,digest in files.items():
        artifact = (manifest_path.parent/name).resolve()
        if manifest_path.parent not in artifact.parents or _sha(artifact) != digest:
            raise IdentityError(f'input file digest/path mismatch: {name}')
    original,partition,snapshot = (from_json((manifest_path.parent/name).read_text())
        for name in ('system-input.json','partition.json','snapshot.json'))
    if not isinstance(original,SystemInput) or not isinstance(partition,PartitionSpec) or not isinstance(snapshot,Snapshot):
        raise MalformedInput('input records must be SystemInput, PartitionSpec and Snapshot')
    resolve_partition(original.topology,partition)
    if snapshot.real_atom_ids != tuple(a.atom_id for a in original.topology.atoms) or snapshot.box_nm != original.box_nm:
        raise IdentityError('input snapshot atom order/box differs from prepared system')
    if snapshot.box_nm is not None:
        from .geometry import orthorhombic_lengths
        orthorhombic_lengths(snapshot.box_nm)
    ligands = [m for m in original.topology.molecules if m.role == 'ligand']
    if len(ligands) != (1 if settings['protocol_kind'] == 'abfe' else 2):
        raise MalformedInput('protocol must transfer the declared complete ligand molecule(s)')
    # Hash the exact resolved declarative schedule, even when defaults were used.
    resolved = {**document,'settings':settings,'schedule':json.loads(to_json(schedule))}
    return Configuration(resolved,original,partition,snapshot,runtime,schedule,settings,manifest)


def _domain(topology, snapshot, displacement, kind, boundary_edges=()):
    """Fixed geometry admission on both full maps; no energy-based pose choice."""
    import numpy as np
    atoms = topology.atoms
    index = {a.atom_id:i for i,a in enumerate(atoms)}
    radii = {'H':.12,'C':.17,'N':.155,'O':.152}
    if any(a.element not in radii for a in atoms):
        raise UnsupportedCapability('geometry guard admits H/C/N/O only')
    x = np.asarray(snapshot.positions_nm,dtype=float)
    from .geometry import minimum_image, unwrap_molecules
    if snapshot.box_nm is not None:
        x = unwrap_molecules(topology,x,snapshot.box_nm)
    def distances(a, b):
        delta = a[:,None,:]-b[None,:,:]
        if snapshot.box_nm is not None:
            delta = minimum_image(delta,snapshot.box_nm)
        return np.linalg.norm(delta,axis=2)
    caps = []
    for a,b in boundary_edges:
        delta = x[index[b]]-x[index[a]]
        length = np.linalg.norm(delta)
        if length == 0 or not math.isfinite(length):
            raise NumericalDomainError('coincident/nonfinite cap parents')
        caps.append(x[index[a]]+.109*delta/length)
    mapped = x.copy()
    ligands = [m for m in topology.molecules if m.role == 'ligand']
    for sign,molecule in zip((1.,-1.),ligands):
        mapped[[index[a] for a in molecule.atom_ids]] += sign*np.asarray(displacement)
    diagnostics = []
    for label,positions in (('map0',x),('map1',mapped)):
        minimum,pair = math.inf,None
        for i,molecule in enumerate(topology.molecules):
            for other in topology.molecules[i+1:]:
                a,b = [index[v] for v in molecule.atom_ids],[index[v] for v in other.atom_ids]
                distance = distances(positions[a],positions[b])
                scale = np.asarray([radii[atoms[j].element] for j in a])[:,None]+np.asarray([radii[atoms[j].element] for j in b])[None,:]
                ratio = distance/scale
                p,q = np.unravel_index(np.argmin(ratio),ratio.shape)
                if ratio[p,q] < minimum:
                    minimum,pair = float(ratio[p,q]),[atoms[a[p]].atom_id,atoms[b[q]].atom_id]
        if minimum < .65:
            raise NumericalDomainError(f'{label} intermolecular Bondi ratio {minimum:.9g} < 0.65 at {pair}')
        diagnostics.append(dict(map=label,minimum_intermolecular_Bondi_ratio=minimum,closest_pair=pair))
        if caps:
            mobile = [index[a] for molecule in ligands for a in molecule.atom_ids]
            cap_distances = distances(positions[mobile],np.asarray(caps))
            scale = np.asarray([radii[atoms[i].element]+radii['H'] for i in mobile])[:,None]
            if float(np.min(cap_distances/scale)) < .65:
                raise NumericalDomainError(f'{label} ligand-cap Bondi ratio below 0.65')
            diagnostics[-1]['minimum_ligand_cap_distance_nm'] = float(np.min(cap_distances))
    # The alternate placement must initially/remain beyond the model's local
    # support plus a 0.2-nm margin from every static host/protein real atom.
    obstacles = [index[a] for m in topology.molecules if m.role in ('host','protein') for a in m.atom_ids]
    if not obstacles:
        raise UnsupportedCapability('preflight requires a declared static host or protein')
    for j,ligand in enumerate(ligands):
        bulk = mapped if j == 0 else x  # RBFE starts ligand2 in bulk; map1 moves it back.
        static = bulk[obstacles]
        if caps:
            static = np.vstack((static,caps))
        distance = float(np.min(distances(bulk[[index[a] for a in ligand.atom_ids]],static)))
        if distance < .65:
            raise NumericalDomainError(f'bulk ligand {ligand.molecule_id} clearance {distance:.9g} nm < 0.65 nm')
        diagnostics.append(dict(bulk_ligand=ligand.molecule_id,minimum_static_distance_nm=distance,required_nm=.65))
        other = [index[a] for molecule in ligands if molecule is not ligand for a in molecule.atom_ids]
        if other:
            other_distance = float(np.min(distances(bulk[[index[a] for a in ligand.atom_ids]],bulk[other])))
            if other_distance < .65:
                raise NumericalDomainError(f'bulk ligand {ligand.molecule_id} other ligand clearance {other_distance:.9g} nm < 0.65 nm')
            diagnostics[-1]['minimum_other_ligand_distance_nm'] = other_distance
    return diagnostics


def _profile():
    distributions = sorted((d.metadata['Name'],d.version) for d in importlib.metadata.distributions())
    distribution_digest = hashlib.sha256(json.dumps(distributions,separators=(',',':')).encode()).hexdigest()
    return {'python':platform.python_version(),'machine':platform.machine(),
            'packages':{name:importlib.metadata.version(name) for name in ('openmm','numpy','torch','mace-torch','atom-openmm')},
            'installed_distribution_identity':distribution_digest,
            'openmm_platform':'Reference','precision':'double','model_device':'CPU','model_dtype':'float64'}


def _snapshot(worker):
    from openmm import unit
    physical = worker.bundle.physical
    state = worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
    indices = [physical.real_to_final[a.atom_id] for a in physical.topology.atoms]
    x = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)[indices]
    v = state.getVelocities(asNumpy=True).value_in_unit(unit.nanometer/unit.picosecond)[indices]
    box = None
    if physical.manifest.get('periodicity') == 'orthorhombic-pme-v1':
        box = state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.nanometer)
    return Snapshot(tuple(a.atom_id for a in physical.topology.atoms),x,box,v)


def _records(rows,bundle,metadata):
    return EvaluationRecords(bundle.schedule,tuple(r['sample_id'] for r in rows),
        tuple(r['state_id'] for r in rows),tuple(r['walker_id'] for r in rows),
        tuple(r['sequence_number'] for r in rows),
        *(tuple(r['raw'][name] for r in rows) for name in
          ('u0_raw_kJ_mol','u1_raw_kJ_mol','outside_energy_kJ_mol','system_total_energy_kJ_mol')),
        bundle.physical.content_identity,bundle.transfer.content_identity,bundle.restraints.content_identity,
        {'run_id':metadata['run_id'],'worker_manifest_sha256':metadata['worker_manifest_sha256'],
         'runtime_identity':metadata['runtime_identity'],'schedule_identity':bundle.schedule.content_identity,
         'profile':'Reference double / pinned MACE CPU float64 / fixed windows'},'correlated')


def _mapped_state_xml(payload, displacement):
    """Copy cached State coordinates through a fixed map, without evaluation.

    XML retains nonfinite coordinates. Parameters and velocities are copied for
    diagnosis; these files are transformed coordinates, not reevaluated states.
    """
    import xml.etree.ElementTree as ET
    state = ET.fromstring(payload)
    for position,shift in zip(state.find('Positions'),displacement):
        for axis,delta in zip(('x','y','z'),shift):
            position.set(axis,repr(float(position.get(axis))+delta))
    return ET.tostring(state,encoding='unicode')


def _compare_saved_sample_state(snapshot, row, worker):
    """Compare the restored real-particle snapshot with its captured row."""
    import numpy as np

    if tuple(row.get('real_atom_ids', ())) != snapshot.real_atom_ids:
        raise IdentityError('restored checkpoint atom order disagrees with saved sample')
    try:
        saved_positions = np.asarray(row['positions_nm'], dtype=float)
        saved_velocities = np.asarray(row['velocities_nm_ps'], dtype=float)
        actual_positions = np.asarray(snapshot.positions_nm, dtype=float)
        actual_velocities = np.asarray(snapshot.velocities_nm_ps, dtype=float)
    except (KeyError, TypeError, ValueError) as error:
        raise IdentityError(f'saved sample coordinates/velocities are malformed: {error}') from error
    if (not np.isfinite(saved_positions).all() or not np.isfinite(saved_velocities).all() or
            saved_positions.shape != actual_positions.shape or saved_velocities.shape != actual_velocities.shape):
        raise IdentityError('saved sample coordinate/velocity shape or finiteness mismatch')
    if not np.allclose(actual_positions, saved_positions, atol=1.e-15, rtol=0):
        raise IdentityError('restored checkpoint coordinates disagree with saved sample')
    if not np.array_equal(actual_velocities, saved_velocities):
        raise IdentityError('restored checkpoint velocities disagree with saved sample')
    saved_box = row.get('box_nm')
    if saved_box is not None:
        try:
            saved_box = np.asarray(saved_box, dtype=float)
        except (TypeError, ValueError) as error:
            raise IdentityError(f'saved sample box is malformed: {error}') from error
        if (saved_box.shape != (3, 3) or not np.isfinite(saved_box).all() or
                not np.array_equal(saved_box, np.asarray(snapshot.box_nm, dtype=float))):
            raise IdentityError('restored checkpoint box disagrees with saved sample')
    elif snapshot.box_nm is not None:
        raise IdentityError('restored checkpoint box disagrees with saved sample')
    saved_parameters = row.get('parameters')
    from .schedule import schedule_state
    expected_parameters = dict(schedule_state(worker.bundle.schedule, row.get('state_id')).parameters)
    if not isinstance(saved_parameters, dict) or expected_parameters != saved_parameters:
        raise IdentityError('restored checkpoint parameters disagree with saved sample')
    if (row.get('temperature_K') != worker.runtime.temperature_K or
            row.get('integrator_seed') != worker.integrator_seed):
        raise IdentityError('restored checkpoint runtime identity disagrees with saved sample')


def _compare_saved_evaluation(result, saved, *, force_field='real_forces_kj_mol_nm', energy_field=None):
    """Compare complete raw/total energies and every influencing real force."""
    import numpy as np

    actual_raw = asdict(result.raw)
    saved_raw = saved.get('raw')
    if not isinstance(saved_raw, dict) or set(actual_raw) != set(saved_raw):
        raise IdentityError('fresh checkpoint raw energy record is incomplete')
    try:
        if any(not math.isfinite(float(actual_raw[name])) or not math.isfinite(float(saved_raw[name])) or
               abs(float(actual_raw[name])-float(saved_raw[name])) > 1.e-8
               for name in actual_raw):
            raise IdentityError('fresh checkpoint raw energy record disagrees with saved state')
        saved_forces = np.asarray(saved[force_field], dtype=float)
        actual_forces = np.asarray(result.total.forces_kj_mol_nm, dtype=float)
    except (KeyError, TypeError, ValueError) as error:
        raise IdentityError(f'saved checkpoint energy/force record is malformed: {error}') from error
    if (not np.isfinite(saved_forces).all() or not np.isfinite(actual_forces).all() or
            saved_forces.shape != actual_forces.shape or
            not np.allclose(actual_forces, saved_forces, atol=1.e-8, rtol=0)):
        raise IdentityError('fresh checkpoint full real forces disagree with saved state')
    if result.parameters != saved.get('parameters'):
        raise IdentityError('fresh checkpoint parameters disagree with saved energy record')
    if energy_field is not None:
        try:
            saved_energy = float(saved[energy_field])
        except (KeyError, TypeError, ValueError) as error:
            raise IdentityError(f'saved checkpoint total energy is malformed: {error}') from error
        if not math.isfinite(saved_energy) or abs(result.total.energy_kj_mol-saved_energy) > 1.e-8:
            raise IdentityError('fresh checkpoint total energy disagrees with saved state')


def _archive_failure(directory, worker, error, identifiers):
    """Retain available evidence; secondary failures never replace the primary.

    Only cached State data and checkpoint bytes are requested. Each independent
    artifact is attempted even when another cannot be saved. Exception notes
    carry archive diagnostics when the filesystem cannot retain error.json.
    """
    import openmm as mm
    from openmm import unit
    unavailable = object()
    archive_errors = []

    def attempt(operation, action):
        try:
            return action()
        except Exception as secondary:
            archive_errors.append({'operation':operation,'error_type':type(secondary).__name__,
                                   'message':str(secondary)})
            error.add_note(f'Failure archive ({operation}): {type(secondary).__name__}: {secondary}')
            return unavailable

    if attempt('create failure directory',lambda:directory.mkdir(exist_ok=False)) is unavailable:
        return  # Never overwrite evidence from an earlier failed attempt.
    metadata = {'error_type':type(error).__name__,'message':str(error),**identifiers,
                'transfer_identity':worker.bundle.transfer.content_identity,
                'map_states':'cached parameters/velocities and transformed coordinates; no energy/force reevaluation',
                'actual_step':None,'actual_time_ps':None,'archive_errors':archive_errors}
    attempt('write primary error.json',lambda:write_json(directory/'error.json',metadata))
    context = worker.evaluator.context
    step = attempt('read step count',lambda:int(context.getStepCount()))
    if step is not unavailable:
        metadata['actual_step'] = step
    saved = attempt('capture cached State',lambda:context.getState(
        getPositions=True,getVelocities=True,getParameters=True))
    payload = unavailable
    if saved is not unavailable:
        def cached_time():
            value = float(saved.getTime().value_in_unit(unit.picosecond))
            if not math.isfinite(value):
                raise NumericalDomainError('nonfinite cached State time')
            return value
        state_time = attempt('read cached State time',cached_time)
        if state_time is not unavailable:
            metadata['actual_time_ps'] = state_time
        payload = attempt('serialize cached State',lambda:mm.XmlSerializer.serialize(saved))
        if payload is not unavailable:
            attempt('write state.xml',lambda:(directory/'state.xml').write_text(payload))
    checkpoint = attempt('capture checkpoint',context.createCheckpoint)
    if checkpoint is not unavailable:
        attempt('write checkpoint.chk',lambda:(directory/'checkpoint.chk').write_bytes(checkpoint))
    if payload is not unavailable:
        transfer = worker.bundle.transfer
        for label,displacement in (('map0',transfer.displacement0_nm),('map1',transfer.displacement1_nm)):
            attempt(f'write {label}-state.xml',lambda:(directory/f'{label}-state.xml').write_text(
                _mapped_state_xml(payload,displacement)))
    attempt('update error.json',lambda:write_json(directory/'error.json',metadata))


def _execute(directory,metadata,*,stop_after_samples=None):
    import openmm as mm
    from openmm import unit
    from .adapters.atom import load_worker_run
    from .schedule import reduced_potentials
    if stop_after_samples is not None:
        _integer(stop_after_samples,'stop_after_samples')
    rows = read_sample_chunks(directory/'samples')
    settings = metadata['settings']
    worker_path = directory/'worker'
    initial = (worker_path/'handover_0.xml').read_text()
    started = time.perf_counter()
    added = 0
    with load_worker_run(worker_path,metadata['worker_manifest_sha256'],trusted=True) as worker:
        bundle = worker.bundle
        # Check the prefix against the planned fixed-window order, beyond hashes.
        planned = [(state.state_id,frame+1) for state in bundle.schedule.states for frame in range(settings['frames_per_state'])]
        if len(rows) > len(planned) or any((r['state_id'],r['sequence_number']) != planned[i] or
            r['walker_id'] != f"{metadata['run_id']}:{r['state_id']}" or
            r['sample_id'] != f"{metadata['run_id']}:{r['state_id']}:{r['sequence_number']}" for i,r in enumerate(rows)):
            raise IdentityError('journal prefix does not match declared run/state/walker sequence')
    for state_index,state in enumerate(bundle.schedule.states):
        existing = [r for r in rows if r['state_id'] == state.state_id]
        if len(existing) == settings['frames_per_state']:
            continue
        with load_worker_run(worker_path,metadata['worker_manifest_sha256'],trusted=True,
                             integrator_seed=settings['seed']+state_index) as worker:
            frame = len(existing)
            try:
                if existing:
                    last = existing[-1]
                    chunk = directory/'samples'/f'{rows.index(last):06d}'
                    portable_xml = (chunk/'state.xml').read_text()
                    worker.restore_checkpoint((chunk/'checkpoint.chk').read_bytes(),state.state_id)
                    snapshot = validate_restored_state(worker,state_id=state.state_id,
                        portable_state_xml=portable_xml,expected_step_count=last['step'],
                        expected_time_ps=last['time_ps'])
                    _compare_saved_sample_state(snapshot,last,worker)
                else:
                    worker.restore_portable_state(initial,state.state_id)
                    expected_step,expected_time = portable_state_clock(initial)
                    snapshot = validate_restored_state(worker,state_id=state.state_id,
                        portable_state_xml=initial,expected_step_count=expected_step,
                        expected_time_ps=expected_time,
                        compare_portable_parameters=state.state_id==worker.manifest['state_id'])
                _domain(bundle.physical.topology,snapshot,settings['displacement_nm'],settings['protocol_kind'],
                        tuple((link.ml_parent_id,link.mm_parent_id) for link in bundle.physical.links))
                refreshed = worker.evaluate(snapshot,state.state_id)
                if existing:
                    _compare_saved_evaluation(refreshed,existing[-1])
                elif (state.state_id==worker.manifest['state_id'] and
                      (directory/'handover-parity.json').is_file()):
                    _compare_saved_evaluation(refreshed,read_json(directory/'handover-parity.json'),
                        force_field='all_real_forces_kj_mol_nm',energy_field='energy_kj_mol')
            except Exception as error:
                _archive_failure(directory/f'failure-{len(rows):06d}',worker,error,{
                    'state_id':state.state_id,'walker_id':f"{metadata['run_id']}:{state.state_id}",
                    'attempted_sample_id':f"{metadata['run_id']}:{state.state_id}:{frame+1}",
                    'sequence_number':frame+1,'journal_index':len(rows),'phase':'restored-state-admission'})
                raise
            for frame in range(len(existing),settings['frames_per_state']):
                step_start = time.perf_counter()
                try:
                    worker.evaluator._guard()
                    worker.evaluator.integrator.step(settings['steps_per_frame'])
                    snapshot = _snapshot(worker)
                    domain = _domain(bundle.physical.topology,snapshot,settings['displacement_nm'],settings['protocol_kind'],
                                     tuple((link.ml_parent_id,link.mm_parent_id) for link in bundle.physical.links))
                    result = worker.evaluate(snapshot,state.state_id)
                    # Preserve the original full-force refresh before a
                    # checkpoint; the failure handler below uses cached state.
                    saved = worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True,getEnergy=True,getForces=True)
                except Exception as error:
                    _archive_failure(directory/f'failure-{len(rows):06d}',worker,error,{
                        'state_id':state.state_id,'walker_id':f"{metadata['run_id']}:{state.state_id}",
                        'attempted_sample_id':f"{metadata['run_id']}:{state.state_id}:{frame+1}",
                        'sequence_number':frame+1,'journal_index':len(rows)})
                    raise
                row = dict(sample_id=f"{metadata['run_id']}:{state.state_id}:{frame+1}",
                    walker_id=f"{metadata['run_id']}:{state.state_id}",sequence_number=frame+1,
                    state_id=state.state_id,positions_nm=snapshot.positions_nm,
                    velocities_nm_ps=snapshot.velocities_nm_ps,real_atom_ids=snapshot.real_atom_ids,
                    box_nm=snapshot.box_nm,real_forces_kj_mol_nm=result.total.forces_kj_mol_nm,
                    parameters=dict(result.parameters),temperature_K=worker.runtime.temperature_K,
                    integrator_seed=worker.integrator_seed,step=int(worker.evaluator.context.getStepCount()),
                    time_ps=saved.getTime().value_in_unit(unit.picosecond),raw=asdict(result.raw),domain=domain,
                    physical_identity=bundle.physical.content_identity,transfer_identity=bundle.transfer.content_identity,
                    elapsed_frame_seconds=time.perf_counter()-step_start)
                commit_sample_chunk(directory/'samples',len(rows),row,mm.XmlSerializer.serialize(saved),worker.evaluator.context.createCheckpoint())
                rows.append(row)
                added += 1
                if stop_after_samples is not None and added >= stop_after_samples:
                    break
        if stop_after_samples is not None and added >= stop_after_samples:
            break
    records = _records(rows,bundle,metadata)
    # Commit complete raw observations before their reconstruction check.
    write_json(directory/'observations.json',rows)
    (directory/'records.json').write_text(to_json(records)+'\n')
    matrix = reduced_potentials(records)
    summary = dict(scope=SCOPE,status='complete' if len(rows)==len(planned) else 'interrupted',
        samples=len(rows),states=[s.state_id for s in bundle.schedule.states],
        all_real_atoms=len(bundle.physical.topology.atoms),binding_result='not_evaluated',
        physical_identity=bundle.physical.content_identity,alchemical_identity=bundle.content_identity,
        runtime_identity=metadata['runtime_identity'],worker_manifest_sha256=metadata['worker_manifest_sha256'],
        profile=metadata['profile'],elapsed_execution_seconds=time.perf_counter()-started,
        peak_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        reconstructed_matrix_shape=list(matrix.shape),limitations=[
            'Fixed windows; replica exchange is pending.',
            'No equilibrium, solvent-density, molecular accuracy, standard corrections or affinity qualification.',
            'Checkpoint continuation requires the identical CPU/software/source profile.',
            'Hard-crash pending transactions are preserved and require inspection.'])
    write_json(directory/'summary.json',summary)
    return summary


def run_configuration(path,directory,*,trusted=False,stop_after_samples=None):
    if trusted is not True:
        raise UnsupportedCapability('prepared System/ML artifacts require explicitly trusted loading')
    configuration = load_configuration(path)
    directory = Path(directory).resolve()
    directory.mkdir(parents=True,exist_ok=False)
    write_json(directory/'configuration.json',configuration.document)
    write_json(directory/'input-manifest.json',configuration.input_manifest)
    for name,record in (('system-input',configuration.original),('partition',configuration.partition),('snapshot',configuration.snapshot)):
        (directory/f'{name}.json').write_text(to_json(record)+'\n')
    settings = configuration.settings
    domain = _domain(configuration.original.topology,configuration.snapshot,settings['displacement_nm'],settings['protocol_kind'],
                     configuration.partition.permitted_cuts)
    write_json(directory/'initial-domain.json',domain)
    from .hybrid import build_physical
    from .models.mace import model_spec
    from .partition import resolve_partition
    from .schema import EmbeddingSpec
    from .prepare import prepare_phases
    from .geometry import resolve_protocol
    from .protocols import abfe,rbfe
    from .adapters.atom import build_atom,export_worker_run,load_worker_run
    started = time.perf_counter()
    physical = build_physical(configuration.original,
        resolve_partition(configuration.original.topology,configuration.partition),model_spec(),
        EmbeddingSpec('mechanical','1','protein_c_c',
                      'orthorhombic-pme-v1' if configuration.snapshot.box_nm is not None else 'nonperiodic'),cap_distance_nm=.109)
    prepared = prepare_phases(physical,configuration.snapshot,configuration.runtime,
        temperatures_K=settings['temperatures_K'],steps_per_phase=settings['steps_per_phase'],
        minimization_iterations=settings['minimization_iterations'],seed=settings['seed'])
    (directory/'prepared-state.xml').write_text(prepared.pop('state_xml'))
    snapshot = prepared.pop('snapshot')
    (directory/'prepared-snapshot.json').write_text(to_json(snapshot)+'\n')
    write_json(directory/'preparation.json',prepared)
    _domain(physical.topology,snapshot,settings['displacement_nm'],settings['protocol_kind'],
            tuple((link.ml_parent_id,link.mm_parent_id) for link in physical.links))
    groups = tuple(MobileGroup(m.molecule_id,m.atom_ids,('ligand',),m.molecule_id)
                   for m in physical.topology.molecules if m.role=='ligand')
    protocol = (abfe if settings['protocol_kind']=='abfe' else rbfe).make_protocol(groups,tuple(settings['displacement_nm']))
    transfer = resolve_protocol(physical,protocol)
    anchor = next(a for m in physical.topology.molecules if m.role in ('host','protein') for a in m.atom_ids)
    restraint = RestraintSpec('static-anchor',(anchor,),settings['outside_spring_kj_mol_nm2'],
                             snapshot.positions_nm[snapshot.real_atom_ids.index(anchor)])
    states = configuration.schedule.states
    thermo = ThermodynamicSpec('restrained_free_energy',{states[0].state_id:1.,states[-1].state_id:-1.},
        'endpoint_difference',tuple((a.state_id,b.state_id) for a,b in zip(states,states[1:])),
        {s.state_id:'Explicit native ATM schedule state; no thermodynamic domain inferred from its label' for s in states},
        (),(),None,('Fixed orthorhombic periodic cell' if snapshot.box_nm is not None else 'Unbounded vacuum coordinates')+'; short geometry-guarded pilot',
        'Outside static harmonic anchor only; no ligand-domain release correction',
        'Lab frame; no orientational correction computed','No physical state-counting qualification')
    with build_atom(physical,transfer,configuration.schedule,restraint,configuration.runtime) as source:
        initial_id = states[0].state_id
        import openmm as mm
        source.evaluator.restore_state(mm.XmlSerializer.deserialize((directory/'prepared-state.xml').read_text()),initial_id)
        answer = source.evaluate(snapshot,initial_id)
        manifest,digest = export_worker_run(source,directory/'worker',snapshot,initial_id,
                                           thermodynamics=thermo,integrator_seed=settings['seed'])
    # Every real force and all named raw energies must survive the actual
    # constructor/PDB/high-precision-State path before the first worker step.
    with load_worker_run(manifest.parent,digest,trusted=True) as worker:
        result = worker.evaluate(snapshot,initial_id)
        import numpy as np
        if abs(result.total.energy_kj_mol-answer.total.energy_kj_mol)>1.e-8 or not np.allclose(
            result.total.forces_kj_mol_nm,answer.total.forces_kj_mol_nm,atol=1.e-7,rtol=0) or result.raw != answer.raw:
            raise IdentityError('actual worker handover parity failed before stepping')
    write_json(directory/'handover-parity.json',{'all_real_atoms':len(snapshot.real_atom_ids),
        'energy_kj_mol':answer.total.energy_kj_mol,'raw':asdict(answer.raw),
        'all_real_forces_kj_mol_nm':answer.total.forces_kj_mol_nm,'parameters':dict(answer.parameters),
        'energy_absolute_tolerance':1.e-8,'force_absolute_tolerance':1.e-7})
    metadata = dict(version=1,run_id=uuid.uuid4().hex,settings=settings,
        runtime_identity=configuration.runtime.content_identity,worker_manifest_sha256=digest,
        profile=_profile(),elapsed_preparation_handover_seconds=time.perf_counter()-started)
    write_json(directory/'metadata.json',metadata)
    (directory/'metadata.sha256').write_text(_sha(directory/'metadata.json')+'\n')
    return _execute(directory,metadata,stop_after_samples=stop_after_samples)


def resume_run(directory,*,trusted=False,stop_after_samples=None):
    if trusted is not True:
        raise UnsupportedCapability('restart requires explicitly trusted System/ML artifacts')
    directory = Path(directory).resolve()
    if _sha(directory/'metadata.json') != (directory/'metadata.sha256').read_text().strip():
        raise IdentityError('restart metadata digest mismatch')
    metadata = read_json(directory/'metadata.json')
    if metadata.get('version') != 1 or metadata['profile'] != _profile():
        raise UnsupportedCapability('checkpoint continuation requires identical admitted runtime/software profile')
    worker_path = directory/'worker'
    manifest_path = worker_path/'manifest.json'
    if _sha(manifest_path) != metadata.get('worker_manifest_sha256'):
        raise IdentityError('restart worker manifest digest mismatch before source admission')
    manifest = read_json(manifest_path)
    verify_source_inventory(worker_path, manifest.get('files'),
                            current_source_root=Path(__file__).resolve().parent)
    return _execute(directory,metadata,stop_after_samples=stop_after_samples)
