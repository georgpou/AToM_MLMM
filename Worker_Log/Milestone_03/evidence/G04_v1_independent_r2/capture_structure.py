import json,pathlib
from dataclasses import asdict
import openmm as mm
from openmm import unit
from tests.integration.test_link_geometry import case
from tests.link_oracle import input_case,upstream_info
from tests.link_permutation import permute_info
from tests.integration.test_boundary_ledger import predicate_fixture
from atm_mlmm.atm import physical_system
from atm_mlmm.embeddings.mechanical import seal_boundary_result
from atm_mlmm.partition import resolve_partition
from atm_mlmm.geometry import resolve_protocol
from atm_mlmm.protocols.abfe import make_protocol
from atm_mlmm.schema import MobileGroup,to_json
from atm_mlmm.ledger import boundary_dispositions
from openmmml import MLPotential
out=pathlib.Path(__file__).parent
b,s=case(pair_k=4.,environment_k=10.)
original,spec,_=input_case();info=upstream_info();actual_old_to_new=info['oldToNew']
p=(9,4,1,12,8,0,11,3,7,2,13,6,10,5)
remapped=seal_boundary_result(original,resolve_partition(original.topology,spec),permute_info(info,p),manifest={'fixture_kind':'analytic_substitute','boundary_builder_version':1})
records=[]
for label,bundle in [('actual',b),('permuted',remapped)]:
 transfer=resolve_protocol(bundle,make_protocol((MobileGroup('ligand',tuple(s.real_atom_ids[8:]),('ligand',),'ligand'),),(.3,.1,-.2)))
 system=physical_system(bundle)
 records.append(dict(label=label,link=asdict(bundle.links[0]),real_ids=s.real_atom_ids,real_to_final=dict(bundle.real_to_final),old_to_new=bundle.old_to_new,model_input_ids=bundle.model_input_ids,model_to_final=dict(bundle.model_to_final),pythonforce_selected=[list(f.getParticles()) for f in system.getForces() if isinstance(f,mm.PythonForce)],map0=transfer.displacement0_nm,map1=transfer.displacement1_nm,masses=bundle.masses_da,constraints=bundle.constraints,physical=json.loads(to_json(bundle))))
top,original,ml=predicate_fixture();actual=MLPotential('g04-diagnostic').createMixedSystem(top,original,ml,returnInfo=True,forceGroup=2)
retained=actual['system'];retained.removeForce(retained.getNumForces()-1)
ledger=boundary_dispositions(original,retained,actual['oldToNew'],tuple(f's{i}' for i in range(8)))
result={'actual_openmmml_old_to_new':actual_old_to_new,'cases':records,'predicate_ledger':ledger,'predicate_original_xml':mm.XmlSerializer.serialize(original),'predicate_retained_xml':mm.XmlSerializer.serialize(retained)}
with (out/'structure.json').open('x') as f:json.dump(result,f,indent=2)
print('Captured actual and nonidentity complete maps/model ordering/geometry/ledger; distinctive predicate ledger rows:',len(ledger))
