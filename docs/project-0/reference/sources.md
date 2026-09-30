# Source register inherited from the revised plan

These locations preserve the preceding research audit's reference trail. The earlier documentation package organized these references. This edition updates wording and handoffs; it did not refetch or reverify upstream pages. G00 must record the actual admitted source commits. Moving documentation is not a lock. U-identifiers below distinguish upstream references from S-identifiers used for shared specifications.

The original brainstorming note and later large plan are preserved as historical context. The [history archive](../../../README.md#history) retains the previous editions and their evidence. Architectural choices in S01-S07 remain proposed until reviewed; this cleanup did not fetch or reverify upstream pages.

| ID | Relevant material | Source |
|---|---|---|
| U01 | Original uploaded brainstorming note; historical, not the current implementation authority | [U01](original-brainstorming-plan.md) |
| U02 | OpenMM release history; API/version checks | [U02](https://github.com/openmm/openmm/releases) |
| U03 | OpenMM-ML releases | [U03](https://github.com/openmm/openmm-ml/releases) |
| U04 | OpenMM-ML 1.8 setup requirements | [U04](https://raw.githubusercontent.com/openmm/openmm-ml/1.8/setup.py) |
| U05 | OpenMM-ML mechanical embedding and link documentation | [U05](https://openmm.github.io/openmm-ml/latest/userguide.html) |
| U06 | OpenMM-ML 1.8 public mixed-system API | [U06](https://raw.githubusercontent.com/openmm/openmm-ml/1.8/openmmml/mlpotential.py) |
| U07 | OpenMM-ML 1.8 mechanical embedding implementation | [U07](https://raw.githubusercontent.com/openmm/openmm-ml/1.8/openmmml/embeddings/mechanicalembedding.py) |
| U08 | OpenMM-ML 1.8 links, mapping and bonded-term utilities | [U08](https://raw.githubusercontent.com/openmm/openmm-ml/1.8/openmmml/embeddings/utilities.py) |
| U09 | Native ATMForce public API and diagnostic ordering | [U09](https://docs.openmm.org/latest/api-python/generated/openmm.openmm.ATMForce.html) |
| U10 | PythonForce callback, subset and serialization API | [U10](https://docs.openmm.org/latest/api-python/generated/openmm.openmm.PythonForce.html) |
| U11 | OpenMM 8.6.1 native ATM implementation | [U11](https://raw.githubusercontent.com/openmm/openmm/8.6.1/openmmapi/src/ATMForceImpl.cpp) |
| U12 | AToM release history | [U12](https://github.com/Gallicchio-Lab/AToM-OpenMM/releases) |
| U13 | AToM v8.5.0 package metadata and entry points | [U13](https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/pyproject.toml) |
| U14 | AToM v8.5.0 force routing, integrators and map keys | [U14](https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/atom_openmm/ommsystem.py) |
| U15 | AToM v8.5.0 ABFE preparation | [U15](https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/atom_openmm/abfe_structprep.py) |
| U16 | AToM v8.5.0 RBFE preparation | [U16](https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/atom_openmm/rbfe_structprep.py) |
| U17 | AToM v8.5.0 worker/reload/process implementation | [U17](https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/atom_openmm/ommworker.py) |
| U18 | AToM v8.5.0 bundled Python UWHAM | [U18](https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/atom_openmm/uwham.py) |
| U19 | OpenMM-ML 1.8 MACE model adapter | [U19](https://raw.githubusercontent.com/openmm/openmm-ml/1.8/openmmml/models/macepotential.py) |
| U20 | MACE releases | [U20](https://github.com/ACEsuit/mace/releases) |
| U21 | MACE v0.3.16 dependency settings | [U21](https://raw.githubusercontent.com/ACEsuit/mace/v0.3.16/setup.cfg) |
| U22 | MACE v0.3.16 foundation-model loader | [U22](https://raw.githubusercontent.com/ACEsuit/mace/v0.3.16/mace/calculators/foundations_models.py) |
| U23 | MACE-OFF model identity and usage license | [U23](https://raw.githubusercontent.com/ACEsuit/mace-off/main/README.md) |
| U24 | Official PyTorch version-specific installation instructions | [U24](https://pytorch.org/get-started/previous-versions/) |
| U25 | PyTorch 2.8 process/CUDA guidance | [U25](https://docs.pytorch.org/docs/2.8/notes/multiprocessing.html) |
| U26 | OpenMM installation and platform test instructions | [U26](https://docs.openmm.org/latest/userguide/application/01_getting_started.html) |
| U27 | OpenMM checkpoint versus portable State documentation | [U27](https://docs.openmm.org/latest/api-python/generated/openmm.app.simulation.Simulation.html) |
| U28 | Enhancing Protein-Ligand Binding Affinity Predictions Using Neural Network Potentials; ligand-only precedent | [U28](https://pmc.ncbi.nlm.nih.gov/articles/PMC11214867/) |
| U29 | Potential distribution theory of alchemical transfer | [U29](https://pmc.ncbi.nlm.nih.gov/articles/PMC11803756/) |
| U30 | AToM theory documentation | [U30](https://gallicchio-lab.github.io/AToM-OpenMM/theory/) |
| U31 | AToM v8.5.0 FKBP ABFE example schedule | [U31](https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/examples/ABFE/fkbp/scripts/defaults.yaml) |
| U32 | AToM v8.5.0 CDK2 RBFE example schedule | [U32](https://raw.githubusercontent.com/Gallicchio-Lab/AToM-OpenMM/v8.5.0/examples/RBFE/cdk2/scripts/defaults.yaml) |
| U33 | PyMBAR 4.0.3 reduced-potential and analysis API | [U33](https://pymbar.readthedocs.io/en/4.0.3/mbar.html) |
| U34 | PyMBAR 4.0.3 timeseries/correlation API | [U34](https://pymbar.readthedocs.io/en/4.0.3/timeseries.html) |
| U35 | openmmforcefields releases | [U35](https://github.com/openmm/openmmforcefields/releases) |
| U36 | openmmforcefields preparation scope | [U36](https://github.com/openmm/openmmforcefields) |
| U37 | AToM ABFE workflow guide | [U37](https://gallicchio-lab.github.io/AToM-OpenMM/user-guide/abfe/) |
| U38 | AToM RBFE workflow guide | [U38](https://gallicchio-lab.github.io/AToM-OpenMM/user-guide/rbfe/) |
| U39 | PyTorch 2.8 serialization and weights_only policy | [U39](https://docs.pytorch.org/docs/2.8/notes/serialization.html) |

## Where the source evidence is used

U04-U11 and U19 support the inherited API/link/adapter issues in G00-G07. U13-U18 and U31-U32 identify the workflow implementation points for G03 and G08-G12. U28 is a ligand-only precedent, not proof of cavity-inclusive caps. U29-U30 support the thermodynamic setting; the harmonic and derivative oracles are mathematical derivations stated explicitly in the specifications. U24-U27 and U39 identify environment, process, loader and restart checks. U33-U34 identify the independent analysis APIs. U35-U36 concern optional preparation, not a prerequisite for analytic tests.
