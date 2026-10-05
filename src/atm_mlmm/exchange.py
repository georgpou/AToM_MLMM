"""Bounded synchronous pair exchange with whole-round local transactions.

Physics/Metropolis live in the existing adapter. This controller owns identity,
both host RNG streams, checkpoints and explicit interruption recovery.
"""
from contextlib import contextmanager,ExitStack
from collections.abc import Sequence
from dataclasses import asdict
import hashlib
from pathlib import Path
import random
import resource
import shutil
import tempfile
import time
import uuid

from .exchange_journal import (controller_lock,preserve_pending,read_exchange_rounds,
                               seal,sha,sync_directory)
from .persistence import read_json,write_json
from .schema import (AlchemicalBundle,EvaluationRecords,IdentityError,MalformedInput,
                     RuntimeSpec,UnsupportedCapability,from_json,to_json)
from .workflow import _archive_failure,_domain,_integer,_profile,_snapshot


def _verify_source_profile(directory,metadata):
    if metadata.get('version')!=1 or metadata['profile']!=_profile():
        raise UnsupportedCapability('exchange checkpoint continuation requires identical runtime/software profile')
    manifest_path=directory/'worker/manifest.json'
    if sha(manifest_path)!=metadata['worker_manifest_sha256']:
        raise IdentityError('exchange worker manifest hash mismatch')
    manifest=read_json(manifest_path)
    prefix='runtime/source/atm_mlmm/'
    bundled={name for name in manifest['files'] if name.startswith(prefix) and name.endswith('.py')}
    current={prefix+path.relative_to(Path(__file__).resolve().parent).as_posix()
             for path in Path(__file__).resolve().parent.rglob('*.py')}
    if bundled!=current:
        raise IdentityError('exchange source inventory differs from the complete current Python source tree')
    for name,digest in manifest['files'].items():
        path=(directory/'worker'/name).resolve()
        if (directory/'worker').resolve() not in path.parents or sha(path)!=digest:
            raise IdentityError(f'exchange worker artifact mismatch: {name}')
        if name.startswith(prefix) and sha(Path(__file__).parent/name[len(prefix):])!=digest:
            raise IdentityError(f'exchange source differs from bundled source: {name}')


def _multistate_selection(state_ids,state_pairs):
    if isinstance(state_ids,(str,bytes)) or not isinstance(state_ids,Sequence):
        raise MalformedInput('state_ids must be an ordered sequence')
    states=tuple(state_ids)
    if not 3<=len(states)<=8:
        raise MalformedInput('multistate exchange requires three to eight schedule states')
    if any(not isinstance(state,str) or not state.strip() for state in states) or len(set(states))!=len(states):
        raise MalformedInput('state_ids must be distinct nonempty schedule identifiers')
    if isinstance(state_pairs,(str,bytes)) or not isinstance(state_pairs,Sequence) or not state_pairs:
        raise MalformedInput('state_pairs must be a nonempty ordered sequence')
    pairs=[]; edges=set()
    for pair in state_pairs:
        if isinstance(pair,(str,bytes)) or not isinstance(pair,Sequence) or len(pair)!=2:
            raise MalformedInput('each state pair must contain exactly two schedule indices')
        left,right=pair
        if type(left) is not int or type(right) is not int or left==right or not (0<=left<len(states) and 0<=right<len(states)):
            raise MalformedInput('state-pair indices must be distinct in-range integers')
        edge=frozenset((left,right))
        if edge in edges:
            raise MalformedInput('an undirected state-pair edge may occur only once per sweep')
        edges.add(edge); pairs.append((left,right))
    if len(pairs)>28:
        raise MalformedInput('multistate sweep exceeds the 28-pair bound')
    reached={0}
    changed=True
    while changed:
        before=len(reached)
        for left,right in pairs:
            if left in reached: reached.add(right)
            if right in reached: reached.add(left)
        changed=len(reached)!=before
    if len(reached)!=len(states):
        raise MalformedInput('state-pair graph must be connected and cover every declared state')
    return states,tuple(pairs)


def _admit_multistate_prepared(prepared_run,state_ids,state_pairs):
    prepared_run=Path(prepared_run).resolve()
    metadata_path=prepared_run/'metadata.json'
    if sha(metadata_path)!=(prepared_run/'metadata.sha256').read_text().strip():
        raise IdentityError('prepared run metadata hash mismatch')
    metadata=read_json(metadata_path)
    _verify_source_profile(prepared_run,metadata)
    manifest=read_json(prepared_run/'worker/manifest.json')
    bundle=from_json((prepared_run/'worker/bundle.json').read_text())
    runtime=from_json((prepared_run/'worker/runtime.json').read_text())
    if not isinstance(bundle,AlchemicalBundle) or not isinstance(runtime,RuntimeSpec):
        raise UnsupportedCapability('multistate exchange requires a sealed alchemical worker bundle')
    if (bundle.content_identity!=manifest.get('alchemical_identity') or
        runtime.content_identity!=manifest.get('runtime_identity') or
        runtime.content_identity!=metadata.get('runtime_identity')):
        raise IdentityError('multistate worker, runtime, and prepared metadata identities disagree')
    if runtime.temperature_K!=300. or bundle.schedule.temperature_K!=300.:
        raise UnsupportedCapability('multistate exchange requires a single exact 300 K runtime and schedule')
    if runtime.platform!='Reference' or runtime.precision!='double':
        raise UnsupportedCapability('multistate exchange requires Reference double precision')
    if (runtime.ensemble!='NVT' or runtime.integrator!='LangevinMiddle' or
        runtime.device_allocation or runtime.timestep_ps<=0 or runtime.timestep_ps>.0005):
        raise UnsupportedCapability('multistate exchange requires NVT LangevinMiddle with an admitted timestep')
    settings=metadata.get('settings')
    if (not isinstance(settings,dict) or
        settings.get('protocol_kind')!=bundle.transfer.protocol.kind or
        tuple(settings.get('displacement_nm',()))!=tuple(
            bundle.transfer.protocol.geometry_requests.get('displacement_nm',()))):
        raise IdentityError('multistate geometry guard settings differ from sealed transfer maps/displacement')
    states,pairs=_multistate_selection(state_ids,state_pairs)
    available={state.state_id for state in bundle.schedule.states}
    if not set(states)<=available:
        raise MalformedInput('multistate state_ids must be present in the sealed schedule')
    return prepared_run,metadata,bundle,runtime,states,pairs


