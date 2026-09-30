# M00 shared architecture review — attempt 1 — audit

**Worker log:** [Milestone_00_v1_worker.md](Milestone_00_v1_worker.md).\
**Audited scope:** Full combined M00 design review; S01–S07 scientific contract version 1; requirement ownership P0-REQ-001–032; both future-change walkthroughs.\
**Snapshot:** Branch `M00`, reviewed source commit `2d7bcc94f901738e39f536f16de84699d4e8d631`, with the worker report and [reviewed input manifest](evidence/Milestone_00_v1/reviewed-files.json). Source hashes below distinguish this decision from subsequent setup, report and STATUS changes.\
**Reviewer:** Independent review agent `/root/m00_review`, separate from the worker; actual model/version and reasoning setting: not exposed.\
**Finished:** 2026-09-30T18:06:07+00:00.\
**Verdict:** accepted_for_scope.

## Independent checks

Read AGENTS.md, M00, STATUS.md, REQUIREMENTS.md, S01–S07, the complete environment guide/YAML, and G00–G08. Inspected the worker report and independently verified its 13 input hashes against both the source commit and working files. No earlier independent M00 acceptance exists. Historical Documentation v1–v4 logs do not establish accepted design or numerical evidence.

### Reviewed revisions

All entries below identify source content at the reviewed commit. S01–S07 retain scientific contract version 1. This audit records their M00 design approval; it does not turn their proposed numerical thresholds into measured qualification.

| Reviewed source | SHA-256 |
|---|---|
| `AGENTS.md` | `08eb4eca7750b124e340a17968934e850f1349512a6c6f5e30944b0c696616a6` |
| `docs/project-0/milestones/M00-architecture-review.md` | `ff40d5c164ac35534ec22d7271479b0bb67be3e9ad58016ce801e3b044b72f57` |
| `docs/project-0/STATUS.md` | `e222085b8b02dd72a570268bfcd910a508bb6b33a032c1c66897d6ef3d0cd67a` |
| `docs/project-0/REQUIREMENTS.md` | `f62a917f6a5d5b496b5b08d695347a5f233d8799f02e5e7a81236000820292df` |
| `docs/project-0/specs/S01-scope-and-invariants.md` | `b739d643382231f35e2a32dcdd5807b7ac2f8a116a9bd5919261b95fccd261c3` |
| `docs/project-0/specs/S02-architecture-and-dependencies.md` | `acf039741c8fa66a4833367f6f81cfcc013e0d263177ef2c2104714709c036d1` |
| `docs/project-0/specs/S03-data-and-interface-contracts.md` | `1fbb01d02e97c85b4581e136860f01a7437b7d6aefcb17284ea099183d4de95b` |
| `docs/project-0/specs/S04-embedding-and-model-contracts.md` | `b562bfe92893e947bdeba2fe2f3b0ebf93b201e2622d84b1155a13a1bc90a7f9` |
| `docs/project-0/specs/S05-protocol-and-thermodynamic-contracts.md` | `e8efb215eef544023adfdc4f4d37761878e4e3d95bb72d909f8e727565fc5773` |
| `docs/project-0/specs/S06-validation-and-tolerances.md` | `9077a689e53c1e8f396365a8867b2aff9f7964735783fb3519b6b110551f6d4f` |
| `docs/project-0/specs/S07-artifacts-and-qualification.md` | `e32cb13f4bf1d6bac8a2a02d4d7280e255f0663372d194126c9677fde24a779f` |
| `ATM_MLMM_Environment.md` | `7028fdf9f1b037e2f0947c512de93b5ecde84d8f2a3341d95c73d64829673504` |
| `ATM_MLMM_environment.yml` | `9e164133a7446268606e555276da600382ddbd4216b9b521676e33fba2eb55d7` |
| `docs/project-0/reference/sources.md` | `b9cc660a894c3847ff471d91d76f27159ab50b954da7ee24bcb69af2a03ffff3` |
| `docs/project-0/gates/G00-environment-and-provenance.md` | `71941a0f17f684f52669c312b73940a4368ae270f5aff4f6d4ebdc75e06dce1a` |
| `docs/project-0/gates/G01-identity-partition-and-contracts.md` | `b8eb455384b1ef78c5237f8b63c054d1e1d9d74c1371eb62d124e949d87b75d5` |
| `docs/project-0/gates/G02-analytic-force-in-native-atm.md` | `0fe0fcd885628dbfdfe6833fa6afb8ea77e61e3183d3ce6acbf2c5efba990e20` |
| `docs/project-0/gates/G03-atom-routing-and-integration.md` | `40f5304191ead4454690bef7c843fee1e65646f6daf9bff20a06e9fbcd46119e` |
| `docs/project-0/gates/G04-link-boundary-and-derivatives.md` | `aa4d8e58b344d605f827e08f80acbba38eca908a41fcd73d0d4be912d8eae6f6` |
| `docs/project-0/gates/G05-local-model-adapter.md` | `a88ab372aa863ffcc794b8664aef61999787837bc68e61481c8d84e57918730b` |
| `docs/project-0/gates/G06-periodicity-and-interaction-ledger.md` | `c48e1a80aaff23600912f0216a3293c176242f067f4a5ccd91240b0bd0af1001` |
| `docs/project-0/gates/G07-joint-cavity-ligand-atm.md` | `f0b692e947e935c891011d109ccc34535cb80720c779f9f704bf486a6c35ed71` |
| `docs/project-0/gates/G08-thermodynamics-and-estimators.md` | `e45921db13deca87810546e5d8f395b46018ea2e13afe552e9e3df83f6669369` |

