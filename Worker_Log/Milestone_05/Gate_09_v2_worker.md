# G09-R1 cloud retention repair — v2 worker

**Scope:** R1 closure and inherited bounded G09/G10 vacuum technical subsets.\
**Outcome:** ready_for_audit; full G09/G10/M05 remain partial.\
**Finished:** 2026-10-04 17:23 UTC.\
**Snapshot:** `m04-engine-readiness`; report-only base
`3fc194dc84bc3711a21ec88812fa7442e4d84d0e`; tested source
`3246f0cbd6f66702e4b196bace593efba776a25e`. Submission adds report/evidence/STATUS
only. Independent closure is assigned to the same actual GPT-6.1-sol/MAX auditor.

The [v1 audit](Gate_09_v1_audit.md) accepts the bounded neutral host/vacuum design
and numerical checks, but confirms that integration exceptions bypass archiving.
The [repair plan](G09-R1-repair-plan.md) preserves that scope and all definitions.
Guard, actual integration and final State acquisition now share the existing
handler. Valid runs retain the original full-force refresh. Failed runs capture
cached coordinates/velocities/parameters and checkpoint without evaluating failed
energy/forces again. Error metadata records the attempted sample/walker/state/
sequence/index and actual advanced step/time; no failed step becomes an accepted
sample. The original exception propagates.

Two new regressions advance real pinned workers before integration/final-State
faults and require exact State/checkpoint retention. The existing strict restart
test now uses the identical exported System/State/seed for its uninterrupted
reference. Earlier v2 attempts revealed that independently minimized starts and
anchor centers differed at roundoff (positions up to 1.67e-16 nm), before any
sampling. Their snapshot/State/bundle hashes and failed outputs are retained.
The initial force-refresh causal guess was disproved; no tolerance was changed.
The corrected comparison preserves exact raw/x/v/full-force equality.

Commands ran from `/workspace/AToM_MLMM` after activating
`/workspace/atom-mlmm-g08-r2/activate.sh`, with `OPENBLAS_NUM_THREADS=2` and
`PYTHONPATH=src` (`src:.` for the external RED test). Scientific runs were serialized.

| Check | Command | Actual outcome |
|---|---|---|
| R1 RED | `pytest -q /tmp/test_g09_r1_retention.py --basetemp=/tmp/g09-r1-red` | 1; 2 failed in 0.79 s, both absent production archives |
| First repair/checkpoint checks | `pytest -q tests/workflow/test_engine_failure_retention.py tests/workflow/test_engine_restart.py` | Two attempts: 4 passes/1 restart-oracle failure in 32.00/31.62 s; pre-sample Hamiltonians already differed |
| Corrected focused checks | Same files, `--basetemp=/tmp/g09-r1-green-3` | 0; **5 passed in 26.83 s**, exact continuity from one prepared bundle |
| Final full CPU | `python -m pytest -q --basetemp=/tmp/g09-v2-root-full` | 0; **461 passed in 399.38 s**, no skips |
| Fresh CLI smoke | `python -m atm_mlmm run fixtures/cloud_host_guest/v2/config.json --output /workspace/cloud-engine-pilots/host-v2 --trusted` | 0; 9 frames/18 steps, all 48 forces, complete 3x9 reconstruction, no binding estimate |
| Docs/whitespace | `python tools/check_docs.py --self-test`; `git diff --check` | 0; zero errors/eight self-tests; clean diff |

[V2 evidence](evidence/G09_v2/README.md) binds 111 source/input/test files and
507 retained prior artifacts. The fresh CLI output has the same physical and
alchemical identities as the frozen v1 longer pilot; execution 10.556 s, peak
RSS 976,871,424 bytes. The complete fresh relocatable attempt is
`/workspace/cloud-engine-pilots/host-v2`; tracked capture excludes duplicate
source/model/environment payloads. V1 numerical/admission/60-frame/300-step
evidence remains explicitly on its original source, with no overwritten logs.

Independent closure must challenge both failure origins and the existing-prefix/
provenance contract, then carry forward unchanged v1 numerical/design evidence.
Full solvent/exchange/M05, GPU, equilibrium, affinity accuracy and protein/HPC
qualification remain open. G07/M03 physical blockers and the quantum ledger are
unchanged; no QM ran. The user requests a graceful stop at this reviewed point
because the session limit is nearly used; no new feature is starting.
