"""Bounded synchronous pair exchange with whole-round local transactions.

Physics/Metropolis live in the existing adapter. This controller owns identity,
both host RNG streams, checkpoints and explicit interruption recovery.
"""
from contextlib import contextmanager,ExitStack
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
from .schema import (EvaluationRecords,IdentityError,UnsupportedCapability,to_json)
from .workflow import _archive_failure,_domain,_integer,_profile,_snapshot


def _verify_source_profile(directory,metadata):
    if metadata.get('version')!=1 or metadata['profile']!=_profile():
        raise UnsupportedCapability('exchange checkpoint continuation requires identical runtime/software profile')
    manifest_path=directory/'worker/manifest.json'
    if sha(manifest_path)!=metadata['worker_manifest_sha256']:
        raise IdentityError('exchange worker manifest hash mismatch')
    manifest=read_json(manifest_path)
    for name,digest in manifest['files'].items():
        path=(directory/'worker'/name).resolve()
        if (directory/'worker').resolve() not in path.parents or sha(path)!=digest:
            raise IdentityError(f'exchange worker artifact mismatch: {name}')
        prefix='runtime/source/atm_mlmm/'
        if name.startswith(prefix) and sha(Path(__file__).parent/name[len(prefix):])!=digest:
            raise IdentityError(f'exchange source differs from bundled source: {name}')


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
