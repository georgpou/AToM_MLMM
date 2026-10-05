# G09 denser water and Colab orchestration — v5 worker

**Scope:** G09 bounded technical increment; Reference double / approved MACE
CPU float64, NVT 300 K, 0.0005 ps, two threads.\
**Outcome:** ready_for_audit; independent review pending.\
**Finished:** 2026-10-05T14:56:55.234424+00:00.\
**Snapshot:** `m05-colab-workflows`, base `fab6388b041acc4362f30b5ff7d3789a33fc536f`,
frozen scientific source `424a859732b77b2f91cd03b12bb3f0b8adf3f541`.
Report-only descendants do not change scientific source.

## Changes

The CPU notebook repeats isolated activation, pins an immutable baseline or
explicit reviewed extension SHA, checks model/input/profile identities, bounds
serial commands and retains failures. Complete stopped attempts can be copied
and hash-verified without executable deserialization; no partial export is
promoted and no original is deleted. Both notebooks have cleared outputs and
pass official nbformat5.10.4 schema validation in separate temporary tooling.

New `solvated_fragment/v2` adds 64 rigid classical TIP3P waters to the original
ABFE/RBFE solutes (224/233 real atoms), preserving solute parameters, masses,
constraints, complete ligands and fixed ML membership. The
[proposed amendment](../../docs/project-0/specs/m05-dense-exchange-amendment.md)
freezes geometry-only construction, inherited PME/ensemble/accounting and
unchanged S06 limits; scientific acceptance awaits independent review.

An initial force sweep exposed a stock Reference periodic pair artifact,
reduced to two waters/six atoms without ML/caps/project code. Evidence is retained;
engine repair is outside the user's priority. Only synthetic fixture coordinates
within eight box-length ULPs of an exact box face are formatted as that face before
selection. OpenMM and general runtime geometry are unchanged. Original failed
inputs and raw FD records remain frozen.

## Verification

Commands ran in `/workspace/AToM_MLMM` after activating
`/workspace/atom-mlmm-m05/activate.sh`, `PYTHONPATH=$PWD/src` and two threads.
The unchanged installer/strict validator passed all nine setup checks.

| Check | Command | Observed result |
|---|---|---|
| Evidence copy/tamper/symlink/partial copy and CPU notebook | `python -m pytest tests/workflow/test_evidence_export.py tests/environment/test_m05_notebooks.py -q` | 11 intended RED then 11 passed0.19s at Task1; later CLI check added |
| Denser geometry/solute conservation/both-map real-model coupling/full forces/FD sweeps | `python -m pytest tests/workflow/test_dense_solvent.py -q --basetemp=/workspace/m05-evidence/dense-input-final` | 8 passed21.10s; no tolerance change |
| Dense ABFE and RBFE fixed windows | `python -m atm_mlmm run fixtures/solvated_fragment/v2/{abfe,rbfe}/config.json --output /workspace/m05-evidence/dense-{abfe,rbfe} --trusted` (two serial commands) | Both exit0; nine frames/18 sampling steps plus six thermal steps each; 27.40/28.75s, peak RSS0.83/0.85GiB |
| Official notebook schema/cleared outputs | Isolated `nbformat.read(...); nbformat.validate(...)` for both notebooks | Passed; CPU lock unchanged |

Independent native-MACE/retained-MM energy errors are zero at saved precision;
maximum full-real-force errors1.65e-12/1.25e-12 kJ/mol/nm. Largest smallest-step
FD errors2.4246e-4/2.4137e-4 kJ/mol/nm meet S06. Sweeps use1e-3/1e-4/1e-5nm
and include both cap parents, ligand and water oxygen at each site.

Complete archives, exact input/model/source/profile hashes, failed records,
commands, resource/exit metadata and raw numerical arrays are in
[evidence/M05_v1](evidence/M05_v1/README.md). The final full suite passed **543 tests in606.45s**, no skips, exit0, on the
frozen source: `python -m pytest -q --basetemp=/workspace/m05-evidence/full-suite-final
--junitxml=/workspace/m05-evidence/full-suite-final.xml`. Resource/exit/JUnit proof
is in the evidence directory. Documentation checks passed all eight self-tests
with zero link errors.

## Handoff

Colab CPU execution is **not_run**: no authorized executor is available. The
notebooks and [run instructions](../../notebooks/README.md) are the assigned
user-run fallback. Returned complete exports must be verified before a Colab
claim. Denser local hydration is not equilibrated liquid density; no NPT/virial,
affinity or physical molecular/protein qualification is claimed. Keep M03's
seven sensitivity failures,29 missing references and QM ledger
2325.644650052/86400s unchanged. G10 combined CPU review is submitted separately;
full G09/G10/M05 remains open.
