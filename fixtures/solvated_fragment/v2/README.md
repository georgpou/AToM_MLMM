# Denser local-water controls

These immutable ABFE/RBFE inputs append 64 rigid TIP3P waters (32 around each
ligand site) to the unchanged solutes: 224/233 real atoms. All solute particle,
exception/bonded parameters, masses, complete ligand membership and caps remain
unchanged. Classical water/ligand interactions stay active at both maps.

The geometry-only 0.32 nm lattice construction, minimum-image 0.80 water Bondi
ratio, cell/PME/constraints/preparation settings and unchanged numerical limits
are frozen in the [proposed definition](../../../docs/project-0/specs/m05-dense-exchange-amendment.md).
This exercises denser local solvent, not equilibrated homogeneous liquid density.
No pressure/virial, molecular accuracy, equilibrium or affinity claim follows.

Reproduce into an unused directory using the locked main environment:

```bash
PYTHONPATH=src python tools/build_dense_solvent_control.py /tmp/new-denser-control
python -m atm_mlmm check fixtures/solvated_fragment/v2/abfe/config.json
```

Each manifest hashes the full SystemInput, unchanged partition and snapshot,
identifies original solute bytes and includes the locked TIP3P XML identity.
V1 sparse inputs and their reviewed artifacts remain immutable.
