"""G04 fixture and hand-derived cap oracle; no production map or callback oracle."""
import hashlib
import json
from pathlib import Path

import numpy as np
import openmm as mm
from openmm import app, unit

from atm_mlmm.schema import (AtomIdentity, Bond, ComponentState, MoleculeState,
                             PartitionSpec, RuntimeSpec, Snapshot, SystemInput,
                             TopologyView)

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT/'fixtures/one_cut_alkane/input.json').read_text())
IDS = tuple(DATA['real_ids'])
REFERENCE = RuntimeSpec('Reference', 'double', (), .0005, 300., 'NVT', 'Verlet')


def input_case():
    topology = TopologyView(
        tuple(AtomIdentity(a, 'C' if i in (0, 1, 8) else 'H', 'P' if i<8 else 'L',
                           '1', '', DATA['atoms'][i]['name']) for i, a in enumerate(IDS)),
        tuple(Bond(IDS[a], IDS[b]) for a, b in DATA['bonds']),
        (MoleculeState('protein', IDS[:8], 'protein', 0, 1),
         MoleculeState('ligand', IDS[8:], 'ligand', 0, 1)))
    xml = (ROOT/'fixtures/one_cut_alkane/original-mm.xml').read_text()
    system = mm.XmlSerializer.deserialize(xml)  # fixed, inspected, hash-checked fixture
    assert hashlib.sha256(xml.encode()).hexdigest() == DATA['mm_system_sha256']
    original = SystemInput(xml, DATA['mm_system_sha256'], topology, DATA['positions_nm'],
                           None, tuple(system.getParticleMass(i).value_in_unit(unit.dalton)
                                       for i in range(13)), (), {'source': DATA['forcefield']})
    protein = ('p0', 'p2', 'p3', 'p4')
    spec = PartitionSpec(protein+IDS[8:], ('p0',), (('p0','p1'),),
                         (ComponentState(protein, 0, 1), ComponentState(IDS[8:], 0, 1)))
    return original, spec, Snapshot(IDS, DATA['positions_nm'], None)


def openmm_topology(view):
    topology = app.Topology()
    residues = {}
    atoms = []
    member = {a: m for m in view.molecules for a in m.atom_ids}
    for a in view.atoms:
        m = member[a.atom_id]
        if m.molecule_id not in residues:
            residues[m.molecule_id] = topology.addResidue(m.role, topology.addChain())
        atoms.append(topology.addAtom(a.atom_name, app.Element.getBySymbol(a.element), residues[m.molecule_id]))
    index = {a.atom_id:i for i,a in enumerate(view.atoms)}
    for b in view.bonds:
        topology.addBond(atoms[index[b.atom1]], atoms[index[b.atom2]])
    return topology


def cap_answer(positions, *, cap_k=7., pair_k=0., environment_k=0., ligand_k=5., distance=.117):
    r = np.asarray(positions, dtype=float)
    v = r[1]-r[0]
    length = np.linalg.norm(v)
    n = v/length
    h = r[0]+distance*n
    projector = distance/length*(np.eye(3)-np.outer(n,n))
    center = np.array((.13,-.08,.11))
    f = np.zeros_like(r)
    d = h-center
    energy = .5*cap_k*np.dot(d,d)
    fh = -cap_k*d
    for partner,k in ((8,pair_k),(5,environment_k)):
        d = h-r[partner]
        energy += .5*k*np.dot(d,d)
        fh -= k*d
        f[partner] += k*d
    d = r[8]-np.array((.02,.3,-.07))
    energy += .5*ligand_k*np.dot(d,d)
    f[8] -= ligand_k*d
    f[0] += (np.eye(3)-projector).T@fh
    f[1] += projector.T@fh
    return energy,f,h,fh


class RawCapPotential:
    """Diagnostic only: raw site forces; deliberately no parent projection."""
    def __call__(self, state):
        x = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
        delta = x-np.array((.13,-.08,.11))
        return float(3.5*np.sum(delta*delta)), -7.*delta


class FaultyBoundaryCallback:
    """Executable omission, extra projection and stale-input negatives."""
    def __init__(self,normal,mode,frozen_cap):
        self.normal,self.mode,self.frozen_cap=normal,mode,tuple(frozen_cap)

    def __call__(self,state):
        r=np.array(state.getPositions(asNumpy=True).value_in_unit(unit.nanometer))
        if self.mode=='stale-cap':r[13]=self.frozen_cap
        class Positions:
            def getPositions(self,asNumpy=False):return r*unit.nanometer
        energy,forces=self.normal(Positions())
        if self.mode=='omit-parent':forces[13]=0.
        elif self.mode=='omit-environment':forces[5]=0.
        elif self.mode=='double-parent':
            # Deliberately pre-project the raw site force onto both parents.
            # OpenMM will project it again, creating an actual double transfer.
            n=r[1]-r[0];length=np.linalg.norm(n);n/=length
            a=.117/length*(np.eye(3)-np.outer(n,n))
            forces[0]+=(np.eye(3)-a).T@forces[13]
            forces[1]+=a.T@forces[13]
        return energy,forces


def upstream_info():
    from openmmml.mlpotential import MLPotential, MLPotentialImpl, MLPotentialImplFactory
    class Impl(MLPotentialImpl):
        def getMLLongRange(self):
            return False
        def addForces(self, topology, system, atoms, forceGroup, **args):
            sites = [i for i in atoms if system.isVirtualSite(i)]
            assert len(sites)==1
            force = mm.PythonForce(RawCapPotential())
            force.setParticles(sites)
            force.setForceGroup(forceGroup)
            force.setName('diagnostic:raw-cap')
            system.addForce(force)
    class Factory(MLPotentialImplFactory):
        def createImpl(self,name,**args):
            return Impl()
    MLPotential.registerImplFactory('g04-diagnostic', Factory())
    original,_,_ = input_case()
    return MLPotential('g04-diagnostic').createMixedSystem(
        openmm_topology(original.topology), mm.XmlSerializer.deserialize(original.prepared_mm_artifact),
        DATA['ml_real_indices'], returnInfo=True, forceGroup=2,
        linkAtomDistances=[(0,1,.117*unit.nanometer)])
