"""Deterministic design-audit evidence; no Context, model load, or integration.

The finite permutation calculation is an independent mathematical reference,
not scheduler code. Only unchanged RNG helpers and the pinned upstream scalar
decision are exercised. Runtime multistate assertions remain unexecuted.
"""
from fractions import Fraction
import hashlib
import inspect
import itertools
import json
import math
from pathlib import Path
import random
import subprocess

import numpy as np

BASE = "3952a9b36a92e37f0f98fdf3981c9320368a18b3"
HEAD = "678aa3e2db9d5f77517ad8cfb278ac8a4df7032d"
DESIGN = "179c3035c6b70293811b6dd6e24319fd9ac932db"
ROOT = Path.cwd().resolve()  # Run from the reviewed repository or its frozen checkout.


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


inspection_head = git("rev-parse", "HEAD").decode().strip()
subprocess.run(["git", "merge-base", "--is-ancestor", HEAD, inspection_head],
               cwd=ROOT, check=True)
subprocess.run(["git", "diff", "--quiet", HEAD, "--", "src", "tests", "fixtures",
                "environment", "models", "Worker_Log/Milestone_05/Gate_10_v3_worker.md",
                "Worker_Log/Milestone_05/evidence/G10_v3/implementation-plan.md",
                "docs/project-0/specs/g10-multistate-runtime-amendment.md"],
               cwd=ROOT, check=True)
subprocess.run(["git", "merge-base", "--is-ancestor",
                "2c02cc2713924140a82aefda37fd5885747e5837", HEAD],
               cwd=ROOT, check=True)
changed = git("diff", "--name-only", BASE, HEAD).decode().splitlines()
assert set(changed) == {
    "Worker_Log/Milestone_05/Gate_10_v3_worker.md",
    "Worker_Log/Milestone_05/evidence/G10_v3/implementation-plan.md",
    "docs/project-0/STATUS.md",
    "docs/project-0/specs/g10-multistate-runtime-amendment.md",
}
subprocess.run(["git", "diff", "--quiet", BASE, HEAD, "--", "src", "tests",
                "fixtures", "environment", "models"], cwd=ROOT, check=True)
assert git("diff", "--name-only", DESIGN, HEAD).decode().splitlines() == [
    "Worker_Log/Milestone_05/Gate_10_v3_worker.md"]
diff = Path("/workspace/g10-design-review.diff").read_bytes()
assert diff == git("diff", BASE, HEAD)
inventory = {str(p.relative_to(ROOT / "src/atm_mlmm")): sha(p.read_bytes())
             for p in sorted((ROOT / "src/atm_mlmm").rglob("*.py"))}
fixture_summaries = []
for kind in ("abfe", "rbfe"):
    fixture = ROOT / "fixtures/solvated_fragment/v2" / kind
    config = json.loads((fixture / "config.json").read_text())
    manifest = json.loads((fixture / "manifest.json").read_text())
    assert sha((fixture / config["input_manifest"]).read_bytes()) == config["input_manifest_sha256"]
    for name, digest in manifest["files"].items():
        assert sha((fixture / name).read_bytes()) == digest
    original = json.loads((fixture / "system-input.json").read_text())["data"]
    topology = original["topology"]["data"]
    molecules = [m["data"] for m in topology["molecules"]]
    ligands = [m for m in molecules if m["role"] == "ligand"]
    fixture_summaries.append({"kind": kind, "atoms": len(topology["atoms"]),
        "ligands": [{"name": m["molecule_id"], "atoms": len(m["atom_ids"]),
                     "charge": m["formal_charge"], "multiplicity": m["multiplicity"]}
                    for m in ligands],
        "waters": sum(m["role"] == "solvent" for m in molecules),
        "temperature_K": config["settings"]["temperature_K"],
        "outside_spring_kj_mol_nm2": config["settings"]["outside_spring_kj_mol_nm2"],
        "manifest_sha256": sha((fixture / "manifest.json").read_bytes())})

# Exact finite assignment distribution: reduced energies are integer multiples
# of ln(2), making every Boltzmann weight and acceptance rational.
energies = ((0, 2, 1), (2, 0, 3), (1, 1, 0))  # rows=states, columns=walkers
permutations = list(itertools.permutations(range(3)))
indices = {p: i for i, p in enumerate(permutations)}
weights = [Fraction(2) ** -sum(energies[s][w] for w, s in enumerate(p))
           for p in permutations]
