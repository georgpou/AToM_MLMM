# G10 Tasks 1–4 plus repairs — v7 complete independent combined audit

**Verdict: RED / changes_required.** R1 and R3–R7 close; R2 remains open because
two coherent backward clock histories pass public admission and resume. This
is the complete continuation of the paused audit, covering all 20 assertions.

Sole auditor: **gpt-6.1-sol / max**, originally `/root/g10_combined_audit_v7`,
resumed as `/root/g10_combined_audit_v7_resume`; no auditor subagents or repairs.
Branch `g10-engine-next`; clean resume HEAD `f4c2f1f0f096c64aadeb58ab21df5bfe202b9f7e`.
Originally reviewed HEAD `acfe9f6922d4029f1628aa69d530f0b642f4bb0d`; worker submission
`883d5a8c5dbe4953d32fc0125c7c42b41d99db21`; code/result `27e1639fefdde8ccca62263846204237391bf621`.
Source/tests/specifications/worker evidence remained frozen and identical.

[Independent evidence](evidence/G10_v7_independent/README.md) records exact UTC,
commands, exits, counts, hashes, profile and final report-only verification.
The [immutable pause](evidence/G10_v7_independent/CONTINUATION.md), original
harness error, all v5 failures and original source bundles remain preserved.
I reused completed checks and unchanged accepted force/probability/stationarity
proofs after exact diff/protected-byte verification; no full-suite rerun occurred.

| Independent evidence | Actual result |
| --- | --- |
| Focused pytest, completed before pause | 53 passed, 0 skips, 44 deselected, 42.53 s; exit 0. |
| Identity | 31 submitted hashes; eight current bundles × 38 source files; exact repair/full diffs and protected trees; exit 0. |
| Resumed repair controls | 33 PASS, including the three preserved prior controls; one helper characterization; exit 0, 18.63 s. |
| Current saved molecular records | ABFE224/RBFE233; 18 actual evaluations, 12 samples/eight attempts; exit 0, 34.65 s. Zero molecular preparation/integration added. |
| Same-attempt records and symlink | Six PASS controls; 12 accepted/two rejected actual attempts, full inverses/capture labels/outside terms; continuation exit 0, 3.51 s. |
| Public clock domain | Three valid origin controls, two product violations; completed exits 1 in 4.12 s and 3.38 s. |

Two harness exits are distinct from product findings: the original strict JSON
writer stopped before admission; the first record driver completed three controls
then detected all 12 natural attempts accepted. Separate continuations preserve
those originals, supply raw JSON `1e309` and add actual high-draw rejections.
The worker's hash-verified 626-pass/0-skip/1221.89-s full suite and fresh two-pilot
208.70-s result remain evidence, not independent acceptance. Current required
collection is **86 = 60+14+8+4**; the old cache contains three stale nodes.
Every scientific shell used the pinned activation, `OPENBLAS_NUM_THREADS=2` and
`PYTHONPATH="$PWD/src"`; serial CPU2/8 GiB, Reference double/MACE CPU float64.
No package, model, fixture, Hamiltonian, chemistry or tolerance changed.

**R2 — Important: the elapsed-clock envelope admits backward histories.**
`exchange_journal.py:551–568` checks a roundoff envelope without enforcing
nondecreasing time or ensuring its arithmetic stays finite. Public controls
start from current-source, clock-only resealed analytic handovers; no preparation
or source substitution is used. Initial reports, States and checkpoints agree.
In each challenge, sample/final JSON and actual cached State/checkpoint clocks
agree; every other JSON field, Snapshot, energy and force stays unchanged.

- At origin `1e308 ps`, sample `0.0005 ps`, step `0→1`, the bound becomes `inf`.
  Independently reordered binary64 and 90-digit Decimal give a finite bound
  about `3.33066907387547e292 ps`; the backward gap is about `1e308 ps`.
- At origin `1e14 ps`, the sample moves one ULP backward, `-0.015625 ps`, with
  the same exact step increment. The finite bound is `0.0333066907387547 ps`
  and admits it, although adding positive `0.0005 ps` cannot decrease binary64 time.

Both inert reads succeed; each actual resume loads all three workers, performs
**25 evaluations and three one-step calls**, and publishes boundary 1. The raw
[overflow](evidence/G10_v7_independent/clock-domain-results.json) and
[finite-bound](evidence/G10_v7_independent/clock-finite-bound-results.json) results
preserve complete public counterexamples. These are not private-helper claims.
Coherent `-1→-0.9995 ps` is a supported finite offset under the current contracts;
no explicit nonnegative absolute-origin requirement was found, so it is no finding.

The `gamma_n=n*u/(1-n*u)`, `u=2^-53`, accumulation/product/subtraction rationale
is sound as an exact-arithmetic upper bound for admitted positive timestep/counts.
Five pure repeated-addition controls, including 100,000/999,999 steps and nonzero
origins, pass. An overflowing implementation is unsound; the envelope also cannot
replace monotonicity. **Smallest repair:** reject decreasing clocks inertly,
compute a finite overflow-safe bound/residual over the admitted finite domain,
and fail closed on nonfinite intermediates. Retain exact saved/checkpoint/portable
clocks and exact step increments; add both public regressions with zero loader,
evaluation, pending, step or mutation, preserving valid large/negative origins
and repeated additions. No fixed cutoff, bound inflation or tolerance waiver.

