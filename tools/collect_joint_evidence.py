"""Collect actual G07 numerical single points on the frozen 50 descriptions.

No DFT is launched. Missing Qfull/alternative references remain explicitly
unqualified; software route agreement cannot supply chemical acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import openmm as mm
from atm_mlmm.atm import PhysicalEvaluator,load_bundle
from atm_mlmm.model_reference import NativeMACE
from atm_mlmm.schema import Snapshot
from tests.joint_oracle import independent_answer,RUNTIME


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('preserve earlier numerical evidence')
    args.output.mkdir(parents=True)
    root=Path(__file__).resolve().parents[1]
    fixtures=root/'fixtures/fragment_ligand/descriptions-v1'
    manifest=json.loads((fixtures/'manifest.json').read_text())
    native=NativeMACE()
    results=[]
    for row in manifest['rows']:
        bundle=load_bundle(fixtures/row['artifact'],row['artifact_sha256'],trusted=True)
        snapshot=Snapshot(tuple(row['real_atom_ids']),row['positions_nm'],None)
        expected_energy,expected_force,raw=independent_answer(bundle,snapshot,native)
        with PhysicalEvaluator(bundle,RUNTIME) as evaluator:actual=evaluator.evaluate(snapshot)
        energy_error=abs(actual.energy_kj_mol-expected_energy)
        force_error=float(np.max(np.abs(np.asarray(actual.forces_kj_mol_nm)-expected_force)))
        if energy_error>1e-4 or force_error>5e-3:
            raise ValueError(f'preserved failed route comparison: {row["row"]} / {row["description"]}: {energy_error}, {force_error}')
        record=dict(row=row['row'],description=row['description'],quantum_job=row['quantum_job'],
            full_reference_job=row['full_reference_job'],physical_identity=bundle.content_identity,
            source_artifact_sha256=row['artifact_sha256'],
            hybrid_energy_kj_mol=actual.energy_kj_mol,hybrid_real_forces_kj_mol_nm=actual.forces_kj_mol_nm,
            independent_hybrid_energy_kj_mol=expected_energy,independent_hybrid_real_forces_kj_mol_nm=expected_force.tolist(),
            energy_error_kj_mol=energy_error,max_force_error_kj_mol_nm=force_error,
            native_raw_model=raw,reference_status='Qfull/alternative reference absent; G07-T4 unqualified')
        name=row['row']+'--'+row['description']+'.json'
        with (args.output/name).open('x') as stream:json.dump(record,stream,indent=2,allow_nan=False);stream.write('\n')
        results.append(record)
        print(row['row'],row['description'],energy_error,force_error,flush=True)
    separated={(r['row'].rsplit('-separated',1)[0],r['description']):r for r in results if r['row'].endswith('-separated')}
    differences=[]
    for r in results:
        if r['row'].endswith('-separated'):continue
        family=r['row'].split('-d',1)[0]
        baseline=separated[(family,r['description'])]
        differences.append(dict(row=r['row'],description=r['description'],
            hybrid_contact_minus_separated_kj_mol=r['hybrid_energy_kj_mol']-baseline['hybrid_energy_kj_mol'],
            scope='within-description diagnostic; no quantum partition-approximation acceptance'))
    summary=dict(rows=len(results),max_energy_error_kj_mol=max(r['energy_error_kj_mol'] for r in results),
        max_force_error_kj_mol_nm=max(r['max_force_error_kj_mol_nm'] for r in results),
        descriptions_manifest_sha256=hashlib.sha256((fixtures/'manifest.json').read_bytes()).hexdigest(),
        physical_reference_qualified=False,new_dft_jobs_launched=0,geometry_differences=differences,
        files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in args.output.iterdir() if p.is_file()})
    with (args.output/'summary.json').open('x') as stream:json.dump(summary,stream,indent=2,allow_nan=False);stream.write('\n')
    print('Full-real route comparisons passed:',len(results),flush=True)


if __name__=='__main__':main()
