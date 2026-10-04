# G08 record admission — additive implementation decisions

**Status:** proposed for the exact G08 independent review; no earlier acceptance is changed.

**Rationale:** S03 plans thermodynamic/observation/result records but does not
pin their constructor field names. G08 requires those records to make signs,
raw energy scope, corrections and uncertainty explicit. This amendment records
the new shared-field admission policy without changing any existing serialized
record, physical Hamiltonian, units, caps, schedule expression or tolerance.

**Affected contracts:** S03 shared records; S05 binding definition, standard
translation and midpoint signs; S06 sampling/covariance. Requirements
P0-REQ-016/017/018/019/030 and all six G08 assertions. Prior M01/M02 and G04-G07
evidence is retained; the full available CPU regression checks their coexistence.

## New record types

- `EvaluationRecords`: complete schedule; unique sample IDs; actual sampled
  states; walker IDs and increasing sequence numbers; raw u0/u1/outside and
  observed sampling-state total in kJ/mol; physical/transfer/restraint identities;
  nonempty provenance; explicit independent/correlated sampling mode.
- `CorrectionRecord`: correction ID, one of S05's four statuses, optional value
  and standard error in kJ/mol, and evidence. Uncomputed entries have no value
  or error. Resolved entries need evidence; demonstrated-zero/not-applicable
  entries have exactly zero value and error.
- `ThermodynamicSpec`: observable, gauge-invariant endpoint weights, sign
  convention, explicit state graph and endpoint descriptions, correction
  obligations/records, standard volume, and descriptions of domains, restraints,
  orientation and state counting. No sign is inferred from paths or upstream
  leg labels. Initial final-standard observable admission is bound-minus-bulk
  ABFE accounting; restrained endpoint and B-minus-A differences are supported.
  A complete molecular standard RBFE definition remains later scope.
- `BindingResult`: restrained value/error, correction ledger, unresolved entries,
  optional final value/error, thermodynamic identity and diagnostics. Missing
  obligations or missing required covariance withhold the final pair.

For final standard ABFE, the policy requires explicit correction IDs
`translation_standard_state`, `bound_release`, `orientation`, `conformation`,
`state_counting`, and `midpoint_bridge`. This checklist prevents an empty
obligation tuple from defining a final quantity. Each entry can be computed,
demonstrated zero or not applicable with evidence; it does not impose a new
physical correction on systems where cancellation is demonstrated.

Joint covariance orders supplied state free energies then resolved corrections
in their recorded order. Its state block must match the estimator covariance,
and its correction diagonal must match each recorded standard error. All cross
terms enter the final weighted variance. Without joint covariance only
deterministic corrections may be added to a final value/error.

## Initially admitted numerical paths

All reduced potentials are reconstructed using the existing exact schedule,
temperature and units; observed totals must agree within 1e-8 kJ/mol. The
finite-wall volume supports explicitly justified separable infinite-space
translation only; periodic/coupled domains reject rather than using a hard sphere.

PyMBAR 4.0.3 and AToM 8.5.0b0 receive identical dimensionless states/counts.
The upstream Python UWHAM default optimizer's measured normalization residual
was 3.0026e-4. Its exact objective/gradient/Hessian are independently refined
before the pinned core computes weights/Fisher covariance. This changes solver
accuracy, not its equations or data. State constants are removed/restored as a
gauge. Normalization residual <=1e-8 and stationary gradient <=1e-10 are required;
same-input free energies agree within 1e-8 dimensionless on the demonstrated
fixture. Direct-exponential canonical density ratios outside +/-600 reject as
an unqualified numerical range. Every declared state must have samples in this
initial profile. Disconnected measured support at overlap threshold 1e-10 rejects.

The initial correlation path supports fixed-state walker histories, preserving
raw input before thinning. It uses the maximum measured inefficiency of u0, u1,
u1-u0 and outside energy. Correlated exchanging histories require later block/
resampling qualification and explicitly reject. Effective contributions below
100 trigger an investigation flag; this is not a universal convergence law.

## Compatibility, tests and reviewer decision

These are additive schema-1.0 record types. Older readers reject unknown types
through the existing policy; existing record payloads/digests are unchanged.
No automatic conversion or reinterpretation of earlier units/records occurs.

Tests: `tests/unit/test_restraint_volume.py`, `tests/unit/test_schedule.py`, and
`tests/sampling/test_analytic_free_energy.py`, plus the full CPU suite. New
numerical/correction/state faults are preserved in the G08 worker evidence.

Reviewer decision is pending the matching G08 audit on the exact submission.
