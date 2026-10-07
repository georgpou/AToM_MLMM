# HPC profile and restart preparation

The checked-in [profile template](profile-template.json) is intentionally incomplete. Replace every `null` with measured or allocation-documented values for the actual platform, device, driver, Python/OpenMM/model versions, source/wheel/asset/input hashes, storage path/filesystem, thread count, memory, wall time, worker count, and scheduler. Do not fill unknown fields with guessed cluster defaults. The local checker validates typed profile values and the actual bytes in the supplied bundle directory; it never submits or resumes a scheduler job:

```bash
cd /workspace/AToM_MLMM-before-HPC
source /workspace/before-hpc-cpu-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONPATH="$PWD/src"
python tools/check_hpc_profile.py environment/hpc/profile-template.json \
  --bundle-manifest /path/to/bundle/manifest.json \
  --output /tmp/hpc-profile-check.json
```

A `held` result is expected while required values are unknown. The actual storage system must pass a local lock, atomic rename, and fsync trial before it is considered for a run directory. Record filesystem type and mount/options, directory ownership, quota, and measured behavior. A local validation result does not establish cluster parity.

The profile schema accepts only its declared fields, integer schema version `1`, positive integer allocations, scheduler `none`, an absolute storage path, and the required lock/rename/fsync safeguard. Checkpoint compatibility is limited to `same-platform-identical-source-profile`; the profile must not promise portable-state RNG identity. Artifact hashes are bound to verified bundle inventory: `source_sha256` and `input_manifest_sha256` are SHA-256 of canonical JSON arrays containing each matching row's `bundle_path`, `bytes`, and `sha256`, sorted by path; `wheel_sha256` is the sole wheel row's content hash; `asset_manifest_sha256` is the content hash of `assets/mace-off23-small/manifest.json`. A manifest JSON object by itself cannot authorize readiness.

Before any future allocation, compare the actual host/device, driver, software stack, precision, thread count, memory/time allocation, model and input identities, and output storage with the exact tested profile. Keep package/asset/source hashes alongside the run. Do not infer a scheduler or change a scientific profile to match one.

Restart evidence must cover complete energies and forces on every declared mapped state, both maps and parameters, same-profile checkpoint continuation, portable-State continuation with its weaker stochastic meaning, worker and host RNG histories, failure archives, and committed record identity. The same-profile checkpoint must match the exact platform/software profile. A portable OpenMM State restores coordinates, velocities and parameters but does not promise identical RNG histories. Exercise output locking, directory creation, atomic rename, fsync, interrupted writes, and rollback on the actual target filesystem. Retain each failed artifact and archive.

This guide prepares requirements only. It does not authorize or launch a cluster job; no scheduler/device values, parity result, or restart trial are available in Batch E.
