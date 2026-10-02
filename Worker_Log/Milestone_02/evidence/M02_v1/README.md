# M02 v1 evidence

Tested source/input snapshot: `4c952dba5563572cf9e39527e64fe28ee201c385`; profile `core-analytic-cpu`.

- [Validation](validation.json.gz): full command outputs, exit codes, fresh baseline, intended RED checks and completed G02/G03/full/analytic results.
- [Strict validation](strict-validation.json.gz): nine locked setup checks, including upstream UWHAM and documentation self-tests.
- [Environment manifest](environment-manifest.json.gz): exact Python distributions, Conda artifact builds/digests, source commits/archive digests, API checks and separate Amber identity.
- [Source/input manifest](source-input-manifest.json): SHA-256 of each tracked source/test/fixture/environment input at the tested commit.
- [Numerical results](numerical-results.json): 16 independently checked nonlinear local/environment cases, full raw energies/forces, identities, routing, masks and frozen thresholds.
- [Stale negative artifact](stale-reproducer.json) and [detection record](stale-detection.json): the smallest complete seven-real-atom test fixture with a deliberately frozen environment descriptor; expected and observed energies/forces and file hash are preserved.

Reproduce from the repository root after activating the locked main environment:

```bash
PYTHONPATH=src:. python Worker_Log/Milestone_02/evidence/M02_v1/reproduce_numerics.py --output /tmp/m02-numerics.json
XDG_CACHE_HOME=/tmp/m02-empty-cache PYTHONPATH=src:. python Worker_Log/Milestone_02/evidence/M02_v1/reproduce_stale_fault.py
```

The numerical script records the checked-out commit in its output. PythonForce serialization is executable: the negative reload script admits only this project-generated fixture with its expected SHA-256 and explicitly declared trust, and denies network connections. It must detect the preserved `u1` error; the broken callback is never used in production.

GPU, chemical/protein accuracy, caps, periodic/actual electrostatic physics, molecular binding and full workflow qualification are deferred. These artifacts do not supply the outstanding M00 physical-reference decisions.