probabilities = [w / sum(weights) for w in weights]


def pair_kernel(pair):
    kernel = [[Fraction(0) for _ in permutations] for _ in permutations]
    for r, before in enumerate(permutations):
        i, j = pair
        x, y = before.index(i), before.index(j)
        delta = energies[i][y] + energies[j][x] - energies[i][x] - energies[j][y]
        accept = min(Fraction(1), Fraction(2) ** -delta)
        after = list(before)
        after[x], after[y] = after[y], after[x]
        kernel[r][indices[tuple(after)]] += accept
        kernel[r][r] += 1 - accept
    assert all(sum(row) == 1 for row in kernel)
    assert all(probabilities[i] * kernel[i][j] == probabilities[j] * kernel[j][i]
               for i in range(6) for j in range(6))
    return kernel


k1, k2 = pair_kernel((0, 1)), pair_kernel((1, 2))
sweep = [[sum(k1[i][k] * k2[k][j] for k in range(6))
          for j in range(6)] for i in range(6)]
assert all(sum(probabilities[i] * sweep[i][j] for i in range(6)) == probabilities[j]
           for j in range(6))
violations = [(i, j) for i in range(6) for j in range(i + 1, 6)
              if probabilities[i] * sweep[i][j] != probabilities[j] * sweep[j][i]]
assert violations  # Stationarity does not imply whole-sweep detailed balance.
example = [0, 1, 2]
resolved = []
history = [example.copy()]
for i, j in ((0, 1), (1, 2)):
    x, y = example.index(i), example.index(j)
    resolved.append([x, y])
    example[x], example[y] = example[y], example[x]
    history.append(example.copy())
assert history == [[0, 1, 2], [1, 0, 2], [2, 0, 1]]
assert resolved == [[0, 1], [0, 2]]
assert math.comb(8, 2) == 28
flat_example = [0, 1, 2]
for i, j in ((0, 1), (1, 2), (0, 2)):
    x, y = flat_example.index(i), flat_example.index(j)
    flat_example[x], flat_example[y] = flat_example[y], flat_example[x]
assert flat_example == [0, 2, 1]  # A connected sweep alone cannot establish mixing.

# Outside terms must be present in every matrix entry even though the currently
# admitted state-independent K cancels from the pair exponent.
beta = 1 / (0.00831446261815324 * 300)
bare = ((2.0, 5.0), (7.0, 11.0))
outside = (1.7, 2.5)
reduced = [[beta * (bare[s][w] + outside[w]) for w in range(2)] for s in range(2)]
delta = reduced[0][1] + reduced[1][0] - reduced[0][0] - reduced[1][1]
bare_delta = beta * (bare[0][1] + bare[1][0] - bare[0][0] - bare[1][1])
assert math.isclose(delta, bare_delta, abs_tol=1e-14)
assert all(reduced[s][w] != beta * bare[s][w] for s in range(2) for w in range(2))

# Verify actual pinned scalar sign/threshold without constructing workers.
from atom_openmm import gibbs_sampling
original_choice, original_random = gibbs_sampling.choice, gibbs_sampling._random
threshold = math.exp(-0.7)
decisions = []
try:
    gibbs_sampling.choice = lambda choices: 1
    for expected, draw in ((True, threshold / 2), (False, (1 + threshold) / 2)):
        gibbs_sampling._random = lambda: draw
        actual = gibbs_sampling.pairwise_metropolis_sampling(0, 0, [0, 1], [0, 1],
                                                            [[0.0, 0.2], [0.5, 0.0]])
        assert (actual == 1) is expected
        decisions.append({"delta": 0.7, "draw": draw, "accepted": expected})
    gibbs_sampling._random = lambda: (_ for _ in ()).throw(AssertionError("downhill draw"))
    assert gibbs_sampling.pairwise_metropolis_sampling(0, 0, [0, 1], [0, 1],
                                                     [[0.0, -0.2], [-0.5, 0.0]]) == 1
finally:
    gibbs_sampling.choice, gibbs_sampling._random = original_choice, original_random

