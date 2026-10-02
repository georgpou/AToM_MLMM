"""Reproduce independent M02 admission findings and unaffected controls.

Exit 0 means all observations were recorded; --require-rejection instead fails
until the improper admissions are closed. No production input is modified.
"""
import argparse
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess

import openmm as mm
from openmm import unit

from tests.analytic_oracle import REFERENCE
from tests.workflow.test_atom_force_routing import atom_case
from atm_mlmm.adapters.atom import build_atom
from atm_mlmm.analytic import seal_physical
from atm_mlmm.atm import (AtmEvaluator, PhysicalEvaluator, build_atm,
                         physical_system, seal_alchemical)
from atm_mlmm.geometry import resolve_protocol
from atm_mlmm.prepare import build_preparation
from atm_mlmm.routing import export_physical
from atm_mlmm.schedule import production_schedule
from atm_mlmm.schema import IdentityError, MalformedInput, UnsupportedCapability

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--require-rejection', action='store_true')
parser.add_argument('--output', type=Path, default=Path(__file__).with_name('admission-results.json'))
args = parser.parse_args()
rows = []


def attempt(name, function, expected_rejection=True):
    try:
        observed = function()
    except (IdentityError, MalformedInput, UnsupportedCapability) as error:
        row = dict(name=name, rejected=True, diagnostic=str(error), expected_rejection=expected_rejection)
    else:
        row = dict(name=name, rejected=False, observed=observed, expected_rejection=expected_rejection)
    rows.append(row)
    print(json.dumps(row), flush=True)


p, t, s, r, x = atom_case('rbfe')


def expression_mismatch(construction, reloaded=False):
    if construction == 'native':
        original = build_atm(p, t, s, r)
    else:
        with build_atom(p, t, s, r, REFERENCE) as run:
            original = run.bundle
    system = mm.XmlSerializer.deserialize(original.system_xml)
    atm = next(f for f in system.getForces() if isinstance(f, mm.ATMForce))
    atm.setEnergyFunction('u0')
    if reloaded:
        xml = mm.XmlSerializer.serialize(system)
        broken = replace(original, system_xml=xml, system_sha256=hashlib.sha256(xml.encode()).hexdigest())
    else:
        broken = seal_alchemical(system, p, t, s, r, construction=original.construction)
    with AtmEvaluator(original, REFERENCE) as evaluator:
        good = evaluator.evaluate(x, 'first')
    with AtmEvaluator(broken, REFERENCE) as evaluator:
        bad = evaluator.evaluate(x, 'first')
    return dict(declared_expression=broken.schedule.expression, actual_expression='u0',
                expected_total=good.total.energy_kj_mol, observed_total=bad.total.energy_kj_mol,
                error=bad.total.energy_kj_mol-good.total.energy_kj_mol)


for construction in ('native', 'upstream'):
    attempt('wrong-expression-'+construction+'-sealer', lambda c=construction: expression_mismatch(c))
    attempt('wrong-expression-'+construction+'-artifact-admission', lambda c=construction: expression_mismatch(c, True))


def add_global(name, value):
    system = physical_system(p)
    force = mm.CustomExternalForce('0.5*'+name+'*(x*x+y*y+z*z)')
    force.addGlobalParameter(name, value)
    force.addParticle(p.real_to_final['protein'], [])
    force.setName('independent:global-harmonic')
    system.addForce(force)
    physical = seal_physical(system, p.topology, ml_atom_ids=p.ml_atom_ids,
                             old_to_new=p.old_to_new, manifest={**p.manifest, 'audit_global': (name, value)})
    return physical, resolve_protocol(physical, t.protocol)


pg, tg = add_global('audit_global_k', 2.)


def mutate_physical(stage, restored=False):
    holder = PhysicalEvaluator(pg, REFERENCE) if stage == 'physical' else build_preparation(pg, REFERENCE)
    with holder as evaluator:
        before = evaluator.evaluate(x)
        evaluator.context.setParameter('audit_global_k', 200.)
        if restored:
            saved = evaluator.context.getState(getPositions=True, getParameters=True)
            evaluator.context.setParameter('audit_global_k', 2.)
            evaluator.context.setState(saved)
        after = evaluator.evaluate(x)
        return dict(before=before.energy_kj_mol, after=after.energy_kj_mol,
                    same_physical_identity=before.physical_identity == after.physical_identity,
                    same_snapshot_identity=before.snapshot_identity == after.snapshot_identity,
                    changed_force_component=(after.forces_kj_mol_nm[4][0]-before.forces_kj_mol_nm[4][0]))


