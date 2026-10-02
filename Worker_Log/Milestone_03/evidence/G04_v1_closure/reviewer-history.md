# G04 v1 reviewer dispatch history

Both actual independent reviewer API calls explicitly used `model="gpt-6-astra"`, `reasoning_effort="high"`, `fork_turns="none"`. The API exposed no deployed model version; none is inferred. Implementation and repairs belong to `/root`, not either reviewer.

The first dispatch, `/root/g04_v1_astra_audit`, reviewed frozen submission `35b48dbe0ac00e2f2270c0fb983b5e10bac9e86a` in a detached worktree. The user's five-hour usage limit interrupted it before an audit or verdict. Its four passing command captures (G04 24, full 262, analytic 261/1 deselected, G02 78) and capture helper are preserved byte-for-byte in `../G04_v1_independent/`; [preservation hashes](interrupted-review-preservation.json) identify the copy. These partial runs do not establish acceptance.

After the user resumed, `/root/g04_v1_astra_audit_resume` was launched with the same three explicit settings and fresh context on the same frozen submission, in a new detached worktree. Its [new outputs](../G04_v1_independent_r2/README.md) independently rerun all applicable checks. The actual completed [Gate_04_v1_audit.md](../../Gate_04_v1_audit.md) records **accepted_for_scope for full G04, all three tasks and all seven stable assertions**. The integrator copied its audit and evidence verbatim; [copy hashes](independent-copy-manifest.json) verify reviewer authorship. No model substitution or self-review supplied the decision.

The worker v1 submission and inherited evidence remain immutable. The review run number distinguishes an interrupted process from the worker attempt; it does not revise the implementation or manufacture an audit for the interrupted run.
