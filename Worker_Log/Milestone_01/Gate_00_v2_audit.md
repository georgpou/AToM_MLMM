# G00-T2 pinned model asset/loading — v2 independent audit

**Verdict: `accepted_for_scope` for G00-T2, P0-TEST-G00-03/04 and applicable P0-REQ-014/029 only**, on exact frozen **`a7768e375476667139db374dc0091999263a37de`**, from accepted G04 base `bc788aeeedb4dc45026ac1bff44bd4fb533b325a`. This asset/loading acceptance does not accept a molecular gate, chemical profile or GPU.

**Worker:** [Gate_00_v2_worker.md](Gate_00_v2_worker.md). **Reviewer:** independent Codex `/root/g05_software_audit_v1_r2`, dispatched as actual gpt-6-astra/high/fresh context according to the assignment; backend build not exposed. **Date:** 2026-10-03 UTC, exact command times in [review evidence](../Milestone_03/evidence/G05_v1_independent_r2/README.md). Source was read and tested in clean detached `/workspace/AToM_MLMM-g05-review-v2`; the live implementing tree was not reviewed. No implementation, repair, delegation or commit was authored.

## Evidence and decision

The exact bundled MACE-OFF23-small bytes have SHA-256 **`165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f`**. The loader verifies the retained bytes before passing those same bytes to explicit `torch.load(weights_only=False)`, checking the academic authorization record, separately pinned checkpoint licence and provenance, file sizes/digests, CPU, float64 and total-energy settings. Missing/wrong assets, absent authorization, wrong licence and incompatible manifest policy reject. A deserialization sentinel verifies authorization is checked first. No replacement download or global torch.load monkey-patch is used.

**P0-TEST-G00-03 passes:** asset, licence, exact manifest and policy rejection cases ran in the resumed review. **P0-TEST-G00-04 passes:** fresh-process actual calculator loading ran with DNS/connect denied and empty caches; tensor dtype, architecture, Default head and unit settings match. Initialized PyTorch safe globals are unchanged by the loader, the upstream unsafe environment override is cleared, and an arbitrary untrusted full-module pickle still rejects under default loading. The narrowly scoped e3nn `slice` allowance is not left globally active.

Actual characterization is ScaleShiftMACE, 4.5 Å edge cutoff, two interaction layers, 96 scalar embedding channels, eight Bessel functions, polynomial cutoff order 5, and the recorded ten checkpoint elements. Candidate application metadata deliberately narrows this to neutral closed-shell C/H/N/O; that declaration is not accuracy evidence. Both native and adapter use `energy` including atom-reference energies, never reinterpret `interaction_energy` as a ligand/protein interaction decomposition. Independent measurements confirm ASE factors 96.48533288249877 kJ/mol/eV and 964.8533288249877 kJ/mol/nm per eV/Å.

The focused resumed run comprises **29 passes, exit 0** across model/loading/environment/admission/metric files (`software.json`). It includes both stable G00-T2 assertions. The same run also reloads moved trusted physical and ATM artifacts through the inert pinned loading recipe, denying original checkout paths and networking; all three ATM states reproduce identity, energy and full real forces. Details and six G05 software decisions are in the [G05 audit](../Milestone_03/Gate_05_v1_audit.md).

Main activation was `/workspace/atom-mlmm-g05-v2/activate.sh`, Python 3.11.16, NumPy 2.4.6, torch 2.8.0, mace-torch 0.3.16, ASE 3.29.0, OpenMM 8.6.1/OpenMM-ML 1.8, two threads. Exact environment API/inventory assertions reran; Amber remains separate. Snapshot verification matches all **269 submitted source/input hashes**, **333 protected inherited files** and **48 exact M00 design files**. Models, licence, locks and old evidence are preserved.

The earlier independent reviewer was quota-interrupted without a verdict. Its same-snapshot strict capture, **9/9 checks, exit 0**, is retained and attributed as prior independent evidence, not a run by this resumed reviewer. Its full-suite result is **285 passed / 2 missing-quantum failures**, analytic **265 passed / 22 deselected**. No successful model install is interpreted as chemical qualification.

## Handoff and limits

No blocking finding remains for this G00-T2 asset/loading scope. The prepared T4 loader has a separate approval-to-plan provenance defect, **G05-v1-R1**, reproduced and left open on this exact snapshot in the G05 audit. Full G05, quantum-reference execution/comparison, physical/chemical qualification, GPU and broader workflows remain pending. The accepted M00 v3 design still requires explicit user agreement; this review provides none.
