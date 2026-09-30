# M00 shared architecture review — attempt 1 — worker

**Scope:** Full combined design review in M00; S01–S07 scientific contract version 1, requirement ownership P0-REQ-001–032. Repository metadata and cloud setup are implementation follow-up, not numerical acceptance.\
**Outcome:** ready_for_audit.\
**Model/version:** GPT-6 family (Codex); exact model version not exposed.\
**Reasoning setting:** not exposed.\
**Finished:** 2026-09-30T17:59:30+00:00.\
**Previous worker/audit:** none for the Milestone_00 design-review stem.

## Snapshot and references

Branch `M00`, base and reviewed specification snapshot `2d7bcc94f901738e39f536f16de84699d4e8d631`. Reviewed AGENTS.md, M00, S01–S07, REQUIREMENTS.md, STATUS.md, G00 and the complete environment note/YAML. [Reviewed file hashes](evidence/Milestone_00_v1/reviewed-files.json) identify the inputs independently of later metadata/report changes. Historical plans are context, not authority. No previous accepted design review or numerical evidence exists.

## Changes and decisions

Submit the existing composition for review: physical builder owns retained-MM/model/coupling physics; protocol owns maps and result meaning; ATM consumes their outputs; AToM adapter alone translates upstream classes, keys and units. Basic records import without a neural backend. Accepting this design cannot qualify an installed combination, real checkpoint, hardware or actual electrostatic Hamiltonian.

Public contracts have explicit nm, kJ/mol, kJ/mol/nm, ps, K units; negative-gradient forces for every influencing real atom; fixed identities/membership; full final-particle maps including undisplaced caps; and versioned schemas rejecting unknown mandatory semantics. Corrections have explicit obligations/statuses; unresolved obligations withhold final standard binding values. Force terms have one owner and must be active during preparation and production. Starting S06 tolerances remain proposed numerical limits requiring profile characterization, never relaxation to hide errors.

Future-change walkthrough 1: an environment-dependent energy changes its embedding/model provider, capability record and provider-specific tests. The provider returns derivatives on MM atoms and rebuilds geometry-dependent inputs under each map. Common ATM, protocol, raw-observable and binding-analysis interfaces remain unchanged if the existing state/coordinate contract suffices. G02's MM harmonic probe and G04/G07's parent/environment checks expose missing derivatives and stale descriptors. A real electrostatic implementation additionally requires a scientific specification and new qualification; no physical theory is approved by this walkthrough.

Future-change walkthrough 2: two unequal/noncontiguous mobile groups change protocol validation, endpoint descriptions, maps, restraints/correction obligations and upstream adapter selection. The same physical builder and ATM assembler consume full maps; no atom-pair correspondence or one-ligand branch enters common physics. G01 collection/map tests and G02/G03 one-/two-group controls expose violated boundaries. G12 remains molecular RBFE qualification, not a new core engine.

REQUIREMENTS.md assigns all 32 IDs to an owning specification/gate. G00 owns source/build/asset provenance; G01 identities/schemas; G02–G03 composition/routing; G04–G07 links/model/periodic integration; G08 thermodynamics; G09–G10 workflow/reload; G11–G13 molecular/performance admission. Candidate dependencies are installation hypotheses: OpenMM 8.6.1, OpenMM-ML 1.8, AToM source v8.5.0, CPU Torch 2.8.0, MACE 0.3.16/e3nn 0.4.4. Source tag and package-reported AToM version must remain distinct. No checkpoint/license approval is implied.

## Checks

| Check | Command or method | Result |
|---|---|---|
| Base identity | `git rev-parse HEAD` in repository root | `2d7bcc94f901738e39f536f16de84699d4e8d631` |
| Baseline documentation | `python tools/check_docs.py --self-test` | Exit 1: two links to absent `scientific-amendment-source-checks` heading; all deliberate-error self-tests passed. Repair tracked separately in setup work. |
| Combined M00 contracts | Read S01–S07 and requirement ownership; two paper walkthroughs above | Submitted for independent review; no numerical tests performed |

## Findings and next handoff

Independent reviewer must decide full M00 scope in `Milestone_00_v1_audit.md`, including any unresolved force/map/unit/correction conflicts. G00-T1 may advance only after that relevant design review. Model assets and GPUs are unavailable/unapproved for this assignment and remain unqualified. No molecular engine, sampling result or numerical gate pass is claimed.
