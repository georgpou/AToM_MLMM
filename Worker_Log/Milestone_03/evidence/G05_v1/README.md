# G05 v1 software evidence and explicit chemical blocker

Base `bc788aeeedb4dc45026ac1bff44bd4fb533b325a`, child
`m03-reference-g05`; all earlier gate artifacts remain unchanged.

The compressed command captures record actual command, cwd, current HEAD,
timestamps, exit, complete stdout/stderr. `source-input-manifest.json` identifies
the preliminary T1/T2 submission; later manifests explicitly identify their
own source scope. No capture is overwritten to hide a failed or inadequate
attempt. `setup-and-lineage.json` records original protected branch tips and
isolated unchanged-installer setup; main/Amber remain separate.

| Stable assertion | Actual current evidence | Scope/status |
|---|---|---|
| P0-TEST-G05-01 native/OpenMM | `software-v4/raw-Reference.json`, `raw-CPU.json` | Software numerical checks pass |
| P0-TEST-G05-02 real cap parents | `software-v4/projected-Reference.json`, `projected-CPU.json`, `finite-differences.json`, `nested-atm.json` | Independent raw autograd, full real cap Jacobian + retained MM, native nested ATM pass |
| P0-TEST-G05-03 local additivity | `software-v4/locality.json` | Disconnected ML contribution only; actual contact cross edges and deliberate split-graph negative |
| P0-TEST-G05-04 invariances/maps | `software-v4/transformed.json`; nonidentity case in 15-test capture | Native/adapter joint transforms, atom order and actual final-map checks pass |
| P0-TEST-G05-05 domain/alternate map | `software-v4/domain-scans.json` | All 36 samples saved; 34 admitted numerical samples, two extreme diagnostics; no chemical adequacy follows |
| P0-TEST-G05-06 offline reload | `software-v4/offline-serialized-reload.json`; asset-loading captures | Moved source/asset root, original checkout denied, empty caches, DNS/connect denied, exact identity/full forces pass |
| P0-TEST-G05-07 conformer quantum | `chemical-reference-pending.json.gz` and full-run captures | **Pending actual agreed/reviewed quantum data**, explicit failure before model evaluation |
| P0-TEST-G05-08 contact quantum | same pending captures | **Pending actual agreed/reviewed quantum data**, explicit failure before model evaluation |

Software cases use the inherited chemically neutral methane cap fixture to
qualify graph/units/order/derivatives/serialization. The independently reviewed
34-row ethanol/butane/methanol/acetamide proposal and ten quantum rotation
controls remain unscored. Metadata admission always reports qualified=false.
No GPU, periodic, electrostatic, protein binding or complete-workflow claim.

The near-coincident diagnostic is finite but pathological: model energy about
2.32e8 kJ/mol and maximum real force about 3.79e21 kJ/mol/nm at map0. Its
coordinates, all edges and forces are preserved, and it is excluded from the
admitted numerical domain before any chemical claim. Ordinary methane
compression from 4 to 3 angstrom raises the ML energy and gives an outward
ligand force. This characterization adds no repair force or clipping.

The original 1.17 angstrom software cap and every inherited numeric tolerance,
retained-MM ledger and full-force/map/routing invariant remain unchanged.
New chemical fixture cap1.09 angstrom is a separate predeclared input, never a
post-score adjustment. Independent M00 v2/v3 reports remain under Milestone_00.

The quantum generation/metric code is prepared, with missing-data, fixed-zero,
localized-force-maximum and missing-atom/broadcast regressions. These known
number tests are **not chemical evidence**. The generation coordinator rejects
the actual pending user-decision record before starting a quantum worker or
creating a reference attempt. Runtime generation and comparisons remain
unexecuted. The final full-gate audit must follow actual T4 data and comparisons.