for stage in ('physical', 'preparation'):
    attempt('global-parameter-mutation-'+stage, lambda stage=stage: mutate_physical(stage))
    attempt('restored-global-parameter-mutation-'+stage, lambda stage=stage: mutate_physical(stage, True))


def mutate_atm(stage):
    holder = AtmEvaluator(build_atm(pg, tg, s, r), REFERENCE) if stage == 'native' else build_atom(pg, tg, s, r, REFERENCE)
    with holder:
        evaluator = holder if stage == 'native' else holder.evaluator
        evaluator.evaluate(x, 'first')
        evaluator.context.setParameter('audit_global_k', 200.)
        return evaluator.evaluate(x, 'first').total.energy_kj_mol


for stage in ('native', 'upstream'):
    attempt('global-parameter-mutation-'+stage, lambda stage=stage: mutate_atm(stage))


def restore_atm(stage):
    holder = AtmEvaluator(build_atm(pg, tg, s, r), REFERENCE) if stage == 'native' else build_atom(pg, tg, s, r, REFERENCE)
    with holder:
        evaluator = holder if stage == 'native' else holder.evaluator
        evaluator.evaluate(x, 'first')
        evaluator.context.setParameter('audit_global_k', 200.)
        saved = evaluator.context.getState(getPositions=True, getParameters=True)
        evaluator.context.setParameter('audit_global_k', 2.)
        evaluator.restore_state(saved, 'second')
        actual = evaluator.evaluate(x, 'second')
        return dict(restored_global=evaluator.context.getParameter('audit_global_k'),
                    restored_lambda1=evaluator.context.getParameter('Lambda1'),
                    total=actual.total.energy_kj_mol)


for stage in ('native', 'upstream'):
    attempt('restored-global-parameter-positive-'+stage, lambda stage=stage: restore_atm(stage), False)


pc, tc = add_global('Lambda1', 0.)
from tests.analytic_oracle import production_parameters
collision_schedule = production_schedule((('first', production_parameters(Lambda1=0.)),
                                         ('second', production_parameters(Lambda1=.3))))


def schedule_collision(stage):
    with PhysicalEvaluator(pc, REFERENCE) as evaluator:
        direct = evaluator.evaluate(x).energy_kj_mol
    holder = AtmEvaluator(build_atm(pc, tc, collision_schedule, r), REFERENCE) if stage == 'native' else build_atom(pc, tc, collision_schedule, r, REFERENCE)
    with holder:
        evaluator = holder if stage == 'native' else holder.evaluator
        first = evaluator.evaluate(x, 'first')
        second = evaluator.evaluate(x, 'second')
        return dict(direct_physical=direct, first_u0=first.raw.u0_raw_kJ_mol,
                    second_u0=second.raw.u0_raw_kJ_mol,
                    child_default=0., shared_runtime_parameter=evaluator.context.getParameter('Lambda1'),
                    same_physical_identity=first.total.physical_identity == second.total.physical_identity)


for stage in ('native', 'upstream'):
    attempt('schedule-child-parameter-collision-'+stage, lambda stage=stage: schedule_collision(stage))


def duplicate(stage, renamed):
    system = physical_system(p)
    force = copy.copy(system.getForce(0))
    if renamed:
        force.setName('independent:renamed-duplicate')
    system.addForce(force)
    physical = seal_physical(system, p.topology, ml_atom_ids=p.ml_atom_ids,
                             old_to_new=p.old_to_new, manifest=p.manifest)
    transfer = resolve_protocol(physical, t.protocol)
    if stage == 'export':
        return dict(export_force_count=export_physical(physical).system.getNumForces())
    holder = AtmEvaluator(build_atm(physical, transfer, s, r), REFERENCE) if stage == 'native' else build_atom(physical, transfer, s, r, REFERENCE)
    with holder:
        evaluator = holder if stage == 'native' else holder.evaluator
        actual = evaluator.evaluate(x, 'first')
        return dict(u0=actual.raw.u0_raw_kJ_mol, u1=actual.raw.u1_raw_kJ_mol,
                    physical_child_count=len(physical.ledger), total=actual.total.energy_kj_mol)


for stage in ('export', 'native', 'upstream'):
    attempt('same-name-duplicate-'+stage, lambda stage=stage: duplicate(stage, False))
    attempt('renamed-duplicate-'+stage, lambda stage=stage: duplicate(stage, True))

report = dict(review_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
              observations=rows, failed_expected_rejections=[row['name'] for row in rows if row['expected_rejection'] and not row['rejected']])
args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
if args.require_rejection:
    assert not report['failed_expected_rejections'], report['failed_expected_rejections']