def _rng_document(python_rng,numpy_rng):
    state=numpy_rng.get_state()
    return {'python':python_rng.getstate(),'numpy':[state[0],state[1].tolist(),*state[2:]]}


def _rng_from_document(document):
    import numpy as np
    def tuples(value): return tuple(tuples(v) for v in value) if isinstance(value,list) else value
    python_rng=random.Random(); python_rng.setstate(tuples(document['python']))
    state=document['numpy']
    numpy_rng=np.random.RandomState(); numpy_rng.set_state((state[0],np.array(state[1],dtype=np.uint32),*state[2:]))
    return python_rng,numpy_rng


@contextmanager
def _host_rng(python_rng,numpy_rng):
    """Pinned upstream imports use both global streams; isolate this serial call."""
    import numpy as np
    old_python,old_numpy=random.getstate(),np.random.get_state()
    random.setstate(python_rng.getstate()); np.random.set_state(numpy_rng.get_state())
    try: yield
    finally:
        python_rng.setstate(random.getstate()); numpy_rng.set_state(np.random.get_state())
        random.setstate(old_python); np.random.set_state(old_numpy)


def _record_phase(pending,phase,report):
    path=pending/(phase+'.json')
    write_json(path,report)
    with path.open('rb') as handle: __import__('os').fsync(handle.fileno())
    sync_directory(pending)


def _publish_round(pending,target,index):
    import os
    seal(pending,index=index)
    if target.exists(): raise FileExistsError(target)
    os.rename(pending,target)
    sync_directory(target.parent)


def _capture(worker,path,w):
    import openmm as mm
    saved=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True,getEnergy=True,getForces=True)
    (path/f'worker-{w}.xml').write_text(mm.XmlSerializer.serialize(saved))
    (path/f'worker-{w}.chk').write_bytes(worker.evaluator.context.createCheckpoint())


def _geometry(worker,snapshot,settings):
    if (worker.bundle.transfer.protocol.kind!=settings['protocol_kind'] or
        tuple(worker.bundle.transfer.protocol.geometry_requests['displacement_nm'])!=tuple(settings['displacement_nm'])):
        raise IdentityError('exchange geometry guard settings differ from actual sealed maps/displacement')
    return _domain(worker.bundle.physical.topology,snapshot,settings['displacement_nm'],settings['protocol_kind'],
                   tuple((link.ml_parent_id,link.mm_parent_id) for link in worker.bundle.physical.links))


def run_exchange(prepared_run,output,*,rounds,steps_per_round,seed,trusted=False,stop_after_rounds=None):
    """Copy one verified prepared bundle; initialize two fixed-identity walkers."""
    if trusted is not True: raise UnsupportedCapability('exchange requires explicitly trusted sealed System/ML assets')
    _integer(rounds,'rounds',500000); _integer(steps_per_round,'steps_per_round')
    _integer(seed,'seed',2**31-10000)
    if stop_after_rounds is not None: _integer(stop_after_rounds,'stop_after_rounds')
    prepared_run,output=Path(prepared_run).resolve(),Path(output).resolve()
    if sha(prepared_run/'metadata.json')!=(prepared_run/'metadata.sha256').read_text().strip():
        raise IdentityError('prepared run metadata hash mismatch')
    prepared=read_json(prepared_run/'metadata.json'); _verify_source_profile(prepared_run,prepared)
    output.mkdir(parents=True,exist_ok=False)
    with controller_lock(output):
        shutil.copytree(prepared_run/'worker',output/'worker')
        (output/'rounds').mkdir()
        from .adapters.atom import load_worker_run
        import numpy as np
        with load_worker_run(output/'worker',prepared['worker_manifest_sha256'],trusted=True) as probe:
            states=[probe.bundle.schedule.states[0].state_id,probe.bundle.schedule.states[-1].state_id]
        run_id=uuid.uuid4().hex; walkers=[f'{run_id}:walker-{w}' for w in (0,1)]
        initial=Path(tempfile.mkdtemp(prefix='.pending-initial-',dir=output))
        source_state=(output/'worker/handover_0.xml').read_text()
        with ExitStack() as stack:
            workers=[stack.enter_context(load_worker_run(output/'worker',prepared['worker_manifest_sha256'],trusted=True,
                integrator_seed=prepared['settings']['seed']+w)) for w in (0,1)]
            for w,worker in enumerate(workers):
                worker.restore_portable_state(source_state,states[w])
                snapshot=_snapshot(worker); _geometry(worker,snapshot,prepared['settings'])
                worker.evaluate(snapshot,states[w]); _capture(worker,initial,w)
        write_json(initial/'record.json',{'state_ids':states,'walker_ids':walkers})
        write_json(initial/'rng.json',_rng_document(random.Random(seed),np.random.RandomState(seed)))
        initial_sha=seal(initial)
        initial.rename(output/'initial'); sync_directory(output)
        metadata={'version':1,'mode':'persistent-pair-exchange-v1','run_id':run_id,
            'rounds':rounds,'steps_per_round':steps_per_round,'host_rng_seed':seed,
            'worker_manifest_sha256':prepared['worker_manifest_sha256'],'profile':prepared['profile'],
            'runtime_identity':prepared['runtime_identity'],'settings':prepared['settings'],
            'walker_ids':walkers,'initial_state_ids':states,'initial_manifest_sha256':initial_sha}
        write_json(output/'metadata.json',metadata)
        (output/'metadata.sha256').write_text(sha(output/'metadata.json')+'\n')
        return _execute_exchange(output,metadata,stop_after_rounds=stop_after_rounds)


