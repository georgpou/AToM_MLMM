"""Independent audit of frozen bytes, matrix, ledgers and saved arithmetic.

This script launches no model, MM context, preparation or quantum calculation.
It never writes submitted evidence. Run from the reviewed repository root.
"""
import collections
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess

import numpy as np
import openmm as mm
from openmm import unit
from atm_mlmm.schema import from_json

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
BASE = '08ccee74d0da900ffb1bd98d076e6e87e9df1b0c'
HEAD = 'ad994d68333a7dabffd4cbcc68dfc9a4a2114b0b'
CONVERSION = 10 * 1.6021766208e-19 * 6.022140857e23 / 1000


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def value(p):
    if unit.is_quantity(p):
        return p.value_in_unit_system(unit.md_unit_system)
    return p


def term_rows(force):
    options = {mm.HarmonicBondForce: ('getNumBonds', 'getBondParameters', 2),
               mm.HarmonicAngleForce: ('getNumAngles', 'getAngleParameters', 3),
               mm.PeriodicTorsionForce: ('getNumTorsions', 'getTorsionParameters', 4),
               mm.RBTorsionForce: ('getNumTorsions', 'getTorsionParameters', 4)}
    count, getter, arity = options[type(force)]
    return [tuple(value(x) for x in getattr(force, getter)(i))
            for i in range(getattr(force, count)())], arity


def ledger_check(bundle):
    """Account for every original and retained term via public APIs only.

    No production inventory, ledger diff or upstream boundary predicate is used.
    """
    original = mm.XmlSerializer.deserialize(bundle.manifest['original_mm_xml'])
    retained = mm.XmlSerializer.deserialize(bundle.manifest['retained_mm_xml'])
    ids = tuple(a.atom_id for a in bundle.topology.atoms)
    old_to_new = dict(enumerate(bundle.old_to_new))
    final_to_id = {v: ids[k] for k, v in old_to_new.items()}
    rows = bundle.manifest['boundary_terms']
    counts = collections.Counter()
    for fidx, (source, target) in enumerate(zip(original.getForces(), retained.getForces())):
        assert type(source) == type(target)
        entries = [r for r in rows if r['force_index'] == fidx]
        if not isinstance(source, mm.NonbondedForce):
            before, arity = term_rows(source)
            after, _ = term_rows(target)
            after = collections.Counter(tuple(final_to_id[int(x)] for x in t[:arity]) + t[arity:]
                                        for t in after)
            assert len(entries) == len(before)
            for index, params in enumerate(before):
                atoms = tuple(ids[int(x)] for x in params[:arity])
                row = next(r for r in entries if r['original_index'] == index)
                assert tuple(row['atom_ids']) == atoms
                assert tuple(row['original_parameters']) == params[arity:]
                key = atoms + params[arity:]
                present = after[key] > 0
                assert row['disposition'] == ('retained' if present else 'removed')
                assert tuple(row['retained_parameters']) == (params[arity:] if present else ())
                if present:
                    after[key] -= 1
            assert not +after
        else:
            before_particles = [tuple(value(x) for x in source.getParticleParameters(i))
                                for i in range(source.getNumParticles())]
            assert target.getNumParticles() == len(ids) + len(bundle.links)
            particle_rows = [r for r in entries if r['kind'] == 'nonbonded_particle']
            assert len(particle_rows) == target.getNumParticles()
            for i, parameters in enumerate(before_particles):
                row = next(r for r in particle_rows if r['original_index'] == i)
                actual = tuple(value(x) for x in target.getParticleParameters(old_to_new[i]))
                assert parameters == actual == tuple(row['original_parameters']) == tuple(row['retained_parameters'])
                assert tuple(row['atom_ids']) == (ids[i],) and row['disposition'] == 'retained'
            for i in set(range(target.getNumParticles())) - set(old_to_new.values()):
                q, _, eps = target.getParticleParameters(i)
                assert value(q) == value(eps) == 0
            ex_rows = [r for r in entries if r['kind'] == 'exception']
            after = {}
            for i in range(target.getNumExceptions()):
                a, b, *parameters = target.getExceptionParameters(i)
                assert a in final_to_id and b in final_to_id
                key = frozenset((final_to_id[a], final_to_id[b]))
                assert key not in after
                after[key] = tuple(value(x) for x in parameters)
            assert len(ex_rows) == len(after)
            seen = set()
            for i in range(source.getNumExceptions()):
                a, b, *parameters = source.getExceptionParameters(i)
                parameters = tuple(value(x) for x in parameters)
                pair = frozenset((ids[a], ids[b])); seen.add(pair)
                row = next(r for r in ex_rows if r['original_index'] == i)
                assert frozenset(row['atom_ids']) == pair
                assert tuple(row['original_parameters']) == parameters
                assert tuple(row['retained_parameters']) == after[pair]
                assert row['disposition'] == ('retained' if parameters == after[pair] else 'replaced_by_exclusion')
                if parameters != after[pair]:
                    assert after[pair][0] == after[pair][2] == 0
            for pair, params in after.items():
                if pair not in seen:
                    row = next(r for r in ex_rows if r['original_index'] is None and frozenset(r['atom_ids']) == pair)
                    assert row['disposition'] == 'added_exclusion'
                    assert params == tuple(row['retained_parameters']) and params[0] == params[2] == 0
            settings = [r for r in entries if r['kind'] == 'nonbonded_settings']
            flag_changed = source.getExceptionsUsePeriodicBoundaryConditions() != target.getExceptionsUsePeriodicBoundaryConditions()
            assert len(settings) == int(flag_changed)
            if flag_changed:
                assert settings[0]['disposition'] == 'changed_periodic_exception_convention'
                assert target.getExceptionsUsePeriodicBoundaryConditions()
        counts.update(r['disposition'] for r in entries)
    source_constraints = {(frozenset((ids[a], ids[b])), value(d))
                          for a, b, d in (original.getConstraintParameters(i) for i in range(original.getNumConstraints()))}
    after_constraints = {(frozenset((final_to_id[a], final_to_id[b])), value(d))
                         for a, b, d in (retained.getConstraintParameters(i) for i in range(retained.getNumConstraints()))}
    assert after_constraints <= source_constraints
    assert len([r for r in rows if r['kind'] == 'constraint']) == original.getNumConstraints()
    return dict(counts)


