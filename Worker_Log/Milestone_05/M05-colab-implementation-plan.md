# M05 Colab and persistent exchange implementation plan

> **For agentic workers:** Use `superpowers:executing-plans` inline. Serialize
> scientific work; dispatch one independent whole-submission reviewer at the end
> and remain idle during that review. Preserve every earlier attempt.

**Goal:** Reproducible CPU Colab orchestration, a denser local-water control,
solvated offline/restart evidence and a transactional two-worker exchange pilot,
followed by a separate actual-MACE TPU compatibility probe.

**Architecture:** Notebooks call the existing common CLI and repository tools.
One physical builder/ATM adapter remains responsible for physics. A new exchange
controller journals complete rounds around `attempt_pair_exchange`; the local
filesystem is authoritative. TPU work is a component experiment and cannot
change the accepted CPU profile.

**Tech stack:** Unchanged two CPU locks; Python/Jupyter; OpenMM Reference double,
MACE CPU float64; separately pinned experimental PyTorch/XLA.

**Spec:** [Assigned handoff](../../docs/project-0/handoffs/M05-colab-next-agent.md),
[G09](../../docs/project-0/gates/G09-solvent-preparation-and-export.md),
[G10](../../docs/project-0/gates/G10-restart-and-replica-exchange.md),
[S04](../../docs/project-0/specs/S04-embedding-and-model-contracts.md),
[S05](../../docs/project-0/specs/S05-protocol-and-thermodynamic-contracts.md),
[S06](../../docs/project-0/specs/S06-validation-and-tolerances.md),
[S07](../../docs/project-0/specs/S07-artifacts-and-qualification.md), and the
[proposed bounded definition](../../docs/project-0/specs/m05-dense-exchange-amendment.md).

## Global constraints

- Child branch `m05-colab-workflows` starts at published M04 HEAD
  `fab6388b041acc4362f30b5ff7d3789a33fc536f`; preserve main and predecessors.
- Reference double / pinned MACE CPU float64, NVT 300 K, 0.0005 ps, two threads.
- Fixed complete-ligand ML membership, original solute parameters, 0.109 nm cap,
  full influencing-real forces, both-map guards and unchanged S06 tolerances.
- No new QM, production, protein, Slurm or GCP work. QM ledger remains
  2325.644650052/86400 s; M03 physical blockers remain visible.
- No Colab execution tool is available. Deliver runnable notebooks and exact
  user-run instructions; Colab/TPU results remain pending until returned and
  verified. Local results must identify this workspace.
- Record resources/counts/seeds/steps/time bound/persistence before heavy work.
  Keep large command output outside the context and scientific payloads outside
  notebook outputs. No full numerical rerun solely for report changes.

## Review focus

1. Fresh checkout/kernel mixes Python environments or silently changes weights.
2. A partial persistent copy loses samples, checkpoints or a failed transaction.
3. Exchange refresh/journal failures lose decisions, labels or either RNG state.
4. Denser water exposes image clashes or lost/doubled solvent/parent forces.
5. XLA device is CPU, silently lowers arithmetic precision or falls back to host.

## Task 1: CPU notebook and evidence transport

**Files:** `notebooks/README.md`, `notebooks/m05_colab_cpu.ipynb`,
`src/atm_mlmm/evidence.py`, `tests/workflow/test_evidence_export.py`,
`tests/environment/test_m05_notebooks.py`.

**Interfaces:** `export_evidence(source, destination) -> dict` copies a complete
quiescent attempt into an unused destination and seals/verifies every relative
file hash; `verify_evidence(directory) -> dict` rejects missing/extra/changed
files, symlinks and unsafe manifest paths without executable deserialization.
Notebook computation subprocesses repeat activation and fail on nonzero exit,
retain command/resource logs, and verify exact source/model/input identities.

- [ ] Write and run failing copy/tamper/partial-copy/symlink/path tests and a
  notebook subprocess-failure test. Expected: missing API/artifact assertions.
- [ ] Implement smallest verified copy API and the CPU notebook. Visible exact
  baseline SHA is `7b41213e87bfcc3ce76def7ffb64565110bbafec`; later experiments
  require an explicit immutable implementation SHA. Never select moving main.
- [ ] Run `python -m pytest tests/workflow/test_evidence_export.py
  tests/environment/test_m05_notebooks.py -q`; expected all checks pass.
- [ ] Commit implementation; retain local setup/baseline results and notebook
  schema validation. Colab execution stays pending.

