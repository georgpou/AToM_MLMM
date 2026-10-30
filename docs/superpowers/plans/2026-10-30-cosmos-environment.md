# Cosmos environment installation plan

Goal: install the existing exact CPU and separate AmberTools locks inside `.runtime/cosmos-cpu`, and provide allocation-aware validation using the supplied LU2025-2-123 account. No new scientific profile or GPU production admission.

1. Reproduce the hard-coded CA-path failure with the actual main activation script, then allow ATOM_MLMM_CA_BUNDLE in installer/main activation and refresh only their bundle checksums. No dependency or model identity changes.
2. Add a Cosmos wrapper for RHEL certificates, repository-local caches/temp files and disabled Conda/Mamba global environment registration. Preserve HOME and sample scripts. Ignore `.runtime/` in Git.
3. Run the exact hash-verified installer. Preserve logs and any failure. Activate main and Amber separately and run strict environment validation plus the available CPU suite under a bounded Slurm allocation where possible. Verify the account using sbatch --test-only first.
4. Supply one-task, explicit-CPU Slurm validation script and an unsent GPU diagnostic template for gpua100i. Do not imply that CPU PyTorch or the current MACE callback supports CUDA production. Keep all job outputs inside the repo.
5. Record actual commands/results, source identities, changed-file hashes and remaining limits in Worker_Log/Documentation/Cosmos_Environment_v1_worker.md and STATUS.md. No installation outside this repository, no shell startup edits, no independent acceptance claims.
