# G08 engine-readiness continuation — attempt 1 — worker

**Scope:** G08-T1/T2/T3 and all six stable assertions; combined M04 review requested on the inherited accepted M02 analytic CPU lineage. No G07 physical acceptance, QM or production claim.  
**Outcome:** ready_for_audit; full G08 and combined M04 analytic scope submitted, independent acceptance pending.  
**Model/version:** parent model label/version not exposed by this harness.  
**Reasoning setting:** not exposed.  
**Started:** 2026-10-04T13:39:48Z.  
**Finished:** 2026-10-04T14:24:00Z.  
**Previous worker/audit:** none for G08.

## Snapshot and references

Replacement checkout initially contained only documentation on branch `work` at `2d7bcc94f901738e39f536f16de84699d4e8d631`. No user modifications were present. Read-only remote inspection found `m04-engine-readiness` at `e24e880abcb0353b8f9c2f2e509d6cbb46174f3b`; fetched and switched to that existing branch, verifying ancestry of `fc6dbe3dfbb33906f85c0756d6c6ba6b44f1dd86`. The prepared branch had no G08 logs or sampling tests.

Tested source/result commit: `966a8d61347f65a69f8ba7e6750c4379d4e0503f`.
The subsequent submission commit adds this worker/evidence and STATUS reporting;
scientific code/test files match the [82-file manifest](evidence/G08_v1/source-test-manifest.json).
[Snapshot](evidence/G08_v1/snapshot.json) records the base, source and inherited
predecessor. The auditor receives the exact submission SHA separately.

Read AGENTS, DEVELOPMENT, CPU environment guide, G08, S03/S05 and relevant S06 sections. The supplied handoff authorizes inline autonomous implementation from its detailed design, overriding generic skill approval pauses. See [implementation plan](G08-implementation-plan.md). S03/S05/S06 SHA-256: `1fbb01d02e97c85b4581e136860f01a7437b7d6aefcb17284ea099183d4de95b`, `bb0b4f46ea2db1369e86d6f2a5863b9fc57e7d574a9b120e84c26c9079dc338b`, `31a906780659012ccf2accba1e492d58d4b62f38650be98fbd869b0daadcaf65`.

## Setup findings

- Main/Amber/reference environments from the handoff were absent. Host Python 3.12 has NumPy/SciPy but no pytest/OpenMM/PyTorch/PyMBAR; it does not qualify the locked profile.
- Default sandbox GitHub access failed connecting to the configured proxy. Tool network permission resolved the connection; proxy/CA were preserved.
- The original single-branch fetch configuration excluded the continuation branch. Added only its fetch mapping and established tracking; main/predecessor were unchanged.
- Locked installer attempt `/workspace/atom-mlmm-g08` verified supplied artifacts and downloaded the exact Miniforge bootstrap, then exited 1 because `/home/agent/.conda` could not be created under the sandbox. Narrow directory creation with reviewed filesystem permission succeeded. Failed attempt and console log were preserved.
- Rebuilding unchanged locks in fresh prefix `/workspace/atom-mlmm-g08-r2`; no reference environment installation or quantum-budget mutation.

## Implementation and specification decisions

Implemented additive dependency-light `CorrectionRecord`, `ThermodynamicSpec`,
`EvaluationRecords` and `BindingResult`. Endpoint weights and graph connections
are explicit; required corrections cannot become implicit zero. Added full
finite-wall translation integral with explicit infinite-space domain admission,
standard-state sign and covariance-aware state/correction accounting. Uncertain
corrections require joint covariance; missing it withholds the final pair.

`schedule.reduced_potentials` reconstructs the existing exact expression from
raw u0/u1/outside terms at all declared states and checks observed sampling
totals. Nonfinite, duplicate, lost-identity and unknown-state records reject.
Independent integration of deliberately unequal active directional midpoints
verifies D1-D0-deltaFm; omitting/reversing the bridge fails the known answer.
Both expressions are cross-evaluated on independent samples from both midpoint
ensembles, with connected support and sampled bridge uncertainty.

Shared analysis consumes reduced potentials, counts and thermodynamic records.
AToM-specific UWHAM translation remains in the existing adapter. The pinned
default optimizer reported success with normalization residual 3.0026e-4;
its exact objective/gradient/Hessian are now independently refined. Canonical
trust-exact subsequently hit objective roundoff at gradient 1.638e-10; a local
exact-Hessian Newton refinement reached machine precision. No PyMBAR result
initializes UWHAM, no upstream source/lock is changed, and no data are clipped.
Same-input free energies agree within 1e-8 dimensionless; Fisher covariance
agrees with PyMBAR. Gauge/state offsets and covariance are tested explicitly.

