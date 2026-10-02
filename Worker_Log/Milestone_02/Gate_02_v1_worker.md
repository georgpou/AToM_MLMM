# G02 analytic native ATM — v1 worker

**Scope:** G02-T1/T2/T3, all nine gate checks, `core-analytic-cpu` on OpenMM Reference and CPU.\
**Outcome:** ready_for_audit.\
**Finished:** 2026-10-02 12:19:48 UTC.\
**Snapshot:** branch `m02-analytic-atm`; copied parent/base `87146b4cc7fbd0b58d6688903a5ba081b813ac13`; G02 implementation `9f36ccbe94bbfacc358586be6510c62bfe58b331`; completed tested M02 code `4c952dba5563572cf9e39527e64fe28ee201c385`. Submitted logs/evidence/STATUS are report-only.\
**Author:** Codex / GPT-6; exact runtime model version and reasoning setting not exposed.

## Changes and scientific scope

The fetched predecessor and new branch started at the same full SHA, with an empty diff and a clean checkout. Main remains `2d7bcc94f901738e39f536f16de84699d4e8d631`. The accepted M01 handoff is an ancestor; its scientific definitions, locks and model-loading safeguards are retained.

Added immutable PhysicalBundle, TransferDefinition, ScheduleSpec, RestraintSpec, AlchemicalBundle and named raw/evaluation records; a full-particle protocol resolver; importable harmonic and geometry-dependent environment callbacks; one shared native assembler/evaluator; independent endpoint checks and coordinate finite-difference sweeps. Protocols select complete mobile ligands and maps without changing the physical builder. Every influencing real coordinate receives its force, with explicit real/final/model maps and nonidentity `oldToNew` coverage. Persistent evaluators reject runtime System, map, membership, parameter, integrator-mask and profile mutation.

[The seven-real-atom fixture](../../fixtures/analytic/transfer-v1.json) has two unequal, noncontiguous ligand groups, selected order `[2,0]`, hand-written translations, independently derived spring forces and a nonzero outside harmonic term. The B ligand has its own nonzero physical energy/forces. Local and MM-environment-dependent analytic substitutes use the same contracts. This is an architectural fixture, with no chemical-reference meaning.

Linear lambda 0/0.37/1 and the exact S05 nonlinear production expression are checked, including soft-core/softplus transition regions, both directions, offsets and independently differentiated endpoint weights. Raw `(u1,u0,expression)` is explicitly unpacked; raw physical, perturbation, softened, expression, outside and total energies stay distinct. The environment callback recomputes its geometry in each mapped evaluation.

PythonForce artifacts remain executable trusted data. External reload requires explicit trust and a matching SHA-256 before deserialization. Fresh processes with empty caches and denied network access load both positive fixtures and a [preserved stale-descriptor negative fixture](evidence/M02_v1/stale-reproducer.json).

## Verification and evidence

All project commands ran at the repository root after `source /workspace/.onboarding/atom-mlmm-m02/activate.sh`. [Validation outputs](evidence/M02_v1/validation.json.gz) retain commands, exit codes, baseline and intended RED results. [Exact environment identity](evidence/M02_v1/environment-manifest.json.gz), [strict validation](evidence/M02_v1/strict-validation.json.gz) and [source/input hashes](evidence/M02_v1/source-input-manifest.json) identify the profile and tested snapshot.

The original fresh baseline failed one test because it assumed the default installation prefix (46 passed). The test now follows the activated `sys.prefix` and preserves every original strict environment assertion. The repaired baseline passed **47**, with **46 passed, 1 deselected** in the analytic selection. No production environment/lock/loader change was made.

| Check | Command/result, exit 0 unless stated |
|---|---|
| Initial G02 RED | Full G02 file selection with `-q`: **44 intended absent-API failures**, exit 1 |
| Second-ligand physical force RED | `python -m pytest tests/contracts/test_transfer_protocols.py::test_second_group_has_nonzero_mapped_force -q`: **1 intended failure**, then covered by the passing gate |
| Full G02 gate | `python -m pytest tests/integration/test_pythonforce_atm.py tests/contracts/test_transfer_protocols.py tests/contracts/test_physical_evaluator.py tests/contracts/test_fault_injection.py -v`: **78 passed in 11.06 s** |
| Completed full project suite | `python -m pytest -q`: **164 passed in 27.88 s** |
| Analytic selection | `python -m pytest -m 'not gpu and not model_assets and not slow' -q`: **163 passed, 1 deselected in 21.36 s** |
| Strict locked installation | `python /workspace/.onboarding/atom-mlmm-m02/validate.py --repository "$PWD"`: **all nine checks passed** |

| Stable test ID | Established assertion |
|---|---|
| P0-TEST-G02-01 | Linear endpoint energies and all-real forces at 0/0.37/1, both shapes/platforms |
| P0-TEST-G02-02 | `[2,0]` selected-particle scatter and nm/kJ/mol force units; factor-ten fault detected |
| P0-TEST-G02-03 | Nonzero outside contribution counted once; explicit raw tuple order |
| P0-TEST-G02-04 | Same physical bundle and assembler for one/two unequal complete groups, including nonidentity final mapping |
| P0-TEST-G02-05 | S04 examples `.45/+3/-3` and `.80/+4/-4`; MM-only motion and mapped MM derivative |
| P0-TEST-G02-06 | Persistent A-B-A history independence on Reference/CPU |
| P0-TEST-G02-07 | Wrong index, omitted child/coupling/MM derivative, reversed tuple, stale input, factor-ten and double-count faults detected; executable stale sample reload repeats failure |
| P0-TEST-G02-08 | Hand-derived negative gradients for endpoint and outside harmonics |
| P0-TEST-G02-09 | Exact nonlinear chain rule, transitions/directions/offsets and full-coordinate FD sweep |

[Numerical evidence](evidence/M02_v1/numerical-results.json) contains 16 direct/native/upstream nonlinear cases (two protocols, local/environment substitutes, Reference/CPU and two states) with full energies/forces, identities, ownership and active masks. Maximum absolute energy error was **5.684341886080802e-14 kJ/mol**; maximum force-component error was **1.1368683772161603e-13 kJ/mol/nm**. Frozen Reference/component limits are `1e-8`/`1e-7`; the existing direct/ATM starting limits `1e-4`/`5e-3` were not relaxed. FD steps are `1e-3`, `1e-4`, `1e-5 nm`, with final maximum component error at most `1e-5 kJ/mol/nm`. No nonfinite result is clipped into a passing value.

## Handoff

G03 is implemented on the same completed snapshot; [its worker](Gate_03_v1_worker.md) submits the **combined G02/G03/M02** review. Independent approval is still required. Full pretrained-model/GPU qualification, caps, actual electrostatic/periodic physics, molecular binding and M00 physical-reference decisions remain pending. The bundled real-weight example passes in the full suite but does not establish chemical accuracy or a molecular gate.
