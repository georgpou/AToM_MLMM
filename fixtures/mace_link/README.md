# Frozen neutral link-atom fixture

`input.json` stores exact coordinates in nm, atom order/elements, bonds, ML selection, boundary parents, cap length, preparation versions and the MM-system hash. `mm-system.xml` contains the corresponding unmodified GAFF 2.2.20 all-MM system before conversion.

Preparation used main OpenFF/openmmforcefields with the separate AmberTools executables. Molecules were `Molecule.from_smiles("CC")` and `Molecule.from_smiles("C")`, each with one generated conformer; their OpenFF topologies were combined. `GAFFTemplateGenerator(..., forcefield="gaff-2.2.20")` supplied the parameters to an OpenMM `ForceField`. System creation used `NoCutoff`, no constraints, `rigidWater=False` and `removeCMMotion=False`.

The methane coordinates were translated so its carbon is 0.4 nm in y from ethane carbon 0. The serialized coordinates are the frozen input; regenerating conformers is unnecessary for a run. ML real indices are `[0, 2, 3, 4, 8, 9, 10, 11, 12]`. The single cut has ML parent 0 and MM parent 1, with a 0.109 nm derived hydrogen site. Real atoms remain in their original order.

This ethane fragment is a minimal neutral surrogate for a protein-style carbon-carbon boundary. It provides no quantum reference or protein-chemistry validation. Run [the example](../../examples/README.md) for full-real-force checks, including both cap parents.
