# Independently executed commands and outcomes

Read commands used the immutable snapshot directory `/workspace/AToM_MLMM-m00-review-v2`. Evidence path below is `/workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_00/evidence/M00_review_v2`.

1. `pwd && git rev-parse HEAD && cat AGENTS.md` — exit 0, expected snapshot/SHA. Read AGENTS/STATUS, M00 plan/worker/settings/manifest/preparation, S01/S04/S06/S07, G05/G07, model manifest/card, provenance records, quantum script and gzipped prior outputs with `cat`, `sed`, `rg`, Python gzip/json. One exploratory `cat models/mace-off23-small/provenance.json` returned exit 1 (file does not exist); resolved with `rg --files` and read actual `manifest.json`, `qualification-card.json` and reference provenance manifest. No evidence is inferred from the failed lookup.
2. `git status --porcelain=v1 && git symbolic-ref -q HEAD` — empty status; symbolic-ref exit 1 as expected for detached HEAD. `source /workspace/atom-mlmm-g05-v2/activate.sh` and Python reported main `/workspace/atom-mlmm-g05-v2/env/bin/python`, RDKit 2026.03.6, NumPy 2.4.6.
3. From the frozen snapshot, after main activation:
   ```bash
   PYTHONDONTWRITEBYTECODE=1 python /workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_00/evidence/M00_review_v2/structural_audit.py > /workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_00/evidence/M00_review_v2/structural-results.json
   ```
   Exit 0, 730/730 integrity/structure checks; full contact minima separately inspected and the retained-parent overlap identified.
4. After main activation, from the evidence directory:
   ```bash
   PYTHONDONTWRITEBYTECODE=1 TMPDIR=/workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_00/evidence/M00_review_v2 PSI_SCRATCH=/workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_00/evidence/M00_review_v2 /workspace/atom-mlmm-reference-pilot-v2/env/bin/python /workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_00/evidence/M00_review_v2/quantum_audit.py > /workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_00/evidence/M00_review_v2/quantum-run.txt 2>&1
   ```
   Exit 0, 113/113 checks; 64.985 s. Exact settings, finite energy and gradient, matching package/basis hashes, D3 present/VV10 absent; methane-only finite-difference errors 0.010334/0.091104 kJ/mol/nm.
5. From the frozen snapshot, after main activation:
   ```bash
   PYTHONDONTWRITEBYTECODE=1 python /workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_00/evidence/M00_review_v2/contact_geometry_audit.py > /workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_00/evidence/M00_review_v2/contact-geometry-results.json
   ```
   Exit 0. Exact pair distances confirm parent p9 is O, not C; p9/l6 0.998831 Å, p9/l0 1.729074 Å, p24/l5 1.462471 Å in ethanol-acetamide-d3-r60.
6. `rg -n 'D3|Dispersion|s6|s8|a1|a2|omega|LibXC|Functional|VV10|Spherical|Radial|convergence|DEF2' .../independent-methane.dat` — confirmed actual method, dispersion parameters, basis and grid output. `git status --porcelain=v1 && git rev-parse HEAD` — exit 0; frozen snapshot remains clean at the requested SHA.

Tool-mediated cloud runtime inspection reported connected/ready with restricted networking; no network work was needed. All reviewer writes are the canonical audit or files in this evidence directory. No implementation changes or Git commits were made.
