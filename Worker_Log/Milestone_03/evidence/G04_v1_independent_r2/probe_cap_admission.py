"""Independent cap record/executable site admission negatives and positive control."""
from dataclasses import replace
import json,pathlib
import openmm as mm
from tests.integration.test_link_geometry import case
from atm_mlmm.atm import physical_system,xml_digest
from atm_mlmm.schema import IdentityError,MalformedInput,UnsupportedCapability,to_json,from_json
b,s=case();link=b.links[0];rows=[]
def reject(name,fn):
 try:fn()
 except (IdentityError,MalformedInput,UnsupportedCapability) as e:rows.append(dict(name=name,rejected=True,error=type(e).__name__,diagnostic=str(e)))
 else:rows.append(dict(name=name,rejected=False))
def changed_link(**kw):return replace(b,links=(replace(link,**kw),))
reject('cap-alias-real',lambda:changed_link(cap_id='p5'))
reject('cap-final-overlaps-real',lambda:changed_link(final_particle_index=5))
reject('wrong-model-slot',lambda:changed_link(model_input_index=0))
reject('MM-parent-is-ML',lambda:changed_link(mm_parent_id='l8'))
reject('reversed-parents',lambda:changed_link(ml_parent_id='p1',mm_parent_id='p0'))
reject('unsupported-site-type',lambda:changed_link(virtual_site_type='TwoParticleAverageSite'))
reject('zero-distance',lambda:changed_link(distance_nm=0.))
reject('future-builder-version',lambda:replace(b,manifest={**b.manifest,'boundary_builder_version':2}))
reject('missing-link-record',lambda:replace(b,links=()))
reject('massive-cap',lambda:replace(b,masses_da=(*b.masses_da[:13],1.)))
reject('metadata-distance-vs-executable',lambda:physical_system(changed_link(distance_nm=.118)))
# Resign only the executable artifact digest to exercise site validation rather
# than a trivial XML hash mismatch. No production artifact is overwritten.
def altered_site(mode):
 system=physical_system(b)
 parents=[1,0] if mode=='parents' else [0,1]
 weights=[.5,.5] if mode=='weights' else [1.,0.]
 system.setVirtualSite(13,mm.LocalCoordinatesSite(parents,weights,[-1.,1.],[0.,0.],[.117,0.,0.]))
 xml=mm.XmlSerializer.serialize(system)
 return physical_system(replace(b,system_xml=xml,system_sha256=xml_digest(xml)))
reject('executable-wrong-parent-order',lambda:altered_site('parents'))
reject('executable-wrong-origin-weights',lambda:altered_site('weights'))
assert from_json(to_json(b))==b
assert physical_system(b).getNumParticles()==14
report={'negative_count':len(rows),'positive_count':2,'rows':rows}
with (pathlib.Path(__file__).parent/'cap-admission-results.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2));assert all(r['rejected'] for r in rows)
