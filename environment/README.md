# CPU setup on GitHub

Use `M00` or another work branch. A clone creates the local `.git` directory automatically; Git internals do not belong in tracked files. Repository metadata consists of the ignore/attribute/editor rules, Python package definition, PR template, Actions and dev-container configuration. No project license has been invented; the owner must choose one before redistribution claims.

## Actions

`Project 0 checks` runs documentation and dependency-light tests on branch pushes and pull requests. `G00 CPU candidate` runs on relevant changes to `M00` and permits manual dispatch on other work branches once the workflow is available on the default branch. Neither workflow commits changes. The CPU job uses Ubuntu 24.04, micromamba 2.3.3, the reviewed [candidate YAML](../ATM_MLMM_environment.yml) and [dependency consistency amendment](cpu-dependency-amendment.md), a 35-minute limit and read-only repository token permissions.

Documentation-only environment edits do not rerun the installation jobs; executable inputs do.

The CPU job runs `bash environment/bootstrap_cpu.sh`: clean solve, source-wheel archive/reinstallation, dependency consistency, OpenMM installation test, API checks and applicable pytest tests. It preserves failures rather than changing versions. The `g00-cpu-<commit>-<attempt>` artifact contains full logs, environment manifest, Conda explicit package URLs/builds/hashes, immutable pip source revisions, hashed wheels and test output. Download it before the 30-day retention expires and keep it with any future qualification bundle. A failed solve has solver logs even when no environment can be captured.

The manifest distinguishes installation from molecular qualification. No approved model file is fetched or deserialized. The absence of a GPU is recorded as `not_run`; this workflow cannot qualify CUDA, neural forces or binding free energies.

## Codespaces

Open a Codespace from the work branch, selecting the repository's dev-container configuration. Its post-create script uses the same candidate and qualification driver. The development-container job builds this configuration and runs its real post-create installation and qualification lifecycle, followed by manifest validation. This tests the supplied runtime configuration; an interactive Codespace session is not provisioned by the job.

The post-create script refuses `main` and a fresh workspace is expected. For manual setup on a machine with micromamba:

```bash
git switch M00
bash environment/bootstrap_cpu.sh
micromamba run -n atm-mlmm-p0 python -m pytest -v
```

For the final command, set `ATM_MLMM_MANIFEST` to the absolute `artifacts/g00-cpu/environment-manifest.json` path; bootstrap already sets it during its own tests. Recreate environments separately after dependency changes.

## Rebuild from recorded artifacts

Extract a successful artifact on Linux x86_64. Create `atm-mlmm-p0` from its `conda-explicit.txt`, then install `pip-wheels.lock` from that directory with `--no-index --no-deps --require-hashes`. Install the exact project source commit with `--no-deps -e .` and rerun the checks. Preserve `source-origins.json`, wheel files and checksums together. Exact CPU package builds do not promise identical numerical behavior on every processor.

The live outcome and audit decisions belong only in [STATUS.md](../docs/project-0/STATUS.md).