Fixed-state correlated walker histories are thinned conservatively using the
largest inefficiency of u0/u1/their difference/outside. Original raw observations
are preserved and validated before thinning. Unsupported correlated exchanging
histories reject pending block/resampling qualification; no GPU/replica claim is
inferred. Connected overlap and contribution diagnostics do not prove chemical
or conformational accuracy.

The [additive record amendment](../../docs/project-0/specs/G08-record-admission-v1.md)
records rationale, field/obligation names, affected contracts/tests, unchanged
prior evidence, compatibility/rejection policy, numerical limits and pending
review. No existing serialized record/identity, Hamiltonian, scientific sign,
force definition or gate tolerance changed. The finite-wall hard-limit test
initially used a spring too small for its unchanged limit; increasing k from
1e18 to 1e20 resolves that oracle setup issue. The installed `examples` package
hid the example namespace; explicit file loading follows the repository's
existing test pattern. The skill-linked generic reviewer template was unavailable;
the actual repository audit template is used.

## Checks and next handoff

At start: two-CPU quota, 8 GiB RAM limit, no swap, zero cgroup OOM/OOM-kill events;
approximately 30 GiB free before installation. After the locked environments,
approximately 20 GiB remained. Scientific workers/tests were serialized; zero
OOM/OOM-kill events persisted. Cgroup total includes reclaimable file cache;
no cache dropping or essential-data cleanup occurred. Environment failure is
not counted as a failing feature regression.

All scientific commands activate `/workspace/atom-mlmm-g08-r2/activate.sh`, use
two threads and run from `/workspace/AToM_MLMM`. [Evidence inventory](evidence/G08_v1/README.md)
links full output and original raw artifacts; the source/test manifest covers
82 scientific code/test/config files.

| Check | Actual result |
|---|---|
| Locked main/Amber installer and recorded validation | exit 0, all 9 checks pass; exact Python 3.11.16/core NumPy 2.4.6/Amber NumPy 1.26.4/OpenMM 8.6.1/PyMBAR 4.0.3/AToM 8.5.0b0 |
| Recovered-branch `python -m pytest -q` | exit 0, 416 passed in 287.25 s |
| Focused T1/T2/T3 initial RED | 9/3/2 intended missing-API failures, respectively; diagnostic numerical failures preserved separately |
| T1/T2 focused known-answer/context/correction checks | exit 0, 12 passed |
| Independent-estimator refined focused checks | exit 0, 14 passed in 11.58 s |
| Three-seed native harmonic MD regression | exit 0, 1 passed in 21.86 s; all seed/full/last-half and contribution assertions pass |
| Supplemental active-midpoint independent ensembles | exit 0, 1 passed in 2.67 s |
| Full CPU suite after implementation | exit 0, 433 passed in 324.84 s; final complete submission repeats with 433 passed in 321.87 s |
| `python tools/check_docs.py --self-test`; `git diff --check` | exit 0; zero local errors, 8 self-tests; no whitespace errors |

The eleven-state independent Gaussian/quadrature fixture checks the complete
lambda curve, +1.5/-1.5 kJ/mol and kr=0 limit before MD. Native MD uses Reference
double, NVT at 300 K, 12 Da, LangevinMiddle friction 1/ps and dt=0.0005 ps.
Seeds 41/73/109 each have five windows with 5 ps warmup then 400 ps recorded;
this is a bounded one-particle analytic trial. Its values are
1.5081551 +/-0.0719544, 1.5018076 +/-0.0790068, and 1.4342246 +/-0.0759785 kJ/mol.
Every run is within 3 SE and <=0.1 kJ/mol of +1.5. Minimum effective contributions
are 1787.9/1427.9/1627.0, after retaining 2828/2506/2656 of 20000 samples.
The independent-run mean is 1.4813958 +/-0.0437064 kJ/mol; replicate spread is
0.0409745 kJ/mol and is reported separately. Full frames, real forces, bundles
and raw records are preserved before analysis.

The matching `Gate_08_v1_audit.md` must be written by the user's actual chosen
GPT-6.1-sol/MAX reviewer on the exact frozen submission. Review includes the
additive amendment, all G08 assertions and combined M04 criteria, carrying
inherited M02 acceptance. No independent acceptance is claimed here. After
acceptance, continue scoped G09 technical solvent/preparation/export; M03/G07
physical blockers and missing references remain unchanged.
