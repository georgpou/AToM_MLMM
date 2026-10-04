# G07 reference execution plan

The user supplied the execution method, frozen specification and authorization on 2026-10-04. Work directly on m03-g06-g07 at 34388d2; no child or additional worktree. The implementation is bounded queue adaptation, with no scientific change.

- [x] Verify clean checkout, starting commit, branch tracking and actual cgroup CPU/RAM/swap/disk; freeze preservation hashes and separate authorization.
- [ ] Rebuild the 105 exact reference packages, verify all installed artifact hashes and basis hashes, and record activation and environment provenance.
- [ ] Add tools/resume_joint_quantum.py, consuming the frozen matrix and separate authorization. Give tools/resume_neutral_quantum.py optional validator/queue/resource-policy hooks with unchanged G05 defaults. Keep quantum_worker_guard.py and the scientific generator unchanged. Use all 30 identities for pilot and continuation checkpoints; require a hash-bound measured pilot assessment to continue.
- [ ] First write and run failing tests for exact 30-job scheduling, input/authorization tamper rejection, pilot ceiling, tighter RSS/disk guards, failed-receipt rejection, cumulative resume budget and concurrent lease rejection. Rerun the inherited recovery/interruption cases after implementation. Independently audit the new code using GPT-6.1-sol/MAX before launch.
- [ ] Start ethanol-methanol-d3-r0--full-parent with 2 threads / 3 GiB; sample every second, stop above 6 GiB process-group RSS or below 5 GiB free disk, track cgroup limit/events/pressure separately from reclaimable cache. Stop after pilot for measured assessment; all charged sessions share 86400 s and pilot attempts share 3600 s.
- [ ] If the measured pilot supports the remaining resource/time envelope, continue under the same attempt/accounting. Otherwise preserve a concrete blocked checkpoint; never change settings/limits.
- [ ] Validate finite gradients/energy, explicit SCF convergence, identities/units/provenance, immutable G05 bytes and every completed receipt. If complete, report within-description contact-minus-separated attribution and once-projected Qcap plus all retained-MM forces. Preserve all seven sensitivity failures and controls.
- [ ] Record actual results in Gate_07_v2_worker.md and STATUS; independently audit applicable new evidence. Commit and normal-push only m03-g06-g07; verify remote SHA.

Failure focus: mismatched matrix or frozen input; receipt known nonzero; coordinator loss during spawn/authorization; duplicate coordinators; resumed budget or pilot ceiling reset. Synthetic records remain software tests only.
