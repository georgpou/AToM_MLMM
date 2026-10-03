"""Reproduce all region comparisons from immutable saved single points.

This is an evidence calculation, not an alternative Hamiltonian, a quantum
comparison, or a repair. It imports no production evaluator and launches no QM.
"""
import hashlib
import itertools
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
FIXTURES = ROOT / 'fixtures/fragment_ligand/descriptions-v1'
POINTS = HERE / 'fifty-description-single-points'
# Match the admitted ASE/MACE CODATA 2014 conversion; no rounded unit factor.
KJ_MOL_NM_PER_EV_ANGSTROM = 10 * 1.6021766208e-19 * 6.022140857e23 / 1000


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def net(forces, ids):
    if len(forces) != len(ids) or any(len(f) != 3 for f in forces):
        raise ValueError('force/identity shape mismatch')
    if not all(math.isfinite(x) for f in forces for x in f):
        raise ValueError('nonfinite forces remain a blocking failure')
    selected = [f for f, atom_id in zip(forces, ids) if atom_id.startswith('a:')]
    if not selected:
        raise ValueError('complete ligand absent')
    return [math.fsum(f[k] for f in selected) / KJ_MOL_NM_PER_EV_ANGSTROM for k in range(3)]


def subtract(a, b):
    return [x-y for x, y in zip(a, b)]


def norm(vector):
    return math.sqrt(math.fsum(x*x for x in vector))


def main():
    manifest = read(FIXTURES / 'manifest.json')
    summary = read(POINTS / 'summary.json')
    settings_path = ROOT / 'fixtures/chemical_reference_v3/reference-settings.json'
    settings = read(settings_path)
    if summary['descriptions_manifest_sha256'] != digest(FIXTURES / 'manifest.json'):
        raise ValueError('description manifest changed after evaluation')
    if len(manifest['rows']) != 50 or len(summary['files']) != 50:
        raise ValueError('incomplete frozen description set')
    energy_limit = settings['g07_contact_region_energy_max_kcal_mol']
    force_limit = settings['g07_net_force_max_eV_angstrom']
    records, groups, sources = {}, {}, {}
    for item in manifest['rows']:
        name = item['artifact']
        if digest(FIXTURES / name) != item['artifact_sha256']:
            raise ValueError('changed physical description: '+name)
        if digest(POINTS / name) != summary['files'][name]:
            raise ValueError('changed numerical record: '+name)
        value = read(POINTS / name)
        if (value['source_artifact_sha256'] != item['artifact_sha256'] or
                value['physical_identity'] != item['physical_identity']):
            raise ValueError('numerical record identity mismatch')
        energy = value['hybrid_energy_kj_mol']
        model_energy = value['native_raw_model']['energy_kj_mol']
        if not all(math.isfinite(x) for x in (energy, model_energy)):
            raise ValueError('nonfinite energy remains a blocking failure')
        total_net = net(value['hybrid_real_forces_kj_mol_nm'], item['real_atom_ids'])
        model_net = net(value['native_raw_model']['forces_kj_mol_nm'], item['model_input_ids'])
        # All cap parents are protein IDs. Raw ligand model forces therefore
        # equal the projected model ligand forces; cap projection is not repeated.
        if any(link['data']['ml_parent_id'].startswith('a:') or link['data']['mm_parent_id'].startswith('a:')
               for link in item['links']):
            raise ValueError('ligand cap parent requires an explicit projection')
        key = (item['row'], item['description'])
        if key in records:
            raise ValueError('duplicate description')
        records[key] = dict(energy=energy, model_energy=model_energy,
                            mm_energy=energy-model_energy, total_net=total_net,
                            model_net=model_net, mm_net=subtract(total_net, model_net))
        groups.setdefault(item['row'], []).append(item['description'])
        sources[name] = dict(physical_sha256=item['artifact_sha256'], numerical_sha256=digest(POINTS/name))
    if len(groups) != 20:
        raise ValueError('incomplete frozen geometry set')
    comparisons = []
    for row, descriptions in sorted(groups.items()):
        items = [r for r in manifest['rows'] if r['row'] == row]
        if any((r['real_atom_ids'], r['positions_nm']) !=
               (items[0]['real_atom_ids'], items[0]['positions_nm']) for r in items):
            raise ValueError('region descriptions do not share real geometry')
        control = row if row.endswith('-separated') else row.split('-d', 1)[0]+'-separated'
        for left, right in itertools.combinations(descriptions, 2):
            a, b = records[(row, left)], records[(row, right)]
            ca, cb = records[(control, left)], records[(control, right)]
            energy = ((a['energy']-ca['energy'])-(b['energy']-cb['energy']))/4.184
            model_energy = ((a['model_energy']-ca['model_energy'])-
                            (b['model_energy']-cb['model_energy']))/4.184
            force = subtract(a['total_net'], b['total_net'])
            model_force = subtract(a['model_net'], b['model_net'])
            mm_force = subtract(a['mm_net'], b['mm_net'])
            comparisons.append(dict(row=row, left=left, right=right, separated_control=control,
                contact_energy_difference_kcal_mol=energy,
                model_contact_energy_difference_kcal_mol=model_energy,
                retained_mm_contact_energy_difference_kcal_mol=energy-model_energy,
                net_ligand_force_difference_eV_angstrom=force,
                net_ligand_force_difference_norm_eV_angstrom=norm(force),
                model_net_ligand_force_difference_eV_angstrom=model_force,
                retained_mm_net_ligand_force_difference_eV_angstrom=mm_force,
                model_net_force_difference_norm_eV_angstrom=norm(model_force),
                retained_mm_net_force_difference_norm_eV_angstrom=norm(mm_force),
                energy_pass=abs(energy)<=energy_limit, force_pass=norm(force)<=force_limit))
    failures = [c for c in comparisons if not (c['energy_pass'] and c['force_pass'])]
    report = dict(scope='hybrid description sensitivity; Qfull/alternative references absent',
        physical_acceptance='blocked', physical_reference_qualified=False,
        reference_settings_sha256=digest(settings_path),
        descriptions_manifest_sha256=digest(FIXTURES/'manifest.json'),
        numerical_summary_sha256=digest(POINTS/'summary.json'),
        unit_conversion_kj_mol_nm_per_eV_angstrom=KJ_MOL_NM_PER_EV_ANGSTROM,
        energy_limit_kcal_mol=energy_limit, net_force_limit_eV_angstrom=force_limit,
        geometries=len(groups), descriptions=len(records), pair_comparisons=len(comparisons),
        failure_count=len(failures),
        max_energy_difference_kcal_mol=max(abs(c['contact_energy_difference_kcal_mol']) for c in comparisons),
        max_net_force_difference_eV_angstrom=max(c['net_ligand_force_difference_norm_eV_angstrom'] for c in comparisons),
        failures=failures, comparisons=comparisons, sources=sources)
    output = HERE/'region-sensitivity.json'
    with output.open('x') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({key:report[key] for key in ('geometries','descriptions','pair_comparisons',
        'failure_count','max_energy_difference_kcal_mol','max_net_force_difference_eV_angstrom')}, indent=2))


if __name__ == '__main__':
    main()
