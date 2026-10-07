# Exchange analysis and relative binding handoff

`design.json`, `seeds.json`, and `expected.json` freeze the bounded S05/S06
synthetic control before its qualification run. The model uses the one
dimensional harmonic distribution

```text
U0(x) = 0.5 k x^2
U1(x) = 0.5 k (x + d)^2
Uoutside(x) = 0.5 kr x^2
x | lambda ~ Normal(-lambda*k*d/(k+kr), RT/(k+kr))
```

with `k=100`, `kr=50` kJ mol-1 nm-2, `d=0.3` nm, and `T=300 K`. The frozen
known answers are `B-A = +1.5`, reversal `A-B = -1.5`, and zero restraint
`0` kJ/mol. The dependent controls use AR(1) `rho=0.5` plus shared innovation
variance fraction `0.5`; the independent baseline uses both values zero. Each
qualification design has 12 independent seeds, 4096 synchronized frames per
run, 32-frame blocks, and 64 draws. `expected.json` stores the numeric
thresholds and calculations. These are synthetic analytic checks only; they do
not establish scheduler mixing, molecular convergence, adequate production
sampling, molecular binding, or G08 acceptance.

## Exchange-analysis API

The opt-in path consumes existing `EvaluationRecords`; it does not produce
exchange decisions or alter the legacy fixed-state `analyze` path. For a
persistent run, `retained-window-evidence.json` is a sidecar with this shape:

```json
{
  "format": "exchange-retained-window-v1",
  "version": 1,
  "source_kind": "persistent_multistate_journal",
  "run_id": "run-001",
  "boundary_source": "path/to/verified-run-journal",
  "retained_frames": [["run-001:w0:b17", "run-001:w1:b17"]],
  "excluded_frames": [["run-001:w0:b1", "run-001:w1:b1"]],
  "selection_evidence": "predeclared equilibration window selection record",
  "independent_initialization_evidence": "path or identity of independent initialization"
}
```

The frame lists above are schematic and must cover the actual selected and
excluded boundaries. `boundary_source` points to the persistent journal, whose
metadata must match the schedule, physical, transfer, restraint, and run
identities in the raw records. The analyzer reopens that journal with
`read_multistate_boundaries`, reconstructs every source frame, and checks every
sample ID, walker, state, sequence number, raw potential, outside energy, and
observed total against `EvaluationRecords` before applying the retained
window. Frame groups must be derived from those verified boundaries; array
position alone is not provenance. The sidecar also records a contiguous
retained window and its complementary excluded frames. The production-journal
adapter is implemented but was not exercised on a molecular history in this
batch.

An existing producer/loader supplies `records` as the complete
`EvaluationRecords`. The retained frame groups in the sidecar become the
`synchronized_frames` argument; construction alone does not establish their
provenance because `analyze_exchange` verifies them against the sidecar and
journal:

```python
import json
from pathlib import Path

from atm_mlmm.exchange_analysis import analyze_exchange
from atm_mlmm.schema import ExchangeAnalysisInput, ExchangeResamplingSpec

sidecar = "run-001/retained-window-evidence.json"
document = json.loads(Path(sidecar).read_text())
history = ExchangeAnalysisInput(
    records=records,  # complete raw EvaluationRecords from the verified producer
    synchronized_frames=tuple(tuple(frame) for frame in document["retained_frames"]),
    run_id=document["run_id"],
    retained_window_evidence=sidecar,
)
resampling = ExchangeResamplingSpec(
    method="synchronized_blocks",
    block_length_frames=32,
    bootstrap_replicates=64,
    seed=77031,
    design_evidence="fixtures/analytic/exchange-analysis-v1/design.json",
)
result = analyze_exchange(
    (history,), thermodynamics, resampling=resampling, estimator="pymbar"
)
```

Use `method="independent_runs"`, `block_length_frames=None`, and at least two
independently initialized complete histories to resample whole runs. It does
not add a second block variance. Every original raw record, including excluded
observations, is validated before selection. Bootstrap multiplicities retain
their original sample IDs; failed draws are included in the raised
qualification error and withhold covariance. Diagnostics distinguish iid
weight contributions from resampling units, report state/walker visits,
overlap, solver residuals, raw/retained/excluded IDs, and separate across-run
spread from mean standard error. Full/last-half estimates share trajectory
samples and are dependent diagnostics, not convergence evidence. Linked
correction uncertainty remains unresolved unless linked observables and a
valid joint covariance are supplied.

## Relative binding and correction ledger

`relative-binding-template.json` is a concrete schema-version-1.0
`ThermodynamicSpec` serialization for `Gbind(B)-Gbind(A)`. The declared
endpoint weights are `B=+1`, `A=-1`; therefore a negative final result favors
B. The six molecular corrections—translation standard state, bound release,
orientation, conformation, state counting, and midpoint bridge—are all
`required_uncomputed`, with null values and errors. `standard_volume_nm3` and
the endpoint/domain/restraint/state-counting descriptions are explicit
placeholders to be replaced with evidence-backed definitions. They do not
resolve standard-volume cancellation or any correction.

Every resolved additive correction needs evidence, a value, and a
nonnegative standard error. Shared or otherwise uncertain corrections also
need the joint-covariance contract; absent a valid covariance, the final value
and error remain null. The `BindingResult` admission path verifies the
correction ledger, thermodynamic identity, final sum, sign definition, and
joint-covariance obligation during construction and deserialization. The
analytic `A->A` test checks zero-compatible equilibrium free-energy difference
while allowing nonzero instantaneous perturbations; the reversal test checks
the declared `B_minus_A` sign. Neither is a molecular closure result. The
general contract that refuses a closure claim for unmatched physical states
is not implemented or qualified: there is no endpoint metadata schema or
closure-comparison service in this batch. The tested relative free-energy path
requires a shared thermodynamic domain/restraint definition, but that does not
prove that two endpoint physical states match for closure.
