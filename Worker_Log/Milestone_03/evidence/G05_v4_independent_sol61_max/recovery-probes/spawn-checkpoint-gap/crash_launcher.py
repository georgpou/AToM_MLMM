import argparse,os,runpy,subprocess,sys
sys.path.insert(0,'/workspace/AToM_MLMM-m03-reference-g05/tools')
functions=runpy.run_path('/workspace/AToM_MLMM-m03-reference-g05/tools/resume_neutral_quantum.py')
real_popen=subprocess.Popen
def crash_after_spawn(*args,**kwargs):
    worker=real_popen(*args,**kwargs)
    os._exit(99)
subprocess.Popen=crash_after_spawn
args=argparse.Namespace(plan_root='/workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_03/evidence/G05_v4_independent_sol61_max/recovery-probes/spawn-checkpoint-gap/plan',approval='/workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_03/evidence/G05_v4_independent_sol61_max/recovery-probes/spawn-checkpoint-gap/approval.json',output='/workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_03/evidence/G05_v4_independent_sol61_max/recovery-probes/spawn-checkpoint-gap/output',reference_python='/workspace/AToM_MLMM-m03-reference-g05/Worker_Log/Milestone_03/evidence/G05_v4_independent_sol61_max/recovery-probes/spawn-checkpoint-gap/reference/bin/audit-worker',resume_from=None,stop_state=None,prior_launch=None,check_resume=False,memory_gib=3.,wall_limit_seconds=None)
functions['run'](args)
