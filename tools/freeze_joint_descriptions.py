"""Freeze the 50 declared G07 physical test fixtures and retained/removed ledgers.

This is a fixture preparation command. It uses the inspected test fixture maps,
the production physical builder and actual prepared MM; it runs no MACE energy
or quantum calculation. Run with PYTHONPATH=src:. in the locked core environment.
"""
import argparse
import hashlib
import json
from pathlib import Path
from atm_mlmm.joint_reference import quantum_job_matrix
from atm_mlmm.schema import to_json
from tests.joint_oracle import joint_case,PREPARED,ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args = parser.parse_args()
    if args.output.exists(): raise FileExistsError('never overwrite a frozen attempt')
    args.output.mkdir(parents=True)
    rows = []
    matrix = quantum_job_matrix(ROOT/'fixtures/chemical_reference_v3')
    for row in matrix['rows']:
        for description in row['descriptions']:
            name = row['name']+'--'+description['name']
            bundle,snapshot = joint_case(row_name=row['name'],choice=description['name'])
            artifact = args.output/(name+'.json')
            with artifact.open('x') as stream: stream.write(to_json(bundle)+'\n')
            rows.append(dict(row=row['name'],description=description['name'],artifact=artifact.name,
                artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
                physical_identity=bundle.content_identity,prepared_mm_sha256=bundle.manifest['original_mm_sha256'],
                system_sha256=bundle.system_sha256,
                retained_mm_sha256=hashlib.sha256(bundle.manifest['retained_mm_xml'].encode()).hexdigest(),
                real_atom_ids=snapshot.real_atom_ids,positions_nm=snapshot.positions_nm,
                model_input_ids=bundle.model_input_ids,model_to_final=dict(bundle.model_to_final),
                links=[json.loads(to_json(link)) for link in bundle.links],
                quantum_job=description['quantum_job'],full_reference_job=row['full_job']))
    result = dict(state='frozen inputs/ledgers; new G07 quantum budget/review pending',rows=rows,
        source_manifest_sha256=matrix['source_manifest_sha256'],
        prepared_mm_manifest_sha256=hashlib.sha256((PREPARED/'manifest.json').read_bytes()).hexdigest(),
        model_checkpoint_sha256='165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f',
        cap_distance_nm=.109,quantum_or_model_energy_evaluated=False)
    with (args.output/'manifest.json').open('x') as stream: json.dump(result,stream,indent=2,allow_nan=False);stream.write('\n')
    print('Frozen physical descriptions:',len(rows))


if __name__ == '__main__': main()
