# Frozen two-cut neutral control

This small synthetic control exercises two independent neutral protein C–C
cuts alongside complete, disconnected ligand groups of three and four atoms.
The real-atom order deliberately interleaves the protein and ligand atoms.
Neither ligand is cut, and the two boundary edges have distinct MM parents.

`input.json` freezes the atom and bond identities, explicit component charge
and multiplicity declarations, coordinates, MM masses and constraints, every
original nonbonded parameter, each harmonic-bond parameter, and the identities
of the serialized MM artifact and its independent force inventory. The two
selected protein fragments carry explicit neutral-singlet declarations even
though their inherited MM partial-charge sums are nonzero. Those partial
charges do not define the model's formal chemical state.

The fixture is an analytic architecture control. It is not a protein model,
chemical-reference result, or qualification of arbitrary caps. The approved
local MACE asset is used only for one bounded fixed-coordinate derivative
cross-check; that check does not establish chemical accuracy.
