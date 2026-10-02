# Independent M00 v2 review evidence

Reviewed SHA: `321d7e3764a46eb5359a8d96bcab9124dccbc5f5` in detached `/workspace/AToM_MLMM-m00-review-v2`. Verdict: **changes_required**, solely blocking finding M00-v2-R1 (severe retained-parent contact overlap). Canonical decision: [Milestone_00_v2_audit.md](../../Milestone_00_v2_audit.md).

The independently authored scripts read the frozen snapshot and write evidence only here. No model is imported/evaluated. `structural_audit.py` imports the frozen preparation module only after intercepting its writer, then regenerates all structures in memory. No snapshot files are changed. Python bytecode writes are disabled.

| Artifact | Meaning |
|---|---|
| `structural_audit.py`, `structural-results.json` | 730/730 integrity, chemistry/valence, chirality, coordinate/cap identity, hashes and deterministic preparation checks. Passing these checks does not assert the complete contact geometry is suitable. |
| `contact_geometry_audit.py`, `contact-geometry-results.json` | Independent complete-parent pair distances exposing the blocking O–H 0.998831 Å / O–C 1.729074 Å overlap. |
| `quantum_audit.py`, `quantum-results.json`, `quantum-run.txt` | 113/113 actual package/basis and quantum-only methane feasibility checks. Exact frozen settings, offline, no target systems/comparisons. |
| `independent-methane.dat`, `.log`, `timer.dat` | Full Psi4 numerical output and native timing evidence. |
| `commands.md`, `evidence-manifest.json` | Executed commands/outcomes, reviewed SHA and independent artifact hashes. |

The reference calculation used `/workspace/atom-mlmm-reference-pilot-v2/env/bin/python` directly, with 2 threads / 5 GiB, output/scratch here, and Python network connections denied. This is separate from the activated main NumPy 2 environment and Amber NumPy 1.26 stack. No package was installed or changed.
