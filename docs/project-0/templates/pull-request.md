# Pull request checklist

**Assigned task and scope:** [Task path and IDs]\
**Worker log:** [Actual path]\
**Audit log:** [Actual path, or pending; do not invent a review]\
**Implementation snapshot:** [Commit or documented patch/base]\
**User-visible effect:** [What changes and why]

- [ ] Only the assigned code, tests, and necessary documentation changed.
- [ ] The required specification is reviewed; any changed scientific meaning is recorded.
- [ ] Focused tests and affected earlier tests are documented with real results.
- [ ] Missing hardware, model files, or checks remain visible.
- [ ] Shared interfaces still support the admitted one-/two-group and environment-force cases.
- [ ] No secrets, restricted weights, or large raw trajectories are included.
- [ ] Worker/audit history was not overwritten. Status changes match their evidence.

Do not equate opening or merging this request with whole-gate acceptance. The audit must state what it actually checked.