| Prior finding | Final independent decision |
| --- | --- |
| R1 | CLOSED: complete metadata/seeds/types/RNG/inverses/identities reject inertly; valid 3/8-state and finite Gaussian-cache controls pass. |
| R2 | OPEN: actual checkpoint/portable/report/sample binding and ordinary bad clocks pass their repairs; the two timeline counterexamples remain. |
| R3 | CLOSED: complementary energy-consistent map0 worker2/map1 worker0 plus focused counterparts reject before any evaluation, pending or step. |
| R4 | CLOSED: accepted/rejected +123 contradictions reject inertly; same-attempt full-outside refresh arithmetic agrees. |
| R5 | CLOSED: nine actual parent/derived/secondary faults retain authority, primary/secondary diagnostics and every available cached worker checkpoint/portable/both-map State, with no energy/force reentry and exact rebuild. |
| R6 | CLOSED: actual fd traces/faults show every publication/rollback file and nested directory synced before rename and both parents attempted afterward; exact replay passes. No power-loss qualification. |
| R7 | CLOSED: root-only manifest exclusion; resealed nested manifests/extra layouts and direct symlinks reject before loading/mutation. |

| Assertion | Final decision and basis |
| --- | --- |
| C1 — Bounded additive API/types/limits | GREEN: complete focused/extra inert admission, including every signed worker seed. |
| C2 — Pair API/modes/source identity | GREEN: unchanged pair path, exact inventories/protected bytes and retained compatibility evidence. |
| C3 — Stable walkers/serial steps/live permutation | GREEN: independently reconstructed 14 histories/full inverses. |
| C4 — Immutable labels/IDs/complete clocks | RED: labels/IDs pass; backward timelines remain admitted, R2. |
| C5 — Atomic all-worker boundary/durability | GREEN: complete seals/cached states and actual fd traces. |
| C6 — Phases/pending/replay/failure preservation | GREEN: retained phase tests, fresh postcommit faults and exact rollback/rebuild. |
| C7 — Ownership/postrename authority | GREEN: unchanged nonblocking lock and immutable committed bytes through actual faults. |
| C8 — Inert/actual restored admission | RED: actual clocks/energy/both-map checks pass; inert elapsed-clock domain fails R2. |
| C9 — Complete consistent phases/history | GREEN: inverse/identity/refresh controls and same-attempt arithmetic. |
| P1 — One Hamiltonian/Metropolis path | GREEN: byte-identical pinned AToM adapter; no alternate physics path. |
| P2 — Fresh complete matrix/refresh/outside | GREEN: protected fresh-matrix proofs and 56 current entries including outside terms. |
| P3 — Complete chemistry/maps/ML/caps/forces/guards | GREEN: protected ownership/chemistry and all-worker restored both-map preflight. |
| P4 — Exact v2 bounded molecular pilots | GREEN: unchanged 224/233 atoms, ligand6/9, 64 waters, four count overrides, three workers/two boundaries. |
| P5 — Scientific definitions/physical limits | GREEN for preservation: models/locks/reference records/limits unchanged. |
| M1 — Beta/units/derivatives/reconstruction | GREEN: retained independent derivatives; fresh raw/full-force errors zero, reconstruction ≤5.83e-11. |
| M2 — Sign/probability/actual accept/reject | GREEN: protected probability proofs plus fresh pinned positive-exponent rejection. |
| M3 — Inverse algebra/capture labels | GREEN: full histories reconstruct; sample labels remain fixed across decisions. |
| M4 — Stationarity/statistical restraint | GREEN: protected exact six-permutation proof; sweep detailed balance/mixing not inferred. |
| M5 — RNG/clocks/deterministic replay | RED: valid host RNG/exact normal replay pass; backward-clock admission remains, R2. |
| M6 — Stored complete-energy phase arithmetic | GREEN: both outcomes match same-attempt matrix totals; +123 contradictions reject. |

**Categories: coding RED; physics/chemistry GREEN for bounded preservation;
mathematics RED for clock admission.** Position `1e-15 nm` and energy/full-force
`1e-8` bounds stay unchanged, with each energy bound to its own Snapshot identity.
Current position roundtrip ≤5.56e-17 nm; raw/full-force/refresh differences are zero.
Only this report/evidence and report-only STATUS are committed. No push/reset/rebase/merge.
All 46 G05 records, seven G07 exceedances/original force failures, 29 missing references,
and charged QM `2325.6446500519996 / 86400 s`, continuation false, are preserved.
Full G10/M05, chemical accuracy/protein, production/release, GPU/HPC, affinity,
equilibrium/mixing/convergence and correlated-walker uncertainty remain open/blocked.
`binding_result=not_evaluated`. Next: bounded R2 repair and independent regression review.
