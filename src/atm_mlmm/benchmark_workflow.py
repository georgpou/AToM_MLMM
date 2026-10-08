"""Hash-bound benchmark jobs; molecular dependencies are loaded only to execute."""
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re

MODES = ('mm', 'ligand', 'cavity')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _input_path(base, relative):
    relative = PurePosixPath(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError(f'unsafe benchmark input path: {relative}')
    path = base
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f'benchmark input contains a symbolic link: {relative}')
    path = path.resolve()
    if not path.is_relative_to(base) or not path.is_file():
        raise ValueError(f'benchmark input is absent or escapes its directory: {relative}')
    return path


def load_benchmark(path):
    path = Path(path).resolve()
    data = json.loads(path.read_text())
    if data.get('schema') != 'atom-protein-benchmark-v1':
        raise ValueError('unsupported benchmark schema')
    if not re.fullmatch(r'[a-z0-9]+', data['target_id']):
        raise ValueError('target identifier must be lowercase and alphanumeric')
    displacement = data['displacement_nm']
    if (len(displacement) != 3 or any(isinstance(v, bool) or not isinstance(v, (int, float))
                                   or not math.isfinite(v) for v in displacement)
            or sum(v*v for v in displacement) == 0):
        raise ValueError('displacement must be a finite nonzero 3-vector in nm')
    cavity = data['cavity']
    if ((cavity['component_charge'], cavity['component_multiplicity']) != (0, 1)
            or cavity['cut'] != ['CB', 'CA'] or not cavity['residues']
            or len(set(cavity['residues'])) != len(cavity['residues'])):
        raise ValueError('cavity requires distinct neutral singlet side chains and CB-CA cuts')
    source = data['source']
    if (source['commit'], source['distribution_version']) != (
            '9e26c5a3811038be1c98e3be6af4c78cd0dd57a7', '8.5.0b0'):
        raise ValueError('benchmark requires the pinned AToM source')
    for relative, expected in data['files'].items():
        if sha256(_input_path(path.parent, relative)) != expected:
            raise ValueError(f'benchmark SHA-256 mismatch: {relative}')
    required = {data['receptor'], 'atom.json', 'atom-source-sha256.json', 'UPSTREAM-LICENSE'}
    seen = set()
    for ligand in data['ligands']:
        if ligand['id'] in seen or not ligand['id'].isalnum():
            raise ValueError('ligand identifiers must be unique and alphanumeric')
        seen.add(ligand['id'])
        if (ligand['formal_charge'], ligand['multiplicity']) != (0, 1):
            raise ValueError('only explicit neutral singlet ligands are supported')
        required.add(ligand['path'])
        lines = _input_path(path.parent, ligand['path']).read_text().splitlines()
        count = int(lines[3][:3])
        if count != ligand['atom_count'] or count <= 0:
            raise ValueError('complete ligand atom count differs from its declaration')
        charge_codes = {0: 0, 1: 3, 2: 2, 3: 1, 5: -1, 6: -2, 7: -3}
        charges = []
        for row in lines[4:4+count]:
            if row[31:34].strip() not in {'H', 'C', 'N', 'O'}:
                raise ValueError('ligand elements exceed the admitted model domain')
            code = int(row[36:39])
            if code not in charge_codes:
                raise ValueError('radical/ambiguous ligand state is unsupported')
            charges.append(charge_codes[code])
        for row in lines:
            if row.startswith('M  RAD'):
                raise ValueError('radical ligand state is unsupported')
            if row.startswith('M  CHG'):
                fields = row.split()
                for i in range(int(fields[2])):
                    charges[int(fields[3+2*i])-1] = int(fields[4+2*i])
        if sum(charges) != 0:
            raise ValueError('SDF charge differs from the declared neutral ligand')
    if not seen or not required <= data['files'].keys():
        raise ValueError('every benchmark input must have a SHA-256 identity')
    return data


def plan_jobs(manifest, output, *, mode='cavity'):
    if mode not in MODES:
        raise ValueError(f'unsupported benchmark mode: {mode}')
    data = load_benchmark(manifest)
    output = Path(output).resolve()
    if output.is_relative_to(Path(manifest).resolve().parent):
        raise ValueError('run outputs must be separate from benchmark inputs')
    return [dict(ligand_id=ligand['id'], mode=mode,
                 basename=f"{data['target_id']}-{ligand['id']}-{mode}",
                 directory=str(output / f"{data['target_id']}-{ligand['id']}-{mode}"))
            for ligand in data['ligands']]


def _source_hashes():
    source = Path(__file__).parent
    return {str(p.relative_to(source)): sha256(p) for p in sorted(source.rglob('*.py'))}


def _write(path, data):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as handle:
        handle.write(json.dumps(data, indent=2, allow_nan=False) + '\n')
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)
    descriptor = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextmanager
