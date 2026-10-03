# G05 v4 independent GPT-6.1 Sol / max audit evidence

Canonical decision: [Gate_05_v4_audit.md](../../Gate_05_v4_audit.md). Reviewer was independently dispatched with fresh context and the user's selected model/reasoning. This directory is new reviewer evidence; production source/data and HEAD are unchanged. No real quantum calculation or finalized coordinator was run.

[audit-start.json](audit-start.json) identifies the initial clean tree and all exact commits. [final-state.json](final-state.json) checks the final tree and submitted hashes. All command receipts contain argv, cwd, UTC times, elapsed time and exit. `run_check.py` writes receipts/logs exclusively. Standard source tests run synthetic recovery stubs only; all real QM records are read from the frozen fixture.

| Receipt | Output | Purpose |
|---|---|---|
| [full-source.json](full-source.json) | [full-source.log](full-source.log) | 312 source tests |
| [focused-g05.json](focused-g05.json) | [focused-g05.log](focused-g05.log), [fresh captures](fresh-g05-captures/) | 18 G05 cases with independent new raw captures |
| [strict-environment.json](strict-environment.json) | [strict-environment.log](strict-environment.log) | 9 exact environment/documentation checks; external prefix output path retained in log |
| [docs-self-test.json](docs-self-test.json) | [docs-self-test.log](docs-self-test.log) | Initial documentation check and eight checker self-tests |
| [integrity-v3.json](integrity-v3.json) | [integrity-v3.log](integrity-v3.log), [integrity-results.json](integrity-results.json) | Canonical independent input/source/data/log/receipt/resource verification |
| [reference-runtime.json](reference-runtime.json) | [reference-runtime.log](reference-runtime.log) | Reference Python version and installed basis hash query, no calculation calls |
| [scientific-recompute-v2.json](scientific-recompute-v2.json) | [scientific-recompute-v2.log](scientific-recompute-v2.log), [scientific-results-v2.json](scientific-results-v2.json) | Independent primitive-array arithmetic and 34-row/28-projection/12-control/sign checks |
| [total-domain.json](total-domain.json) | [total-domain.log](total-domain.log), [total-domain-results.json](total-domain-results.json) | Total physical energy/full-real forces on all 36 saved domain rows |
| [recovery-contract-probes.json](recovery-contract-probes.json) | [recovery-contract-probes.log](recovery-contract-probes.log), [test source](test_recovery_audit.py) | Three expected-contract failures establishing R1–R3 |
| [final-docs.json](final-docs.json) | [final-docs.log](final-docs.log) | Documentation check after adding audit/guide |

The synthetic recovery probes retain new immutable attempt orders, records, receipts and observed facts under `recovery-probes/`. Mutable progress files there belong to isolated test fixtures and reflect the exercised resumes; no submitted attempt was modified. Each expected-contract test failed after reaching its intended assertion. Probe worker executables are explicit stand-ins, never Psi4 or the locked reference interpreter.

- [R1 observed known nonzero exit](recovery-probes/known-nonzero/observed.json): exit 23 becomes null/ready on resume.
- [R2 observed launch/checkpoint gap](recovery-probes/spawn-checkpoint-gap/observed.json): duplicate attempt while first worker remains live; the synthetic orphan is killed by probe cleanup.
- [R3 observed fsync order](recovery-probes/record-fsync-order/observed.json): no promoted record bytes fsynced before durable progress.

The probes use fixed new subdirectories to preserve evidence exclusively and must be run in a **new evidence directory** for replay; they refuse to overwrite these artifacts. Future regression copies should be parameterized with fresh fixtures. Their failures specify required closure behavior; no fixes were made.

Earlier reviewer script errors remain preserved: [integrity.log](integrity.log) failed on an incorrect local path assumption; [integrity-v2.log](integrity-v2.log) incorrectly assumed SCF energy excluded D3; canonical v3 uses the separately recorded functional energy. [scientific-recompute.log](scientific-recompute.log) failed serializing a NumPy boolean after all assertions and left a partial `scientific-results.json`; canonical complete results are `scientific-results-v2.json`. These outputs do not invalidate the scientific records.

[reference-import-side-effect.json](reference-import-side-effect.json) documents the sole unexpected root artifact. [reference-import-timer.dat](reference-import-timer.dat) preserves the exact timer emitted by Psi4 import/exit during version/basis inspection; there are no quantum-module call entries.

Source scripts: [integrity_check_v3.py](integrity_check_v3.py), [scientific_recompute_v2.py](scientific_recompute_v2.py), [total_domain_check.py](total_domain_check.py), [test_recovery_audit.py](test_recovery_audit.py). All scientific shells activate `/workspace/atom-mlmm-g05-v2/activate.sh`; reviewer scripts set repository and `src` on PYTHONPATH.
