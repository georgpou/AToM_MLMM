# Development guide

Start with the assigned gate's assertions and the current [status](project-0/STATUS.md). M01 implements dependency-light records, identity/partition/protocol descriptions, capability/evidence checks and the original-MM inventory under `src/atm_mlmm/`. M02 implements the shared analytic physical/ATM evaluators, complete transfer maps, production schedule, preparation/export ownership and pinned AToM routing adapter, with independently reviewed admission safeguards. Its checks span `tests/contracts/`, `tests/integration/` and `tests/workflow/`. Follow the [G04 handoff](project-0/handoffs/M03-G04-fresh-agent.md) on a new child of `m02-analytic-atm`; cap building, retained-MM boundary dispositions and later physical modules remain with their owning gates. Existing regressions cover CPU loading policy and Cloud setup fallback under `tests/environment/`, plus the local-weight [MACE link example](../examples/README.md) under `tests/integration/`.

## Environment and imports

Install and activate using the [CPU guide](../environment/cloud-cpu/README.md). Main Python has NumPy 2, OpenMM, PyTorch CPU, MACE, TorchANI, ASE, OpenMM-ML, OpenFF, openmmforcefields, AToM and PyMBAR. AmberTools has its own Python/NumPy 1.26 prefix; main activation exposes its preparation executables without switching main Python.

| Work | Installed imports/tools | Boundary |
|---|---|---|
| G00 APIs; G01 records and identity | Python standard library, `numpy`, `importlib.metadata`; `openmm` for API checks | Schema/identity/protocol records import without OpenMM or ML libraries. |
| G02 native ATM and G03 routing | `import openmm as mm`; `from openmm import app, unit`; `mm.ATMForce`, `mm.PythonForce`; pinned `atom_openmm` source | Keep AToM-specific classes, keys and conversions in `adapters/atom.py`. |
| G04 caps and G06 MM ledger/PBC | OpenMM `System`, virtual sites, `XmlSerializer`, NumPy | Validate energy derivatives on real coordinates and enumerate retained/removed terms. |
| G05 model adapter | `from openmmml import MLPotential`; ASE `Atoms`; PyTorch autograd; pinned MACE calculator or TorchANI | Import inside model adapters. The approved academic MACE-OFF23-small checkpoint is bundled for the link example; full real-model qualification still belongs to the gates. |
| G07 composed physical/ATM evaluation | Earlier physical builder, protocol and ATM modules | Reuse their records and checker for one/two groups; add no separate engine. |
| G08 thermodynamics and estimators | NumPy/SciPy; `from pymbar import MBAR`; pinned AToM UWHAM | Compare to quadrature and independent samples; keep signs and corrections explicit. |
| G09 preparation | `from openff.toolkit import Molecule`; `from openmmforcefields.generators import GAFFTemplateGenerator`; OpenMM `app`; Amber `antechamber`, `parmchk2`, `tleap`, `sqm` | Use main OpenFF with separate Amber executables; call Amber Python tools through its interpreter. |
| G10-G12 workflows | Pinned AToM sources, OpenMM State/checkpoint APIs, MDTraj, the common physical/protocol/analysis modules | Preserve physical identity, active forces, raw records and correction obligations. |
| G13 release | `pytest`, timing/profiling tools, saved manifests and fixtures | Benchmark the admitted profile; qualify any optimization against the same Hamiltonian. |

Inspect installed APIs and the full pinned sources under `<setup-prefix>/sources/` when integrating upstream code. [S02](project-0/specs/S02-architecture-and-dependencies.md) defines module ownership; [S03](project-0/specs/S03-data-and-interface-contracts.md) defines records and units. Package versions alone do not establish numerical behavior.

For the analytic metadata profile, `EmbeddingSpec` uses `kind="mechanical"`, `policy_version="1"`, `boundary_policy="protein_c_c"` and `periodic_convention="nonperiodic"`. Both analytic model descriptions use `output_energy_convention="declared_relative_energy"`; `analytic-local` declares `locality="local"`, while `analytic-environment` declares `locality="environment_dependent"`. These descriptions preserve the common kJ/mol convention and explicitly identify the MM dependence of the architectural probe. Unknown policy or model semantics are rejected; an admitted description still reports `qualified=False` until its owning numerical gate supplies evidence.

## G04 boundary builder

`hybrid.build_physical(original, partition, model, embedding, *, probe, cap_distance_nm)` implements the narrow analytic nonperiodic mechanical path. It consumes a hash-identified `SystemInput` and an inherited resolved one-cut protein partition, rechecks selection/connectivity, and uses a registered analytic model through the actual OpenMM-ML mechanical builder. `models/analytic_boundary.py` returns raw cap/partner/MM derivatives; `embeddings/mechanical.py` consumes `oldToNew`, actual final topology/site parents, and constructed site parameters. `ledger.boundary_dispositions` diffs complete original/retained parameters rather than duplicating upstream selection predicates. The physical manifest saves both MM descriptions and all term dispositions; hybrid energy is retained MM plus model.

`PhysicalBundle.links` is an additive tuple of `LinkRecord`s, with cap ID, both real parent IDs, final/model indices, actual site type and distance. `model_input_ids` orders fixed real ML IDs followed by caps; `model_to_final` covers that complete order. Empty links are omitted from canonical JSON, preserving old schema-1.0 real-only artifact and transfer identities. Capped records require `boundary_builder_version=1`; future versions, unidentified derived particles, inconsistent links/maps and independent cap mass reject. Inert JSON decoding stays separate from explicitly trusted, hash-checked executable loading. The shared evaluator reconstructs virtual sites after every coordinate assignment. Native machinery projects forces once, including inside ATM; the measured G04 diagnosis needs no internal-site copying or manual production projection.

