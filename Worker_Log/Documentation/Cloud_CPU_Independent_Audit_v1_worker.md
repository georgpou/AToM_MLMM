# Independent CPU-baseline audit delivery - attempt 1 - worker

**Scope:** Execute the user's independent reproduction v2 setup/baseline audit and deliver evidence, findings and a concrete repair assignment. No gate implementation or production repair.\
**Outcome:** `ready_for_audit` for this reporting delivery; the substantive independent audit verdict on reproduction v2 is `changes_required`.\
**Model/version:** Codex, GPT-6 family; exact served version not exposed.\
**Reasoning setting:** not exposed.\
**Finished:** 2026-10-01T15:00:33.469899+00:00.\
**Previous worker/audit:** [Submitted reproduction v2](Cloud_CPU_Reproduction_v2_worker.md); this assignment produces its [independent sibling audit](Cloud_CPU_Reproduction_v2_audit.md).

## Snapshot and references

Branch `m01-g00-environment-audit-v1` starts exactly at latest fetched setup tip `28f89cb23bdb7081c3723b9794fbde7d9bb50dca`, not main. The submitted worker is `dcfd99d51e991f0cf6f838b81f2f14752b0a9afa`, with artifact ancestor `be26b7c25e9a30f67f6d3a884001084fa710bd8c`. The current audit/report delivery commit is the commit adding this file; identify it with `git log -1 --format=%H -- Worker_Log/Documentation/Cloud_CPU_Independent_Audit_v1_worker.md`. The [delivery manifest](evidence/Cloud_CPU_Reproduction_v2_audit/delivery-manifest.sha256) covers changed/new reporting files, excluding itself; the [inherited manifest](evidence/Cloud_CPU_Reproduction_v2_audit/inherited-files.json) covers all original 204 tracked files.

Read both uploaded assignment files and every task-specific document/artifact listed in the audit. Used systematic debugging, managed cloud runtime guidance, and verification-before-completion; supplied assignment/template format controls the reporting style. No external writing sample was required. Linux x86_64, two threads, 8 GiB memory limit; no pretrained weights, simulation, Docker, global package changes or extra agents.

## Changes and decisions

Added the real independent sibling audit, raw/structured evidence and audit-only reproduction probes. Added [NEXT_AGENT_REPAIR_HANDOUT.md](../../NEXT_AGENT_REPAIR_HANDOUT.md). Updated STATUS and root AGENTS/README/handoff pointers to actual findings and the repair predecessor. The original setup scripts, package locks/wheels/source archives, candidate YAML, scientific specifications and every submitted historical log remain byte-identical. No scientific/specification amendment was performed.

A01 records 18 missing historical documentation deliveries; A02 distinguishes low runtime impact from genuine missing source provenance; A03 reproduces the calculator import's unsafe-loading override. A04 is closed as nonblocking for CPU; A05 retains the historical unknown while current success/failure propagation passes; A06 administrative reporting is updated. A scratch-only second cleanup demonstrated the smallest A03 repair but was not applied to production or independently approved.

## Checks

The independent audit contains exact commands, profiles, statuses and findings. [Command records](evidence/Cloud_CPU_Reproduction_v2_audit/commands.json) and four preserved validation JSONs record the executed fresh, strict, replay and Cloud runs. All eight environment checks pass; docs exit 1 for the same two anchors with eight self-tests passing. The original loading-policy regression exits 1 for its intended postcondition; scratch candidate exits 0. All five controlled artifact failures return 1 before installation, with original checkout/artifact preservation. All 51 wheels and three upstream source archives are independently verified. Final documentation/preservation/report consistency checks are recorded in the evidence folder before commit; no entire scientific gate test command was run.

## Findings and next handoff

The user specifically asked whether the anchors are trivial legacy bookkeeping. They do not affect CPU calculations, but the target heading/source records were never delivered, and 17 other documentation files also matched before hashes at the audited parent. They are not evidence of an environment failure or mere folder renaming. Repair the genuine source record once as part of A01 and retain the nonblocking CPU dispositions without repeated speculative work.

Continue on a child of this audit branch, suggested `m01-g00-environment-repair-v3`, with next unused reproduction v3/documentation v5 records after reservation checks. Independent review is required for the actual repairs. No M00/G00, pretrained loading or GPU acceptance is claimed. The clean baseline remains incomplete for A01-A03; no remaining package/network installation blocker was observed on this host.
