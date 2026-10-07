# Before HPC user flow

Batch E adds packaging, local evidence routing and thin command wrappers around the existing library APIs. It does not choose a target, protonation, ligand parameter set, solvent model, or physical binding protocol.

Activate the retained CPU environment and thread profile from the checkout:

```bash
cd /workspace/AToM_MLMM-before-HPC
source /workspace/before-hpc-cpu-v2/activate.sh
export OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
export PYTHONPATH="$PWD/src"
python -m atm_mlmm --help
```

`python -m atm_mlmm check CONFIG.json` validates a declared configuration without loading executable artifacts. `python -m atm_mlmm run CONFIG.json --output RUN --trusted` invokes the existing bounded worker API after explicitly authorizing the supplied sealed System/model assets. `python -m atm_mlmm resume RUN --trusted` resumes the verified committed prefix on the identical runtime/software/source profile.

For multistate exchange, provide a JSON plan with exactly `state_ids`, `state_pairs`, `boundaries`, `steps_per_boundary`, and `seed`. The declared state list must cover 3–8 schedule states; `state_pairs` must explicitly define a connected graph covering each state. Counts, seed, trust, and recovery are explicit. Example shape:

```json
{
  "state_ids": ["state-a", "state-b", "state-c"],
  "state_pairs": [[0, 1], [1, 2]],
  "boundaries": 20,
  "steps_per_boundary": 1,
  "seed": 73
}
```

Start with `python -m atm_mlmm exchange-multistate PREPARED PLAN.json --output RUN --trusted`. An intentional bounded interruption can use `--stop-after-boundaries N`; continue it with `python -m atm_mlmm resume-multistate RUN --trusted`. If a pending boundary needs recovery, pass `--recover-pending` explicitly. The library archives pending bytes and resumes from its last committed boundary; it does not silently infer a retry. The controller is bounded CPU plumbing and does not claim molecular mixing, equilibrium, convergence, or affinity.

For analysis, pass a JSON document containing serialized nonempty `histories`, explicit `thermodynamics`, and an explicit `resampling` specification. `estimator` and `joint_covariance_kj2_mol2` are optional documented fields. `python -m atm_mlmm analyze ANALYSIS.json` delegates to `analyze_exchange`; it does not create a second estimator. The frozen known-answer and covariance controls cover synthetic records only. C3's unmatched-physical-state closure-refusal contract remains unimplemented and unqualified.

Model assets can be routed explicitly with `ATOM_MLMM_MODEL_DIR=/path/to/approved/mace-off23-small`. The loader verifies the manifest, checkpoint, license, and exact user-authorization bytes before use, and rejects missing, modified, symlinked, or untrusted assets. The installed-wheel evidence uses the identical asset hashes recorded in Batch E. The academic asset license does not grant commercial rights; no project-level license is invented here.

Every report must retain its stated profile and scope. `binding_result=not_evaluated` is not a binding conclusion. A same-profile OpenMM checkpoint carries the runtime's stochastic continuation; a portable OpenMM State restores observables but does not promise identical random-number histories.
