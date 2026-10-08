# Benchmark validation evidence

Final verification used one stable runtime source snapshot on 2026-10-08 UTC.
Large molecular outputs remain in `/workspace/fkbp-final-validation` and
`/workspace/fkbp-mm-validation`, outside the repository.
Compact log copies remove incidental trailing spaces; raw command output remains
in the external validation logs. Molecular inputs and the upstream licence retain
their exact original bytes.

| Evidence | Meaning |
|---|---|
| [validated-files.json](validated-files.json) | Final source/input/test identities; matches independent review and sealed molecular setup |
| [reviewed-files.json](reviewed-files.json), [independent-review.json](independent-review.json) | Independent source review and repair findings |
| [cpu-suite.log](cpu-suite.log) | 713 passed, 57 deselected; stable-source CPU suite |
| [focused-final.log](focused-final.log), [model-compatibility.log](model-compatibility.log) | 26 focused tests; two real-model compatibility tests |
| [setup-summary.json](setup-summary.json) | All three complete-ligand cavity setups, caps and initial bulk clearances |
| [mm-preparation.json](mm-preparation.json), [mm-production.json](mm-production.json), [mm-production-summary.log](mm-production-summary.log) | Actual MM control preparation and short upstream scheduler run |
| [cavity-preparation-summary.json](cavity-preparation-summary.json), [cavity-preparation.log](cavity-preparation.log) | Successful ordinary minimization and stock preparation; six finite states and exact fixed cells |
| [cavity-production-summary.json](cavity-production-summary.json), [cavity-production-summary.log](cavity-production-summary.log) | Native MACE force in spawned AToM CPU worker; finite short samples, fixed cells and replica exchanges |
| [cleanup.json](cleanup.json) | Deleted historical file/byte count and retained-byte preservation check |
| [documentation.json](documentation.json) | Final documentation check and eight checker self-tests |

Receipts bind setup, preparation, state and production identities. Red-test logs
retain the interruption, centroid and timestep failures that drove the repairs.
The one-minute capped production run sampled 11 of 22 scheduled replicas; it
does not establish equilibration, mixing or a binding estimate.
