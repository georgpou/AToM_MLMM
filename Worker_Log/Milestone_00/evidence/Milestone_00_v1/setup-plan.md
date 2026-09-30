# M00 metadata and G00-T1 cloud setup implementation plan

> Agent execution: root implements inline; a separate reviewer audits M00 and the resulting setup. Follow AGENTS.md and the named gate; no later molecular gate is included.

**Goal:** Review M00, add essential repository metadata, and characterize the inherited CPU candidate using GitHub Actions. Codespaces reuses the same recipe.

**Architecture:** Keep the candidate YAML authoritative. A dependency-light provenance module records source/build identities; a cloud driver resolves, checks and archives the actual installation. No physical/protocol interfaces are implemented here.

**Specs:** M00 and G00-T1; S02 module ownership, S03 versioned records, S07 capability-specific evidence; ATM_MLMM_Environment.md.

## Constraints and review focus

Work only on M00; never push or merge main. Preserve submitted historical logs. Do not change candidate versions to make installation pass. CPU installation is not molecular qualification. Model asset and GPU checks remain unavailable, not passes. Source tag and package version are different identities. Missing hashes or failed solver/checks prevent profile acceptance.

## Tasks

1. Record M00 full review input hashes, ownership and the two extension walkthroughs; obtain independent design audit. Add `.gitignore`, `.gitattributes`, `.editorconfig`, minimal `pyproject.toml` and PR handoff template. Clone creates local `.git`; never track Git internals. Repair the baseline missing source heading without rewriting historical logs. Check with `python tools/check_docs.py --self-test`.
2. Write focused tests first for `capture_environment(repo_root, conda_prefix, checks)` and `check_required_apis()`. Cover absent source/build evidence, failed dependency checks, immutable source identities, missing APIs, CPU backend consistency and explicitly unavailable hardware. Verify intended failure, then implement `src/atm_mlmm/persistence.py` and G00 tests. Keep package import free of model/GPU initialization.
3. Add `environment/qualify_cpu.sh` and artifact archiving/manifest CLI. Resolve the unchanged YAML in a clean prefix on Ubuntu GitHub-hosted CPU. Preserve solver, pip check, OpenMM installation, pytest, source commits, Conda explicit URLs/builds/hashes, Python patch, replayable source wheels and file checksums. Test archived pip wheels after installation; do not call a freeze file alone a lock.
4. Add Actions for lightweight docs/provenance tests and the CPU candidate with timeouts/read-only token permissions, no main pushes, and artifacts uploaded on failures. Add Codespaces config/bootstrap using the same scripts, refusing main. Do not provision an interactive paid Codespace without need.
5. Push M00 and inspect Actions jobs/logs. Record actual outcome and raw evidence, diagnose failures without silently changing the scientific recipe. Independently audit the final setup, update only STATUS.md progress, and open an unmerged PR.

## Verification and handoff

Local: documentation self-tests, lightweight provenance tests, package import, shell syntax, JSON/YAML parsing, diff whitespace. Cloud: successful solve; pip consistency; OpenMM installation; all applicable G00-T1 API/manifest assertions; archived artifact replay. Real weights and CUDA have no execution evidence. Save Gate_00_v1_worker.md and matching independent audit; a partial installation is recorded blocked/partial rather than accepted.
