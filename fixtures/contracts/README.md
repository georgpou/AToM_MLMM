# M01 contract fixtures

`protocol-v1.json` is a hand-written version 1 RBFE description with two unequal, noncontiguous groups. Group order defines A/B meaning and is preserved through JSON round trips. The displacement is in nm; no coordinate-map engine is exercised here.

`original-mm.xml` is a frozen four-particle OpenMM 8.6.1 inventory fixture. Its independent definition is `build_original()` in [the inventory test](../../tests/unit/test_force_inventory.py). Distinct masses, a constraint, periodic box, bonded terms, PME settings, exception, global parameter and both offset types make omissions visible. The test verifies the XML exactly and checks a hand-specified inventory without changing the System. Offsets are inventoried here; that does not admit them into the initial periodic hybrid Hamiltonian.

The topology in [the test fixtures](../../tests/conftest.py) deliberately interleaves an abstract protein graph and two unequal ligand graphs with duplicate residue numbers. These are structural identity/connectivity inputs, not chemically qualified molecules or chemical-reference data. Formal component states are explicit; no result is inferred from partial-charge sums.
