#!/usr/bin/env python
"""One fixed-coordinate/tiny-step benchmark case, intended for a fresh process."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _finite(evaluation):
    import math
    result = evaluation.total if hasattr(evaluation, "total") else evaluation
    values = [result.energy_kj_mol]
    if hasattr(result, "forces_kj_mol_nm"):
        values.extend(value for row in result.forces_kj_mol_nm for value in row)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("benchmark evaluation produced a nonfinite value")


def _input_identity():
    paths = (ROOT / "fixtures/two_cut_control/input.json",
             ROOT / "fixtures/two_cut_control/original-mm.xml")
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode() + b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _source_identity():
    tracked = [ROOT / "tools/benchmark_case.py", ROOT / "tools/benchmark_cpu.py",
               ROOT / "tests/link_oracle.py", ROOT / "tests/cap_collection_oracle.py",
               ROOT / "tests/analytic_oracle.py"]
    tracked.extend(sorted((ROOT / "src/atm_mlmm").rglob("*.py")))
    file_hashes = {}
    for path in tracked:
        if path.is_file():
            relative = path.relative_to(ROOT).as_posix()
            file_hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    def git(*args):
        try:
            return subprocess.check_output(["git", *args], cwd=ROOT, text=True,
                                           stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    return {"commit": git("rev-parse", "HEAD"),
            "tree": git("rev-parse", "HEAD^{tree}"),
            "working_tree_dirty": bool(git("status", "--porcelain")),
            "source_file_sha256": file_hashes}


def run(case, workdir):
    import numpy as np
    import openmm as mm
    from openmm import unit
    from tests.link_oracle import REFERENCE
    from tests.cap_collection_oracle import input_case as cap_input
    from atm_mlmm.schema import RuntimeSpec

    wall_start, cpu_start = time.perf_counter(), time.process_time()
    original, partition_spec, snapshot = cap_input(mixed_zero_cut=(case == "ligand-only"))
    runtime = RuntimeSpec("Reference", "double", (), .0005, 300., "NVT", "LangevinMiddle")
    source_identity = _source_identity()
    model_load_seconds = None
    physical = atm = transfer = schedule = restraints = None
    if case != "all-mm":
        from atm_mlmm.models.mace import make_calculator, model_spec
        from atm_mlmm.hybrid import build_physical
        from atm_mlmm.partition import resolve_partition
        from atm_mlmm.schema import EmbeddingSpec, MobileGroup, RestraintSpec
        from atm_mlmm.geometry import resolve_protocol
        from atm_mlmm.protocols.rbfe import make_protocol
        from atm_mlmm.schedule import production_schedule
        from tests.analytic_oracle import production_parameters
        from atm_mlmm.atm import build_atm

        load_start = time.perf_counter()
        calculator = make_calculator()
        model_load_seconds = time.perf_counter() - load_start
        del calculator
        partition = resolve_partition(original.topology, partition_spec)
        physical = build_physical(original, partition, model_spec(),
            EmbeddingSpec("mechanical", "1", "protein_c_c", "nonperiodic"), cap_distance_nm=.117)
        mobile_groups = tuple(MobileGroup(f"mobile-{molecule.molecule_id}", molecule.atom_ids,
                                          (molecule.role,), molecule.molecule_id)
                              for molecule in original.topology.molecules
                              if molecule.role == "ligand")
        transfer = resolve_protocol(physical, make_protocol(mobile_groups, (.3, 0., 0.)))
        schedule = production_schedule(tuple((name, production_parameters(
            Lambda1=lam, Lambda2=lam, Umax=10000., Ubcore=500., Acore=0.,
            W0=0., UOffset=0.)) for name, lam in (("contact", 0.), ("middle", .5), ("separated", 1.))))
        restraints = RestraintSpec("anchor", (snapshot.real_atom_ids[0],), 1., tuple(snapshot.positions_nm[0]))
        atm = build_atm(physical, transfer, schedule, restraints)

    startup = time.perf_counter()
    if case == "all-mm":
        system = mm.XmlSerializer.deserialize(original.prepared_mm_artifact)
        integrator = mm.VerletIntegrator(REFERENCE.timestep_ps * unit.picoseconds)
        context = mm.Context(system, integrator, mm.Platform.getPlatformByName("Reference"))
        context.setPositions(snapshot.positions_nm * unit.nanometer)

        class Direct:
            def evaluate(self):
                state = context.getState(getEnergy=True, getForces=True)
                return state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole), state.getForces(asNumpy=True).value_in_unit(unit.kilojoule_per_mole/unit.nanometer)
            def step(self):
                integrator.step(1)
        evaluator = Direct()
        close = lambda: (setattr(evaluator, "context", None), setattr(evaluator, "integrator", None))
    elif case in ("ligand-only", "cavity-inclusive"):
        from atm_mlmm.atm import PhysicalEvaluator
        evaluator = PhysicalEvaluator(physical, runtime)
        startup_seconds = time.perf_counter() - startup
        first_start = time.perf_counter()
        first = evaluator.evaluate(snapshot)
        first_seconds = time.perf_counter() - first_start
        _finite(first)
        repeats = []
        for _ in range(8):
            start = time.perf_counter(); answer = evaluator.evaluate(snapshot)
            repeats.append(time.perf_counter() - start); _finite(answer)
        step_start = time.perf_counter(); evaluator.integrator.step(1)
        step_seconds = time.perf_counter() - step_start
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        evaluator.close()
        return {"case": case, "context_startup_seconds": startup_seconds,
                "model_load_seconds": model_load_seconds, "first_evaluation_seconds": first_seconds,
                "evaluation_seconds": repeats, "step_seconds": step_seconds,
                "simulated_ns": REFERENCE.timestep_ps * 1.0e-3,
                "wall_seconds": time.perf_counter()-wall_start,
                "cpu_seconds": time.process_time()-cpu_start,
                "peak_rss_bytes": rss, "real_atoms": len(snapshot.real_atom_ids),
                "ml_atoms": len(physical.model_input_ids), "caps": len(physical.links),
                "source_identity": source_identity,
                "model_identity": "MACE-OFF23-small/165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f",
                "input_identity": _input_identity(), "profile_identity": "Linux CPU; OpenMM Reference double; MACE float64; fixed coordinates; one 0.5 fs step"}
    else:
        from atm_mlmm.atm import AtmEvaluator
        if case == "native-atm":
            evaluator = AtmEvaluator(atm, runtime)
            evaluate = lambda: evaluator.evaluate(snapshot, "middle")
            integrator = evaluator.integrator
        elif case == "actual-worker":
            from atm_mlmm.adapters.atom import build_atom, export_worker_run, load_worker_run
            with build_atom(physical, transfer, schedule, restraints, runtime) as source_run:
                handover, digest = export_worker_run(source_run, Path(workdir)/"worker-export", snapshot, "middle")
            worker_start = time.perf_counter()
            evaluator = load_worker_run(handover.parent, digest, trusted=True)
            startup_seconds = time.perf_counter() - worker_start
            evaluate = lambda: evaluator.evaluate(snapshot, "middle")
            integrator = evaluator.evaluator.integrator
        else:
            raise ValueError(f"unknown benchmark case {case}")

        startup_seconds = locals().get("startup_seconds", time.perf_counter()-startup)
        first_start = time.perf_counter(); first = evaluate()
        first_seconds = time.perf_counter()-first_start; _finite(first)
        repeats=[]
        for _ in range(8):
            start=time.perf_counter(); answer=evaluate(); repeats.append(time.perf_counter()-start); _finite(answer)
        step_start=time.perf_counter(); integrator.step(1); step_seconds=time.perf_counter()-step_start
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
        evaluator.close()
        return {"case":case,"context_startup_seconds":startup_seconds,
                "model_load_seconds":model_load_seconds,"first_evaluation_seconds":first_seconds,
                "evaluation_seconds":repeats,"step_seconds":step_seconds,
                "simulated_ns":REFERENCE.timestep_ps*1.0e-3,
                "wall_seconds":time.perf_counter()-wall_start,
                "cpu_seconds":time.process_time()-cpu_start,"peak_rss_bytes":rss,
                "real_atoms":len(snapshot.real_atom_ids),"ml_atoms":len(physical.model_input_ids),
                "caps":len(physical.links),"source_identity":source_identity,
                "model_identity":"MACE-OFF23-small/165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f",
                "input_identity":_input_identity(),"profile_identity":"Linux CPU; OpenMM Reference double; MACE float64; fixed coordinates; one 0.5 fs step"}

    startup_seconds = time.perf_counter() - startup
    first_start = time.perf_counter(); first = evaluator.evaluate()
    first_seconds = time.perf_counter()-first_start
    repeats=[]
    for _ in range(8):
        start=time.perf_counter(); answer=evaluator.evaluate(); repeats.append(time.perf_counter()-start)
    step_start=time.perf_counter(); evaluator.step(); step_seconds=time.perf_counter()-step_start
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    context=None; integrator=None
    energy,forces=first
    if not np.isfinite(energy) or not np.isfinite(forces).all(): raise ValueError("all-MM evaluation is nonfinite")
    return {"case":case,"context_startup_seconds":startup_seconds,"model_load_seconds":None,
            "first_evaluation_seconds":first_seconds,"evaluation_seconds":repeats,
            "step_seconds":step_seconds,"simulated_ns":REFERENCE.timestep_ps*1.0e-3,
            "wall_seconds":time.perf_counter()-wall_start,"cpu_seconds":time.process_time()-cpu_start,
            "peak_rss_bytes":rss,"real_atoms":len(snapshot.real_atom_ids),"ml_atoms":0,"caps":0,
            "source_identity":source_identity,
            "model_identity":"not applicable; retained original MM fixture",
            "input_identity":_input_identity(),"profile_identity":"Linux CPU; OpenMM Reference double; fixed coordinates; one 0.5 fs step"}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case",choices=("all-mm","ligand-only","cavity-inclusive","native-atm","actual-worker"))
    parser.add_argument("--workdir",type=Path,required=True)
    args=parser.parse_args()
    args.workdir.mkdir(parents=True,exist_ok=False)
    print(json.dumps(run(args.case,args.workdir),sort_keys=True,allow_nan=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
