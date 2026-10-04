#!/usr/bin/env bash
set -u
cd /workspace/AToM_MLMM
source /workspace/atom-mlmm-g08-r2/activate.sh
export OPENBLAS_NUM_THREADS=2
export PYTHONPATH=/workspace/AToM_MLMM/src
audit_out=/workspace/AToM_MLMM/Worker_Log/Milestone_04/evidence/G08_v1_independent_sol61_max
case "$1" in
  full)
    run_name=full-cpu
    run_cmd=(python -m pytest -q --basetemp "$audit_out/full-pytest-temp")
    ;;
  focused)
    run_name=g08-focused
    run_cmd=(python -m pytest tests/sampling/test_analytic_free_energy.py tests/unit/test_schedule.py tests/unit/test_restraint_volume.py -v --basetemp "$audit_out/focused-pytest-temp")
    ;;
  *) exit 2 ;;
esac
printf '%q ' "${run_cmd[@]}" > "$audit_out/$run_name.command"
printf '\n' >> "$audit_out/$run_name.command"
date -u +%FT%TZ > "$audit_out/$run_name.started"
cat /sys/fs/cgroup/memory.events > "$audit_out/$run_name.memory-before"
python "$audit_out/command_runner.py" "$run_name" "${run_cmd[@]}"
run_status=$?
printf '%s\n' "$run_status" > "$audit_out/$run_name.exit"
date -u +%FT%TZ > "$audit_out/$run_name.finished"
cat /sys/fs/cgroup/memory.events > "$audit_out/$run_name.memory-after"
tail -n 12 "$audit_out/$run_name.stdout"
tail -n 24 "$audit_out/$run_name.stderr"
exit "$run_status"
