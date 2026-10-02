# M02 analytic transfer fixtures

[transfer-v1.json](transfer-v1.json) is a hand-inspected seven-real-atom abstract graph, not a molecular reference. Ligand A has two noncontiguous particles (2, 0); ligand B has three (3, 6, 5). Environment particle 1 and protein particle 4 do not transfer. All positions/maps use nm; springs use kJ/mol/nm squared. The two nontrivial full maps are written independently of the resolver.

The energy is the sum of selected harmonic terms and, when enabled, the S04 model/environment spring. Tests independently calculate each negative gradient and the outside harmonic energy. The optional large marker is a physical harmonic force on protein particle 4. No weights, caps, periodic physics or molecular binding calculation are represented.

PythonForce XML contains executable pickle data. Fresh-process tests reload only locally generated artifacts with an explicitly trusted flag and a pinned digest; they disable networking and use a fresh cache. JSON parsing alone never executes a callback.
