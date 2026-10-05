"""Separate, unqualified actual-MACE XLA component experiment.

Nothing here routes the production evaluator onto XLA. CPU reference data are
inert and hash bound; failed precision/operator probes remain failed evidence.
"""
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import time
import traceback


def _save(path, document):
    def inert(value):
        if isinstance(value,float) and not math.isfinite(value): return {'nonfinite':repr(value)}
        if isinstance(value,dict): return {k:inert(v) for k,v in value.items()}
        if isinstance(value,(list,tuple)): return [inert(v) for v in value]
        return value
    Path(path).write_text(json.dumps(inert(document), indent=2, allow_nan=False)+'\n')


def read_reference(path, expected_sha256):
    payload=Path(path).read_bytes()
    if hashlib.sha256(payload).hexdigest()!=expected_sha256:
        raise ValueError('CPU reference hash mismatch')
    document=json.loads(payload)
    from .models.mace import CHECKPOINT_SHA256
    if document.get('version')!=1 or document.get('model_sha256')!=CHECKPOINT_SHA256:
        raise ValueError('CPU reference model/version mismatch')
    root=Path(__file__).resolve().parent
    sources=document.get('source_files',{})
    current={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*.py')}
    if sources!=current: raise ValueError('CPU reference source hash set differs from this exact experiment')
    return document


def admit_tpu(device_type, double_arithmetic, fallback_counters):
    if device_type!='TPU': raise ValueError('actual XLA backend is not TPU')
    if not double_arithmetic: raise ValueError('actual float64 arithmetic is unsupported or lowered')
    if any(v for k,v in fallback_counters.items() if k.startswith('aten::')):
        raise ValueError('host ATen fallback cannot qualify TPU execution')
    return True


def compare(reference, energy, all_real_forces):
    import numpy as np
    force=np.asarray(all_real_forces); expected=np.asarray(reference['all_real_ml_forces'])
    if force.shape!=expected.shape: raise ValueError('full-real force shape mismatch')
    de=abs(float(energy)-reference['energy_kj_mol'])
    df=float(np.max(np.abs(force-expected)))
    return {'energy_error_kj_mol':de,'max_full_real_force_error_kj_mol_nm':df,
            'passed':bool(np.isfinite(force).all() and np.isfinite(energy) and de<=1e-4 and df<=5e-3)}


def _derived(ids, elements, model_ids, links, coordinates):
    """Explicit cap inputs and sparse parent projection for this experiment."""
    import numpy as np
    x=np.asarray(coordinates); numbers=[]; raw=[]; projections=[]
    index={a:i for i,a in enumerate(ids)}; caps={v['cap_id']:v for v in links}
    for atom in model_ids:
        if atom in caps:
            link=caps[atom]; a=index[link['ml_parent_id']]; b=index[link['mm_parent_id']]
            delta=x[b]-x[a]; radius=np.linalg.norm(delta); direction=delta/radius
            jac=link['distance_nm']/radius*(np.eye(3)-np.outer(direction,direction))
            raw.append(x[a]+link['distance_nm']*direction); numbers.append(1)
            projections.append(((a,(np.eye(3)-jac).T),(b,jac.T)))
        else:
            i=index[atom]; raw.append(x[i]); numbers.append({'H':1,'C':6,'N':7,'O':8}[elements[i]])
            projections.append(((i,np.eye(3)),))
    return numbers,np.asarray(raw),projections


def _project(forces, projections, count):
    import numpy as np
    result=np.zeros((count,3))
    for f,parents in zip(forces,projections):
        for i,jac in parents: result[i]+=jac@f
    return result


def export_cpu_reference(output):
    """Identical ABFE/RBFE, both maps, changed coordinates and real-parent FDs."""
    import numpy as np
    from dataclasses import asdict
    import subprocess
    from .hybrid import build_physical
    from .partition import resolve_partition
    from .models.mace import model_spec,CHECKPOINT_SHA256
    from .model_reference import NativeMACE
    from .schema import EmbeddingSpec
    from .workflow import load_configuration,_domain,_profile
    output=Path(output); output.mkdir(parents=True,exist_ok=False)
    root=Path(__file__).resolve().parents[2]; load_start=time.monotonic(); native=NativeMACE()
    model_load_s=time.monotonic()-load_start
    source_root=Path(__file__).resolve().parent
    document={'version':1,'model_sha256':CHECKPOINT_SHA256,'profile':_profile(),
              'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
              'source_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)),
              'source_files':{p.relative_to(source_root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_root.rglob('*.py')},
              'cpu_model_load_s':model_load_s,
              'component':'actual joint MACE only; MM/PME/OpenMM integration remain CPU',
              'cases':[],'rows':[],'fd_steps_nm':[1e-3,1e-4,1e-5]}
    start=time.monotonic()
    for kind in ('abfe','rbfe'):
        config=load_configuration(root/f'fixtures/solvated_fragment/v2/{kind}/config.json')
        physical=build_physical(config.original,resolve_partition(config.original.topology,config.partition),model_spec(),
            EmbeddingSpec('mechanical','1','protein_c_c','orthorhombic-pme-v1'),cap_distance_nm=.109)
        ids=config.snapshot.real_atom_ids; elements=[a.element for a in physical.topology.atoms]
        links=[asdict(v) for v in physical.links]
        case={'kind':kind,'real_atom_ids':ids,'elements':elements,'model_input_ids':physical.model_input_ids,
              'links':links,'box_nm':config.snapshot.box_nm,'input_identity':config.original.content_identity}
        document['cases'].append(case)
        link=physical.links[0]
        selected=[ids.index(link.ml_parent_id),ids.index(link.mm_parent_id),26,
                  next(i for i,a in enumerate(ids) if a.startswith('dense-water-'))]
        base=np.asarray(config.snapshot.positions_nm)
        for mapping in (0,1):
            x=base.copy()
            if mapping:
                index={a:i for i,a in enumerate(ids)}
                for sign,m in zip((1.,-1.),[m for m in physical.topology.molecules if m.role=='ligand']):
                    x[[index[a] for a in m.atom_ids]]+=sign*np.asarray(config.settings['displacement_nm'])
            variants=[('base',x,None,None,None)]
            changed=x.copy(); changed[selected[0],1]+=.002
            variants.append(('changed',changed,None,None,None))
            shape=x.copy()
            first_ligand=next(m for m in physical.topology.molecules if m.role=='ligand')
            shape[[ids.index(a) for a in first_ligand.atom_ids],1]+=.08
            variants.append(('graph-shape',shape,None,None,None))
            for atom,step,sign in itertools.product(selected,document['fd_steps_nm'],(1,-1)):
                moved=x.copy(); moved[atom,1]+=sign*step
                variants.append(('fd',moved,atom,step,sign))
            for label,moved,atom,step,sign in variants:
                from dataclasses import replace
                # Domain guards consume the unmapped worker configuration and
                # check both maps themselves. Do not map an already mapped frame.
                unmapped=moved.copy()
                if mapping:
                    for map_sign,m in zip((1.,-1.),[m for m in physical.topology.molecules if m.role=='ligand']):
                        unmapped[[ids.index(a) for a in m.atom_ids]]-=map_sign*np.asarray(config.settings['displacement_nm'])
                _domain(physical.topology,replace(config.snapshot,positions_nm=unmapped),
                    config.settings['displacement_nm'],kind,config.partition.permitted_cuts)
                row_start=time.monotonic()
                numbers,raw,projection=_derived(ids,elements,physical.model_input_ids,links,moved)
                answer=native.evaluate(numbers,raw,box_nm=config.snapshot.box_nm)
                document['rows'].append({'case':kind,'map':mapping,'variant':label,'fd_atom':atom,'step_nm':step,'sign':sign,
                    'real_positions_nm':moved.tolist(),'model':answer,'energy_kj_mol':answer['energy_kj_mol'],
                    'all_real_ml_forces':_project(answer['forces_kj_mol_nm'],projection,len(ids)).tolist(),
                    'cpu_synchronized_end_to_end_s':time.monotonic()-row_start})
                _save(output/'reference.json',document)
    document['cpu_steady_timings']=[]
    for row in (r for r in document['rows'] if r['variant']=='base'):
        case=next(c for c in document['cases'] if c['kind']==row['case']); times=[]
        for _ in range(5):
            t=time.monotonic()
            numbers,raw,projection=_derived(case['real_atom_ids'],case['elements'],case['model_input_ids'],case['links'],row['real_positions_nm'])
            answer=native.evaluate(numbers,raw,box_nm=case['box_nm'])
            _project(answer['forces_kj_mol_nm'],projection,len(case['real_atom_ids']))
            times.append(time.monotonic()-t)
        document['cpu_steady_timings'].append({'case':row['case'],'map':row['map'],'synchronized_end_to_end_s':times})
    document['cpu_reference_wall_s']=time.monotonic()-start
    _save(output/'reference.json',document)
    digest=hashlib.sha256((output/'reference.json').read_bytes()).hexdigest()
    _save(output/'identity.json',{'reference_sha256':digest,'rows':len(document['rows']),'model_sha256':CHECKPOINT_SHA256})
    return {'reference_sha256':digest,'rows':len(document['rows'])}


def run_tpu(reference_path, reference_sha256, output, repeats=5):
    """Retain a negative probe and stop timing qualification on any mismatch."""
    import numpy as np
    output=Path(output); output.mkdir(parents=True,exist_ok=False)
    report={'status':'incomplete','reference_sha256':reference_sha256,'rows':[],
            'component':'MACE energy/coordinate gradient; no OpenMM TPU platform',
            'environment':{k:os.environ.get(k) for k in ('PJRT_DEVICE','XLA_USE_BF16','XLA_DOWNCAST_BF16')}}
    _save(output/'report.json',report)
    try:
        reference=read_reference(reference_path,reference_sha256)
        report['cpu_steady_timings']=reference['cpu_steady_timings']
        shapes={len(r['model']['directed_edges']) for r in reference['rows']}
        report['graph_edge_counts']=sorted(shapes)
        if len(shapes)<2: raise ValueError('CPU reference does not exercise graph shape changes')
        import torch
        import torch_xla
        import torch_xla.core.xla_model as xm
        import torch_xla.runtime as xr
        import torch_xla.debug.metrics as metrics
        from .models.mace import load_model,EV_TO_KJ_MOL,EV_A_TO_KJ_MOL_NM
        report.update(torch_version=torch.__version__,xla_version=torch_xla.__version__,
                      backend=xr.device_type(),device_attributes=xr.global_runtime_device_attributes())
        if report['backend']!='TPU': raise ValueError('actual XLA backend is not TPU')
        device=xm.xla_device()
        # Device arithmetic, then synchronized return. A requested tensor dtype
        # alone is not evidence of arithmetic precision on TPU.
        one=torch.tensor([1.125817395831287],dtype=torch.float64).to(device)
        epsilon=torch.tensor([2.**-40],dtype=torch.float64).to(device)
        summed=one+epsilon
        # Materialize the addition in a separate execution so algebraic
        # simplification cannot cancel x from (x+epsilon)-x before rounding.
        xm.mark_step(); xm.wait_device_ops()
        precision=summed-one
        xm.mark_step(); xm.wait_device_ops()
        report['precision']={'requested_dtype':'float64','returned_dtype':str(precision.cpu().dtype),
                             'delta':float(precision.cpu()[0]),'expected_delta':2.**-40}
        double_ok=report['precision']['delta']==2.**-40
        before={k:metrics.counter_value(k) or 0 for k in metrics.counter_names()}
        start=time.monotonic(); model=load_model().to(device)
        for parameter in model.parameters(): parameter.requires_grad_(False)
        xm.mark_step(); xm.wait_device_ops()
        report['model_transfer_s']=time.monotonic()-start
        report['model_tensor_dtypes']=sorted({str(t.dtype) for t in list(model.parameters())+list(model.buffers())})
        def evaluate(row,diagnostic=False):
            # Rebuild the graph from current coordinates on every invocation.
            # Returning to CPU includes gradient transfer; no scalar-only timing.
            start=time.monotonic(); raw=row['model']; xyz=np.asarray(raw['positions_nm'])*10.
            cell=np.asarray(raw['box_nm'])*10.; cutoff=raw['cutoff_angstrom']
            edges=[]; shifts=[]
            for i,j in itertools.product(range(len(xyz)),repeat=2):
                if i==j: continue
                delta=xyz[j]-xyz[i]; center=-np.floor(delta/np.diag(cell)).astype(int)
                for offset in itertools.product((-1,0,1),repeat=3):
                    shift=center+offset
                    if np.linalg.norm(delta+shift@cell)<cutoff: edges.append((i,j)); shifts.append(shift)
            graph_s=time.monotonic()-start
            if edges!=[tuple(e) for e in raw['directed_edges']] or shifts and np.asarray(shifts).tolist()!=raw['unit_shifts']:
                raise ValueError('current graph differs from saved independent CPU graph')
            numbers=tuple(int(z) for z in model.atomic_numbers.cpu()); attrs=np.zeros((len(xyz),len(numbers)))
            for i,z in enumerate(raw['numbers']): attrs[i,numbers.index(z)]=1.
            shifts=np.asarray(shifts,dtype=float).reshape(-1,3)
            position=torch.tensor(xyz,dtype=torch.float64,device=device,requires_grad=True)
            data={'positions':position,'node_attrs':torch.tensor(attrs,dtype=torch.float64,device=device),
                  'edge_index':torch.tensor(np.asarray(edges,dtype=np.int64).reshape(-1,2).T.copy(),device=device),
                  'shifts':torch.tensor(shifts@cell,dtype=torch.float64,device=device),
                  'unit_shifts':torch.tensor(shifts,dtype=torch.float64,device=device),
                  'cell':torch.tensor(cell,dtype=torch.float64,device=device),
                  'batch':torch.zeros(len(xyz),dtype=torch.int64,device=device),
                  'ptr':torch.tensor([0,len(xyz)],dtype=torch.int64,device=device),
                  'head':torch.zeros(1,dtype=torch.int64,device=device)}
            energy=model(data,compute_force=False)['energy'].sum()
            gradient=torch.autograd.grad(energy,position)[0]
            if diagnostic:
                try: (output/'mace-hlo.txt').write_text(torch_xla._XLAC._get_xla_tensors_hlo([energy,gradient]))
                except Exception as error: report['hlo_diagnostic_error']=repr(error)
            xm.mark_step(); xm.wait_device_ops()
            e=float(energy.cpu())*EV_TO_KJ_MOL; forces=-gradient.cpu().numpy()*EV_A_TO_KJ_MOL_NM
            case=next(c for c in reference['cases'] if c['kind']==row['case'])
            _,_,projection=_derived(case['real_atom_ids'],case['elements'],case['model_input_ids'],case['links'],row['real_positions_nm'])
            full=_project(forces,projection,len(case['real_atom_ids']))
            return e,full,{'graph_s':graph_s,'synchronized_end_to_end_s':time.monotonic()-start},forces
        for i,row in enumerate(reference['rows']):
            e,f,timing,raw_force=evaluate(row,diagnostic=i==0)
            report['rows'].append({'index':i,'energy_kj_mol':e,'all_real_ml_forces':f.tolist(),
                                   'model_forces_kj_mol_nm':raw_force.tolist(),
                                   **compare(row,e,f),**timing})
            _save(output/'report.json',report)
        fallback={k:(metrics.counter_value(k) or 0)-before.get(k,0) for k in metrics.counter_names() if k.startswith('aten::')}
        report['fallback_counters']=fallback
        (output/'metrics.txt').write_text(metrics.metrics_report())
        admit_tpu(report['backend'],double_ok,fallback)
        if not all(r['passed'] for r in report['rows']): raise ValueError('CPU energy/full-real force limits failed')
        # The device energies must also differentiate back to each base real
        # coordinate across all predeclared step sizes, including cap parents.
        fd=[]
        for i,row in enumerate(reference['rows']):
            if row['variant']!='base': continue
            candidates=[(j,v) for j,v in enumerate(reference['rows']) if v['case']==row['case'] and v['map']==row['map'] and v['variant']=='fd']
            for atom,step in sorted({(v['fd_atom'],v['step_nm']) for _,v in candidates}):
                energies={v['sign']:report['rows'][j]['energy_kj_mol'] for j,v in candidates if v['fd_atom']==atom and v['step_nm']==step}
                value=-(energies[1]-energies[-1])/(2*step); force=report['rows'][i]['all_real_ml_forces'][atom][1]
                fd.append({'base_index':i,'atom':atom,'step_nm':step,'fd':value,'force':force,'error':abs(value-force)})
        report['finite_differences']=fd; _save(output/'report.json',report)
        if any(r['step_nm']==1e-5 and r['error']>1e-3+1e-4*abs(r['force']) for r in fd):
            raise ValueError('TPU real-parent coordinate step sweeps failed')
        timings=[]
        for kind,mapping in itertools.product(('abfe','rbfe'),(0,1)):
            row=next(v for v in reference['rows'] if v['case']==kind and v['map']==mapping and v['variant']=='base')
            timings.append({'case':kind,'map':mapping,'repeats':[evaluate(row)[2] for _ in range(repeats)]})
        report['steady_timings']=timings
        report['status']='component-numerical-pass'; report['full_engine_qualification']=False
    except Exception as error:
        report['status']='incompatible'; report['error']=repr(error)
        (output/'exception.txt').write_text(traceback.format_exc())
        try:
            import torch_xla.debug.metrics as metrics
            (output/'metrics.txt').write_text(metrics.metrics_report())
        except Exception: pass
    _save(output/'report.json',report)
    return report['status']
