"""Offline frozen-reference generation, gated by recorded M00 decisions.

This program never imports/evaluates a learned model. Run its coordinator in
the core environment and pass the separate locked reference Python explicitly.
It writes each attempt, including failures, before deciding batch readiness.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def validate_plan(root, approval_path):
    approval=json.loads(Path(approval_path).read_text())
    if approval.get('user_agreed') is not True or approval.get('design_verdict')!='accepted_for_scope':
        raise ValueError('recorded user agreement and independent design acceptance are required')
    if approval.get('reviewer_model')!='gpt-6-astra' or approval.get('reasoning_effort')!='high' or approval.get('fresh_context') is not True:
        raise ValueError('the required independent Astra/high fresh-context review is absent')
    if len(approval.get('reviewed_commit',''))!=40:
        raise ValueError('exact reviewed commit is missing')
    if digest(root/'input-manifest.json')!=approval.get('input_manifest_sha256'):
        raise ValueError('frozen plan manifest differs from the accepted decision')
    manifest=json.loads((root/'input-manifest.json').read_text())
    for name,expected in manifest['files'].items():
        if digest(root/name)!=expected:raise ValueError('changed frozen input: '+name)
    return approval,manifest


def worker(order_path):
    import socket
    def denied(*args,**kwargs):raise RuntimeError('reference generation must run offline')
    socket.socket.connect=denied;socket.create_connection=denied;socket.getaddrinfo=denied
    order=json.loads(Path(order_path).read_text());output=Path(order['output'])
    started=time.monotonic();diagnostic={}
    try:
        import numpy as np
        import psi4
        data=order['structure'];settings=order['settings']
        if psi4.__version__!='1.10.2':raise ValueError('unexpected Psi4 reference version')
        runtime_memory=order.get('runtime_memory','5 GiB')
        memory_value,memory_unit=runtime_memory.split()
        if memory_unit!='GiB' or not np.isfinite(float(memory_value)) or not 0<float(memory_value)<=5:
            raise ValueError('runtime memory exceeds the approved 5 GiB cap')
        psi4.set_num_threads(2);psi4.set_memory(runtime_memory)
        psi4.core.IOManager.shared_object().set_default_path(order.get('scratch_directory',str(output.parent)))
        psi4.set_output_file(str(output.with_suffix('.psi4.txt')),False)
        psi4.set_options(settings)
        lines=['0 1']+[e+' '+' '.join(format(float(v),'.17g') for v in xyz)
                     for e,xyz in zip(data['elements'],data['positions_angstrom'])]
        lines+=['units angstrom','no_reorient','no_com','symmetry c1']
        molecule=psi4.geometry('\n'.join(lines))
        gradient,wfn=psi4.gradient('wb97m-d3bj',molecule=molecule,return_wfn=True)
        g=np.asarray(gradient).copy();e=float(wfn.energy())
        variables={k:float(v) for k,v in psi4.core.variables().items()
                   if isinstance(v,(int,float)) and ('ENERGY' in k or 'DISPERSION' in k)}
        if abs(variables.get('DFT VV10 ENERGY',0.))>1e-15 or 'DISPERSION CORRECTION ENERGY' not in variables:
            raise ValueError('reference dispersion convention differs from the plan')
        diagnostic={'energy_hartree':e if np.isfinite(e) else str(e),
                    'gradient_hartree_bohr':[[v if np.isfinite(v) else str(v) for v in row] for row in g.tolist()]}
        if not (np.isfinite(e) and np.isfinite(g).all()):raise ValueError('nonfinite reference energy/gradient')
        basis={}
        for name,expected in order['basis_file_sha256'].items():
            value=digest(Path(psi4.core.get_datadir())/'basis'/name)
            if value!=expected:raise ValueError('reference basis digest mismatch: '+name)
            basis[name]=value
        record={'status':'computed','name':order.get('job_name',data['name']),'source_input_sha256':order['source_input_sha256'],
                'method':'wb97m-d3bj/def2-tzvppd','psi4_version':psi4.__version__,
                'formal_charge':0,'multiplicity':1,'positions_angstrom':data['positions_angstrom'],
                'atomic_numbers':data['atomic_numbers'],'energy_hartree':e,
                'gradient_hartree_bohr':g.tolist(),'quantum_energy_variables':variables,
                'basis_file_sha256':basis,'settings':settings,'network_denied':True,
                'wall_seconds':time.monotonic()-started,'threads':2,'memory':runtime_memory,
                'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        dump(output,record);print(json.dumps({'name':data['name'],'status':'computed','wall_seconds':record['wall_seconds']}))
        return 0
    except Exception as error:
        dump(output,{'status':'failed','name':order['structure']['name'],
                     'source_input_sha256':order['source_input_sha256'],'exception':repr(error),
                     'traceback':traceback.format_exc(),'raw_diagnostic':diagnostic,'wall_seconds':time.monotonic()-started})
        traceback.print_exc();return 1


def coordinator(args):
    root=Path(args.plan_root).resolve();approval,manifest=validate_plan(root,args.approval)
    reference_prefix=Path(args.reference_python).resolve().parents[1]
    installed={}
    for p in (reference_prefix/'conda-meta').glob('*.json'):
        entry=json.loads(p.read_text());url=entry.get('url','');installed[url.rsplit('/',1)[-1]]=entry.get('sha256')
    lock=(root/'reference-explicit.lock').read_text().splitlines()[1:]
    expected={line.rsplit('#',1)[0].rsplit('/',1)[-1]:line.rsplit('#',1)[1] for line in lock}
    if installed!=expected:raise ValueError('reference environment differs from the frozen 105-package lock')
    output=Path(args.output).resolve()
    if output.exists():raise FileExistsError('reference attempt directory must be new')
    output.mkdir(parents=True);(output/'orders').mkdir();(output/'records').mkdir()
    settings=json.loads((root/'reference-settings.json').read_text())
    paths=sorted((root/'structures').glob('*.json'))+sorted((root/'quadrature_controls').glob('*.json'))
    queue=[(p,False) for p in paths]
    queue += [(root/'structures'/(name+'.json'),True) for name in settings['convergence_checks']['rows']]
    started=time.monotonic();results=[]
    for path,fine in queue:
        data=json.loads(path.read_text());name=data['name']+('-fine-grid' if fine else '')
        target=output/'records'/(name+'.json')
        remaining=settings['wall_cap_hours']*3600-(time.monotonic()-started)
        if remaining<=0:
            dump(target,{'name':name,'status':'not_run_budget_exhausted','source_input_sha256':digest(path)})
            results.append({'name':name,'exit':None,'path':str(target.relative_to(output))});continue
        options={**settings['settings']}
        if fine:options.update(settings['convergence_checks']['settings'])
        order={'structure':data,'source_input_sha256':digest(path),'settings':options,
               'basis_file_sha256':settings['basis_file_sha256'],'output':str(target)}
        order_path=output/'orders'/(name+'.json');dump(order_path,order)
        command=[str(Path(args.reference_python).resolve()),str(Path(__file__).resolve()),'--worker',str(order_path)]
        began=datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            with (output/(name+'.launcher.txt')).open('x') as log:
                run=subprocess.run(command,cwd=output,stdout=log,stderr=subprocess.STDOUT,
                                   timeout=remaining,check=False)
            exit_code=run.returncode
        except subprocess.TimeoutExpired:
            exit_code=124
            dump(target,{'name':name,'status':'timeout','source_input_sha256':digest(path)})
        results.append({'name':name,'exit':exit_code,'command':command,'started_utc':began,
                        'path':str(target.relative_to(output))})
        print(name,'exit',exit_code,flush=True)
    report={'scope':'independent quantum references only; no model comparison',
            'approval':approval,'approval_sha256':digest(args.approval),
            'input_manifest_sha256':digest(root/'input-manifest.json'),
            'reference_settings_sha256':digest(root/'reference-settings.json'),
            'results':results,'wall_seconds':time.monotonic()-started,
            'ready_for_comparison':all(r['exit']==0 for r in results),
            'files':{str(p.relative_to(output)):digest(p) for p in sorted((output/'records').glob('*.json'))}}
    dump(output/'manifest.json',report)
    return 0 if report['ready_for_comparison'] else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker');parser.add_argument('--plan-root');parser.add_argument('--approval')
    parser.add_argument('--reference-python');parser.add_argument('--output')
    args=parser.parse_args()
    if args.worker:sys.exit(worker(args.worker))
    if not all((args.plan_root,args.approval,args.reference_python,args.output)):
        parser.error('coordinator requires --plan-root --approval --reference-python --output')
    sys.exit(coordinator(args))
