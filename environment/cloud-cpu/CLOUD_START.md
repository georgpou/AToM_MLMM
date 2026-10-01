# Cloud startup

Use `m01-g00-environment-audit-v1` as the repository branch, then create an unused child for the assigned milestone/gate. Keep main unchanged and retain completed predecessor work.

Read README, AGENTS, docs/project-0/STATUS.md and the assigned gate's linked sections. Use environment/cloud-cpu/README.md for installation and docs/DEVELOPMENT.md for imports, source layout and tests. A new workspace can run `bash environment/cloud-cpu/install.sh`; no prepared filesystem or external wheel bundle is needed. In each Bash session activate `source /workspace/.onboarding/atom-mlmm/activate.sh`, substituting your custom setup prefix when used.

Keep main ML/AToM and AmberTools Python environments separate. All locks/wheels/sources are in this branch. Academic MACE-OFF23-small weights are bundled for `python examples/mace_link_cpu.py`; GPU and full real-model physical profiles are later qualification work.

Next work: relevant M00 design review, M01 analytic CPU G00-T1 and G01-T1/T2/T3, then combined review. Write a concise worker log with actual tests and update STATUS. Historical documentation audits need no reconstruction before implementation.
