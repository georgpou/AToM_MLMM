# G08 result admission — v2 repair amendment

**Status:** proposed for the exact G08 v2 independent review.

This supersedes only the BindingResult admission decision in
[v1](G08-record-admission-v1.md). The [v1 independent audit](../../../Worker_Log/Milestone_04/Gate_08_v1_audit.md)
established G08-R1: a final record could bypass the producer's correction checks
because declared obligations were absent from its admission context.

BindingResult adds optional typed `thermodynamics: ThermodynamicSpec`. The sole
producer supplies it. When present, its content identity and ordered correction
ledger must exactly match the result. Missing/uncomputed obligations must remain
in the unresolved tuple; unknown/duplicate entries reject. The special unresolved
`correction_covariance` marker requires an uncertain correction.

Any final value/error pair now requires the embedded standard thermodynamic
definition and every declared obligation resolved with evidence. Its value must
equal the restrained value plus recorded corrections to 1e-12 absolute/relative
floating-point arithmetic precision. This is record consistency, not a new
scientific accuracy threshold. The producer retains responsibility for validating
joint covariance and computing the final uncertainty; an arbitrary error number
does not itself establish scientific uncertainty evidence.

Legacy partial records with the new field absent remain readable. Canonical
encoding omits the field when None, preserving their bytes/content identities.
Legacy final records without a verifiable definition now reject deliberately;
no automatic acceptance or migration occurs. V1 submitted artifacts stay intact.
No prior physical record, Hamiltonian, estimator, numerical tolerance, asset,
environment or G06/G07 acceptance changes.

Affected requirements: P0-REQ-016/017/018 and G08-05. Tests cover direct/serialized
empty, missing, uncomputed, duplicate/reordered/mismatched ledgers, identity and
observable mismatches; deterministic and covariance-aware final producer round
trips; and legacy partial encoding. Affected G08 tests and full CPU regression
are required before review.
