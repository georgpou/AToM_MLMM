import json
from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[2]


def test_claimed_profiles_require_exact_profile_and_evidence_level():
    from atm_mlmm.release import validate_support_matrix

    matrix = json.loads((ROOT / "docs/project-0/support-matrix.json").read_text())
    result = validate_support_matrix(matrix)
    assert result["profile_count"] >= 5
    assert result["capability_rows"] >= 14
    assert result["unavailable_hardware_rows"] >= 1
    assert result["physical_hold_rows"] >= 1


def test_code_checkbox_cannot_promote_unrun_gpu_or_physics():
    from atm_mlmm.release import validate_support_matrix

    matrix = json.loads((ROOT / "docs/project-0/support-matrix.json").read_text())
    row = next(row for row in matrix["claims"] if row["claim_id"] == "g13-cuda-device")
    row["implementation"] = "implemented"
    row["evidence_status"] = "accepted_prior"
    row["evidence"] = ["code-checkbox:complete"]
    with pytest.raises(ValueError, match="accepted evidence"):
        validate_support_matrix(matrix)


def test_release_validator_rejects_missing_profile_dimensions():
    from atm_mlmm.release import validate_support_matrix

    matrix = json.loads((ROOT / "docs/project-0/support-matrix.json").read_text())
    del matrix["profiles"][0]["precision"]
    with pytest.raises(ValueError, match="precision"):
        validate_support_matrix(matrix)


def test_requirement_matrix_covers_every_original_gate_assertion_and_holds():
    matrix = json.loads((ROOT / "docs/project-0/before-hpc-requirement-matrix.json").read_text())
    expected = set()
    for gate in sorted((ROOT / "docs/project-0/gates").glob("G[0-9][0-9]-*.md")):
        for line in gate.read_text().splitlines():
            if line.lstrip().startswith("| P0-TEST-"):
                match = re.search(r"P0-TEST-(G\d\d-\d\d)", line)
                if match:
                    expected.add("P0-TEST-" + match.group(1))
    actual = [row["assertion_id"] for row in matrix["assertions"]]
    assert matrix["assertion_count"] == len(expected)
    assert len(actual) == len(set(actual))
    assert set(actual) == expected
    assert {row["gate"] for row in matrix["assertions"]} == {f"G{i:02d}" for i in range(14)}
    assert len(matrix["m05_conditions"]) >= 4
    assert matrix["frozen_g07_obligations"]["reference_inventory"] == {
        "total_missing": 29, "full_parent": 19, "alternate_cap": 10,
        "inventory_regenerated": False,
        "source": "Worker_Log/Repository_Review/evidence/Repository_Review_v1/physical-evidence.json",
        "source_sha256": matrix["frozen_g07_obligations"]["reference_inventory"]["source_sha256"],
    }
    assert matrix["qm_feasibility"]["charged_seconds"] == 2325.6446500519996
    assert matrix["qm_feasibility"]["remaining_seconds"] == 84074.355349948
    assert matrix["qm_feasibility"]["existing_continuation_estimate_seconds"] == 122992.52458401839
    assert matrix["qm_feasibility"]["authorized"] is False
