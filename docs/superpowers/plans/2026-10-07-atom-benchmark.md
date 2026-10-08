# AToM benchmark and cluster cleanup implementation plan

**Goal:** Supply a small, reproducible protein benchmark and reuse pinned AToM
preparation and production APIs with the existing capped mechanical ML/MM builder.
**Architecture:** Keep AToM translations in `adapters/atom.py`, molecular input
conversion in `protein_input.py`, and file/stage orchestration in
`benchmark_workflow.py`. Keep outputs outside versioned inputs. Historical runs
remain reproducible from the exact predecessor commit.
**Spec:** The user's benchmark/automation/cleanup request and the unchanged S01,
S03, S04 and S05 contracts. This is workflow implementation, not a new physical
qualification or a request to launch production sampling.

## Constraints and review focus

- Base: `before_HPC`, `590cb5258696042b29856df37f6053ba820d2f56`.
- Pin AToM v8.5.0 / distribution 8.5.0b0; preserve environment locks/model bytes.
- Complete neutral ligands; fixed neutral protein side chains; C-C cuts only.
- Same hybrid energy during preparation and production; every force active once.
- Preserve fixed volume, source/input hashes, failed attempts and physical holds.
- Review partial preparation, tampered inputs, atom remapping, force masks and
  upstream restoration after an adapter exception.

## Tasks

1. Curate FKBP12 BUT/PRP/neutral-DAP inputs from the pinned AToM example, with
   ligand chemistry, source/licence hashes and references. Validate the input
   manifest without importing molecular dependencies.
2. Add focused failing tests for dependency-free planning, tamper rejection,
   neutral/whole-ligand selection and stage prerequisites. Implement the smallest
   immutable job planner and CLI under `scripts/`.
3. Test the stock preparation mask against an actual nonzero additional force.
   Add the narrow AToM adapter: MM system construction, shared hybrid builder,
   full force mask in preparation, fixed-volume barostat and unchanged upstream
   production scheduler. Verify nested ownership and complete ligand maps.
4. Retire historical generated run directories and obsolete plan artifacts from
   the working tree. Keep active scientific/reference fixtures, approvals, budgets,
   environment replay artifacts and model bytes. Replace retired local Markdown
   links with exact predecessor GitHub links; document recovery.
5. Run focused checks, the available CPU suite, documentation checks and a final
   review. Record outcomes, unavailable tests and current holds in STATUS and one
   worker log. Do not push, merge, run QM or submit a cluster allocation.

Execution is inline under the user's authorized scope. Record implementation
decisions and actual verification in the task worker log instead of adding a
second live status index.