def _job_lock(directory):
    import fcntl
    with (directory / '.workflow.lock').open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('another process is using this benchmark job') from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def _verify_job(directory, manifest, job):
    receipt = directory / 'setup.json'
    if not receipt.is_file():
        raise ValueError('verified setup is required before preparation or production')
    saved = json.loads(receipt.read_text())
    if saved['benchmark_sha256'] != sha256(manifest) or saved['job'] != job:
        raise ValueError('benchmark identity or job definition differs from setup')
    if saved['source_files'] != _source_hashes():
        raise ValueError('runtime source differs from the setup snapshot; make a new job')
    for relative, expected in saved['files'].items():
        if sha256(_input_path(directory, relative)) != expected:
            raise ValueError(f'job SHA-256 mismatch: {relative}')
    return saved


def run_stage(manifest, output, ligand_id, mode, stage, *, smoke=False, nodefile=None,
              platform='CPU'):
    """Execute one explicit stage; never launch MD from planning or setup."""
    if stage not in ('setup', 'prepare', 'run'):
        raise ValueError('stage must be setup, prepare, or run')
    if platform not in ('CPU', 'Reference'):
        raise ValueError('this model profile currently supports CPU or Reference only')
    manifest = Path(manifest).resolve()
    data = load_benchmark(manifest)
    matches = [j for j in plan_jobs(manifest, output, mode=mode)
               if j['ligand_id'] == ligand_id]
    if len(matches) != 1:
        raise ValueError(f'unknown benchmark ligand: {ligand_id}')
    job = matches[0]
    directory = Path(job['directory'])
    if stage == 'setup':
        # Import before making a directory: a missing backend is not a failed run.
        from .adapters.atom import setup_benchmark_job
        directory.mkdir(parents=True, exist_ok=False)
    elif not directory.is_dir():
        raise ValueError('verified setup is required before preparation or production')
    with _job_lock(directory):
        attempted = False
        try:
            if stage == 'setup':
                attempted = True
                setup_benchmark_job(manifest, directory, job, smoke=smoke, platform=platform)
                saved = dict(schema='atom-benchmark-setup-v1', job=job,
                             benchmark_sha256=sha256(manifest), source_files=_source_hashes(),
                             files={str(p.relative_to(directory)): sha256(p)
                                    for p in sorted(directory.rglob('*'))
                                    if p.is_file() and p.name != '.workflow.lock'})
                _write(directory / 'setup.json', saved)
                return saved
            _verify_job(directory, manifest, job)
            if stage == 'prepare':
                state = directory / (job['basename'] + '_0.xml')
                if (state.exists() or (directory / 'failure-prepare.json').exists()
                        or (directory / 'preparation-attempt.json').exists()):
                    raise ValueError('preparation already exists or failed; use a fresh setup')
                from .adapters.atom import prepare_benchmark_job
                _write(directory / 'preparation-attempt.json', dict(
                    status='started', setup_sha256=sha256(directory / 'setup.json')))
                attempted = True
                prepare_benchmark_job(directory)
                receipt = dict(schema='atom-benchmark-preparation-v1',
                               setup_sha256=sha256(directory / 'setup.json'),
                               state_file=state.name, state_sha256=sha256(state),
                               ensemble='NVT', physical_acceptance=False)
                _write(directory / 'preparation.json', receipt)
                return receipt
            receipt_path = directory / 'preparation.json'
            if not receipt_path.exists():
                raise ValueError('verified preparation is required before production')
            receipt = json.loads(receipt_path.read_text())
            if (receipt['setup_sha256'] != sha256(directory / 'setup.json') or
                    receipt['state_sha256'] != sha256(directory / receipt['state_file'])):
                raise ValueError('preparation SHA-256 mismatch')
            if nodefile is None or not Path(nodefile).is_file():
                raise ValueError('production requires an explicit local AToM nodefile')
            if (directory / 'production.json').exists() or (directory / 'failure-run.json').exists():
                raise ValueError('a production attempt already exists; retain it and use a new job')
            from .adapters.atom import produce_benchmark_job, validate_benchmark_nodefile
            validate_benchmark_nodefile(nodefile)
            attempted = True
            _write(directory / 'production.json', dict(status='started',
                   preparation_sha256=sha256(receipt_path), nodefile_sha256=sha256(nodefile),
                   binding_result='not_evaluated'))
            produce_benchmark_job(directory, Path(nodefile).resolve())
            result = dict(status='returned', preparation_sha256=sha256(receipt_path),
                          nodefile_sha256=sha256(nodefile), binding_result='not_evaluated')
            _write(directory / 'production.json', result)
            return result
        except BaseException as exc:
            # Retain upstream outputs and the first failure; never relabel it a pass.
            failure = directory / f'failure-{stage}.json'
            if attempted and not failure.exists():
                _write(failure, dict(stage=stage, error_type=type(exc).__name__, message=str(exc)))
            raise
