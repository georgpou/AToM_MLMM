"""Local single-controller round transactions and strict inert prefix validation."""
from contextlib import contextmanager
import fcntl
import hashlib
import math
import os
from pathlib import Path
import re
import random
import sys
import uuid

from .persistence import read_json,write_json
from .schema import IdentityError


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sync_directory(path):
    fd=os.open(path,os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


def _sync_rename_parents(source_parent,destination_parent):
    errors=[]
    for path in (Path(destination_parent),Path(source_parent)):
        try: sync_directory(path)
        except Exception as error:
            if errors:
                errors[0].add_note(f'Additional rename-parent fsync failure at {path}: {error}')
            else:
                errors.append(error)
    if errors: raise errors[0]


@contextmanager
def controller_lock(directory):
    with (Path(directory)/'.controller.lock').open('a') as handle:
        try: fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise IdentityError('another exchange controller owns this local attempt') from error
        try: yield
        finally: fcntl.flock(handle,fcntl.LOCK_UN)


def seal(directory, *, index=None):
    files={p.name:sha(p) for p in sorted(directory.iterdir()) if p.is_file()}
    write_json(directory/'manifest.json',{'version':1,'index':index,'files':files})
    for p in directory.iterdir():
        with p.open('rb') as handle: os.fsync(handle.fileno())
    sync_directory(directory)
    return sha(directory/'manifest.json')


def verify(directory, *, index=None):
    if directory.is_symlink() or not directory.is_dir():
        raise IdentityError('exchange transaction directory identity mismatch')
    manifest=read_json(directory/'manifest.json')
    required={'record.json','rng.json','worker-0.xml','worker-1.xml','worker-0.chk','worker-1.chk'}
    if index is not None: required |= {'evaluated.json','decision.json','refreshed.json'}
    if (manifest.get('version')!=1 or manifest.get('index')!=index or
            set(manifest.get('files',{}))!=required or
            {p.name for p in directory.iterdir()}!=required|{'manifest.json'}):
        raise IdentityError('exchange transaction complete artifact identity mismatch')
    for name,digest in manifest['files'].items():
        path=directory/name
        if path.is_symlink() or not path.is_file() or sha(path)!=digest:
            raise IdentityError(f'exchange transaction hash mismatch: {path}')
    return manifest


def read_exchange_rounds(directory, *, allow_pending=False):
    """Return hash/identity/history-verified committed records; never load code."""
    directory=Path(directory)
    if sha(directory/'metadata.json')!=(directory/'metadata.sha256').read_text().strip():
        raise IdentityError('exchange metadata hash mismatch')
    metadata=read_json(directory/'metadata.json')
    initial=directory/'initial'
    verify(initial)
    previous=sha(initial/'manifest.json')
    if previous!=metadata['initial_manifest_sha256']:
        raise IdentityError('exchange initial boundary identity mismatch')
    initial_record=read_json(initial/'record.json')
    states=list(metadata['initial_state_ids'])
    walkers=metadata['walker_ids']
    if initial_record['state_ids']!=states or initial_record['walker_ids']!=walkers:
        raise IdentityError('exchange initial worker/state identity mismatch')
    rounds=directory/'rounds'
    paths=sorted(rounds.iterdir())
    pending=[p for p in paths if p.name.startswith('.pending-')]
    if pending and not allow_pending:
        raise IdentityError('incomplete exchange transaction preserved; inspect before explicit rollback/replay')
    paths=[p for p in paths if p not in pending]
    if any(not re.fullmatch(r'\d{6}',p.name) for p in paths):
        raise IdentityError('unrecognized exchange journal entry')
    if len(paths)>metadata['rounds']:
        raise IdentityError('exchange journal exceeds declared rounds')
    rows=[]; sample_ids=set()
    for index,path in enumerate(paths):
        if path.name!=f'{index:06d}': raise IdentityError('missing/reordered exchange round')
        manifest=verify(path,index=index)
        row=read_json(path/'record.json'); report=row['exchange']
        expected_after=list(reversed(states)) if report['accepted'] is True else states
        if (type(report['accepted']) is not bool or row['round_index']!=index or
            row['previous_manifest_sha256']!=previous or report['state_ids_before']!=states or
            report['state_ids_after']!=expected_after or report['walker_ids']!=walkers or
            len(row['samples'])!=2 or row['state_ids_after']!=expected_after or
            row['rng_before_sha256']!=sha((initial if index==0 else paths[index-1])/'rng.json')):
            raise IdentityError('exchange state/walker/RNG history identity mismatch')
        for w,sample in enumerate(row['samples']):
            expected=f"{metadata['run_id']}:walker-{w}:round-{index+1}"
            if (sample['sample_id']!=expected or sample['sample_id'] in sample_ids or
                sample['walker_id']!=walkers[w] or sample['state_id']!=states[w] or
                sample['sequence_number']!=index+1):
                raise IdentityError('exchange sample/sequence identity mismatch')
            sample_ids.add(sample['sample_id'])
        evaluated=read_json(path/'evaluated.json'); decision=read_json(path/'decision.json')
        if (read_json(path/'refreshed.json')!=report or
            any(evaluated[k]!=report[k] for k in evaluated) or
            any(decision[k]!=report[k] for k in decision)):
            raise IdentityError('exchange decision/refresh history mismatch')
        previous=sha(path/'manifest.json'); states=expected_after; rows.append(row)
    return rows


def read_multistate_boundaries(directory, *, allow_pending=False):
    """Read only a versioned multistate journal, without loading worker code."""
    if type(allow_pending) is not bool:
        raise ValueError('allow_pending must be boolean')
    directory=Path(directory)
    if sha(directory/'metadata.json')!=(directory/'metadata.sha256').read_text().strip():
        raise IdentityError('multistate metadata hash mismatch')
    metadata=read_json(directory/'metadata.json')
    if metadata.get('mode')!='persistent-multistate-exchange-v1':
        raise IdentityError('exchange journal mode is not persistent-multistate-exchange-v1')
    _verify_multistate_source(directory,metadata)
    _validate_multistate_metadata(metadata)
    timestep_ps=_validate_multistate_worker_contract(directory,metadata)
    initial=directory/'initial'
    initial_manifest=verify_tree(initial,index=-1)
    if sha(initial/'manifest.json')!=metadata.get('initial_manifest_sha256'):
        raise IdentityError('multistate initial boundary identity mismatch')
    n=len(metadata['state_ids']); workers=metadata['walker_ids']
    initial_expected={'record.json','rng.json','walker-to-state.json','final-state-reports.json'}
    for w in range(n):
        initial_expected|={f'workers/worker-{w:03d}-state.xml',f'workers/worker-{w:03d}.chk'}
    if set(initial_manifest['files'])!=initial_expected:
        raise IdentityError('multistate initial artifact layout mismatch')
    initial_record=read_json(initial/'record.json')
    _validate_permutation(initial_record.get('walker_to_state'),n,'initial permutation')
    _validate_permutation(initial_record.get('state_to_walker'),n,'initial record inverse')
    if (initial_record.get('run_id')!=metadata['run_id'] or
        initial_record.get('walker_ids')!=workers or initial_record['walker_to_state']!=list(range(n)) or
        initial_record['state_to_walker']!=list(range(n))):
        raise IdentityError('multistate initial walker/state identity mismatch')
    _validate_inverse(initial/'walker-to-state.json',list(range(n)),n)
    _validate_rng_document(read_json(initial/'rng.json'))
    initial_reports=_validate_final_reports(initial/'final-state-reports.json',metadata,None,
                                            expected_permutation=list(range(n)))
    previous_reports=initial_reports

    pending=directory/'pending'
    if pending.exists() or pending.is_symlink():
        if not allow_pending:
            raise IdentityError('incomplete multistate boundary preserved; explicit rollback/replay is required')
        if pending.is_symlink() or not pending.is_dir():
            raise IdentityError('multistate pending path identity mismatch')
    boundary_root=directory/'boundaries'
    if boundary_root.is_symlink() or not boundary_root.is_dir():
        raise IdentityError('multistate boundaries directory identity mismatch')
    paths=sorted(boundary_root.iterdir())
    if any(not re.fullmatch(r'\d{6}',p.name) or p.is_symlink() or not p.is_dir() for p in paths):
        raise IdentityError('unrecognized multistate boundary entry')
    if len(paths)>metadata['boundaries']:
        raise IdentityError('multistate journal exceeds declared boundary count')
    rows=[]; previous=sha(initial/'manifest.json')
    before=list(range(n)); sample_ids=set(); sequences={walker:0 for walker in workers}
    schedule_pairs=metadata['state_pairs']
    for index,path in enumerate(paths):
        if path.name!=f'{index:06d}':
            raise IdentityError('multistate boundary prefix is missing or reordered')
        manifest=verify_tree(path,index=index)
        record=read_json(path/'record.json')
        rng_parent=initial if index==0 else paths[index-1]
        if (type(record.get('boundary_index')) is not int or record['boundary_index']!=index or
            record.get('previous_manifest_sha256')!=previous or
            record.get('rng_before_sha256')!=sha(rng_parent/'rng.json')):
            raise IdentityError('multistate boundary chain/permutation identity mismatch')
        _validate_permutation(record.get('walker_to_state_start'),n,'start permutation')
        if record['walker_to_state_start']!=before:
            raise IdentityError('multistate boundary chain/permutation identity mismatch')
        _validate_permutation(record.get('walker_to_state_final'),n,'final permutation')
        expected_final_inverse=[record['walker_to_state_final'].index(i) for i in range(n)]
        _validate_permutation(record.get('state_to_walker_final'),n,'final record inverse')
        if record['state_to_walker_final']!=expected_final_inverse:
            raise IdentityError('multistate final record inverse disagrees with its permutation')
        _validate_inverse(path/'walker-to-state.json',record['walker_to_state_final'],n)
        if type(record.get('pair_count')) is not int or record['pair_count']!=len(schedule_pairs):
            raise IdentityError('multistate boundary pair count mismatch')
        expected_files={'record.json','rng.json','walker-to-state.json','final-state-reports.json'}
        sample_rows=[]
        start=record['walker_to_state_start']
        for w in range(n):
            stem=f'worker-{w:03d}'
            expected_files|={f'samples/{stem}.json',f'samples/{stem}-state.xml',f'samples/{stem}.chk',
                             f'workers/{stem}-state.xml',f'workers/{stem}.chk'}
            sample=read_json(path/'samples'/f'{stem}.json')
            sample_id=f"{metadata['run_id']}:walker-{w}:boundary-{index+1}"
            state_id=metadata['state_ids'][start[w]]
            if (not isinstance(sample.get('sample_id'),str) or sample.get('sample_id')!=sample_id or sample_id in sample_ids or
                not isinstance(sample.get('walker_id'),str) or sample.get('walker_id')!=workers[w] or
                type(sample.get('walker_index')) is not int or sample.get('walker_index')!=w or
                not isinstance(sample.get('state_id'),str) or sample.get('state_id')!=state_id or
                type(sample.get('sequence_number')) is not int or sample.get('sequence_number')!=index+1 or
                not _same_parameters(sample.get('parameters'),metadata['state_parameters'].get(state_id))):
                raise IdentityError('multistate sample ID/sequence/state/parameter identity mismatch')
            _validate_sample(sample,metadata)
            _validate_expected_clock(sample['step'],sample['time_ps'],previous_reports[w],
                                     metadata['steps_per_boundary'],timestep_ps)
            sample_ids.add(sample_id); sequences[workers[w]]=index+1; sample_rows.append(sample)
        current=list(start); attempt_rows=[]
        for q,(state_left,state_right) in enumerate(schedule_pairs):
            attempt_dir=path/'attempts'/f'{q:04d}'
            names={f'attempts/{q:04d}/{name}.json' for name in
                   ('attempt','evaluated','decision','refreshed','history')}
            expected_files|=names
            attempt=read_json(attempt_dir/'attempt.json')
            inverse=[current.index(i) for i in range(n)]
            selected=[inverse[state_left],inverse[state_right]]
            pair_states=[metadata['state_ids'][state_left],metadata['state_ids'][state_right]]
            pair_walkers=[workers[w] for w in selected]
            before_attempt=list(current)
            sample_ids_for_pair=[sample_rows[w]['sample_id'] for w in selected]
            if type(attempt.get('attempt_index')) is not int or attempt['attempt_index']!=q:
                raise IdentityError('multistate attempt index identity mismatch')
            _validate_exact_int_list(attempt.get('state_pair_indices'),[state_left,state_right],
                                     'attempt state-pair indices')
            _validate_exact_int_list(attempt.get('worker_indices'),selected,'attempt worker indices')
            _validate_permutation(attempt.get('walker_to_state_before'),n,'attempt before permutation')
            _validate_permutation(attempt.get('state_to_walker_before'),n,'attempt before inverse')
            if (attempt.get('state_ids')!=pair_states or
                attempt.get('walker_ids')!=pair_walkers or attempt['walker_to_state_before']!=before_attempt or
                attempt['state_to_walker_before']!=inverse or
                attempt.get('sample_ids')!=sample_ids_for_pair):
                raise IdentityError('multistate resolved attempt identity mismatch')
            evaluated=read_json(attempt_dir/'evaluated.json')
            decision=read_json(attempt_dir/'decision.json')
            refreshed=read_json(attempt_dir/'refreshed.json')
            history=read_json(attempt_dir/'history.json')
            _validate_pair_evaluations(evaluated,pair_states,pair_walkers,metadata)
            expected_common={'attempt_index':q,'state_pair_indices':[state_left,state_right],
                'worker_indices':selected,'walker_to_state_before':before_attempt}
            for document in (evaluated,decision,refreshed):
                if type(document.get('attempt_index')) is not int or document['attempt_index']!=q:
                    raise IdentityError('multistate attempt phase index is malformed')
                _validate_exact_int_list(document.get('state_pair_indices'),[state_left,state_right],
                                         'attempt phase state-pair indices')
                _validate_exact_int_list(document.get('worker_indices'),selected,
                                         'attempt phase worker indices')
                _validate_permutation(document.get('walker_to_state_before'),n,
                                      'attempt phase before permutation')
                if any(document.get(key)!=value for key,value in expected_common.items()):
                    raise IdentityError('multistate attempt phase identity differs from its resolved pair')
            if any(decision.get(key)!=value for key,value in evaluated.items()):
                raise IdentityError('multistate evaluated and decision phases disagree')
            accepted=decision.get('accepted')
            if type(accepted) is not bool:
                raise IdentityError('multistate decision acceptance must be boolean')
            after=list(current)
            if accepted:
                after[selected[0]],after[selected[1]]=after[selected[1]],after[selected[0]]
            _validate_permutation(decision.get('walker_to_state_after'),n,'decision after permutation')
            if (decision['walker_to_state_before']!=before_attempt or
                decision['walker_to_state_after']!=after or
                decision.get('state_ids_after')!=[metadata['state_ids'][after[w]] for w in selected]):
                raise IdentityError('multistate decision permutation mismatch')
            for key in ('walker_ids','state_ids_before','state_ids_after','accepted',
                        'reduced_energies','exponent','raw_energies'):
                if refreshed.get(key)!=decision.get(key):
                    raise IdentityError('multistate refreshed and decision phases disagree')
            _validate_permutation(refreshed.get('walker_to_state_after'),n,'refreshed after permutation')
            if (refreshed['walker_to_state_after']!=after or
                refreshed.get('physical_identity')!=metadata.get('physical_identity') or
                refreshed.get('alchemical_identity')!=metadata.get('alchemical_identity') or
                refreshed.get('runtime_identity')!=metadata.get('runtime_identity')):
                raise IdentityError('multistate refreshed assignment/worker identity mismatch')
            _validate_refreshed(refreshed,selected,after,metadata,evaluated)
            _validate_permutation(history.get('walker_to_state_before'),n,'history before permutation')
            _validate_permutation(history.get('walker_to_state_after'),n,'history after permutation')
            _validate_permutation(history.get('resolved_state_to_walker'),n,'history resolved inverse')
            if (type(history.get('accepted')) is not bool or
                history.get('attempt')!=attempt or history.get('decision')!=decision or
                history['walker_to_state_before']!=before_attempt or
                history['walker_to_state_after']!=after or
                history['resolved_state_to_walker']!=inverse or history.get('accepted')!=accepted):
                raise IdentityError('multistate attempt history disagrees with durable phases')
            attempt_rows.append(history); current=after
        if current!=record['walker_to_state_final']:
            raise IdentityError('multistate final permutation does not reconstruct from decisions')
        _validate_rng_document(read_json(path/'rng.json'))
        previous_reports=_validate_final_reports(path/'final-state-reports.json',metadata,sample_rows,
                                                 expected_permutation=current)
        for w in range(n):
            if not (path/'samples'/f'worker-{w:03d}-state.xml').is_file() or not (path/'samples'/f'worker-{w:03d}.chk').is_file():
                raise IdentityError('multistate sample State/checkpoint is missing')
            if not (path/'workers'/f'worker-{w:03d}-state.xml').is_file() or not (path/'workers'/f'worker-{w:03d}.chk').is_file():
                raise IdentityError('multistate final State/checkpoint is missing')
        if set(manifest['files'])!=expected_files:
            raise IdentityError('multistate recursive boundary artifact layout mismatch')
        record['samples']=sample_rows
        record['attempts']=attempt_rows
        rows.append(record)
        before=current; previous=sha(path/'manifest.json')
    return rows


def seal_tree(directory, *, index):
    """Hash and fsync every nested artifact in one multistate transaction."""
    directory=Path(directory)
    files={}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise IdentityError('multistate transaction cannot contain symbolic links')
        if path.is_file() and path!=directory/'manifest.json':
            files[path.relative_to(directory).as_posix()]=sha(path)
    write_json(directory/'manifest.json',{'version':1,'index':index,'files':files})
    for path in sorted((p for p in directory.rglob('*') if p.is_file())):
        with path.open('rb') as handle: os.fsync(handle.fileno())
    for path in sorted((p for p in directory.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):
        sync_directory(path)
    sync_directory(directory)
    return sha(directory/'manifest.json')


def verify_tree(directory, *, index):
    directory=Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise IdentityError('multistate transaction directory identity mismatch')
    manifest=read_json(directory/'manifest.json')
    actual={}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise IdentityError('multistate transaction contains a symbolic link')
        if path.is_file() and path!=directory/'manifest.json':
            actual[path.relative_to(directory).as_posix()]=path
    if (manifest.get('version')!=1 or manifest.get('index')!=index or
        set(manifest.get('files',{}))!=set(actual)):
        raise IdentityError('multistate recursive artifact inventory mismatch')
    expected_dirs=set()
    for name in actual:
        parent=Path(name).parent
        while str(parent)!='.':
            expected_dirs.add(parent.as_posix())
            parent=parent.parent
    actual_dirs={p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_dir()}
    if actual_dirs!=expected_dirs:
        raise IdentityError('multistate recursive directory inventory mismatch')
    for name,digest in manifest['files'].items():
        path=actual[name]
        if sha(path)!=digest:
            raise IdentityError(f'multistate artifact hash mismatch: {name}')
    return manifest


def _verify_multistate_source(directory,metadata):
    worker=Path(directory)/'worker'
    manifest_path=worker/'manifest.json'
    if sha(manifest_path)!=metadata.get('worker_manifest_sha256'):
        raise IdentityError('multistate worker manifest hash mismatch')
    manifest=read_json(manifest_path)
    from .runtime_validation import verify_source_inventory
    verify_source_inventory(worker,manifest.get('files'),
                            current_source_root=Path(__file__).resolve().parent)


def _validate_multistate_metadata(metadata):
    if not isinstance(metadata,dict):
        raise IdentityError('multistate metadata must be an object')
    states=metadata.get('state_ids'); pairs=metadata.get('state_pairs'); walkers=metadata.get('walker_ids')
    if (type(metadata.get('version')) is not int or metadata['version']!=1 or
        type(metadata.get('boundaries')) is not int or not 1<=metadata['boundaries']<=500000 or
        type(metadata.get('steps_per_boundary')) is not int or not 0<metadata['steps_per_boundary']<1000000 or
        type(metadata.get('host_rng_seed')) is not int or not 0<metadata['host_rng_seed']<2**31-10000 or
        not isinstance(metadata.get('run_id'),str) or not metadata['run_id']):
        raise IdentityError('multistate metadata limits or identity are malformed')
    if (not isinstance(states,list) or not 3<=len(states)<=8 or
        any(not isinstance(s,str) or not s.strip() for s in states) or len(set(states))!=len(states)):
        raise IdentityError('multistate metadata state IDs are malformed')
    if (not isinstance(walkers,list) or len(walkers)!=len(states) or
        any(not isinstance(w,str) or not w for w in walkers) or len(set(walkers))!=len(walkers)):
        raise IdentityError('multistate metadata walker IDs are malformed')
    if (type(metadata.get('integrator_seed_base')) is not int or
        not 0<metadata['integrator_seed_base'] or
        metadata['integrator_seed_base']+len(states)-1>=2**31):
        raise IdentityError('multistate worker seed range is invalid for the complete schedule')
    if (not isinstance(pairs,list) or not pairs or len(pairs)>28 or
        any(not isinstance(p,list) or len(p)!=2 or any(type(i) is not int for i in p) for p in pairs)):
        raise IdentityError('multistate metadata pair sweep is malformed')
    edges=[]; reached={0}
    for left,right in pairs:
        if left==right or not (0<=left<len(states) and 0<=right<len(states)):
            raise IdentityError('multistate metadata pair index is invalid')
        edge=frozenset((left,right))
        if edge in edges: raise IdentityError('multistate metadata repeats an undirected edge')
        edges.append(edge)
    changed=True
    while changed:
        n=len(reached)
        for left,right in pairs:
            if left in reached: reached.add(right)
            if right in reached: reached.add(left)
        changed=n!=len(reached)
    if len(reached)!=len(states):
        raise IdentityError('multistate metadata pair graph is disconnected')
    parameters=metadata.get('state_parameters')
    if not isinstance(parameters,dict) or set(parameters)!=set(states):
        raise IdentityError('multistate schedule parameter identity is incomplete')
    if metadata.get('temperature_K')!=300. or metadata.get('beta_mol_per_kJ')!=1/(.00831446261815324*300.):
        raise IdentityError('multistate temperature/beta identity mismatch')
    real_ids=metadata.get('real_atom_ids')
    if (not isinstance(real_ids,list) or not real_ids or
        any(not isinstance(atom_id,str) for atom_id in real_ids) or len(set(real_ids))!=len(real_ids)):
        raise IdentityError('multistate real atom identity is malformed')
    if (not isinstance(metadata.get('profile'),dict) or
        not isinstance(metadata.get('runtime_identity'),str) or
        not isinstance(metadata.get('worker_manifest_sha256'),str)):
        raise IdentityError('multistate runtime identity is malformed')


def _validate_multistate_worker_contract(directory,metadata):
    """Bind inert journal declarations to the sealed dependency-light worker records."""
    from .schema import AlchemicalBundle,RuntimeSpec,from_json
    worker=Path(directory)/'worker'
    manifest=read_json(worker/'manifest.json')
    bundle=from_json((worker/'bundle.json').read_text())
    runtime=from_json((worker/'runtime.json').read_text())
    if not isinstance(bundle,AlchemicalBundle) or not isinstance(runtime,RuntimeSpec):
        raise IdentityError('multistate worker bundle/runtime record type mismatch')
    if (manifest.get('physical_identity')!=metadata.get('physical_identity') or
        manifest.get('alchemical_identity')!=metadata.get('alchemical_identity') or
        manifest.get('runtime_identity')!=metadata.get('runtime_identity') or
        bundle.physical.content_identity!=metadata.get('physical_identity') or
        bundle.content_identity!=metadata.get('alchemical_identity') or
        bundle.transfer.content_identity!=metadata.get('transfer_identity') or
        bundle.restraints.content_identity!=metadata.get('restraints_identity') or
        bundle.schedule.content_identity!=metadata.get('schedule_identity') or
        runtime.content_identity!=metadata.get('runtime_identity')):
        raise IdentityError('multistate runtime or sealed worker identity mismatch')
    if (runtime.platform!='Reference' or runtime.precision!='double' or
        runtime.temperature_K!=300. or runtime.ensemble!='NVT' or
        runtime.integrator!='LangevinMiddle' or runtime.device_allocation or
        runtime.timestep_ps<=0 or runtime.timestep_ps>.0005 or
        bundle.schedule.temperature_K!=300.):
        raise IdentityError('multistate sealed runtime must be 300 K Reference double NVT LangevinMiddle')
    schedule={state.state_id:dict(state.parameters) for state in bundle.schedule.states}
    states=metadata['state_ids']
    expected_parameters={state:schedule[state] for state in states if state in schedule}
    if (set(expected_parameters)!=set(states) or metadata.get('state_parameters')!=expected_parameters):
        raise IdentityError('multistate metadata schedule membership/parameters differ from the sealed worker')
    atom_ids=[atom.atom_id for atom in bundle.physical.topology.atoms]
    if metadata.get('real_atom_ids')!=atom_ids:
        raise IdentityError('multistate real atom identity differs from the sealed worker')
    settings=metadata.get('settings')
    if (not isinstance(settings,dict) or settings.get('protocol_kind')!=bundle.transfer.protocol.kind or
        tuple(settings.get('displacement_nm',()))!=tuple(bundle.transfer.protocol.geometry_requests.get('displacement_nm',()))):
        raise IdentityError('multistate geometry settings differ from the sealed transfer maps')
    return runtime.timestep_ps


def _validate_permutation(value,n,name):
    if (not isinstance(value,list) or len(value)!=n or any(type(i) is not int for i in value) or
        sorted(value)!=list(range(n))):
        raise IdentityError(f'multistate {name} is not a complete permutation')


def _validate_exact_int_list(value,expected,name):
    if (not isinstance(value,list) or len(value)!=len(expected) or
        any(type(item) is not int for item in value) or value!=expected):
        raise IdentityError(f'multistate {name} are malformed or inconsistent')


def _validate_inverse(path,permutation,n):
    document=read_json(path)
    inverse=[permutation.index(i) for i in range(n)]
    if not isinstance(document,dict):
        raise IdentityError('multistate full permutation/inverse document is malformed')
    _validate_permutation(document.get('walker_to_state'),n,'inverse document permutation')
    _validate_permutation(document.get('state_to_walker'),n,'inverse document inverse')
    if document['walker_to_state']!=permutation or document['state_to_walker']!=inverse:
        raise IdentityError('multistate full permutation and inverse disagree')


def _tuple_tree(value):
    return tuple(_tuple_tree(item) for item in value) if isinstance(value,list) else value


def _validate_rng_document(document):
    try:
        if not isinstance(document,dict):
            raise ValueError('RNG document must be an object')
        python=document.get('python')
        if not isinstance(python,(list,tuple)) or len(python)!=3:
            raise ValueError('invalid Python random-state shape')
        version,internal,gaussian=python
        if type(version) is not int or version!=3:
            raise ValueError('invalid Python random-state version')
        if (not isinstance(internal,(list,tuple)) or len(internal)!=625 or
            any(type(value) is not int or not 0<=value<2**32 for value in internal[:-1]) or
            type(internal[-1]) is not int or not 0<=internal[-1]<=624):
            raise ValueError('invalid Python random-state internal vector or index')
        if gaussian is not None and not _finite(gaussian):
            raise ValueError('invalid Python Gaussian cache')
        random.Random().setstate(_tuple_tree(python))
        numpy=document['numpy']
        if (not isinstance(numpy,list) or len(numpy)!=5 or numpy[0]!='MT19937' or
            not isinstance(numpy[1],list) or len(numpy[1])!=624 or
            any(type(v) is not int or not 0<=v<2**32 for v in numpy[1]) or
            type(numpy[2]) is not int or not 0<=numpy[2]<=624 or
            type(numpy[3]) is not int or numpy[3] not in (0,1) or
            isinstance(numpy[4],bool) or not isinstance(numpy[4],(float,int)) or not math.isfinite(numpy[4])):
            raise ValueError('invalid NumPy legacy RNG state')
    except Exception as error:
        raise IdentityError(f'multistate host RNG document is malformed: {error}') from error


def _same_parameters(actual,expected):
    return isinstance(actual,dict) and isinstance(expected,dict) and actual==expected


def _finite(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)


def _clock_matches(actual_step,actual_time,expected_step,expected_time):
    return actual_step==expected_step and actual_time==expected_time


def _validate_expected_clock(step,time_ps,origin,expected_steps,timestep_ps):
    expected_step=origin['step']+expected_steps
    if step!=expected_step:
        raise IdentityError('multistate sample clock disagrees with declared step/time increments')
    origin_time=origin['time_ps']
    if not all(_finite(value) for value in (time_ps,origin_time,timestep_ps)):
        raise IdentityError('multistate sample clock contains a nonfinite value')
    if time_ps<origin_time:
        raise IdentityError('multistate sample clock moves backward')
    try:
        observed_delta=time_ps-origin_time
        expected_delta=expected_steps*timestep_ps
        timestep_scale=expected_steps*abs(timestep_ps)
    except (OverflowError,ValueError):
        raise IdentityError('multistate sample clock arithmetic is nonfinite') from None
    if not all(_finite(value) for value in (observed_delta,expected_delta,timestep_scale)):
        raise IdentityError('multistate sample clock arithmetic is nonfinite')
    unit_roundoff=sys.float_info.epsilon/2
    accumulated_roundoff=expected_steps*unit_roundoff
    if accumulated_roundoff>=1:
        raise IdentityError('multistate declared time increment exceeds the floating-point comparison bound')
    gamma_n=math.nextafter(accumulated_roundoff/(1-accumulated_roundoff),math.inf)
    single_operation_bound=math.nextafter(unit_roundoff/(1-unit_roundoff),math.inf)
    # Weight each nonnegative magnitude before summing. Summing raw clocks can
    # overflow even when the justified gamma_n envelope is finite. nextafter
    # rounds each positive product and the final sum outward, keeping this a
    # computed upper bound despite binary64 rounding.
    terms=tuple(math.nextafter(value,math.inf) for value in (
        gamma_n*abs(origin_time),gamma_n*timestep_scale,
        single_operation_bound*timestep_scale,single_operation_bound*abs(time_ps),
        single_operation_bound*abs(origin_time),single_operation_bound*abs(expected_delta),
        single_operation_bound*abs(observed_delta)))
    if not all(_finite(value) for value in terms):
        raise IdentityError('multistate sample clock roundoff bound is nonfinite')
    try:
        bound=math.nextafter(math.fsum(terms),math.inf)
        residual=observed_delta-expected_delta
        residual_magnitude=math.nextafter(abs(residual),math.inf)
    except (OverflowError,ValueError):
        raise IdentityError('multistate sample clock comparison is nonfinite') from None
    if not _finite(bound) or not _finite(residual) or not _finite(residual_magnitude):
        raise IdentityError('multistate sample clock comparison is nonfinite')
    if residual_magnitude>bound:
        raise IdentityError('multistate sample clock disagrees with declared step/time increments')


def _validate_raw(raw):
    required=('u0_raw_kJ_mol','u1_raw_kJ_mol','delta_u_raw_kJ_mol','delta_u_softcore_kJ_mol',
              'atm_expression_energy_kJ_mol','outside_energy_kJ_mol','system_total_energy_kJ_mol')
    if not isinstance(raw,dict) or any(name not in raw or not _finite(raw[name]) for name in required):
        raise IdentityError('multistate raw-energy record is incomplete or nonfinite')
    if (abs(raw['delta_u_raw_kJ_mol']-(raw['u1_raw_kJ_mol']-raw['u0_raw_kJ_mol']))>1e-8 or
        abs(raw['system_total_energy_kJ_mol']-(raw['atm_expression_energy_kJ_mol']+raw['outside_energy_kJ_mol']))>1e-8):
        raise IdentityError('multistate raw-to-total energy arithmetic mismatch')


def _validate_sample(sample,metadata):
    atoms=metadata['real_atom_ids']; count=len(atoms)
    if not isinstance(sample,dict):
        raise IdentityError('multistate sample must be an object')
    if sample.get('real_atom_ids')!=atoms or sample.get('temperature_K')!=300.:
        raise IdentityError('multistate sample atom/temperature identity mismatch')
    if (sample.get('physical_identity')!=metadata.get('physical_identity') or
        sample.get('transfer_identity')!=metadata.get('transfer_identity')):
        raise IdentityError('multistate sample physical/transfer identity differs from sealed records')
    if (type(sample.get('integrator_seed')) is not int or
        sample['integrator_seed']!=metadata['integrator_seed_base']+sample['walker_index']):
        raise IdentityError('multistate sample integrator-seed identity is malformed')
    for name in ('positions_nm','velocities_nm_ps','real_forces_kj_mol_nm'):
        rows=sample.get(name)
        if not isinstance(rows,list) or len(rows)!=count or any(not isinstance(row,list) or len(row)!=3 or any(not _finite(v) for v in row) for row in rows):
            raise IdentityError(f'multistate sample {name} shape/value mismatch')
    if sample.get('box_nm') is not None:
        box=sample['box_nm']
        if not isinstance(box,list) or len(box)!=3 or any(not isinstance(row,list) or len(row)!=3 or any(not _finite(v) for v in row) for row in box):
            raise IdentityError('multistate sample box shape/value mismatch')
    state=sample.get('state_id')
    if not _same_parameters(sample.get('parameters'),metadata['state_parameters'].get(state)):
        raise IdentityError('multistate sample parameter/state mismatch')
    _validate_raw(sample.get('raw'))
    if not _finite(sample.get('time_ps')) or type(sample.get('step')) is not int or sample['step']<0:
        raise IdentityError('multistate sample time/step is malformed')
    if not _finite(sample.get('total_energy_kJ_mol')) or sample['total_energy_kJ_mol']!=sample['raw']['system_total_energy_kJ_mol']:
        raise IdentityError('multistate sample total does not match raw total')


def _validate_pair_evaluations(evaluated,state_ids,walker_ids,metadata):
    if evaluated.get('state_ids_before')!=state_ids or evaluated.get('walker_ids')!=walker_ids:
        raise IdentityError('multistate evaluated pair identity mismatch')
    matrix=evaluated.get('reduced_energies'); raw=evaluated.get('raw_energies')
    if (not isinstance(matrix,list) or len(matrix)!=2 or any(not isinstance(row,list) or len(row)!=2 for row in matrix) or
        not isinstance(raw,list) or len(raw)!=2 or any(not isinstance(row,list) or len(row)!=2 for row in raw)):
        raise IdentityError('multistate pair energy matrix must be complete 2-by-2')
    for i in range(2):
        for j in range(2):
            _validate_raw(raw[i][j])
            expected=raw[i][j]['system_total_energy_kJ_mol']*metadata['beta_mol_per_kJ']
            if not _finite(matrix[i][j]) or abs(matrix[i][j]-expected)>1e-10:
                raise IdentityError('multistate reduced-energy matrix disagrees with full total')
    if not _finite(evaluated.get('exponent')):
        raise IdentityError('multistate pair exponent is nonfinite')
    delta=matrix[0][1]+matrix[1][0]-matrix[0][0]-matrix[1][1]
    if abs(delta-evaluated['exponent'])>1e-10:
        raise IdentityError('multistate pair exponent arithmetic mismatch')


def _validate_refreshed(report,selected,permutation,metadata,evaluated):
    energies=report.get('energies_after_kj_mol')
    if not isinstance(energies,list) or len(energies)!=2 or any(not _finite(v) for v in energies):
        raise IdentityError('multistate refreshed energy report is incomplete')
    states=[metadata['state_ids'][permutation[w]] for w in selected]
    if report.get('state_ids_after')!=states:
        raise IdentityError('multistate refreshed parameters do not match final pair states')
    evaluated_states=evaluated.get('state_ids_before')
    raw=evaluated.get('raw_energies')
    if (not isinstance(evaluated_states,list) or not isinstance(raw,list) or len(raw)!=2 or
        any(not isinstance(row,list) or len(row)!=2 for row in raw)):
        raise IdentityError('multistate refreshed report has no complete evaluated energy matrix')
    for column,worker_index in enumerate(selected):
        state_id=metadata['state_ids'][permutation[worker_index]]
        try:
            row=evaluated_states.index(state_id)
        except ValueError as error:
            raise IdentityError('multistate refreshed state is absent from its evaluated matrix') from error
        expected=raw[row][column]['system_total_energy_kJ_mol']
        if abs(energies[column]-expected)>1e-8:
            raise IdentityError('multistate refreshed total disagrees with its evaluated raw-energy matrix')


def _coordinate_digest(positions):
    import json
    text=json.dumps(positions,separators=(',',':'),allow_nan=False)
    return hashlib.sha256(text.encode()).hexdigest()


def _validate_final_reports(path,metadata,samples,expected_permutation=None):
    report=read_json(path)
    rows=report.get('workers')
    n=len(metadata['state_ids'])
    if not isinstance(rows,list) or len(rows)!=n:
        raise IdentityError('multistate final-state reports do not cover every worker')
    for w,row in enumerate(rows):
        if (not isinstance(row,dict) or type(row.get('walker_index')) is not int or
            row.get('walker_index')!=w or row.get('walker_id')!=metadata['walker_ids'][w]):
            raise IdentityError('multistate final-state report worker identity mismatch')
        if (type(row.get('step')) is not int or row['step']<0 or not _finite(row.get('time_ps'))):
            raise IdentityError('multistate final-state report clock is malformed')
        state=row.get('state_id')
        if state not in metadata['state_parameters'] or not _same_parameters(row.get('parameters'),metadata['state_parameters'][state]):
            raise IdentityError('multistate final-state report parameter identity mismatch')
        if expected_permutation is not None and state!=metadata['state_ids'][expected_permutation[w]]:
            raise IdentityError('multistate final-state report disagrees with assignment')
        _validate_raw(row.get('raw'))
        total=row.get('total')
        if not isinstance(total,dict) or total.get('energy_kj_mol')!=row['raw']['system_total_energy_kJ_mol']:
            raise IdentityError('multistate final-state total/raw mismatch')
        if (total.get('real_atom_ids')!=metadata['real_atom_ids'] or
            total.get('physical_identity')!=metadata.get('physical_identity') or
            total.get('units')!={'positions':'nm','energy':'kJ/mol','forces':'kJ/mol/nm',
                                  'time':'ps','temperature':'K'} or
            not isinstance(total.get('diagnostics'),dict)):
            raise IdentityError('multistate final-state total identity/units mismatch')
        forces=total.get('forces_kj_mol_nm')
        if not isinstance(forces,list) or len(forces)!=len(metadata['real_atom_ids']) or any(not isinstance(a,list) or len(a)!=3 or any(not _finite(v) for v in a) for a in forces):
            raise IdentityError('multistate final-state full force report is malformed')
        if not isinstance(row.get('coordinate_sha256'),str) or not re.fullmatch(r'[0-9a-f]{64}',row['coordinate_sha256']):
            raise IdentityError('multistate final-state coordinate identity is malformed')
        if samples is not None:
            if row['coordinate_sha256']!=_coordinate_digest(samples[w]['positions_nm']):
                raise IdentityError('multistate final-state report coordinates disagree with sample')
            if row['step']!=samples[w]['step'] or row['time_ps']!=samples[w]['time_ps']:
                raise IdentityError('multistate final-state report clock disagrees with captured sample')
    return rows


def preserve_pending(directory):
    """Explicit rollback: retain whole incomplete trees and their inert hashes."""
    directory=Path(directory)
    for pending in sorted((directory/'rounds').glob('.pending-*')):
        target=directory/'failures'/f'rollback-{uuid.uuid4().hex}'
        target.parent.mkdir(exist_ok=True)
        files={str(p.relative_to(pending)):sha(p) for p in pending.rglob('*') if p.is_file()}
        write_json(pending/'rollback.json',{'policy':'replay from last committed checkpoints and both host RNG streams',
            'original_pending_name':pending.name,'preserved_file_hashes':files})
        os.rename(pending,target)
        sync_directory(target.parent); sync_directory(directory/'rounds')


def preserve_multistate_pending(directory):
    """Archive every byte of an incomplete boundary before deterministic replay."""
    directory=Path(directory); pending=directory/'pending'
    if not pending.exists():
        return None
    if pending.is_symlink() or not pending.is_dir():
        raise IdentityError('multistate pending tree identity mismatch')
    target=directory/'failures'/f'rollback-{uuid.uuid4().hex}'
    target.parent.mkdir(exist_ok=True)
    files={}
    for path in sorted(pending.rglob('*')):
        if path.is_symlink():
            raise IdentityError('multistate pending tree contains a symbolic link')
        if path.is_file():
            files[path.relative_to(pending).as_posix()]=sha(path)
    write_json(pending/'rollback.json',{'policy':'archive all evidence; replay from previous all-worker checkpoints/permutation/host RNG',
        'original_pending_name':pending.name,'preserved_file_hashes':files})
    for path in sorted(p for p in pending.rglob('*') if p.is_file()):
        with path.open('rb') as handle: os.fsync(handle.fileno())
    for path in sorted((p for p in pending.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):
        sync_directory(path)
    sync_directory(pending)
    os.rename(pending,target)
    _sync_rename_parents(directory,target.parent)
    return target