Run all seven stable G04 assertions and their additional regression controls with `python -m pytest tests/integration/test_link_geometry.py tests/integration/test_boundary_ledger.py -v`. The required FD steps remain 1e-3, 1e-4 and 1e-5 nm. Full retained-GAFF checks add 1e-6 nm to attain the same strict 1e-5 component target; the S06 RMS bound remains unchanged. Isolated analytic cap Jacobian energy/force checks use 1e-8/1e-7 and mapped direct/ATM checks use 1e-4/5e-3. This qualifies analytic boundary behavior only, with the exact scope/decision in STATUS.

## Source and test layout

Create implementation modules under `src/atm_mlmm/` according to S02 and the gate's paths. `pytest.ini` adds `src` to Python's test import path, so testing source code does not require changing the locked package inventory. For direct development commands use:

```bash
PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}" python your_script.py
```

When packaging the implemented project later, add its package metadata in the release scope. An editable project install adds a distribution beyond the baseline inventory; account for that explicitly rather than weakening the dependency locks.

Use `tests/unit/` for small pure checks, `tests/contracts/` for shared invariants, `tests/integration/` for backends, `tests/workflow/` for preparation/routing/restart and `tests/sampling/` for estimators/sampling. Put hand-inspected small inputs and frozen reference data under `fixtures/`. Keep fixture identities, chemical states and reference provenance with the data. Compare calculations to independent expectations rather than copying the function under test into the expected value.

## Commands

Run from the repository root after main activation:

```bash
# All available project tests, including the bundled academic MACE example.
python -m pytest -q

# CPU work without deferred weights, GPUs or long sampling.
python -m pytest -m "not gpu and not model_assets and not slow" -q

# After implementation, use the precise node listed in your assigned gate.
# Example: python -m pytest tests/unit/test_identity.py::test_chain_insertion_and_permutation_identity -v

# Complete environment, preparation, upstream regression and documentation checks.
python /workspace/.onboarding/atom-mlmm/validate.py --repository "$PWD"

# Local links/headings; useful after documentation changes.
python tools/check_docs.py --self-test
```

Substitute a custom setup prefix in validation commands. Register model/GPU/extended-sampling tests with `model_assets`, `gpu` or `slow`. A deselected or skipped test leaves its profile unqualified. Verify actual collection and test counts; planned gate nodes become executable only when implemented. The full CPU suite includes new unit/contract/integration tests as you add them.

The installed upstream AToM regression can be run separately:

```bash
cd /workspace/.onboarding/atom-mlmm/sources/AToM-OpenMM
python -m pytest -q tests/test_uwham.py
```

It is one test covering three reference datasets; preserve upstream collection configuration. Passing it does not qualify the new ML/MM code.

## Scientific work and records

### G08 analytic thermodynamics

`EvaluationRecords` saves explicit sample/state/walker identities and sequences,
raw u0/u1/outside/observed-total energies, the complete schedule and provenance.
`schedule.reduced_potentials` reconstructs the admitted expression at every
state and checks observed totals. `analysis.analyze` uses PyMBAR 4.0.3 or the
pinned AToM Python UWHAM objective through `adapters/atom.py`; both receive the
same dimensionless states and counts. UWHAM's independent objective refinement
uses its exact gradient/Hessian, avoiding the default optimizer's insufficient
normalization. State constants are removed and restored explicitly; data are
never clipped. The pinned direct-exponential UWHAM profile rejects density
ratios beyond its declared finite numerical range.

`ThermodynamicSpec` supplies endpoint weights, state connections, endpoint/domain,
restraint/orientation/state-counting descriptions, standard volume and correction
obligations. The new records are additive schema-1.0 types; existing serialized
records and their identities are unchanged. Standard binding uses the S05
bound-minus-bulk convention and requires explicit entries for translation,
bound release, orientation, conformation, state counting and midpoint connection.
Missing/uncomputed corrections withhold a final result. Evidence-backed zero
and not-applicable entries require proof. Uncertain corrections need joint
covariance with state estimates; independent errors are not silently assumed.

The initial correlation profile thins fixed-state walker histories using the
largest measured statistical inefficiency among both endpoints, their difference
and the outside term. It preserves all original observations and validates them
before thinning. Exchanging correlated walkers explicitly require later block/
resampling qualification. Overlap and effective contributions are diagnostics,
not proof of chemical accuracy or complete conformational sampling.

The bounded known-answer example saves immutable attempts, complete frames,
full real forces, raw records and identities:

```bash
source /workspace/atom-mlmm-g08-r2/activate.sh
PYTHONPATH="$PWD/src" python examples/g08_known_answer.py --output /tmp/new-g08-attempt
python -m pytest tests/sampling/test_analytic_free_energy.py tests/unit/test_schedule.py tests/unit/test_restraint_volume.py -v
```

Use the actual installed setup prefix. This analytic Reference/NVT example
does not define a molecular standard binding free energy.

Freeze the relevant M00 decisions before implementation: Hamiltonian, cap rule, units, force ownership, maps, supported chemistry, ensemble, corrections and numerical/reference limits. Keep the existing cap Jacobian, midpoint bridge and restraint-volume definitions. Run structural and analytic tests before a real-model or protein calculation. [S06](project-0/specs/S06-validation-and-tolerances.md) supplies numerical and chemical-reference checks; each gate owns its planned assertions.

Keep one short [worker log](project-0/templates/worker-log.md) per task with exact commands/statuses and the tested profile/snapshot. Update STATUS, then continue from the completed predecessor. Review the implemented gate/milestone on its combined snapshot; do not create another documentation-audit cycle. Earlier documentation and environment-audit artifacts remain in Git at `ecd2c90bc67a8f9b6a5ab35e3da0e9cdeca89368` if a specific historical investigation needs them.
