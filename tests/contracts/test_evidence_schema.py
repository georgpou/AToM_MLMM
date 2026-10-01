from dataclasses import replace
import pytest


def make_report():
    from atm_mlmm.schema import ValidationReport
    return ValidationReport('P0-TEST-G01-07', ('P0-REQ-003', 'P0-REQ-023'),
                            'core-analytic-cpu', ('fixture-sha256',),
                            {'inventory_equal': True}, {'inventory_equal': True}, 'passed',
                            ('command-output.log',), ('reviewer-audit.md',), tested_snapshot='a'*40)


def test_acceptance_requires_evidence():
    from atm_mlmm.schema import AcceptanceRecord, QualificationError, from_json, to_json
    report = make_report()
    evidence = AcceptanceRecord('G01-T3', 'core-analytic-cpu', 'a'*40,
                                ('P0-REQ-003', 'P0-REQ-023'), ('P0-TEST-G01-07',),
                                (report,), 'independent-auditor', 'accepted_for_scope', 'reviewer-audit.md', 'accepted')
    assert from_json(to_json(evidence)) == evidence
    cases = (
        {'reports': ()}, {'reviewer': ''}, {'reviewer_decision': ''},
        {'snapshot': 'main'}, {'requirement_ids': ('P0-REQ-999',)},
        {'required_test_ids': ('P0-TEST-G01-08',)},
        {'reports': (replace(report, status='skipped'),)},
        {'reports': (replace(report, profile='gpu'),)},
        {'reports': (replace(report, logs=()),)},
        {'reports': (replace(report, fixture_identities=()),)},
        {'verdict': 'changes_required'},
        {'reports': (replace(report, tested_snapshot='b'*40),)},
    )
    for malformed in cases:
        with pytest.raises(QualificationError):
            replace(evidence, **malformed)
    # A documented not-applicable profile is not an accepted GPU profile.
    assert replace(evidence, status='blocked', reports=(), reviewer='', reviewer_decision='', verdict='blocked').status == 'blocked'
