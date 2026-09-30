# CPU dependency consistency amendment — 30 September 2026

**Decision:** proposed for G00-T1 installation experiments; independent acceptance belongs in the final G00 audit. No scientific contract or numerical tolerance changes.

The unchanged M00 candidate successfully solved and installed but failed `python -m pip check` on source snapshot `8733fdb9d82bef667b0b0251eefde7c27fbed11e`, [Actions run 36765198681](https://github.com/georgpou/AToM_MLMM/actions/runs/36765198681). [Raw dependency diagnostics](../Worker_Log/Milestone_01/evidence/Gate_00_v2/pip-check-original-candidate.log) establish missing netCDF4, pdb2pqr and requests, NumPy upper bounds below 2, and Biopython below 1.86 in AmberTools' bundled Python utilities. A solver pass did not enforce all bundled distribution metadata.

## Smallest repair and evidence impact

Keep Python 3.11 and every inherited pinned engine/model/workflow version: OpenMM 8.6.1, OpenMM-ML tag 1.8, AToM tag v8.5.0, CPU Torch 2.8.0, MACE 0.3.16, e3nn 0.4.4, AmberTools 26.0, openmmforcefields 0.16.0, configobj 5.0.9 and PyMBAR 4.0.3.

Add Conda constraints `numpy>=1.26,<2` and `biopython>=1.83,<1.86`, and the missing `netcdf4`, `pdb2pqr`, `requests` and subsequently identified `docutils` dependencies. Pin MACE's transitive pip dependency `matscipy==1.1.1`: [upstream v1.1.1 metadata](https://github.com/libAtoms/matscipy/blob/v1.1.1/pyproject.toml) requires runtime NumPy >=1.16,<2, whereas [v1.3.0](https://github.com/libAtoms/matscipy/blob/v1.3.0/pyproject.toml) requires NumPy >=2. [PyPI's 1.1.1 release files](https://pypi.org/project/matscipy/1.1.1/) include CPython 3.11/Linux x86_64 wheels. Sources were retrieved on 2026-09-30; final installed wheels and source commits still require captured hashes.

The amended solve at `39ad3b54b982b4d63e06f9cda99ac67647b0aca3` additionally exposed PDB2PQR's missing docutils and MDTraj 1.11.1's NumPy ~=2.0 requirement. [Actual diagnostics](../Worker_Log/Milestone_01/evidence/Gate_00_v2/test-initializer-and-dependency-diagnostic.log) preserve these observations. Pin the originally unpinned MDTraj to 1.10.3; its [upstream setup.py](https://github.com/mdtraj/mdtraj/blob/1.10.3/setup.py) declares runtime NumPy >=1.25,<3 (build isolation is separate).

MACE and PROPKA also ship the same top-level `tests/__init__.py`. Their exact tagged source initializers and actual RECORD digests identify this collision; MACE's initializer changes a Torch loading environment flag if imported. Project tests must resolve their own explicit package in a fresh process and leave that override unset. Only this exact initializer with the observed pinned owners/source digests may be recorded as a nonruntime test collision; other files/owners/digests remain rejected. The bundled upstream test namespace is not admitted or executed. Model loading must separately reject unsafe override flags before later model admission.

This changes the executable candidate's content hash and resolved transitive builds. The old candidate's installation evidence remains failed and cannot qualify the amended environment. M00's accepted force/map/unit/correction design is unchanged; there was no accepted CPU runtime to invalidate. No in-place upgrade is allowed: rebuild clean host and development-container environments and regenerate every lock/evidence file.

## Acceptance conditions and migration

Run the full dependency check without filtering errors; verify Conda integrity before and after immutable-wheel reinstallation, OpenMM installation/API/version checks, and all applicable tests. Preserve exact amended YAML hash, Python patch/build, resolved Conda builds/URLs/SHA-256, original source tags and installed commits, hashed wheels, final manifest and raw outputs. The auditor must explicitly accept the amended candidate and scope.

Old records retain their own candidate hash and failure status. Current validation must match the current checkout's candidate hash before admission; no older artifact can be relabeled as the new setup. Model assets/loading, GPU execution and molecular-method qualification remain separate and unrun.
