# Batch D evidence index

This evidence belongs to the serial `gpt-6-luna/max` D worker on `before_HPC`.
`capture-command.sh` records each exact argv, UTC interval, base HEAD, source
patch identity and file hashes, activation script SHA-256, prescribed thread and
memory settings, exit code, pytest counts, and log path in its matching JSON
receipt. No adequacy sampling, protein-target calculation, or independent audit
was run.

The preserved test history is:

| Receipt stem | Result | Finding or scope |
|---|---:|---|
| `red-focused-attempt1` | 1; 8 failed | Expected RED before the D interfaces and fixtures existed. |
| `generate-host-guest-fixture` | 0 | First deterministic fixture generation. |
| `green-focused-attempt1` | 1; 3 failed, 5 passed | Test incorrectly equated unequal ligand atom arrays; used a stale fifth `build_atm` argument; and the checker rejected a legitimate sibling fixture path. |
| `green-focused-attempt2` | 1; 2 failed, 6 passed | Test still needed explicit per-atom displacement broadcast and the schema's `displacement1_nm` field. |
| `green-focused-attempt3` | 0; 8 passed, 0 skipped | First complete focused host/protein-input pass. |
| `green-protein-abfe-controls` | 1; 1 failed, 2 passed | Harness compared real-particle masses to a cap-extended system; changed to compare mapped real masses and separately assert zero cap masses. |
| `green-protein-abfe-controls-attempt2` | 0; 3 passed, 0 skipped | Corrected real/cap particle comparison. |
| `generate-host-guest-fixture-attempt2` | 0 | Regenerated after the frozen run-definition content changed. |
| `final-focused-host-protein-inputs` | 0; 9 passed, 0 skipped | Focused command before importer declaration tightening. |
| `final-focused-host-protein-inputs-attempt2` | 0; 9 passed, 0 skipped | Focused command after importer declaration tightening. |
| `final-protein-abfe-structural-controls` | 1; 1 failed, 2 passed | Harness used a guessed cap field name; schema field is `final_particle_index`. |
| `final-protein-abfe-structural-controls-attempt2` | 0; 3 passed, 0 skipped | Bounded structural-control and correction-ledger nodes. |
| `final-protein-abfe-structural-controls-attempt3` | 0; 3 passed, 0 skipped | Rerun after complete-target manifest contract changes. |
| `generate-host-guest-fixture-final` | 0 | Final deterministic fixture generation including the blocked ABFE/RBFE closure declaration. |
| `final-focused-host-protein-inputs-attempt3` | 0; 9 passed, 0 skipped | Required focused packet command on the final generated host fixture. |
| `final-protein-abfe-structural-controls-attempt4` | 0; 3 passed, 0 skipped | Bounded protein nodes on the final generated fixture/source tree. |
| `generate-host-guest-fixture-parameter-route` | 0 | Final regeneration sealing prepared-mm-v1's digest and exact missing-crown parameter limitation. |
| `final-host-guest-parameter-route-controls` | 0; 4 passed, 0 skipped | Entire affected host–guest test file on the final parameter-route metadata. |

The exact runnable test commands are preserved in the receipts. Every shell ran
from `/workspace/AToM_MLMM-before-HPC`, sourced
`/workspace/before-hpc-cpu-v2/activate.sh`, and set the two-thread BLAS/OpenMP
profile and repository `src` path. The focused command was:

```bash
python -m pytest tests/workflow/test_host_guest_rbfe.py tests/workflow/test_protein_input_admission.py -q
```

The required focused packet command passed 9 tests, 0 skipped in 21.98 s. The
bounded protein structural controls passed 3 tests, 0 skipped in 0.18 s. After
the final host parameter-route metadata change, the affected host–guest file
passed all 4 tests, 0 skipped in 20.81 s. These validate fixture loading,
geometry admission, shared-builder assembly, and mechanics/restart plumbing only.

## Correction-source retrieval

U15 was read from
`https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/atom_openmm/abfe_structprep.py`.
The response was HTTP 200 at `2026-10-07T13:48:06Z`; its SHA-256 is
`171bf698ea95ccd6e7653fa5b5596e192a233c7d2a4940bb1fa1dfcaef10856b`. The saved
source and the installed
`/workspace/before-hpc-cpu-v2/env/lib/python3.11/site-packages/atom_openmm/abfe_structprep.py`
have the same SHA-256. The installed distribution reports `atom-openmm==8.5.0b0`,
while the retrieved tag is `v8.5.0`; the version-string difference is retained.
U15 shows preparation restraint machinery and does not define a postprocessing
correction equation.

The cited U37 guide
`https://gallicchio-lab.github.io/AToM-OpenMM/user-guide/abfe/` returned HTTP 403
at `2026-10-07T13:48:02Z`; the targeted release-doc index also returned HTTP 403
at `2026-10-07T13:48:31Z`. Headers are preserved under `upstream/`. No alternate
correction scheme was substituted. Actual correction applicability and equations
remain a hold.

The pre-D tracked historical `Worker_Log/Before_HPC/evidence/**` files and the
accepted `fixtures/cloud_host_guest/v2` and `fixtures/solvated_fragment/v2`
fixtures have no source diff. The 386 protected items are extracted files from
one supplied ZIP, not 386 ZIP archives. Their authoritative path/digest list is
`Worker_Log/Before_HPC/evidence/setup-v1/handoff-identity.json`; the root worker
will compare it at the D checkpoint. No re-extraction or mutation of that
archive was performed here.