## Task 2: denser control and persistent exchange

**Files:** `src/atm_mlmm/solvent.py`, `tools/build_dense_solvent_control.py`,
`fixtures/solvated_fragment/v2/`, `src/atm_mlmm/exchange.py`,
`src/atm_mlmm/adapters/atom.py`, `src/atm_mlmm/__main__.py`,
`tests/workflow/test_dense_solvent.py`,
`tests/workflow/test_persistent_exchange.py`,
`tests/workflow/test_solvated_process_restart.py`.

**Interfaces:** `build_dense_control(kind, destination)` freezes 64 rigid TIP3P
waters selected by a deterministic 0.32 nm local lattice around both sites,
solely using predeclared geometry. `run_exchange(prepared_run, output, *, rounds,
steps_per_round, seed, trusted=False, stop_after_rounds=None) -> dict` copies a
verified prepared worker bundle and makes a bounded two-state/two-walker pilot.
`resume_exchange(directory, *, trusted=False, stop_after_rounds=None,
recover_pending=False) -> dict` verifies source/profile/committed history before
loading. `read_exchange_rounds(directory) -> list[dict]` verifies the immutable
prefix. Optional adapter `phase_callback(phase, report)` exposes evaluated,
decision and refreshed phases; it never supplies alternate energy/Metropolis
logic. CLI commands are `exchange` and `resume-exchange`.

- [ ] Freeze solvent and transaction definitions in the amendment before results.
- [ ] Write and observe RED tests for 64-water geometry/solute preservation,
  image/clash rejection and round/RNG/sample continuity. Include actual analytic
  workers, accepted/rejected upstream decisions and phase/journal faults.
- [ ] Implement solvent construction and round journal; retain both workers'
  cached original/mapped States after any scientific/refresh/write failure.
  Pending rounds block default resume; explicit recovery preserves their entire
  contents in a failure archive and replays from the prior committed boundary.
  A round published before a later reporting error remains committed.
- [ ] Establish exact same-prepared-worker checkpoint continuation and portable
  State fixed-coordinate agreement separately. Exercise fresh relocated solvent
  bundles with original checkout/run/cache/network paths denied.
- [ ] Run `python -m pytest tests/workflow/test_dense_solvent.py
  tests/workflow/test_persistent_exchange.py
  tests/workflow/test_solvated_process_restart.py -q`; expected all checks pass.
  Both-map real-model preflight uses independent retained-MM/native MACE forces,
  all-real arrays and 1e-3/1e-4/1e-5 nm FD sweeps including both cap parents and
  solvent. Keep raw values, per-component errors and timing/RSS evidence.
- [ ] Run bounded ABFE/RBFE fixed-window and exchange pilots serially after
  preflight; heavier Colab variants remain user-run pending. Commit source.

## Task 3: separate TPU probe, verification and review

**Files:** `notebooks/m05_colab_tpu_benchmarks.ipynb`,
`environment/colab-tpu/`, `tools/m05_tpu_probe.py`, notebook regression tests,
new `Gate_09_v5_worker.md` / `Gate_10_v2_worker.md`, evidence and STATUS/handoff.

**Interfaces:** Experimental probe loads only the approved hash-verified MACE
bytes, records actual XLA device/hardware/arithmetic precision and actual MACE
energy/coordinate gradients. CPU float64 reference input contains identical
ABFE/RBFE map0/map1 model inputs and cap-parent maps. Numerical failure blocks
timing qualification. Synchronized startup/steady timings include graph creation,
transfer, gradient and return. Unsupported precision/operators and absent
hardware are retained outcomes. CPU locks/guards are unchanged.

- [ ] Write failing notebook/profile/probe admission tests; implement pinned
  experimental orchestration and real-model input/reference export.
- [ ] Validate notebook JSON/schema, cleared outputs and failure propagation;
  run affected checks and `python -m pytest -q` once on the final source.
  Expected zero failures; record every unavailable check explicitly.
- [ ] Run `python tools/check_docs.py --self-test`; expected zero link errors
  and eight self-tests. Freeze source/submission with exact identities.
- [ ] Dispatch one independent reviewer for G09/G10 declared technical scope,
  including the proposed definitions; idle while it audits. Fix material findings
  in one RED/GREEN pass and rerun affected/full checks as justified.
- [ ] Publish only the child branch using normal commits/pushes. Update STATUS
  from actual results and leave a handoff naming the exact published source,
  Colab user-run dependency, unresolved M03 and unqualified profiles.
