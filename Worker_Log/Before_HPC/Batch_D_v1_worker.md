# Before HPC Batch D worker record

This is the inline serial `gpt-6-luna/max` worker submission for Batch D. It
implements the authorized preflight scope on `before_HPC`; it is not an audit,
scientific qualification, or gate/milestone acceptance.

The worker started at base commit
`317a72e69391e9618b04d15b25c8b644b1e3221e`. Source, tests, fixtures, and run
evidence are committed at `e117a18ef253caa1bca354376c6d1badbd635515`, with
source tree `e24d98ebc128b95290dff3c5243855adbde8a70e`. The following worker
report and status update are recorded in a later documentation-only commit.

## Implemented and exercised

`tools/prepare_host_guest_rbfe.py` creates a separate deterministic methanol A
to ethanol B 18-crown-6 RBFE preflight input. It emits stable atom identities,
complete unequal guest maps, explicit neutral-singlet component states,
geometry-only placements with recorded provenance, and a loadable
`SystemInput`/partition/snapshot configuration. Admission checks test both
maps against the whole host and each other. The fixture's parameter ledger
records that host parameters are absent. Its inert zero-charge, zero-LJ MM
terms are for mechanics and plumbing only; they do not model a physical
solvent or produce an affinity result.

The host test file exercised geometry admission, deterministic regeneration,
direct/native mechanism checks, and a bounded common-worker execution with a
fresh-process export/restart. The worker proof used three workers, two
boundaries, and one step. It tests consistency of the mechanics and handover
plumbing only. No adequate molecular sampling or physical energy claim is
made. The accepted 18-crown-6/methanol ABFE v2 input and 64-water fixture remain
unchanged.

`tools/prepare_protein_input.py` provides a generic admission path. It returns
a readable missing-choice checklist for an incomplete complete-target
proposal and validates declared source/artifact identities, components,
selection IDs, force-field provenance, and physical conventions when a
complete proposal is supplied. No target, ligand, protonation, missing-atom
repair, ion policy, or production parameter route was selected: the user
steered this batch to generic controls and deferred the real target.

The synthetic two-cut structural control imports through the common builder
and loads the existing configuration types. Bounded controls include an
all-MM original-system inventory reference, a zero-cut ligand-only mixed path,
and a cavity-inclusive two-cap path with matching source coordinates,
real-particle masses, constraints, box, and declared conventions. The cap
ledger checks parent completeness, zero cap masses, and virtual-site entries.
These controls ran on B's synthetic structural fixture; no real protein
fixed-coordinate calculation or protein energy/derivative/worker run occurred.
Byte-identical B derivative, parent-force, and worker proofs were reused, not
replayed. D did not add a new cap-force derivative proof.

`tools/validate_solvent_recipe.py` checks a versioned, explicit NVT recipe and
rejects an absent physical liquid definition, implicit NPT/pressure/virial,
HMR, or hidden integration conventions. The existing 64-water input is
checked only as a plumbing reference. No physical solvent/NPT recipe or
liquid run is admitted.

## Corrections, run definitions, and scientific limits

The correction-source retrieval and raw response headers are indexed in
[`evidence/batch-d-v1/README.md`](evidence/batch-d-v1/README.md). The cited
AToM-OpenMM v8.5.0 `abfe_structprep.py` source was retrieved successfully and
is byte-identical to the installed 8.5.0b0 module (SHA-256
`171bf698ea95ccd6e7653fa5b5596e192a233c7d2a4940bb1fa1dfcaef10856b`). The tag
and installed distribution version strings differ. That source documents
preparation restraint machinery but gives no postprocessing correction
equation. The cited U37 guide and its targeted source index both returned HTTP
403. Therefore no alternate correction scheme or numerical correction was
invented. Applicability and calculation status remain distinct and held until
the documented procedure and physical domains/reference atoms are available.

The ABFE ledger labels all six schema obligations individually; it does not
turn them into six automatic calculations. Translation, bound release,
orientation, conformation, state counting, and midpoint-bridge applicability
are explicitly unresolved or required only for a defined physical path, and
all values remain uncomputed. The RBFE ledger records the intermediate
midpoint as already in the proposed schedule, avoiding a duplicate additive
term. No correction is declared zero merely because it was not computed.

The host run definitions freeze proposed A-to-A identity, forward A-to-B, and
independently initialized reverse B-to-A runs with seeds, matched conventions,
retention/uncertainty needs, and operation-count resource formulas. They are
`proposed_not_run`; production retention ceilings and wall-time estimates
remain blocked until the physical route and measured profile are admitted.
The matched ABFE/RBFE cycle is explicitly blocked: physical host/solvent
parameters, domains/restraint references, and correction definitions are
unmatched, and C3's general unmatched-physical-state closure refusal contract
remains an uncovered implementation/definition hold. No closure expression
or result is asserted. Predictive Pearson r and Kendall tau remain separate
from convergence of individual energies. `binding_result` remains
`not_evaluated`.

No adequate trajectory, cluster run, QM run, or GPU benchmark was performed.
The six correction rows do not imply six calculations, and the tiny worker
pilot does not establish molecular accuracy, overlap, convergence, or
production readiness. Larger production calculations may reach predeclared
sampling ceilings; those ceilings are still future inputs.

## Verification and preserved failures

All captured commands record exact arguments, UTC interval, source identity,
activation script digest, thread/memory profile, exit code, counts, and logs.
The required focused command passed 9 tests with 0 skips in 21.98 seconds.
The bounded protein-preflight tests passed 3 tests with 0 skips in 0.18
seconds. After the final regenerated host parameter-route metadata, the
affected host test file passed all 4 tests with 0 skips in 20.81 seconds,
including direct/native and fresh worker restart checks. The exact commands
and receipts are in the evidence index. No full CPU suite or docs self-test was
run; those checks remain reserved until after Batch E.

The initial RED run recorded 8 expected failures before D interfaces existed.
The preserved green failures led to test/harness corrections rather than
scientific-threshold changes: the first focused attempt had 3 failures from
assuming unequal guests had identical atom arrays, passing a stale fifth
`build_atm` argument, and rejecting a valid sibling fixture path; the second
had 2 failures because atom displacements needed per-atom broadcasting and
the checked field is `displacement1_nm`. The first protein structural-control
attempt compared cap-extended particle masses with real-only input masses;
the corrected harness compares mapped real masses and separately checks cap
masses. A later control attempt guessed a cap-record field name; the committed
schema uses `final_particle_index`. Every failure and passing rerun is retained
verbatim with its receipt in `evidence/batch-d-v1/README.md`.

The existing historical evidence, accepted fixtures, and supplied handoff
items were not re-extracted or edited. The root worker owns the final
comparison against the supplied 386-path digest manifest. No release,
publication, independent audit, or next-batch work is part of this submission.
