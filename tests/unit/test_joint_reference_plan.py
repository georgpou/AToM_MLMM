"""G07 frozen reference matrix; these tests never launch a quantum engine."""
from pathlib import Path
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]/'fixtures/chemical_reference_v3'


def test_frozen_joint_matrix_preserves_twenty_rows_and_fifty_descriptions():
    from atm_mlmm.joint_reference import quantum_job_matrix
    matrix = quantum_job_matrix(ROOT)
    assert len(matrix['rows']) == 20
    assert sum(len(row['descriptions']) for row in matrix['rows']) == 50
    assert len(matrix['new_jobs']) == 30
    assert len(matrix['reused_jobs']) == 20
    assert {job['kind'] for job in matrix['new_jobs']} == {'full-parent', 'alternative-ethane'}
    assert matrix['new_quantum_authorized'] is False
    for row in matrix['rows']:
        assert row['descriptions'][0]['name'] == 'baseline'
        assert row['descriptions'][1]['name'] == 'uncut'
        full = next(job for job in matrix['new_jobs'] if job['name'] == row['full_job'])
        assert full['formal_charge'] == 0 and full['multiplicity'] == 1
        assert len(full['positions_angstrom']) == len(full['atomic_numbers'])
        assert all(np.isfinite(full['positions_angstrom']).flat)
        assert row['descriptions'][1]['quantum_job'] == row['full_job']


def test_cap_reference_rejects_changed_geometry_before_reusing_quantum():
    from atm_mlmm.joint_reference import validate_capped_geometry
    from atm_mlmm.schema import IdentityError
    import json
    row = json.loads((ROOT/'structures/ethanol-methanol-d3-r0.json').read_text())
    validate_capped_geometry(row)
    row['g07_controls']['parent']['positions_angstrom'][4][0] += .1
    with pytest.raises(IdentityError, match='cap'):
        validate_capped_geometry(row)