def _execute_exchange(directory,metadata,*,stop_after_rounds=None):
    from .adapters.atom import load_worker_run,attempt_pair_exchange
    from openmm import unit
    rows=read_exchange_rounds(directory)
    boundary=directory/'initial' if not rows else directory/'rounds'/f'{len(rows)-1:06d}'
    states=metadata['initial_state_ids'] if not rows else rows[-1]['state_ids_after']
    python_rng,numpy_rng=_rng_from_document(read_json(boundary/'rng.json'))
    started=time.perf_counter(); added=0
    with ExitStack() as stack:
        workers=[stack.enter_context(load_worker_run(directory/'worker',metadata['worker_manifest_sha256'],trusted=True,
            integrator_seed=metadata['settings']['seed']+w)) for w in (0,1)]
        bundle=workers[0].bundle
        for w,worker in enumerate(workers):
            worker.restore_checkpoint((boundary/f'worker-{w}.chk').read_bytes(),states[w])
            snapshot=_snapshot(worker); _geometry(worker,snapshot,metadata['settings'])
            refreshed=worker.evaluate(snapshot,states[w])
            if rows:
                last=rows[-1]['exchange']
                s=last['state_ids_before'].index(states[w])
                if (abs(refreshed.total.energy_kj_mol-last['energies_after_kj_mol'][w])>1e-8 or
                    asdict(refreshed.raw)!=last['raw_energies'][s][w]):
                    raise IdentityError('stale saved exchange energies disagree with fresh checkpoint evaluation')
        while len(rows)<metadata['rounds'] and (stop_after_rounds is None or added<stop_after_rounds):
            index=len(rows)
            pending=Path(tempfile.mkdtemp(prefix=f'.pending-{index:06d}-',dir=directory/'rounds'))
            samples=[]
            try:
                snapshots=[]
                for w,worker in enumerate(workers):
                    worker.evaluator._guard(); worker.evaluator.integrator.step(metadata['steps_per_round'])
                    snapshot=_snapshot(worker); domain=_geometry(worker,snapshot,metadata['settings'])
                    result=worker.evaluate(snapshot,states[w])
                    saved=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
                    samples.append(dict(sample_id=f"{metadata['run_id']}:walker-{w}:round-{index+1}",
                        walker_id=metadata['walker_ids'][w],sequence_number=index+1,state_id=states[w],
                        positions_nm=snapshot.positions_nm,velocities_nm_ps=snapshot.velocities_nm_ps,
                        real_atom_ids=snapshot.real_atom_ids,box_nm=snapshot.box_nm,
                        real_forces_kj_mol_nm=result.total.forces_kj_mol_nm,raw=asdict(result.raw),
                        parameters=dict(result.parameters),domain=domain,temperature_K=worker.runtime.temperature_K,
                        integrator_seed=worker.integrator_seed,step=worker.evaluator.context.getStepCount(),
                        time_ps=saved.getTime().value_in_unit(unit.picosecond)))
                    snapshots.append(snapshot)
                with _host_rng(python_rng,numpy_rng):
                    report=attempt_pair_exchange(workers,snapshots,states,metadata['walker_ids'],
                        phase_callback=lambda phase,result:_record_phase(pending,phase,result))
                after=list(report['state_ids_after'])
                for w,worker in enumerate(workers): _capture(worker,pending,w)
                write_json(pending/'rng.json',_rng_document(python_rng,numpy_rng))
                write_json(pending/'record.json',{'round_index':index,'samples':samples,'exchange':report,
                    'state_ids_after':after,'previous_manifest_sha256':sha(boundary/'manifest.json'),
                    'rng_before_sha256':sha(boundary/'rng.json')})
                target=directory/'rounds'/f'{index:06d}'
                _publish_round(pending,target,index)
            except Exception as error:
                archive=pending if pending.exists() else directory/'failures'/f'published-{uuid.uuid4().hex}'
                if not archive.exists():
                    try: archive.mkdir(parents=True)
                    except Exception as secondary: error.add_note(f'Exchange failure archive: {secondary}')
                for w,worker in enumerate(workers):
                    _archive_failure(archive/f'worker-{w}',worker,error,{'round_index':index,'state_id_before':states[w],
                        'walker_id':metadata['walker_ids'][w],'transaction':'incomplete preserved or published round authoritative'})
                raise
            rows=read_exchange_rounds(directory); states=after; boundary=target; added+=1
    samples=[s for row in rows for s in row['samples']]
    records=EvaluationRecords(bundle.schedule,tuple(s['sample_id'] for s in samples),tuple(s['state_id'] for s in samples),
        tuple(s['walker_id'] for s in samples),tuple(s['sequence_number'] for s in samples),
        *(tuple(s['raw'][k] for s in samples) for k in ('u0_raw_kJ_mol','u1_raw_kJ_mol','outside_energy_kJ_mol','system_total_energy_kJ_mol')),
        bundle.physical.content_identity,bundle.transfer.content_identity,bundle.restraints.content_identity,
        {'run_id':metadata['run_id'],'worker_manifest_sha256':metadata['worker_manifest_sha256'],
         'runtime_identity':metadata['runtime_identity'],'schedule_identity':bundle.schedule.content_identity,
         'profile':'Reference double / pinned CPU model / persistent pair exchange'},'correlated')
    from .schedule import reduced_potentials
    matrix=reduced_potentials(records)
    (directory/'records.json').write_text(to_json(records)+'\n')
    write_json(directory/'observations.json',samples)
    summary={'scope':'bounded two-worker exchange; no equilibrium, affinity or exchanging-walker uncertainty qualification',
        'status':'complete' if len(rows)==metadata['rounds'] else 'interrupted','rounds':len(rows),'samples':len(samples),
        'accepted_exchanges':sum(r['exchange']['accepted'] for r in rows),'walker_ids':metadata['walker_ids'],
        'state_ids_after':states,'all_real_atoms':len(bundle.physical.topology.atoms),'profile':metadata['profile'],
        'elapsed_execution_seconds':time.perf_counter()-started,
        'peak_process_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        'reconstructed_matrix_shape':list(matrix.shape),'binding_result':'not_evaluated'}
    write_json(directory/'summary.json',summary)
    return summary


def resume_exchange(directory,*,trusted=False,stop_after_rounds=None,recover_pending=False):
    if trusted is not True: raise UnsupportedCapability('exchange restart requires explicitly trusted System/ML assets')
    if type(recover_pending) is not bool: raise ValueError('recover_pending must be boolean')
    if stop_after_rounds is not None: _integer(stop_after_rounds,'stop_after_rounds')
    directory=Path(directory).resolve()
    with controller_lock(directory):
        if sha(directory/'metadata.json')!=(directory/'metadata.sha256').read_text().strip():
            raise IdentityError('exchange metadata hash mismatch')
        metadata=read_json(directory/'metadata.json')
        if metadata.get('mode')!='persistent-pair-exchange-v1': raise UnsupportedCapability('unsupported exchange restart mode')
        _verify_source_profile(directory,metadata)
        read_exchange_rounds(directory,allow_pending=recover_pending)
        if recover_pending: preserve_pending(directory)
        return _execute_exchange(directory,metadata,stop_after_rounds=stop_after_rounds)


def _durable_json(path,document):
    import os
    path=Path(path)
    write_json(path,document)
    with path.open('rb') as handle: os.fsync(handle.fileno())
    sync_directory(path.parent)


def _durable_bytes(path,payload):
    import os
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('wb') as handle:
        handle.write(payload); handle.flush(); os.fsync(handle.fileno())
    sync_directory(path.parent)


def _new_durable_directory(path):
    path=Path(path); path.mkdir(parents=True,exist_ok=False); sync_directory(path.parent)
    return path


def _coordinate_digest(positions):
    import json
    payload=json.dumps(positions,separators=(',',':'),allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def _capture_multistate(worker,state_path,checkpoint_path):
    import openmm as mm
    saved=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
    _durable_bytes(state_path,mm.XmlSerializer.serialize(saved).encode())
    _durable_bytes(checkpoint_path,worker.evaluator.context.createCheckpoint())
    return saved


def _multistate_report(worker,index,walker_id,state_id,snapshot,result,saved):
    from openmm import unit
    return {'walker_index':index,'walker_id':walker_id,'state_id':state_id,
        'raw':asdict(result.raw),'total':_plain_document(result.total),'parameters':dict(result.parameters),
        'coordinate_sha256':_coordinate_digest(snapshot.positions_nm),
        'step':int(worker.evaluator.context.getStepCount()),
        'time_ps':float(saved.getTime().value_in_unit(unit.picosecond))}


def _plain_document(value):
    from dataclasses import fields,is_dataclass
    from collections.abc import Mapping
    if is_dataclass(value):
        return {field.name:_plain_document(getattr(value,field.name)) for field in fields(value)}
    if isinstance(value,Mapping):
        return {str(key):_plain_document(item) for key,item in value.items()}
    if isinstance(value,(tuple,list)):
        return [_plain_document(item) for item in value]
    return value


def _multistate_sample(worker,index,walker_id,sequence,state_id,snapshot,result,saved,domain):
    from openmm import unit
    return {'sample_id':None,'walker_id':walker_id,'walker_index':index,
        'sequence_number':sequence,'state_id':state_id,'positions_nm':snapshot.positions_nm,
        'velocities_nm_ps':snapshot.velocities_nm_ps,'real_atom_ids':snapshot.real_atom_ids,
        'box_nm':snapshot.box_nm,'real_forces_kj_mol_nm':result.total.forces_kj_mol_nm,
        'total_energy_kJ_mol':result.total.energy_kj_mol,'raw':asdict(result.raw),
        'parameters':dict(result.parameters),'domain':domain,
        'temperature_K':worker.runtime.temperature_K,'integrator_seed':worker.integrator_seed,
        'step':int(worker.evaluator.context.getStepCount()),
        'time_ps':float(saved.getTime().value_in_unit(unit.picosecond)),
        'physical_identity':worker.bundle.physical.content_identity,
        'transfer_identity':worker.bundle.transfer.content_identity}


def _write_multistate_phase(attempt_directory,name,document):
    if name not in ('evaluated','decision','refreshed','history','attempt'):
        raise ValueError(f'unsupported multistate attempt artifact: {name}')
    _durable_json(Path(attempt_directory)/(name+'.json'),document)


def _publish_multistate_boundary(pending,target,index):
    import os
    from .exchange_journal import seal_tree
    seal_tree(pending,index=index)
    if target.exists(): raise FileExistsError(target)
    os.rename(pending,target)
    sync_directory(target.parent)


def _state_ids_for_permutation(state_ids,permutation):
    return [state_ids[index] for index in permutation]


def _fresh_multistate_check(worker,index,walker_id,state_id,boundary,report,metadata,sample=None):
    import numpy as np
    import openmm as mm
    from openmm import unit
    from .schema import IdentityError
    checkpoint=(boundary/'workers'/f'worker-{index:03d}.chk').read_bytes()
    state_path=boundary/'workers'/f'worker-{index:03d}-state.xml'
    worker.restore_checkpoint(checkpoint,state_id)
    snapshot=_snapshot(worker)
    portable=mm.XmlSerializer.deserialize(state_path.read_text())
    particle_indices=[worker.bundle.physical.real_to_final[a.atom_id] for a in worker.bundle.physical.topology.atoms]
    portable_x=portable.getPositions(asNumpy=True).value_in_unit(unit.nanometer)[particle_indices]
    portable_v=portable.getVelocities(asNumpy=True).value_in_unit(unit.nanometer/unit.picosecond)[particle_indices]
    if not np.array_equal(np.asarray(snapshot.positions_nm),portable_x) or not np.array_equal(
        np.asarray(snapshot.velocities_nm_ps),portable_v):
        raise IdentityError('restored checkpoint coordinates/velocities disagree with portable State')
    actual_parameters=dict(worker.evaluator.context.getParameters())
    portable_parameters=dict(portable.getParameters())
    if portable_parameters!=actual_parameters:
        raise IdentityError('restored checkpoint parameters disagree with portable State')
    if snapshot.box_nm is not None:
        portable_box=portable.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.nanometer)
        if not np.array_equal(np.asarray(snapshot.box_nm),portable_box):
            raise IdentityError('restored checkpoint box vectors disagree with portable State')
    expected_parameters=metadata['state_parameters'][state_id]
    if any(actual_parameters.get(name)!=value for name,value in expected_parameters.items()):
        raise IdentityError('restored checkpoint parameters disagree with final assignment')
    if _coordinate_digest(snapshot.positions_nm)!=report['coordinate_sha256']:
        raise IdentityError('restored checkpoint coordinates disagree with final-state report')
    if sample is not None and snapshot.positions_nm!=tuple(tuple(v) for v in sample['positions_nm']):
        raise IdentityError('restored checkpoint coordinates disagree with captured sample')
    result=worker.evaluate(snapshot,state_id)
    actual_total=_plain_document(result.total); saved_total=report['total']
    total_matches=set(actual_total)==set(saved_total)
    if total_matches:
        for name,value in actual_total.items():
            saved=saved_total[name]
            if name=='energy_kj_mol':
                total_matches=abs(value-saved)<=1e-8
            elif name=='forces_kj_mol_nm':
                total_matches=np.allclose(value,saved,atol=1e-8,rtol=0)
            else:
                total_matches=value==saved
            if not total_matches: break
    if (asdict(result.raw)!=report['raw'] or result.parameters!=report['parameters'] or
        not total_matches):
        raise IdentityError('fresh actual-context complete raw/total/parameter report disagrees with checkpoint')


def _archive_multistate_failure(pending,workers,metadata,boundary_index,error):
    pending=Path(pending)
    primary={'error_type':type(error).__name__,'message':str(error),'boundary_index':boundary_index,
             'run_id':metadata['run_id'],'archive_errors':[]}
    try: _durable_json(pending/'failure.json',primary)
    except Exception as secondary:
        primary['archive_errors'].append({'operation':'write primary failure record',
            'error_type':type(secondary).__name__,'message':str(secondary)})
        error.add_note(f'Multistate failure archive (primary record): {secondary}')
    for w,worker in enumerate(workers):
        try:
            _archive_failure(pending/'failures'/f'worker-{w:03d}',worker,error,
                {'boundary_index':boundary_index,'walker_id':metadata['walker_ids'][w],
                 'state_id_before':metadata['state_ids'][metadata.get('last_walker_to_state',[w]*len(workers))[w]],
                 'transaction':'incomplete multistate boundary; replay the whole boundary'})
        except Exception as secondary:
            primary['archive_errors'].append({'operation':f'capture worker {w}',
                'error_type':type(secondary).__name__,'message':str(secondary)})
            error.add_note(f'Multistate failure archive (worker {w}): {secondary}')
    if primary['archive_errors']:
        try: _durable_json(pending/'failure.json',primary)
        except Exception as secondary:
            error.add_note(f'Multistate failure archive (secondary diagnostics): {secondary}')


def _execute_multistate(directory,metadata,*,stop_after_boundaries=None):
    import openmm as mm
    import numpy as np
    from openmm import unit
    from .adapters.atom import load_worker_run,attempt_pair_exchange
    from .exchange_journal import read_multistate_boundaries
    from .schema import EvaluationRecords
    rows=read_multistate_boundaries(directory)
    initial=directory/'initial'
    boundary=initial if not rows else directory/'boundaries'/f'{len(rows)-1:06d}'
    state_record=read_json(boundary/'record.json')
    walker_to_state=list(state_record['walker_to_state'] if not rows else state_record['walker_to_state_final'])
    current_state_ids=_state_ids_for_permutation(metadata['state_ids'],walker_to_state)
    python_rng,numpy_rng=_rng_from_document(read_json(boundary/'rng.json'))
    started=time.perf_counter(); added=0
    with ExitStack() as stack:
        workers=[stack.enter_context(load_worker_run(directory/'worker',metadata['worker_manifest_sha256'],trusted=True,
            integrator_seed=metadata['integrator_seed_base']+w)) for w in range(len(metadata['walker_ids']))]
        reports=read_json(boundary/'final-state-reports.json')['workers']
        sample_by_worker={sample['walker_index']:sample for sample in rows[-1]['samples']} if rows else None
        for w,worker in enumerate(workers):
            _geometry(worker,_snapshot(worker),metadata['settings'])
            _fresh_multistate_check(worker,w,metadata['walker_ids'][w],current_state_ids[w],
                                    boundary,reports[w],metadata,
                                    None if sample_by_worker is None else sample_by_worker[w])
        while len(rows)<metadata['boundaries'] and (
                stop_after_boundaries is None or added<stop_after_boundaries):
            index=len(rows); pending=directory/'pending'
            _new_durable_directory(pending)
            start_permutation=list(walker_to_state)
            try:
                sample_root=_new_durable_directory(pending/'samples')
                attempt_root=_new_durable_directory(pending/'attempts')
                worker_root=_new_durable_directory(pending/'workers')
                snapshots=[None]*len(workers); sample_rows=[None]*len(workers)
                for w,worker in enumerate(workers):
                    worker.evaluator._guard()
                    worker.evaluator.integrator.step(metadata['steps_per_boundary'])
                    snapshot=_snapshot(worker)
                    domain=_geometry(worker,snapshot,metadata['settings'])
                    state_id=metadata['state_ids'][walker_to_state[w]]
                    result=worker.evaluate(snapshot,state_id)
                    saved=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
                    row=_multistate_sample(worker,w,metadata['walker_ids'][w],index+1,state_id,
                                           snapshot,result,saved,domain)
                    row['sample_id']=f"{metadata['run_id']}:walker-{w}:boundary-{index+1}"
                    sample_rows[w]=row; snapshots[w]=snapshot
                    stem=f'worker-{w:03d}'
                    _durable_json(sample_root/f'{stem}.json',row)
                    _durable_bytes(sample_root/f'{stem}-state.xml',mm.XmlSerializer.serialize(saved).encode())
                    _durable_bytes(sample_root/f'{stem}.chk',worker.evaluator.context.createCheckpoint())

                for q,(state_left,state_right) in enumerate(metadata['state_pairs']):
                    inverse=[walker_to_state.index(state) for state in range(len(walker_to_state))]
                    selected=[inverse[state_left],inverse[state_right]]
                    pair_states=[metadata['state_ids'][state_left],metadata['state_ids'][state_right]]
                    pair_walkers=[metadata['walker_ids'][w] for w in selected]
                    before=list(walker_to_state)
                    attempt_dir=_new_durable_directory(attempt_root/f'{q:04d}')
                    attempt_doc={'attempt_index':q,'state_pair_indices':[state_left,state_right],
                        'state_ids':pair_states,'worker_indices':selected,'walker_ids':pair_walkers,
                        'walker_to_state_before':before,'state_to_walker_before':inverse,
                        'sample_ids':[sample_rows[w]['sample_id'] for w in selected]}
                    _write_multistate_phase(attempt_dir,'attempt',attempt_doc)
                    decision_state={'document':None}
                    def phase_callback(phase,report):
                        common={'attempt_index':q,'state_pair_indices':[state_left,state_right],
                            'worker_indices':selected,'walker_to_state_before':before}
                        if phase=='evaluated':
                            _write_multistate_phase(attempt_dir,'evaluated',{**report,**common})
                        elif phase=='decision':
                            after=list(before)
                            if report['accepted']:
                                after[selected[0]],after[selected[1]]=after[selected[1]],after[selected[0]]
                            document={**report,**common,'walker_to_state_after':after}
                            _write_multistate_phase(attempt_dir,'decision',document)
                            history={'attempt':attempt_doc,'decision':document,
                                'walker_to_state_before':before,'walker_to_state_after':after,
                                'resolved_state_to_walker':inverse,'accepted':report['accepted']}
                            _write_multistate_phase(attempt_dir,'history',history)
                            decision_state['document']=document
                            walker_to_state[:]=after
                        elif phase=='refreshed':
                            document={**report,**common,
                                'walker_to_state_after':list(walker_to_state)}
                            _write_multistate_phase(attempt_dir,'refreshed',document)
                        else:
                            raise IdentityError(f'unknown adapter exchange phase: {phase}')
                    pair_workers=[workers[w] for w in selected]
                    pair_snapshots=[snapshots[w] for w in selected]
                    with _host_rng(python_rng,numpy_rng):
                        report=attempt_pair_exchange(pair_workers,pair_snapshots,pair_states,pair_walkers,
                                                      phase_callback=phase_callback)
                    if decision_state['document'] is None:
                        raise IdentityError('actual pair adapter omitted its durable decision callback')

                final_reports=[]
                for w,worker in enumerate(workers):
                    state_id=metadata['state_ids'][walker_to_state[w]]
                    snapshot=_snapshot(worker); _geometry(worker,snapshot,metadata['settings'])
                    result=worker.evaluate(snapshot,state_id)
                    saved=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
                    final_reports.append(_multistate_report(worker,w,metadata['walker_ids'][w],
                        state_id,snapshot,result,saved))
                _durable_json(pending/'final-state-reports.json',{'workers':final_reports})
                for w,worker in enumerate(workers):
                    stem=f'worker-{w:03d}'
                    _capture_multistate(worker,worker_root/f'{stem}-state.xml',worker_root/f'{stem}.chk')
                inverse=[walker_to_state.index(state) for state in range(len(walker_to_state))]
                _durable_json(pending/'walker-to-state.json',{'walker_to_state':list(walker_to_state),
                    'state_to_walker':inverse})
                _durable_json(pending/'rng.json',_rng_document(python_rng,numpy_rng))
                _durable_json(pending/'record.json',{'boundary_index':index,
                    'previous_manifest_sha256':sha(boundary/'manifest.json'),
                    'rng_before_sha256':sha(boundary/'rng.json'),
                    'walker_to_state_start':start_permutation,
                    'walker_to_state_final':list(walker_to_state),
                    'state_to_walker_final':inverse,'pair_count':len(metadata['state_pairs'])})
                target=directory/'boundaries'/f'{index:06d}'
                _publish_multistate_boundary(pending,target,index)
            except Exception as error:
                if pending.exists():
                    try: _new_durable_directory(pending/'failures')
                    except FileExistsError: pass
                    except Exception as secondary:
                        error.add_note(f'Multistate failure archive (failure directory): {secondary}')
                    metadata['last_walker_to_state']=list(walker_to_state)
                    _archive_multistate_failure(pending,workers,metadata,index,error)
                raise
            rows=read_multistate_boundaries(directory)
            walker_to_state=list(rows[-1]['walker_to_state_final'])
            current_state_ids=_state_ids_for_permutation(metadata['state_ids'],walker_to_state)
            boundary=target; added+=1
    samples=[sample for row in rows for sample in row['samples']]
    bundle=workers[0].bundle
    records=EvaluationRecords(bundle.schedule,tuple(s['sample_id'] for s in samples),
        tuple(s['state_id'] for s in samples),tuple(s['walker_id'] for s in samples),
        tuple(s['sequence_number'] for s in samples),
        *(tuple(s['raw'][name] for s in samples) for name in
          ('u0_raw_kJ_mol','u1_raw_kJ_mol','outside_energy_kJ_mol','system_total_energy_kJ_mol')),
        bundle.physical.content_identity,bundle.transfer.content_identity,bundle.restraints.content_identity,
        {'run_id':metadata['run_id'],'worker_manifest_sha256':metadata['worker_manifest_sha256'],
         'runtime_identity':metadata['runtime_identity'],'schedule_identity':bundle.schedule.content_identity,
         'profile':'Reference double / pinned CPU model / persistent multistate exchange'},'correlated')
    from .schedule import reduced_potentials
    matrix=reduced_potentials(records)
    (directory/'records.json').write_text(to_json(records)+'\n')
    write_json(directory/'observations.json',samples)
    final_perm=list(range(len(metadata['state_ids']))) if not rows else rows[-1]['walker_to_state_final']
    summary={'scope':'bounded serial multistate exchange; no equilibrium, affinity or exchanging-walker uncertainty qualification',
        'status':'complete' if len(rows)==metadata['boundaries'] else 'interrupted',
        'boundaries':len(rows),'samples':len(samples),'attempts_per_boundary':len(metadata['state_pairs']),
        'accepted_exchanges':sum(bool(attempt['accepted']) for row in rows for attempt in row['attempts']),
        'walker_ids':metadata['walker_ids'],'state_ids_after':_state_ids_for_permutation(metadata['state_ids'],final_perm),
        'walker_to_state_final':final_perm,'all_real_atoms':len(bundle.physical.topology.atoms),
        'profile':metadata['profile'],'elapsed_execution_seconds':time.perf_counter()-started,
        'peak_process_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        'reconstructed_matrix_shape':list(matrix.shape),'binding_result':'not_evaluated'}
    write_json(directory/'summary.json',summary)
    return summary


def run_multistate_exchange(prepared_run,output,*,state_ids,state_pairs,boundaries,
                            steps_per_boundary,seed,trusted=False,stop_after_boundaries=None):
    """Start the separate, versioned serial multistate exchange controller."""
    if trusted is not True:
        raise UnsupportedCapability('multistate exchange requires explicitly trusted sealed System/ML assets')
    _integer(boundaries,'boundaries',500001)
    _integer(steps_per_boundary,'steps_per_boundary')
    _integer(seed,'seed',2**31-10000)
    if stop_after_boundaries is not None:
        _integer(stop_after_boundaries,'stop_after_boundaries')
    prepared,prepared_metadata,bundle,runtime,states,pairs=_admit_multistate_prepared(
        prepared_run,state_ids,state_pairs)
    output=Path(output).resolve()
    if output.exists():
        raise FileExistsError(output)
    import os
    import numpy as np
    import openmm as mm
    from .adapters.atom import load_worker_run
    from .exchange_journal import seal_tree
    output.mkdir(parents=True)
    with controller_lock(output):
        shutil.copytree(prepared/'worker',output/'worker')
        _verify_source_profile(output,prepared_metadata)
        (output/'boundaries').mkdir()
        settings=dict(prepared_metadata['settings'])
        integrator_seed_base=settings.get('seed',seed)
        _integer(integrator_seed_base,'prepared integrator seed',2**31)
        run_id=uuid.uuid4().hex
        walker_ids=[f'{run_id}:walker-{w}' for w in range(len(states))]
        source_state=(output/'worker/handover_0.xml').read_text()
        pending_initial=output/f'.pending-initial-{uuid.uuid4().hex}'
        _new_durable_directory(pending_initial)
        _new_durable_directory(pending_initial/'workers')
        python_rng,numpy_rng=random.Random(seed),np.random.RandomState(seed)
        with ExitStack() as stack:
            workers=[stack.enter_context(load_worker_run(output/'worker',prepared_metadata['worker_manifest_sha256'],
                trusted=True,integrator_seed=integrator_seed_base+w)) for w in range(len(states))]
            reports=[]
            for w,worker in enumerate(workers):
                worker.restore_portable_state(source_state,states[w])
                snapshot=_snapshot(worker); _geometry(worker,snapshot,settings)
                result=worker.evaluate(snapshot,states[w])
                saved=worker.evaluator.context.getState(getPositions=True,getVelocities=True,getParameters=True)
                reports.append(_multistate_report(worker,w,walker_ids[w],states[w],snapshot,result,saved))
                _capture_multistate(worker,pending_initial/'workers'/f'worker-{w:03d}-state.xml',
                                    pending_initial/'workers'/f'worker-{w:03d}.chk')
        identity=list(range(len(states)))
        _durable_json(pending_initial/'record.json',{'run_id':run_id,'walker_ids':walker_ids,
            'walker_to_state':identity,'state_to_walker':identity})
        _durable_json(pending_initial/'walker-to-state.json',{'walker_to_state':identity,
            'state_to_walker':identity})
        _durable_json(pending_initial/'final-state-reports.json',{'workers':reports})
        _durable_json(pending_initial/'rng.json',_rng_document(python_rng,numpy_rng))
        seal_tree(pending_initial,index=-1)
        os.rename(pending_initial,output/'initial')
        sync_directory(output)
        beta=1/(.00831446261815324*300.)
        metadata={'version':1,'mode':'persistent-multistate-exchange-v1','run_id':run_id,
            'boundaries':boundaries,'steps_per_boundary':steps_per_boundary,'host_rng_seed':seed,
            'integrator_seed_base':integrator_seed_base,'worker_manifest_sha256':prepared_metadata['worker_manifest_sha256'],
            'profile':prepared_metadata['profile'],'runtime_identity':runtime.content_identity,
            'physical_identity':bundle.physical.content_identity,'alchemical_identity':bundle.content_identity,
            'transfer_identity':bundle.transfer.content_identity,'restraints_identity':bundle.restraints.content_identity,
            'schedule_identity':bundle.schedule.content_identity,'settings':settings,
            'temperature_K':300.,'beta_mol_per_kJ':beta,'state_ids':list(states),
            'state_pairs':[list(pair) for pair in pairs],
            'state_parameters':{state.state_id:dict(state.parameters) for state in bundle.schedule.states if state.state_id in states},
            'walker_ids':walker_ids,'real_atom_ids':[atom.atom_id for atom in bundle.physical.topology.atoms],
            'initial_manifest_sha256':sha(output/'initial/manifest.json')}
        _durable_json(output/'metadata.json',metadata)
        _durable_bytes(output/'metadata.sha256',(sha(output/'metadata.json')+'\n').encode())
        return _execute_multistate(output,metadata,stop_after_boundaries=stop_after_boundaries)


def resume_multistate_exchange(directory,*,trusted=False,stop_after_boundaries=None,recover_pending=False):
    if trusted is not True:
        raise UnsupportedCapability('multistate restart requires explicitly trusted System/ML assets')
    if type(recover_pending) is not bool:
        raise MalformedInput('recover_pending must be boolean')
    if stop_after_boundaries is not None:
        _integer(stop_after_boundaries,'stop_after_boundaries')
    directory=Path(directory).resolve()
    with controller_lock(directory):
        if sha(directory/'metadata.json')!=(directory/'metadata.sha256').read_text().strip():
            raise IdentityError('multistate metadata hash mismatch')
        metadata=read_json(directory/'metadata.json')
        if metadata.get('mode')!='persistent-multistate-exchange-v1':
            raise UnsupportedCapability('unsupported multistate exchange restart mode')
        _verify_source_profile(directory,metadata)
        from .exchange_journal import read_multistate_boundaries
        read_multistate_boundaries(directory,allow_pending=recover_pending)
        if recover_pending:
            from .exchange_journal import preserve_multistate_pending
            preserve_multistate_pending(directory)
        return _execute_multistate(directory,metadata,stop_after_boundaries=stop_after_boundaries)
