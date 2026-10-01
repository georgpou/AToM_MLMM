# G00/G01 and M01 analytic CPU — v1 audit

**Reviewed workers:** [Gate_00_v1_worker.md](Gate_00_v1_worker.md) and [Gate_01_v1_worker.md](Gate_01_v1_worker.md).\
**Reviewed snapshot:** branch `m00-audit-m01-development`, exact HEAD `c649deea395344c197e33f9628a02a045992dca6`; worker-tested code `e3303000e187e9d03fb0e2fa53d0a22a709feb80`; base `b2e35845f4be7e274cc9d501ec0e020e1d97edac`.\
**Scope/profile:** combined G00-T1, G01-T1/T2/T3 and M01 review on `core-analytic-cpu`.\
**Reviewer:** independent Codex reviewer `/root/m01_review_fallback`, GPT-6 family; exact runtime model/version and reasoning settings are not exposed. This reviewer did not author or modify the implementation. The earlier reviewer failed before performing a review and supplies no evidence.\
**Finished:** 2026-10-01 18:05:18 UTC.\
**Verdict:** `changes_required`.

## Evidence

Read AGENTS, STATUS, G00/G01, the relevant S02 dependency/ownership rules, S03 units/record/error/evolution sections, S04 physical and boundary policy, S07 applicability/provenance/acceptance sections, the CPU guide, worker logs, fixtures and the [M00 analytic design audit](../Milestone_00/Milestone_00_v1_audit.md). Inspected every implemented module under `src/atm_mlmm/` and the applicable tests. Full M00 physical-reference closure remains open and is nonblocking for this review's scope.

All independently executed commands ran at the repository root after `source /workspace/.onboarding/atom-mlmm/activate.sh`. Standalone Python probes additionally used `PYTHONPATH=src`.

| Independent check | Actual outcome |
|---|---|
| `git rev-parse HEAD` and `git status --short` | Exact reviewed HEAD above; initial tree clean. |
| `git diff e3303000e187e9d03fb0e2fa53d0a22a709feb80 HEAD -- src tests fixtures environment` | Exit 0, empty: worker-tested and independently reviewed implementation/test/fixture/environment files match. |
| `python -m pytest -m 'not gpu and not model_assets and not slow' -q` | Exit 0, **34 passed, 1 deselected in 17.24 s**. Includes all applicable G00-T1 and G01 tests. |
| `python /workspace/.onboarding/atom-mlmm/validate.py --repository "$PWD"` | Exit 0, **all nine checks passed**: both exact inventories, both pip checks, OpenMM installation, CPU potentials/native ATM smoke, separate Amber integration, upstream UWHAM and documentation. Output at `/workspace/.onboarding/atom-mlmm/logs/validation-20261001T180432Z-4924/results.json`. |
| Load the saved gzip environment manifest and call `validate_environment_manifest` | Exit 0. Main/Amber inventories contain 156/80 distributions. Source tag/package version separation and deferred model/GPU profiles are explicit. |
| Recompute SHA-256 for each of the saved validation artifact's three fixture entries | Exit 0, all three match; saved code/base snapshot identities match the workers. |
| Additional policy and evidence probes below | Exit 0, reproduced two incorrect admissions. These are findings, not acceptance tests. |

The worker's full-suite 35-pass result was inspected in saved evidence, not independently rerun. The independent analytic suite deliberately deselected the model test. Neither setup smoke nor the existing trusted example qualifies G00-T2, a molecular Hamiltonian, GPU execution or G02+.

Stable real IDs survive permutations, metadata ambiguity has an explicit lookup failure, and complete unequal mobile groups are admitted without a pairing assumption. Partition resolution uses connectivity to complete protein hydrogens and enumerate crossings; tests reject incomplete/disconnected ligands, inconsistent molecule edges, ring/peptide cuts, charged/ambiguous fragments, unknown selected elements, repeated MM cap parents and multiple cuts per component. These are abstract graph fixtures, not chemical-reference qualification.

Owned tuples and protected nested mappings support immutable records; common units, nonfinite/shape errors, schema-version and required-field rejection, exact all-real-force ordering and dependency-light imports have working tests. The original-MM fixture independently distinguishes masses, constraints, box, all admitted bonded force terms, exceptions, nonbonded settings, global parameters and both offset types. Inventory preserves the original serialized System and rejects unknown force classes. Explicit actual-electrostatic, unsupported backend/ensemble/platform/precision/integrator requests reject, and admitted metadata reports `qualified=False`. The two gaps below prevent combined acceptance.

