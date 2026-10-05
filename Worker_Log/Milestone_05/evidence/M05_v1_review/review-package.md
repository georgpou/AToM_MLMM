# One combined M05 technical review

Base: fab6388b041acc4362f30b5ff7d3789a33fc536f (published M04 HEAD).
Frozen submission: bc6fd520308fba7e7448929138eb91e80ca6f063.
Tested scientific source:424a859732b77b2f91cd03b12bb3f0b8adf3f541;
submission adds evidence/reports only. Branch m05-colab-workflows, main unchanged.

Requirements: attached assignment now tracked at docs/project-0/handoffs/M05-colab-next-agent.md;
plan Worker_Log/Milestone_05/M05-colab-implementation-plan.md;
proposed scientific definition docs/project-0/specs/m05-dense-exchange-amendment.md;
gates G09/G10 and their relevant S04-S07. Workers Gate_09_v5_worker.md / Gate_10_v2_worker.md.
Ledger progress.md adjacent contains all rulings and RED/GREEN outcomes.

Implemented: CPU Colab wrappers/verified complete evidence copy; new64-water
224/233-atom frozen inputs and independent both-map full forces/FDs; solvated
offline/cache-denied reconstruction/checkpoint-vs-State evidence; persistent
2-worker exchange using existing adapter, transaction phases, immutable committed
rounds and both host RNG streams; separately pinned experimental actual-MACE TPU
probe and108 CPU reference configurations. CPU locks/weights/tolerances unchanged.
General runtime geometry/OpenMM unchanged. Input-only water box-face roundoff
formatting needs scientific review. Stock6-atom engine reproducer is report-only;
user explicitly deprioritizes engine repair. No external upstream message sent.

Evidence: Worker_Log/Milestone_05/evidence/M05_v1 has complete sealed archives,
raw forces/FDs/failures/checkpoints/source+model+profile hashes/journals,
notebook official schema proof, JUnit/full log/resources.543 root tests passed
606.45s,0skips; strict unchanged setup9 passes. Both dense pilots9samples/18MDsteps,
4round/8sample exchange each, all exit0. Source hashes and archive hashes bind
bytes. Prior malformed TPU-reference attempts are intentionally retained failures;
final accepted reference hash8a625d5bdcbac5cc1ddeb244ff12d095b14f811a287ca18732f86c943dba8d73.

Declared acceptance: proposed bounded CPU technical increment and combined G09/G10
coverage ONLY. Colab CPU/TPU hardware execution pending; runnable exact user-run
fallback required. No full M05/M03/physical/protein/affinity/statistical-exchanging-
walker/GPU/liquid-equilibrium/pressure/virial claims. QM ledger unchanged.

Review focus verbatim:
1. Fresh checkout/kernel mixes Python environments or silently changes weights.
2. A partial persistent copy loses samples, checkpoints or a failed transaction.
3. Exchange refresh/journal failures lose decisions, labels or either RNG state.
4. Denser water exposes image clashes or lost/doubled solvent/parent forces.
5. XLA device is CPU, silently lowers arithmetic precision or falls back to host.

Reviewer: fresh-context independent audit. Read minimal onboarding AGENTS/current
STATUS plus above spec/plan, inspect changed implementation/tests and challenge
those risks independently. Serialize any actual scientific checks. Activate
/workspace/atom-mlmm-m05/activate.sh in each shell; export OPENBLAS_NUM_THREADS=2
PYTHONPATH=$PWD/src.2 CPU/8GiB; full suite peakRSS~5GiB. Do focused checks/probes;
no full rerun solely for reporting or duplication. Keep full outputs outside
context in unused /workspace/m05-evidence/reviewer-v1. Package templates from
skills unavailable; equivalent reviewer rubric: requirement/architecture/science
consistency, concrete defects with severity/reproducer/closure check, explicit
unjudged items, exact snapshot and acceptance scope. Don't modify implementation,
commit or push. Write canonical Gate_09_v5_audit.md and Gate_10_v2_audit.md (combined)
with actual commands/results/verdict. One reviewer only; root will grade/fix
material findings in one tested pass. No second reviewer or implementation agent.
