"""Reproduce the initial correction-receipt gap on isolated actual-data copies.

Never writes the canonical attempt and forbids every subprocess launch.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sys

EVIDENCE=Path(__file__).resolve().parent
REPO=EVIDENCE.parents[3]
sys.path[:0]=[str(EVIDENCE/'source-initial/tools'),str(REPO/'src')]
import resume_joint_quantum as joint


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    case=EVIDENCE/'initial-idempotence-case';case.mkdir()
    actual=REPO/'Worker_Log/Milestone_03/evidence/G07_v2/quantum-attempt-v1'
    output=case/'output';source=output/'jobs'/joint.PILOT/'attempt-0001'
    shutil.copytree(actual/'jobs'/joint.PILOT/'attempt-0001',source)
    (output/'records').mkdir()
    approval=json.loads((REPO/'Worker_Log/Milestone_03/evidence/G07_v2/authorization.json').read_text())
    approval['attempt_path']=str(output)
    auth=case/'authorization.json';auth.write_text(json.dumps(approval,indent=2)+'\n')
    joint.APPROVAL_PATH=auth;joint.APPROVAL_SHA256=digest(auth)
    state=json.loads((actual/'progress.json').read_text())
    state['identity']['approval_sha256']=digest(auth)
    (output/'progress.json').write_text(json.dumps(state,indent=2)+'\n')
    original_hashes={p.name:digest(p) for p in source.iterdir() if p.is_file()}
    canonical_progress=digest(actual/'progress.json')
    canonical_original={p.name:digest(p) for p in (actual/'jobs'/joint.PILOT/'attempt-0001').iterdir() if p.is_file()}
    def forbidden(*args,**kwargs):raise AssertionError('Audit must never launch any subprocess or worker')
    joint.recovery.subprocess.Popen=forbidden
    plan=REPO/'fixtures/chemical_reference_v3'
    matrix_path=REPO/'fixtures/fragment_ligand/prepared-mm-v1/quantum-job-matrix.json'
    approval,matrix=joint.validate_authorization(plan,auth,matrix_path)
    reference='/workspace/atom-mlmm-g07/reference-env/bin/python'
    receipt_path=joint.revalidate_pilot(output,plan,approval,matrix,reference)
    receipt=json.loads(receipt_path.read_text());original_time=receipt['wall_seconds']
    receipt['wall_seconds']=0.0
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    repeated=joint.revalidate_pilot(output,plan,approval,matrix,reference)
    settings=json.loads((plan/'reference-settings.json').read_text())
    order=joint.joint_queue(matrix,settings)[joint.PILOT]
    validated=joint.validate_joint_record(receipt_path.with_name('record.json'),order)
    completed=joint.recovery.completion_receipt(receipt_path.with_name('record.json'),joint.PILOT)
    result=dict(source_sha256=digest(EVIDENCE/'source-initial/tools/resume_joint_quantum.py'),
        first_corrected_wall_seconds=original_time,altered_wall_seconds=completed['wall_seconds'],
        repeated_call_accepted=repeated==receipt_path,record_validator_accepted=validated['status']=='computed',
        ordinary_recovery_receipt_admitted=joint.recovery.admitted(completed),
        original_copy_unchanged=original_hashes=={p.name:digest(p) for p in source.iterdir() if p.is_file()},
        canonical_original_unchanged=canonical_original=={p.name:digest(p) for p in (actual/'jobs'/joint.PILOT/'attempt-0001').iterdir() if p.is_file()},
        canonical_progress_unchanged=canonical_progress==digest(actual/'progress.json'),
        fixture_progress_debit_unchanged=json.loads((output/'progress.json').read_text())['wall_seconds_debited']==state['wall_seconds_debited'],
        subprocess_launches=0)
    (EVIDENCE/'initial-idempotence-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    assert result['repeated_call_accepted'] and result['ordinary_recovery_receipt_admitted']
    assert result['canonical_original_unchanged'] and result['canonical_progress_unchanged']


if __name__=='__main__':main()