# Exercise unchanged serialization/isolation helpers with both actual upstream
# RNG aliases. No molecular trajectory or multistate runtime is exercised.
from atm_mlmm.exchange import _host_rng, _rng_document, _rng_from_document
caller_py, caller_np = random.getstate(), np.random.get_state()
py_rng, np_rng = random.Random(73), np.random.RandomState(73)
py_rng.gauss(0, 1)
np_rng.normal()
before_rng = json.loads(json.dumps(_rng_document(py_rng, np_rng)))
assert before_rng["python"][2] is not None and before_rng["numpy"][3] == 1
draw_sequences, post_rng = [], []
for _ in range(2):
    py_rng, np_rng = _rng_from_document(before_rng)
    with _host_rng(py_rng, np_rng):
        cached_normals = (random.gauss(0, 1), float(np.random.normal()))
        draw_sequences.append([cached_normals] + [
            (gibbs_sampling.choice(range(3)), float(gibbs_sampling._random())) for _ in range(9)])
    post_rng.append(json.loads(json.dumps(_rng_document(py_rng, np_rng))))
assert draw_sequences[0] == draw_sequences[1] and post_rng[0] == post_rng[1]
assert random.getstate() == caller_py
after_np = np.random.get_state()
assert after_np[0] == caller_np[0] and after_np[2:] == caller_np[2:]
assert np.array_equal(after_np[1], caller_np[1])

validation_path = Path("/workspace/m05-cpu-setup-v2/latest-validation.json")
validation = json.loads(validation_path.read_text())
assert len(validation["results"]) == 9 and all(r["exit_code"] == 0 for r in validation["results"])
baseline_path = Path("/workspace/g10-start-baseline.log")
baseline = baseline_path.read_text()
assert "31 passed in 115.64s" in baseline and "skipped" not in baseline
v = violations[0]
report = {
    "scope": "design evidence only; no multistate implementation claim",
    "reviewed_head": HEAD, "inspection_checkout_head": inspection_head,
    "design_head": DESIGN, "base": BASE,
    "changed_paths": changed, "compact_diff_sha256": sha(diff),
    "protected_trees_unchanged": ["src", "tests", "fixtures", "environment", "models"],
    "source_inventory_files": len(inventory),
    "source_inventory_sha256": sha(json.dumps(inventory, sort_keys=True).encode()),
    "fixtures": fixture_summaries,
    "beta_mol_per_kJ": beta, "outside_inclusive_reduced_energies": reduced,
    "outside_cancels_from_delta_but_not_matrix": True,
    "pair_kernel_detailed_balance": "exact Fraction equality, both 6x6 kernels",
    "ordered_kernel_stationarity": "exact Fraction equality at all six permutations",
    "whole_sweep_detailed_balance_violations": len(violations),
    "flat_connected_triangle_all_accept_final": flat_example,
    "detailed_balance_counterexample": {
        "from": permutations[v[0]], "to": permutations[v[1]],
        "forward_flux": str(probabilities[v[0]] * sweep[v[0]][v[1]]),
        "reverse_flux": str(probabilities[v[1]] * sweep[v[1]][v[0]])},
    "permutation_history": history, "resolved_workers": resolved,
    "max_unique_pairs_eight_states": math.comb(8, 2),
    "pinned_scalar_decisions": decisions, "pinned_downhill_accepts_without_draw": True,
    "pinned_pair_source": inspect.getfile(gibbs_sampling),
    "pinned_pair_source_sha256": sha(Path(inspect.getfile(gibbs_sampling)).read_bytes()),
    "host_rng_aliases": [gibbs_sampling.choice.__module__, gibbs_sampling._random.__module__],
    "host_rng_roundtrip_and_caller_isolation": "cached normal variates, identical nine-draw replay, both post-streams",
    "inherited_baseline": {"path": str(baseline_path), "sha256": sha(baseline_path.read_bytes()),
                           "result": baseline.strip(), "rerun_by_auditor": False},
    "inherited_setup": {"path": str(validation_path), "sha256": sha(validation_path.read_bytes()),
                        "finished": validation["finished"], "rerun_by_auditor": False,
                        "results": [{"name": r["name"], "exit_code": r["exit_code"]}
                                    for r in validation["results"]]},
    "multistate_runtime_and_fault_tests": "planned, not run",
}
print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
