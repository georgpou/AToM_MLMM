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
        raise UnsupportedCapability('this initial common preflight admits nonperiodic inputs; solvated PME workflow is pending')
    ligands = [m for m in original.topology.molecules if m.role == 'ligand']
    if len(ligands) != (1 if settings['protocol_kind'] == 'abfe' else 2):
        raise MalformedInput('protocol must transfer the declared complete ligand molecule(s)')
    # Hash the exact resolved declarative schedule, even when defaults were used.
    resolved = {**document,'settings':settings,'schedule':json.loads(to_json(schedule))}
    return Configuration(resolved,original,partition,snapshot,runtime,schedule,settings,manifest)


def _domain(topology, snapshot, displacement, kind):
    """Fixed geometry admission on both full maps; no energy-based pose choice."""
    import numpy as np
    atoms = topology.atoms
    index = {a.atom_id:i for i,a in enumerate(atoms)}
    radii = {'H':.12,'C':.17,'N':.155,'O':.152}
    if any(a.element not in radii for a in atoms):
        raise UnsupportedCapability('geometry guard admits H/C/N/O only')
    x = np.asarray(snapshot.positions_nm,dtype=float)
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
                distance = np.linalg.norm(positions[a,None,:]-positions[None,b,:],axis=2)
                scale = np.asarray([radii[atoms[j].element] for j in a])[:,None]+np.asarray([radii[atoms[j].element] for j in b])[None,:]
                ratio = distance/scale
                p,q = np.unravel_index(np.argmin(ratio),ratio.shape)
                if ratio[p,q] < minimum:
                    minimum,pair = float(ratio[p,q]),[atoms[a[p]].atom_id,atoms[b[q]].atom_id]
        if minimum < .65:
            raise NumericalDomainError(f'{label} intermolecular Bondi ratio {minimum:.9g} < 0.65 at {pair}')
        diagnostics.append(dict(map=label,minimum_intermolecular_Bondi_ratio=minimum,closest_pair=pair))
    # The alternate placement must initially/remain beyond the model's local
    # support plus a 0.2-nm margin from every static host/protein real atom.
    obstacles = [index[a] for m in topology.molecules if m.role in ('host','protein') for a in m.atom_ids]
    if not obstacles:
        raise UnsupportedCapability('preflight requires a declared static host or protein')
    for j,ligand in enumerate(ligands):
        bulk = mapped if j == 0 else x  # RBFE starts ligand2 in bulk; map1 moves it back.
        distance = float(np.min(np.linalg.norm(bulk[[index[a] for a in ligand.atom_ids],None,:]-bulk[None,obstacles,:],axis=2)))
        if distance < .65:
            raise NumericalDomainError(f'bulk ligand {ligand.molecule_id} clearance {distance:.9g} nm < 0.65 nm')
        diagnostics.append(dict(bulk_ligand=ligand.molecule_id,minimum_static_distance_nm=distance,required_nm=.65))
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
    return Snapshot(tuple(a.atom_id for a in physical.topology.atoms),x,None,v)


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
            if existing:
                chunk = directory/'samples'/f'{rows.index(existing[-1]):06d}'
                worker.restore_checkpoint((chunk/'checkpoint.chk').read_bytes(),state.state_id)
            else:
                worker.restore_portable_state(initial,state.state_id)
            for frame in range(len(existing),settings['frames_per_state']):
                worker.evaluator._guard()
                step_start = time.perf_counter()
                worker.evaluator.integrator.step(settings['steps_per_frame'])
                try:
                    snapshot = _snapshot(worker)
                    domain = _domain(bundle.physical.topology,snapshot,settings['displacement_nm'],settings['protocol_kind'])
                    result = worker.evaluate(snapshot,state.state_id)
                except Exception as error:
                    # Save even a rejected finite frame before raising. XML also
                    # retains nonfinite numeric output that strict JSON rejects.
                    failed = directory/f'failure-{len(rows):06d}'
                    failed.mkdir(exist_ok=False)
                    # Request only cached state: a rejected domain/force must
                    # not be evaluated again while preserving its coordinates.
                    saved = worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
                    (failed/'state.xml').write_text(mm.XmlSerializer.serialize(saved))
                    (failed/'checkpoint.chk').write_bytes(worker.evaluator.context.createCheckpoint())
                    write_json(failed/'error.json',{'error_type':type(error).__name__,'message':str(error),'state_id':state.state_id})
                    raise
                saved = worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True,getEnergy=True,getForces=True)
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
            'No equilibrium, solvent, molecular accuracy, standard corrections or affinity qualification.',
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
    domain = _domain(configuration.original.topology,configuration.snapshot,settings['displacement_nm'],settings['protocol_kind'])
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
        EmbeddingSpec('mechanical','1','protein_c_c','nonperiodic'),cap_distance_nm=.109)
    prepared = prepare_phases(physical,configuration.snapshot,configuration.runtime,
        temperatures_K=settings['temperatures_K'],steps_per_phase=settings['steps_per_phase'],
        minimization_iterations=settings['minimization_iterations'],seed=settings['seed'])
    (directory/'prepared-state.xml').write_text(prepared.pop('state_xml'))
    snapshot = prepared.pop('snapshot')
    (directory/'prepared-snapshot.json').write_text(to_json(snapshot)+'\n')
    write_json(directory/'preparation.json',prepared)
    _domain(physical.topology,snapshot,settings['displacement_nm'],settings['protocol_kind'])
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
        (),(),None,'Unbounded vacuum coordinates; short geometry-guarded pilot',
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
    # Current runtime code must match every exact bundled source file. Paths may
    # relocate; changing source is a new run, never a silent restart.
    manifest = read_json(directory/'worker/manifest.json')
    source = Path(__file__).resolve().parent
    for name,digest in manifest['files'].items():
        prefix = 'runtime/source/atm_mlmm/'
        if name.startswith(prefix) and _sha(source/name[len(prefix):]) != digest:
            raise IdentityError(f'restart source differs from bundled source: {name}')
    return _execute(directory,metadata,stop_after_samples=stop_after_samples)