### Combined contract decision

S02's physical-builder, protocol, shared-ATM and AToM-adapter ownership agrees with S03's signatures and S04/S05's energy and thermodynamic meanings. ADR-0001 and ADR-0002 are accepted as design decisions. No amendment of force, map, unit or correction semantics is needed for this scope.

The physical builder owns retained-MM/model/coupling terms and their ledger, without protocol or bound/bulk energy branches. Protocols own complete mobile groups, endpoint geometry and observable/correction meaning. The common assembler consumes two full final-particle maps and physical energy/derivatives. The adapter contains upstream classes, group keys and unit conversion. Dependency-light records and forbidden imports have assigned structural tests; behavior tests prevent static imports alone from claiming independence.

Full-real-force semantics include influencing MM atoms and both cap parents. Sparse adapter forces must be scattered and validated before the common API. Virtual sites have no independent thermal coordinate; the parent Jacobian is mathematically consistent and redistribution must occur once. Fixed ML membership, complete ligands, zero explicit cap displacement, ordinary dynamic parent motion, nonidentity index-map consumption and unchanged masses/constraints across states agree across S01, S03–S05. Actual nested virtual-site propagation remains a G04/G07 test obligation, not an assumed runtime success.

Units and negative-gradient signs are explicit. S03's schema evolution rejects incompatible/unknown mandatory semantics. S05 and S07 keep raw child, softened perturbation, ATM expression, outside and total energies distinct. S05's bound-minus-bulk standard-state sign and directional bridge algebra are internally consistent. Missing correction obligations prevent a final standard binding result; sampling and covariance cannot supply an absent definition.

The initial neutral local/mechanical, fixed-volume NVT and orthorhombic boundaries are explicit. S04/G04–G06 require an exact retained/removed boundary ledger, measured cap parameters, declared periodic reconnection and consistent mask/background settings before molecular qualification. This design approval does not preapprove unmeasured builder predicates, a universal cap distance, all image seams, dispersion changes or a numerical PME correction. Unsupported chemistry, maps and force classes must fail explicitly.

### Independent future-change walkthroughs

| Change | Modules that change | Modules/interfaces that remain common | Assigned guards |
|---|---|---|---|
| Environment-dependent physical energy | New/revised `embeddings/*`, compatible `models/*`, builder dispatch, capability/profile declarations and provider tests; any genuinely new state inputs need a reviewed schema extension | `protocols/*`, `geometry.py` fixed translation contract, `atm.py`, `RawAtmEnergies`/`AtmEvaluation`, shared reduced-potential analysis and correction assembly | G01 dependency/capability tests; G02-05/06/07 full MM derivatives, mapped reevaluation, A-B-A and fault injection; G04-06 cap/environment derivatives; G07-05 integrated substitution |
| Two unequal, noncontiguous mobile groups | `protocols/rbfe.py` group validation/maps/endpoint weights, restraint and correction configuration, `adapters/atom.py` upstream selection, fixtures/profile evidence | `build_physical`, provider energy definition, shared `build_atm`/evaluators, full-real force ordering and raw records; no common atom-pair correspondence or ligand-count physics branch | G01-02/03/04 complete groups/schema/imports; G02-04 same assembler and unequal IDs; G03-04/05 both upstream paths/units; G07 extension regressions |

