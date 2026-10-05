# Unqualified Colab TPU component profile

The accepted CPU locks and model guards remain unchanged. Clone the installed
CPU main environment into an unused prefix, then add exactly the hash-pinned
PyTorch/XLA 2.8.0, libtpu 0.0.17 and absl-py 2.3.1 wheels. XLA 2.8.0's published
`tpu` extra specifies that libtpu version; the CPU profile already supplies
PyTorch 2.8.0, NumPy, PyYAML and requests. Use CPython 3.11/Linux x86_64 and
glibc >=2.31. Run `pip check` and retain the inventory. ABI compatibility and
actual TPU execution remain pending hardware evidence; import failure is a
retained negative result, not grounds to change the CPU lock or weights.

```
bash environment/colab-tpu/install.sh /content/atom-mlmm-colab-cpu /content/atom-mlmm-colab-tpu
```

First export the CPU references with the accepted CPU prefix, exact reviewed
source and approved model. These contain ABFE/RBFE both-map model inputs, full
real coordinates, cap parents, full projected ML forces and real-parent/ligand/
solvent finite differences. Preserve the printed reference SHA with the complete
verified evidence export. Select a Colab TPU runtime explicitly, reconstruct the
same source/profile/model assets and import that reference by its hash.

Run the separate notebook or `tools/m05_tpu_probe.py tpu` with `PJRT_DEVICE=TPU`,
no BF16/downcast settings, and the experimental prefix's Python. The probe checks
the actual backend and device arithmetic, attempts actual MACE energy/coordinate
gradients, rebuilds changed-coordinate graphs and projects cap forces to all real
atoms. Requested tensor dtype alone does not prove float64 arithmetic. Keep
operator failures, HLO, fallback counters, raw arrays and logs. Any unsupported
precision, ATen host fallback, or S06 mismatch prevents timing qualification.
The first invocation includes startup/compilation; synchronized steady repeats
include graph construction, transfers, autograd and gradient return. Compare
with identical CPU work; do not call this full-engine throughput or TPU support.

OpenMM/PME/integration stay on CPU. Missing TPU hardware is pending, not a pass
or a numerical failure. No CUDA substitution, lower precision, new model,
training, GCP service or production run is included.
