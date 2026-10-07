# Before HPC CPU resource note

These are serial measurements on one 15-real-atom synthetic control, from five fresh CPU processes on AMD EPYC 9V74 (x86_64), OpenMM Reference double, MACE-OFF23-small float64 where applicable, and the retained two-thread BLAS/OpenMP profile. Each case made one initial evaluation, eight repeated fixed-coordinate evaluations, and one permitted 0.5 fs step. The input identity is `2c9a2addb366ce3ba14d81ad5a489fbe6b53140eb2700ff22c4d15b5783d6c41`; source/tools/per-file identities and raw timings are in [the hashed benchmark receipt](../../Worker_Log/Before_HPC/evidence/batch-e-v1/benchmark-receipt-final-001.json).

| Case | Model load (s) | Context start (s) | First eval (s) | 8-eval mean (min–max, s) | One-step time (s) | Measured ns/day | Process wall (s) | Process CPU (s) | Peak RSS (MiB) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All-MM | — | 0.000831 | 0.000235 | 0.0000264 (0.0000204–0.0000420) | 0.00000898 | 4808.55 | 0.200 | 0.00564 | 66.3 |
| Ligand-only | 3.052 | 0.00225 | 0.2125 | 0.002096 (0.001959–0.002268) | 0.0002394 | 180.47 | 4.607 | 3.464 | 582.7 |
| Cavity-inclusive | 3.180 | 0.00253 | 0.1981 | 0.002557 (0.002323–0.003082) | 0.0004203 | 102.78 | 4.648 | 3.593 | 587.5 |
| Native ATM | 3.008 | 0.04136 | 0.5476 | 0.005466 (0.005202–0.006585) | 0.0003918 | 110.27 | 4.885 | 4.181 | 606.7 |
| Actual worker | 3.082 | 0.4975 | 0.01042 | 0.009935 (0.009415–0.010182) | 0.0003736 | 115.63 | 5.382 | 5.129 | 661.6 |

The rate is derived as `ns/day = 0.0864 * timestep_fs / step_seconds`; an independent unit check gives 0.432 ns/day for a 0.5 fs step taking 0.1 s. The five trials together represent only `2.5e-6 ns` of simulated time; their serial aggregate is 19.723 s wall, 16.372 s CPU, and 0.01095 aggregate ns/day. Per-worker rates, aggregate simulated time, serial wall time, and CPU time are reported separately. The tiny fixture rates are setup and plumbing measurements, not production forecasts. They do not support GPU extrapolation, an optimization claim, a timestep change, or scientific adequacy. No suite RSS substitutes for process RSS.
