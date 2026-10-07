# Before HPC audit fixes v1

One gpt-6-luna/max worker implemented the five findings from the independent A–E audit. The worker ran alone, with no nested agents or new audit. This is an implementation and focused-test handoff, not independent acceptance of the patch.

Branch: `before_HPC`. Base: `a78af5ce9c74f09c8ddeba373187c99a7f72035b`. Implementation commit: `4887cc40b56e29bfd0760e487b1ebe5b110eefb3`; source tree: `9181b18a10900f17badc5b21eee2b1ea7bc4bc64`; tests tree: `da52a0df1acad7f0550198db14ba264742762855`.

| Finding | Implemented behavior |
|---|---|
| F1: independent-run provenance | Persistent initialization identities use verified initial states, integrator seeds, runtime identity and initial host RNG evidence. Renamed IDs or narrative claims cannot distinguish duplicate initialization streams. The journal format and public analysis API remain unchanged. |
| F2: HPC admission | Typed declarations, positive resources, storage/checkpoint safeguards, verified bundle bytes and matching artifact identities are required before the dry-run ready status. The CLI consumes an actual bundle directory. No cluster job was run. |
| F3: source inventory | Declared, current and recursively enumerated bundled Python files must agree. Undeclared files and symlinks reject; relocation remains supported. |
| F4: solvent force ownership | Every preparation stage must include each declared force owner exactly once. Empty and partial owner sets reject. |
| F5: protein declarations | Explicit nonperiodic boxes, empty constraints and zero cuts are distinguished from absent decisions. Admission remains input-only. |

The worker also fixed the newly exposed immutable-provenance comparison on the complete-input path and replaced STATUS's stale “pause before Batch B” instruction. Details, interface changes and original failing controls are in [the worker report](Audit_Fixes_v1_worker.md). The [independent audit](Before_HPC_Audit_v1.md) remains unchanged and records its original reviewed snapshot.

The final bounded compatibility run passed **27 tests, zero skipped, exit 0, 10.00 seconds**, at 19:32:25–19:32:36 UTC. It covers producer-to-analyzer duplicate initialization and distinct-state/RNG controls, existing synthetic uncertainty guards, persistent loading, recursive source inventory, HPC CLI/profile semantics, and protein/solvent admission. Counts from isolated runs overlap and are not added. The exact command and output are retained in [compatibility-002.log](evidence/audit-fixes-v1/compatibility-002.log).

New worker test logs had trailing whitespace normalized before commit; they are text evidence rather than byte-exact stdout captures. Historical/sealed evidence was not changed. Final identities confirm all 386 supplied files and the original independent audit are unchanged, no source/tool/test/input delta exists after the implementation commit, and the original checkout remains clean. The final documentation self-test passed with zero errors across 278 Markdown files and 1,740 local links. Final source/file identities and documentation/whitespace checks are recorded in `evidence/audit-fixes-orchestration-v1/`.

The earlier full suite remains unresolved after its SIGKILL/OOM evidence; no full-suite replay occurred. These focused passes do not establish whole-suite or whole-milestone acceptance. C3's physical-endpoint comparison/refusal contract remains open, along with physical preparation, applicable AToM corrections, sampling/covariance qualification, G07/QM obligations, cluster/storage/GPU trials and licensing/offline reproduction. Existing wheels and bundles predate this patch; they were not rebuilt or relabeled as current-source artifacts.

No production sampling, QM, cluster/GPU work, dependency reinstall, remote publication or second audit occurred. Implementation is finished for the five findings; stop after reporting and await further instructions.
