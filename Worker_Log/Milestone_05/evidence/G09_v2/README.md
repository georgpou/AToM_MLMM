# Frozen v2 repair evidence

[Worker](../../Gate_09_v2_worker.md), tested source
`3246f0cbd6f66702e4b196bace593efba776a25e`. Source/input/test hashes are in
`source-input-test-manifest.json`; prior accepted/frozen artifacts are in
`retained-submission-manifest.json`. V1 worker/audit/evidence remain unchanged.

`retention-red.txt` reproduces both missing archives. `retention-focused.txt`
and `retention-focused-2.txt` retain the incorrect two-preparation restart oracle
failures. `prepared-start-diagnostic.json` verifies pre-sampling snapshots,
States and bundles already differ. `retention-focused-3.txt` passes all five
checks from one identical prepared bundle, without changing tolerance.
`retention-faults/` contains exact advanced production States/checkpoints/error
metadata for both fault origins. `full-cpu.txt` records 461 passes/399.38 s.

`host-pilot-run.txt` is the actual fresh v2 CLI output. `host-pilot-capture/`
retains all raw records, States/checkpoints, settings/preparation, sealed
PDB/System/State/bundle and manifest. `host-pilot-capture-index.json` binds this
capture; full local source/model/environment payload is in
`/workspace/cloud-engine-pilots/host-v2`. This subset is evidence, not a complete
standalone installation. No binding estimate is produced.
