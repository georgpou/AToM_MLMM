# Terms used in the plan

Read only the terms needed for your task. Exact field names remain in the specifications.

**ML / MM:** a machine-learning energy model and classical molecular mechanics. The hybrid system uses both under a defined interaction rule.

**ATM / AToM:** ATM is the Alchemical Transfer Method. AToM-OpenMM is the workflow software used to run it.

**ABFE / RBFE:** absolute binding free energy for one ligand, or the difference between binding free energies of two ligands. The state definition, corrections, and sign must be explicit.

**Hamiltonian:** the mathematical energy definition. These plans mostly discuss its potential-energy part. Changing its terms changes the model being simulated.

**Mechanical embedding:** ML describes the selected region while ML-MM interactions remain classical under the specified bookkeeping.

**Electrostatic embedding:** the model responds to the external electrostatic environment. Correct energy and forces must include that dependence. A simple environment-dependent test is not a real electrostatic model.

**Link atom / cap:** an artificial hydrogen closing a cut protein fragment. Its position is computed from real atoms; it is not an independently moving physical hydrogen.

**Virtual site:** a particle whose position is computed from other particles. Forces must reach the real coordinates on which it depends.

**Contract / interface:** the agreed input fields, output fields, units, ordering, and behavior between code components. An implementation can change internally without changing that agreement.

**Protocol:** the definition of which ligand groups move, the coordinate maps, the endpoint meanings, and required thermodynamic accounting.

**Fixture:** a small, saved test system with known inputs and expected behavior.

**Oracle:** an independent expected answer, such as a hand-derived formula or a separately checked calculation. Reusing the code under test is not an independent answer.

**Profile / qualification:** a profile names the exact software, model, inputs, hardware, and settings tested. Qualification means evidence supports that particular setup, not every possible combination.

**Capability:** something a component says it can support. A declaration alone is not proof that a complete calculation works.

**Snapshot:** the exact coordinates, files, or code revision being checked. A code snapshot must include relevant uncommitted files, not merely a branch name.

**Bundle / artifact:** a collection of related records or a saved file. A complete bundle must contain what another process needs to reproduce its result.

**Provenance / manifest:** the record of where inputs and results came from, including versions and hashes. A hash identifies file contents but does not supply missing bytes.

**Force ledger:** a record of which energy terms are retained, removed, or replaced. It helps detect missing or double-counted interactions.

**PME / periodic images:** PME is a method for periodic electrostatics. Periodic images are repeated copies of the simulation box that can create contacts not obvious in the central box alone.

**Neighbor graph:** the atom connections used by a local model. Separate components can be independent only when the model's rules justify that property.

**Counterfactual geometry:** the alternate coordinate set ATM evaluates at the current saved configuration. It can have difficult contacts even when the weighted simulation state looks reasonable.

**Finite-difference force:** a force check obtained by moving a coordinate slightly in both directions and comparing energies. It tests the derivative independently of the returned force.

**Jacobian / chain rule:** the derivatives that describe how one computed coordinate changes when a real coordinate changes. They determine how a cap's force reaches its parents.

**Regression test:** a check that previously correct behavior still works after a change. Deliberately introducing a known mistake also tests whether the check can detect it.

**Overlap / effective samples:** overlap describes whether the sampled configurations represent the states being compared. Effective sample counts account for unequal contributions or correlation; many saved frames need not mean many independent observations.

**Standard error / covariance:** standard error estimates uncertainty in a reported mean or free energy. Covariance tracks shared fluctuations between estimates and matters when combining them.

**Gate / milestone / task / attempt:** a gate is a testable work package; a milestone reviews related gate results together; a task is a smaller assigned part; an attempt is one numbered worker session and its possible audit.

**Worker / auditor:** the worker implements or prepares the assigned result. The auditor independently checks the recorded snapshot and leaves actionable repair directions. Self-review is not an independent audit.
