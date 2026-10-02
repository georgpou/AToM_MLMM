import ast
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def test_shared_contracts_have_no_model_import():
    code = '''
import importlib.abc, sys
forbidden = {'openmm','openmmml','mace','torch','torchani','ase','cupy'}
class BlockHeavy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in forbidden:
            raise AssertionError('heavy dependency: ' + fullname)
sys.meta_path.insert(0, BlockHeavy())
import atm_mlmm.schema, atm_mlmm.identity, atm_mlmm.partition, atm_mlmm.capabilities
import atm_mlmm.protocols.abfe, atm_mlmm.protocols.rbfe
assert not forbidden.intersection(sys.modules)
'''
    result = subprocess.run([sys.executable, '-c', code], env=dict(os.environ, PYTHONPATH=str(ROOT/'src')), text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    for path in (ROOT/'src/atm_mlmm').rglob('*.py'):
        names = []
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                names.extend(a.name for a in node.names)
            if isinstance(node, ast.ImportFrom):
                names.append(node.module or '')
        relative = str(path.relative_to(ROOT/'src/atm_mlmm'))
        if relative.startswith('protocols/'):
            assert not any('models' in n or 'embeddings' in n for n in names), relative
        if relative.startswith('embeddings/'):
            assert not any('protocols' in n for n in names), relative
        if relative in ('schema.py', 'identity.py'):
            assert not any(n.split('.')[0] in {'openmm', 'mace', 'torch'} for n in names), relative


def test_new_transfer_modules_keep_upstream_knowledge_in_adapter():
    for path in (ROOT/'src/atm_mlmm').rglob('*.py'):
        relative = str(path.relative_to(ROOT/'src/atm_mlmm'))
        tree = ast.parse(path.read_text())
        imports = [node.module or '' for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        if any(name.startswith('atom_openmm') for name in imports):
            assert relative == 'adapters/atom.py', relative
        if relative != 'adapters/atom.py':
            literals = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
            assert not literals.intersection({'VARIABLE_FORCE_GROUP', 'LIGAND_ATOMS', 'LIGAND1_ATOMS', 'LIGAND2_ATOMS'}), relative
        if relative == 'atm.py':
            assert not any(name.startswith(('mace', 'torch', 'atm_mlmm.models', 'atm_mlmm.embeddings')) for name in imports)
