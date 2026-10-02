"""Independent geometry-only diagnosis; no scores, no structure changes."""
import json,pathlib,numpy as np
root=pathlib.Path('/workspace/AToM_MLMM-m00-review-v2/fixtures/chemical_reference/structures')
out=[]
for path in sorted(root.glob('ethanol-*-d*.json')):
 s=json.loads(path.read_text())
 if 'g07_controls' not in s:continue
 p=s['g07_controls']['parent'];r=np.array(p['positions_angstrom']);n=s['fragment_count'];l=np.array(s['positions_angstrom'])[n:];d=np.linalg.norm(r[:,None,:]-l[None,:,:],axis=2)
 pairs=[]
 for i,j in zip(*np.where(d<2.0)):
  pairs.append({'parent_id':p['atom_ids'][i],'parent_element':p['elements'][i],'ligand_id':s['atom_ids'][n+j],'ligand_element':s['elements'][n+j],'distance_angstrom':float(d[i,j]),'parent_in_baseline_ml':p['atom_ids'][i] in s['g07_controls']['choices'][0]['protein_ml_ids']})
 out.append({'row':s['name'],'pairs_below_2_A':sorted(pairs,key=lambda x:x['distance_angstrom'])})
print(json.dumps(out,indent=2))