def main():
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == HEAD
    start = read(HERE/'audit-start.json')
    assert all(sha(ROOT/p) == digest for p, digest in start['tracked_sha256'].items())
    submission = read(ROOT/'Worker_Log/Milestone_03/evidence/G07_v1/snapshot.json')
    hashes = submission['changed_source_and_evidence_files']
    assert all(sha(ROOT/p) == digest for p, digest in hashes.items())
    allowed_changes = {'src/atm_mlmm/adapters/atom.py', 'src/atm_mlmm/atm.py', 'src/atm_mlmm/embeddings/mechanical.py',
                       'src/atm_mlmm/geometry.py', 'src/atm_mlmm/hybrid.py', 'src/atm_mlmm/ledger.py',
                       'src/atm_mlmm/model_reference.py', 'docs/project-0/STATUS.md'}
    base_entries = subprocess.check_output(['git', 'ls-tree', '-rz', BASE]).split(b'\0')
    preserved, changed = [], []
    for entry in filter(None, base_entries):
        metadata, name = entry.decode().split('\t'); mode, kind, oid = metadata.split()
        assert kind == 'blob' and mode != '120000'
        raw = (ROOT/name).read_bytes()
        current = hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()
        if current == oid:
            preserved.append(name)
        else:
            assert name in allowed_changes, name
            changed.append(name)
    verified = []
    for directory in ('fixtures/periodic_ledger', 'fixtures/fragment_ligand/prepared-mm-v1'):
        parent = ROOT/directory
        for name, digest in read(parent/'manifest.json')['files'].items():
            assert name != 'manifest.json' and sha(parent/name) == digest
            verified.append(str(parent/name))
    fixtures = ROOT/'fixtures/fragment_ligand/descriptions-v1'
    manifest = read(fixtures/'manifest.json')
    points = ROOT/'Worker_Log/Milestone_03/evidence/G07_v1/fifty-description-single-points'
    summary = read(points/'summary.json')
    settings = read(ROOT/'fixtures/chemical_reference_v3/reference-settings.json')
    records = {}; ledger_counts = collections.Counter(); errors = []
    for item in manifest['rows']:
        assert sha(fixtures/item['artifact']) == item['artifact_sha256']
        assert sha(points/item['artifact']) == summary['files'][item['artifact']]
        verified.append(str(fixtures/item['artifact']))
        bundle = from_json((fixtures/item['artifact']).read_text())
        assert bundle.content_identity == item['physical_identity']
        ledger_counts.update(ledger_check(bundle))
        ligand, = [m for m in bundle.topology.molecules if m.role == 'ligand']
        ids = item['real_atom_ids']
        selected = [ids.index(a) for a in ligand.atom_ids]
        model_selected = [item['model_input_ids'].index(a) for a in ligand.atom_ids]
        assert all(link.ml_parent_id not in ligand.atom_ids and link.mm_parent_id not in ligand.atom_ids for link in bundle.links)
        record = read(points/item['artifact'])
        total = np.array(record['hybrid_real_forces_kj_mol_nm'])
        reference = np.array(record['independent_hybrid_real_forces_kj_mol_nm'])
        errors.append((abs(record['hybrid_energy_kj_mol']-record['independent_hybrid_energy_kj_mol']), float(np.max(abs(total-reference)))))
        assert np.isfinite(total).all() and np.isfinite(reference).all()
        model = np.array(record['native_raw_model']['forces_kj_mol_nm'])
        records[item['row'], item['description']] = dict(
            total_energy=record['hybrid_energy_kj_mol'], model_energy=record['native_raw_model']['energy_kj_mol'],
            total_net=total[selected].sum(axis=0)/CONVERSION, model_net=model[model_selected].sum(axis=0)/CONVERSION,
            real_ids=ids, positions=item['positions_nm'], complete_ligand_ids=ligand.atom_ids)
    groups = collections.defaultdict(list)
    for row, description in records:
        groups[row].append(description)
    comparisons = []
    for row, descriptions in sorted(groups.items()):
        control = row if row.endswith('-separated') else row.split('-d', 1)[0]+'-separated'
        for left, right in itertools.combinations(descriptions, 2):
            a, b = records[row, left], records[row, right]
            assert (a['real_ids'], a['positions']) == (b['real_ids'], b['positions'])
            ca, cb = records[control, left], records[control, right]
            energy = ((a['total_energy']-ca['total_energy'])-(b['total_energy']-cb['total_energy']))/4.184
            model_energy = ((a['model_energy']-ca['model_energy'])-(b['model_energy']-cb['model_energy']))/4.184
            force = a['total_net']-b['total_net']; model_force = a['model_net']-b['model_net']
            comparisons.append(dict(row=row,left=left,right=right,separated_control=control,
                contact_energy_difference_kcal_mol=energy,
                model_contact_energy_difference_kcal_mol=model_energy,
                retained_mm_contact_energy_difference_kcal_mol=energy-model_energy,
                net_ligand_force_difference_eV_angstrom=force.tolist(),
                net_ligand_force_difference_norm_eV_angstrom=float(np.linalg.norm(force)),
                model_net_ligand_force_difference_eV_angstrom=model_force.tolist(),
                retained_mm_net_ligand_force_difference_eV_angstrom=(force-model_force).tolist(),
                energy_pass=abs(energy)<=settings['g07_contact_region_energy_max_kcal_mol'],
                force_pass=np.linalg.norm(force)<=settings['g07_net_force_max_eV_angstrom']))
    submitted = read(ROOT/'Worker_Log/Milestone_03/evidence/G07_v1/region-sensitivity.json')
    for expected, actual in zip(submitted['comparisons'], comparisons):
        assert (expected['row'], expected['left'], expected['right']) == (actual['row'], actual['left'], actual['right'])
        for key in ('contact_energy_difference_kcal_mol', 'net_ligand_force_difference_norm_eV_angstrom'):
            assert math.isclose(expected[key], actual[key], rel_tol=0, abs_tol=2e-13)
        assert expected['force_pass'] == bool(actual['force_pass'])
        actual['force_pass'] = bool(actual['force_pass'])
    alternative = []
    for row in sorted(groups):
        if not row.startswith('butane') or row.endswith('-separated'):
            continue
        full, baseline, alt = (records[row, name] for name in ('uncut','baseline','alternative-ethane'))
        distances = {name: float(np.linalg.norm(r['total_net']-full['total_net'])) for name,r in (('baseline',baseline),('alternative-ethane',alt))}
        alternative.append(dict(row=row,**distances,alternative_farther_than_baseline=distances['alternative-ethane']>distances['baseline']))
    matrix = read(ROOT/'fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json')
    assert len(matrix['rows']) == 20 and len(matrix['new_jobs']) == 30 and len(matrix['reused_jobs']) == 20
    assert len({j['name'] for j in matrix['new_jobs']}) == 30
    assert sum(j['kind']=='full-parent' for j in matrix['new_jobs']) == 20
    assert sum(j['kind']=='alternative-ethane' for j in matrix['new_jobs']) == 10
    for job in matrix['new_jobs']:
        row = read(ROOT/'fixtures/chemical_reference_v3'/job['source_input'])
        ligand_z = row['atomic_numbers'][row['fragment_count']:]
        control = row['g07_controls']
        component = control['parent'] if job['kind']=='full-parent' else next(c for c in control['choices'] if c['name']=='alternative-ethane')['exact_model_fragment']
        assert job['atomic_numbers'] == component['atomic_numbers']+ligand_z
        assert job['positions_angstrom'] == component['positions_angstrom']+control['ligand_positions_angstrom']
        assert job['formal_charge']==0 and job['multiplicity']==1
    for job in matrix['reused_jobs']:
        assert sha(ROOT/'fixtures/chemical_reference_v3'/job['path']) == job['sha256']
    quantum_manifest = read(ROOT/'fixtures/chemical_reference_v3/quantum/manifest.json')
    assert all(sha(ROOT/'fixtures/chemical_reference_v3/quantum'/p)==digest for p,digest in quantum_manifest['files'].items())
    failures = [c for c in comparisons if not(c['energy_pass'] and c['force_pass'])]
    result = dict(reviewed_head=HEAD, submission_hashes_verified=len(hashes), frozen_start_hashes_verified=len(start['tracked_sha256']),
        accepted_base_files=len(preserved)+len(changed), unchanged_base_files=len(preserved), changed_base_files=changed,
        accepted_quantum_record_count=sum(p.startswith('records/') for p in quantum_manifest['files']),
        new_fixture_hashes_verified=len(verified), exact_frozen_description_ledgers=50, ledger_dispositions=dict(ledger_counts),
        independently_recomputed_saved_energy_error_max_kj_mol=max(v[0] for v in errors),
        independently_recomputed_saved_force_component_error_max_kj_mol_nm=max(v[1] for v in errors),
        geometries=len(groups),descriptions=len(records),pair_comparisons=len(comparisons),failure_count=len(failures),
        max_energy_sensitivity_kcal_mol=max(abs(c['contact_energy_difference_kcal_mol']) for c in comparisons),
        max_force_sensitivity_eV_angstrom=max(c['net_ligand_force_difference_norm_eV_angstrom'] for c in comparisons),
        energy_limit_kcal_mol=settings['g07_contact_region_energy_max_kcal_mol'],force_limit_eV_angstrom=settings['g07_net_force_max_eV_angstrom'],
        alternative_isoleucine_vs_uncut=alternative,new_reference_jobs=30,full_parent_jobs=20,alternative_cap_jobs=10,
        reused_g05_jobs=20,new_quantum_runs=0,physical_acceptance='blocked',comparisons=comparisons,failures=failures)
    with (HERE/'inputs-and-arithmetic.json').open('x') as stream:
        json.dump(result,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('comparisons','failures','alternative_isoleucine_vs_uncut')},indent=2))


if __name__ == '__main__':
    main()
