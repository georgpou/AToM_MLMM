# M05 Colab notebooks

[Open the CPU notebook in Colab](https://colab.research.google.com/github/georgpou/AToM_MLMM/blob/m05-colab-workflows/notebooks/m05_colab_cpu.ipynb).

1. Choose **Runtime → Change runtime type → no accelerator**. Read the visible
   source pin, output paths and resource limits. Run the baseline cells in order.
2. Reproduce exact checkpoint `7b41213e87bfcc3ce76def7ffb64565110bbafec` with the
   unchanged two CPU locks. Every calculation activates the isolated main prefix;
   Colab kernel Python and Amber's NumPy 1.26 remain separate.
3. Export/download the complete stopped baseline attempts and logs. For the M05
   extensions, explicitly select the reviewed implementation SHA and a fresh
   evidence directory/checkout; repeat setup/profile checks before numerical
   preflight and serial denser/exchange pilots.
4. Keep active work on local `/content`. Only stopped safe-point snapshots go to
   storage you authorize. `atm_mlmm.evidence.export_evidence` preserves every
   file/empty directory, including failed pending transactions, and verifies
   hashes before publishing a copy. It does not delete local data. A partial
   copy remains inspectable and is not saved evidence.
5. Verify any returned copy with `verify_evidence`. Preserve its immutable export
   and resume a separate local working copy using its bundled source and identical
   environment. Fixed windows use `resume`; exchange uses `resume-exchange`.
   Incomplete exchange rounds require inspection and explicit rollback/replay.
   Checkpoints and portable States have different RNG guarantees.
6. Only after CPU evidence, use the separately documented TPU component notebook.

The link opens this branch's notebook for convenience; executable science always
checks the visible immutable source SHA, approved model hash and input manifest
hashes. No secrets or large outputs belong in notebook cells. The user selects
the runtime and authenticates storage/repository access as needed. Logs, raw
energies/full forces, preparation, States/checkpoints, source/model/profile hashes
and actual resource reports are evidence; a saved notebook alone is not.

No authorized Colab executor is available in the implementing session. Delivery
and local checks therefore leave actual Colab CPU and TPU execution pending.
Returned bundles must be verified before any hardware/profile acceptance claim.
This technical work does not qualify equilibrium, liquid density, pressure/virial,
protein production, molecular accuracy or affinity; M03 blockers remain visible.

[Open the separate TPU component notebook in Colab](https://colab.research.google.com/github/georgpou/AToM_MLMM/blob/m05-colab-workflows/notebooks/m05_colab_tpu_benchmarks.ipynb).
See the [experimental profile](../environment/colab-tpu/README.md). Its empty
`SOURCE_SHA` and `REFERENCE_SHA256` fields deliberately require the exact reviewed
implementation/reference identities; branch names are rejected. First save the
CPU reference with `python tools/m05_tpu_probe.py cpu-reference --output UNUSED`.
Switching runtimes requires restoring that verified complete export and
reinstalling the CPU base before cloning the separate XLA prefix. The probe
retains failed precision/operators and never qualifies timing from those results.

Executable extension/TPU source pin: `424a859732b77b2f91cd03b12bb3f0b8adf3f541`.
The implementing session's review/result is recorded in the
[G09 worker](../Worker_Log/Milestone_05/Gate_09_v5_worker.md) and
[G10 combined worker](../Worker_Log/Milestone_05/Gate_10_v2_worker.md); actual
Colab execution remains pending.

For the old baseline, which predates the export helper, stop all jobs and use
standard Python to download a complete archive before changing runtimes:

```python
import hashlib, shutil
assert not Path(str(EVIDENCE) + "-stopped.zip").exists(), "Preserve prior archives."
archive = shutil.make_archive(str(EVIDENCE) + "-stopped", "zip", str(EVIDENCE))
print(archive, hashlib.sha256(Path(archive).read_bytes()).hexdigest())
```

Choose an unused archive path; retain its printed SHA and download the entire
archive. Verify its bytes before extraction/import. Its individual worker/sample
manifests remain authoritative. For M05 attempts use the notebook's sealed
complete-tree export cell, which also captures command logs and failed pending
transactions without writing a new log into the source during copying.
