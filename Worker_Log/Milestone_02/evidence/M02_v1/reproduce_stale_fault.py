"""Reload the preserved, deliberately broken analytic callback offline.

Run from the repository root after activation with PYTHONPATH=src:.
This project-generated fixture is executable; its expected digest is checked
before loading. It is a negative example, never a production Hamiltonian.
"""
import json
from pathlib import Path
import socket


def deny(*args, **kwargs):
    raise AssertionError('network forbidden in fresh-process fault reproduction')


socket.socket.connect = deny
socket.create_connection = deny

from atm_mlmm.atm import evaluate_atm, load_bundle
from atm_mlmm.schema import QualificationError
from tests.analytic_oracle import REFERENCE, case, check, expected_linear

evidence = Path(__file__).resolve().parent
metadata = json.loads((evidence / 'stale-detection.json').read_text())
bundle = load_bundle(evidence / 'stale-reproducer.json', metadata['file_sha256'], trusted=True)
snapshot = case('rbfe')[-1]
actual = evaluate_atm(bundle, snapshot, 'middle', REFERENCE)
try:
    check(actual, expected_linear(snapshot, 'rbfe', .37))
except QualificationError as error:
    assert str(error) == metadata['diagnostic'], str(error)
    print('Preserved stale descriptor detected after fresh offline reload: ' + str(error))
else:
    raise AssertionError('stale descriptor was not detected')