Both walkthroughs preserve the same physical definition at both maps. Environment inputs must be rebuilt at mapped geometry, including an unchanged MM coordinate's changed derivative. The proposed PythonForce subset optimization cannot keep an ML-only subset when the provider needs MM coordinates. Actual electrostatic field, response, polarization convergence and periodic physics require a separate scientific specification and qualification. Two-group analytic support cannot qualify molecular RBFE.

### Requirement ownership, tolerances and dependencies

REQUIREMENTS.md and the owning gate tables cover all 32 active requirements; an independent scan found every ID referenced by an acceptance row and 82 unique planned test IDs. This is ownership coverage, not executed evidence. Module ownership follows S02: G00 provenance; G01 identities/schemas/capabilities; G02 common endpoints/full derivatives; G03 routing/active groups/adapter; G04 caps; G05 model/native references; G06 periodic ledger; G07 combined composition; G08 thermodynamics; G09 preparation/export; G10 restart/workers; G11/G12 molecular protocols; G13 performance/release evidence. Cross-gate requirements retain their shared acceptance obligations.

S06's exact structural equality, absolute analytic/double-precision errors, finite-difference step convergence and statistical known-answer criteria are accepted as starting validation policy. Profile precision/noise must be characterized and final thresholds frozen before numerical acceptance. Force components and boundary errors must not be hidden by aggregate protein energy or RMS statistics. No limit was relaxed here.

The candidate OpenMM 8.6.1, OpenMM-ML 1.8, AToM source v8.5.0, CPU Torch 2.8.0, MACE 0.3.16/e3nn 0.4.4 combination is accepted only as a G00 experiment input. AToM source/package identities remain distinct; tags must resolve to exact installed commits. G00 must solve and lock the actual builds, check APIs and pip consistency, and test approved executable assets when applicable. No upstream availability, complete compatibility, checkpoint license or loader success is established by this audit. Basic analytic work requires neither model weights nor GPU; model-loader tests are nonapplicable to that narrower scope and cannot be counted as passes.

### Commands and observations

Working directory for all checks: `/workspace/scratch/c125c57e3282/AToM_MLMM`; current shell Python with standard library only. No molecular environment was installed or qualified.

- `git rev-parse HEAD`, `git branch --show-current`, `git status --short`: exit 0; base `2d7bcc94f901738e39f536f16de84699d4e8d631`, branch `M00`, initially clean scientific sources; later untracked worker/evidence reports only.
- `python tools/check_docs.py --self-test`: exit 1; exactly two missing source-register anchors, recorded in A01. All eight documentation-checker self-tests pass. External sources were counted, not fetched.
- `sha256sum docs/project-0/gates/G0*.md Worker_Log/Milestone_00/Milestone_00_v1_worker.md`: exit 0; source revisions above. Worker completion metadata was corrected before submission to `2026-09-30T17:59:30+00:00`; final inspected worker SHA-256 `8f2f7d3d40f6bf9dc35a24af3cc1320ed691ff292b2346cad836a879b382b3f2`. This report metadata correction does not alter reviewed source content.
- A subsequent `python tools/check_docs.py --self-test` after the worker's separate source-register/setup changes exited 0: no documentation errors; all eight self-tests pass. Those setup changes are not scientific implementation evidence or a different reviewed S01–S07 contract snapshot.
- The following exact independent standard-library check exited 0 and reported `13 source hashes match base; 32 requirements covered by 82 unique planned tests; scalar oracle identities verified. No runtime qualification.`

