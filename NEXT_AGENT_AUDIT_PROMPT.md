# Copy this assignment to the next agent

Work on `georgpou/AToM_MLMM`. Your immediate assignment is an **independent audit
of the delivered CPU setup and currently flagged repository inconsistencies**,
before any M00 design review or scientific gate implementation.

Fetch the latest `m01-g00-cloud-environment-setup` branch and create an unused
child such as `m01-g00-environment-audit-v1` directly from its tip. Verify the
starting commit and ancestry. Never start from, change or push to main. Preserve
existing changes; do not create a worktree unless explicitly requested.

Read `NEXT_AGENT_AUDIT_HANDOUT.md` on that branch and follow it. Also read AGENTS.md,
the reproduction v2 worker/evidence and environment/cloud-cpu/README.md. The worker
result to audit is `dcfd99d51e991f0cf6f838b81f2f14752b0a9afa`; separately identify
the latest handout commit and any later changes. All 51 wheels, exact locks and
pinned source archives are in Git. Reproduce with the branch's installer, ideally
in an empty prefix with its own bootstrap/cache, and independently run the checks.

There are two Python 3.11.16 environments: main ML/AToM uses NumPy 2.4.6 and CPU
PyTorch 2.8.0; AmberTools 26.0 is separate with NumPy 1.26.4. Main activation
exposes Amber executables while retaining main Python. Do not merge the environments,
substitute package versions, download model weights, disable TLS/hash verification
or introduce unsafe global checkpoint loading.

Investigate the two broken docs anchors and missing U40/U41 source entries,
historical versus current documentation claims, the earlier outer-driver exit 1
despite installer exit 0, the OpenCL replay warning, and stale or inconsistent
handoff/status/startup wording. Verify artifact/source provenance, both full
inventories and pip checks, OpenMM CPU, ML/ATM smokes, separate Amber preparation,
AToM's upstream regression, branch integrity and failure propagation. Preserve
raw outputs and statuses. Installer exit 0 in environment-only mode does not
mean the documentation or whole repository passed.

Write the real independent sibling audit at
Worker_Log/Documentation/Cloud_CPU_Reproduction_v2_audit.md, with your own findings,
severity, evidence, smallest repairs, regression checks and closure conditions.
Preserve existing submitted reports. Give any required repair worker a concrete
assignment on a child of your audit branch and require independent review of the
repairs. Do not silently mix repairs into the original audit or self-approve them.

Commit and push only your new branch. Report its name/commit, audit path, passed
and failed checks, remaining uncertainty and actual blockers. A clean baseline
requires zero local doc errors/eight self-tests plus all applicable environment
checks and issue closure. Do not claim M00/G00, model or GPU acceptance. Do not
start project implementation until the required audit findings are addressed.