## Findings

| Finding and importance | Evidence/location | Required repair and closure check |
|---|---|---|
| **M01-R1, blocking:** unsupported embedding policy and model semantics are admitted | `capabilities.py:5` checks embedding kind/backend but ignores `policy_version`, `boundary_policy`, `output_energy_convention` and `locality`; their records require only nonempty strings. The probe below returns `passed` for unknown policy version `999`, forbidden boundary names and unsupported model conventions. This conflicts with P0-REQ-023 and S03's early rejection of known incompatibilities. | Explicitly define admitted analytic policy versions/boundary conventions and backend-appropriate model energy/locality semantics. Reject unknown/unsupported values rather than interpreting them under a default. Add focused negative regressions and verify existing analytic requests still pass. |
| **M01-R2, blocking:** whitespace references count as acceptance evidence | `schema.py:AcceptanceRecord._validate` checks tuple truthiness, while `ValidationReport` does not reject blank fixture/log/reviewer-reference entries. A record with all three fields `(' ',)` constructs as `accepted`. This violates P0-TEST-G01-06 / P0-REQ-025: there is no identified input, result log or review reference. | Reject blank/whitespace entries in required acceptance evidence reference fields. Add a negative test for each field independently and together; preserve valid evidence round trips and same-snapshot enforcement. |

### Reproducers

Run with the activation and `PYTHONPATH=src` stated above:

```python
from dataclasses import replace
from atm_mlmm.schema import *
from atm_mlmm.protocols.abfe import make_protocol
from atm_mlmm.capabilities import validate_request

p = PartitionSpec(('a',), (), (), (ComponentState(('a',), 0, 1),))
r = CalculationRequest(
    ModelSpec('analytic-local', None, 'declared_relative_energy',
              ('H', 'C'), 'neutral_singlet', 'local', 'float64'),
    EmbeddingSpec('mechanical', '1', 'protein_c_c', 'nonperiodic'), p,
    make_protocol((MobileGroup('a', ('a',), ('ligand',), 'm'),), (1, 0, 0)),
    RuntimeSpec('Reference', 'double', (), 0.0005, 300, 'NVT'))
c = CapabilitySet(('analytic-local',), ('mechanical',), ('abfe',),
                  ('H', 'C'), ('nonperiodic',), 'all_real', ('json-v1',))
for field, value in [('policy_version', '999'),
                     ('boundary_policy', 'charged_fragment'),
                     ('boundary_policy', 'disulfide')]:
    print(field, value,
          validate_request(replace(r, embedding=replace(r.embedding,
                           **{field: value})), c).status)
for field, value in [('output_energy_convention', 'eV'), ('locality', 'reactive')]:
    print(field, value,
          validate_request(replace(r, model=replace(r.model,
                           **{field: value})), c).status)

report = ValidationReport('P0-TEST-G01-07', ('P0-REQ-003',),
    'core-analytic-cpu', (' ',), {'ok': True}, {'ok': True}, 'passed',
    (' ',), (' ',), 'a' * 40)
acceptance = AcceptanceRecord('G01-T3', 'core-analytic-cpu', 'a' * 40,
    ('P0-REQ-003',), ('P0-TEST-G01-07',), (report,), 'auditor',
    'accepted_for_scope', 'audit.md', 'accepted')
print('Blank evidence admitted:', acceptance.status)
```

Observed output: all five policy/model probes print `passed`; the final line prints `Blank evidence admitted: accepted`. No context or model deserialization is needed to reproduce either gap.

## Decision and handoff

G00-T1 CPU API/provenance evidence and the reviewed identity, selection and inventory behavior are adequate for their stated analytic scope. G01-T2's fail-closed policy validation and G01-T3's evidence validation need the two repairs above; therefore combined G01/M01 is **not accepted** on this snapshot. Preserve this v1 audit and record repairs/tests on a new snapshot and attempt. Independent closure may focus on these findings, the affected tests and the new exact snapshot rather than repeating unchanged review work.

G00-T2 model-asset/loader qualification, G00-T3 hardware qualification and full M00 physical-reference closure remain pending for their owning profiles. No neural chemistry, molecular ABFE/RBFE, actual electrostatic physics, periodic physical evaluation or G02+ qualification is granted. The parent integrator owns STATUS and commits; this reviewer changed only this audit file.