```bash
python - <<'PY'
from pathlib import Path
import hashlib,json,re,subprocess
base='2d7bcc94f901738e39f536f16de84699d4e8d631'
manifest=json.loads(Path('Worker_Log/Milestone_00/evidence/Milestone_00_v1/reviewed-files.json').read_text())
for path,digest in manifest['sha256'].items():
 data=subprocess.check_output(['git','show',f'{base}:{path}'])
 assert hashlib.sha256(data).hexdigest()==digest,path
 assert Path(path).read_bytes()==data,path
ids=set(re.findall(r'P0-REQ-\d{3}',Path('docs/project-0/REQUIREMENTS.md').read_text()))
rows=[line for p in Path('docs/project-0/gates').glob('G*.md') for line in p.read_text().splitlines() if line.startswith('| P0-TEST-')]
assert ids==set(re.findall(r'P0-REQ-\d{3}','\n'.join(rows)))
assert len(rows)==len({line.split('|')[1].strip() for line in rows})
from math import isclose
assert isclose(.5*100*50/(100+50)*.3**2,1.5,abs_tol=1e-14)
assert .5*100*0/(100+0)*.3**2==0
for m,e,E,F in ((.2,.5,.45,3.),(.3,.5,.20,2.),(.2,.6,.80,4.)):
 assert isclose(.5*10*(m-e)**2,E,abs_tol=1e-14)
 assert isclose(-10*(m-e),F,abs_tol=1e-14)
F0,F1,Fplus,Fminus=1.,4.,7.,9.
assert (Fminus-F1)-(Fplus-F0)-(Fminus-Fplus)==F0-F1
print(f'{len(manifest["sha256"])} source hashes match base; {len(ids)} requirements covered by {len(rows)} unique planned tests; scalar oracle identities verified. No runtime qualification.')
PY
```

These scalar checks independently corroborate stated examples and bridge algebra; they do not exercise an implementation of the proposed numerical APIs. No OpenMM/MACE/AToM energy or force test, scientific reference calculation, environment solve, checkpoint load, GPU test or sampling run was performed. Those gates remain unrun.

## Findings

**A01 — optional for M00 design acceptance; documentation maintenance needed for setup.** The reviewed `ATM_MLMM_Environment.md` and historical `Documentation_v4_worker.md` link to a nonexistent `docs/project-0/reference/sources.md#scientific-amendment-source-checks` heading. The independent checker reproduces both failures. The active register has U01–U39, while the guide refers to U40/U41 and an amendment source check. Historical Documentation v4 additionally describes P0-REQ-033/reference additions absent from this source commit. Expected: provenance links resolve and current claims identify actual source content. Smallest repair: separately reconcile the current guide/register against verified provenance while preserving historical submitted logs; never fabricate completed source checks or adopt absent amendments. Regression: `python tools/check_docs.py --self-test`, plus inspection that restored provenance claims are supported. Closure: no missing anchor and accurate current source records. This is not a force/map/unit/correction conflict; it does not block G00 investigation or M00 acceptance. No historical chemical-reference claim is imported into this decision.

After this review's source snapshot, the worker added the missing source-register heading; the later checker run confirms anchor closure. The historical v4 verification record describes a register edit but does not itself contain U40/U41 raw observations. The worker was asked to preserve that distinction in the separately repaired provenance wording. Source-register/setup changes and their acceptance belong to that separate record.

No blocking or required repair was found in the reviewed M00 public contracts.

## Accepted scope and next action

Accept the full combined M00 design scope on the exact source revisions above, including ADR-0001/0002, module/requirement ownership, full-real derivatives, fixed complete maps/membership, units/schema/correction contracts, two future-change walkthroughs, starting tolerance policy and candidate-dependency investigation boundaries. This is design acceptance only. It provides no scientific/model, GPU, actual electrostatic or numerical runtime acceptance.

G00-T1 setup for `core-analytic-cpu` may proceed. Its next worker handoff is `Worker_Log/Milestone_01/Gate_00_v1_worker.md`, with matching independent audit after actual environment/source/API evidence. G01 follows its feature-applicable G00 evidence. Later numerical gates, exact boundary/periodic decisions, real-model chemical-reference admission and molecular claims retain their own prerequisites and tests. Metadata/CI work does not count as those tests.

The warranted STATUS change is M00 `accepted`, linking this worker/audit pair and the reviewed source commit, explicitly labeled design-only. G00 and all numerical/model/GPU profiles must retain their actual unrun/unqualified status until evidence exists. A01 belongs to the separate setup/documentation repair record. No new M00 repair attempt is required unless a relevant contract changes or this review's scope is reopened.
