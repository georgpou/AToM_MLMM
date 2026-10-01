# Quick MACE ML/MM calculation with a link atom

After the [CPU installation](../environment/cloud-cpu/README.md), run from the repository root:

```bash
source /workspace/.onboarding/atom-mlmm/activate.sh
python examples/mace_link_cpu.py --output /workspace/.onboarding/atom-mlmm/mace-link-result.json
python -m pytest tests/integration/test_mace_link_example.py -v
```

The 7.3 MB MACE-OFF23-small checkpoint is carried in [models/mace-off23-small](../models/mace-off23-small/). Its [manifest](../models/mace-off23-small/manifest.json) pins the upstream commit, SHA-256 and academic-use authorization. Preserve the supplied [Academic Software Licence](../models/mace-off23-small/LICENSE.md); these weights permit academic noncommercial use. The [pinned upstream README](https://github.com/ACEsuit/mace-off/blob/91a78c5a9c300d1104700d9352c8bfe449227737/README.md) supplies attribution and citation.

The calculation uses a frozen GAFF 2.2.20 ethane/methane fixture: 13 real atoms, one carbon-carbon ML/MM cut, and one massless hydrogen link site. One carbon with its three hydrogens and the complete methane ligand are ML; the remaining ethane atoms are MM. OpenMM-ML's mechanical embedding constructs the link and retained MM terms. The real local MACE calculator runs through its ASE/PythonForce interface on the OpenMM CPU platform in double precision.

The script verifies the checkpoint before an explicit trusted-artifact `torch.load(weights_only=False)`, passes the loaded model through `MACECalculator(models=...)`, and keeps global unsafe loading disabled. It does not invoke a model downloader or modify installed packages. The scoped e3nn import allowance is restored. This permits this identified academic checkpoint, not arbitrary pickle files.

The JSON reports total, MACE and retained-MM energy, real-atom forces, cap geometry/mass, model/software identities and boundary-parent finite-difference errors. Both parent x/y/z derivatives use Reference-platform energy finite differences at two step sizes, compared to the CPU forces with a 0.005 kJ/mol/nm absolute component limit. This avoids amplifying CPU nonbonded-energy rounding at small steps. Virtual sites are recomputed, and the original snapshot is reevaluated for repeatability. The model contributes forces to both sides of the cut.

This is a single-point calculation and integration smoke. It exercises a simple neutral boundary surrogate and a complete ligand; it does not qualify a protein boundary, periodic system, chemical-reference accuracy, ATM binding calculation or GPU. The planned gates supply those checks. The [fixture record](../fixtures/mace_link/README.md) identifies the MM parameters and inputs for this reproducer.
