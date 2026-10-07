"""Pinned academic MACE-OFF23-small loading; heavy imports stay at this boundary."""
import hashlib
import io
import json
import os
from pathlib import Path

from ..schema import IdentityError, ModelSpec, UnsupportedCapability


ROOT = Path(__file__).resolve().parents[3]
_configured_asset_dir = os.environ.get('ATOM_MLMM_MODEL_DIR')
ASSET = (Path(_configured_asset_dir).expanduser().resolve() if _configured_asset_dir
         else ROOT / 'models/mace-off23-small')
CHECKPOINT = ASSET / 'MACE-OFF23_small.model'
CHECKPOINT_SHA256 = '165cce4cfec5a34b9c64d4ebf95de15d71106bb584b7291c8470f0749977c46f'
LICENSE_SHA256 = '6a77e88bfed86fe9476ed36e453e2ea1e154ff1ec464b0fdeb3e079b6112d71e'
MANIFEST_SHA256 = '6d78f71f779798b67d73da573c67e2ce65ba6c2bfe1d1d3b8fa6c72d603a0926'
USER_AUTHORIZATION = 'I will use it for academic purposes.'
UPSTREAM_COMMIT = '91a78c5a9c300d1104700d9352c8bfe449227737'
ELEMENTS = ('H', 'C', 'N', 'O')
# CODATA 2014 constants: the independently recorded convention of pinned ASE.
EV_TO_KJ_MOL = 1.6021766208e-19 * 6.022140857e23 / 1000.
EV_A_TO_KJ_MOL_NM = 10. * EV_TO_KJ_MOL


def _verified_bytes(checkpoint, manifest_path):
    checkpoint = Path(checkpoint)
    if checkpoint.is_symlink():
        raise IdentityError('approved model checkpoint must not be a symlink')
    try:
        payload = checkpoint.read_bytes()
    except OSError as exc:
        raise IdentityError('approved model asset is absent or unreadable') from exc
    if hashlib.sha256(payload).hexdigest() != CHECKPOINT_SHA256:
        raise IdentityError('MACE checkpoint SHA-256 differs from the approved asset')
    manifest_path = Path(manifest_path) if manifest_path is not None else checkpoint.parent / 'manifest.json'
    if manifest_path.is_symlink() or (manifest_path.parent / 'LICENSE.md').is_symlink():
        raise IdentityError('approved model manifest and licence must not be symlinks')
    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes)
    except (OSError, ValueError) as exc:
        raise IdentityError('approved model manifest is absent or malformed') from exc
    if not isinstance(manifest, dict):
        raise IdentityError('approved model manifest must be an object')
    authorization = manifest.get('user_authorization')
    if authorization != USER_AUTHORIZATION:
        raise IdentityError('model authorization record differs from the approved user authorization')
    if hashlib.sha256(manifest_bytes).hexdigest() != MANIFEST_SHA256:
        raise IdentityError('model manifest SHA-256 differs from the approved asset manifest')
    expected = {
        'name': 'MACE-OFF23-small',
        'upstream_repository': 'https://github.com/ACEsuit/mace-off',
        'upstream_commit': UPSTREAM_COMMIT,
        'checkpoint_url': f'https://raw.githubusercontent.com/ACEsuit/mace-off/{UPSTREAM_COMMIT}/mace_off23/MACE-OFF23_small.model',
        'license': 'Academic Software Licence v1.0; academic noncommercial use',
        'energy_convention': 'energy (includes atom reference energies)',
        'device': 'CPU',
        'dtype': 'float64',
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise UnsupportedCapability(f'model manifest {key} differs from the admitted checkpoint policy')
    for key in ('retrieved', 'loading_policy', 'citation', 'upstream_readme_url'):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            raise IdentityError(f'model manifest is missing {key}')
    files = manifest.get('files')
    expected_files = {
        'MACE-OFF23_small.model': {'sha256': CHECKPOINT_SHA256, 'bytes': 7347350},
        'LICENSE.md': {'sha256': LICENSE_SHA256, 'bytes': 16366},
    }
    if files != expected_files:
        raise IdentityError('model manifest file identities differ from pinned checkpoint/licence')
    try:
        license_bytes = (manifest_path.parent / 'LICENSE.md').read_bytes()
    except OSError as exc:
        raise IdentityError('model licence is absent or unreadable') from exc
    if len(payload) != 7347350 or len(license_bytes) != 16366 or hashlib.sha256(license_bytes).hexdigest() != LICENSE_SHA256:
        raise IdentityError('model/licence bytes or SHA-256 differ from the approved asset')
    return manifest, payload


def verify_asset(checkpoint=CHECKPOINT, manifest_path=None):
    """Validate asset, permission, licence and settings without importing ML code."""
    manifest, _ = _verified_bytes(checkpoint, manifest_path)
    return manifest


def _imports():
    import torch
    try:
        import mace  # Its upstream import sets a global unsafe-load override.
    finally:
        os.environ.pop('TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD', None)
    try:
        with torch.serialization.safe_globals([slice]):
            from mace.calculators import MACECalculator
    finally:
        os.environ.pop('TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD', None)
    return torch, MACECalculator


def load_model(checkpoint=CHECKPOINT, manifest_path=None):
    """Explicitly deserialize only the same retained bytes that passed all guards."""
    _, payload = _verified_bytes(checkpoint, manifest_path)
    torch, _ = _imports()
    model = torch.load(io.BytesIO(payload), map_location='cpu', weights_only=False)
    if type(model).__module__ + '.' + type(model).__qualname__ != 'mace.modules.models.ScaleShiftMACE':
        raise UnsupportedCapability('checkpoint architecture differs from ScaleShiftMACE')
    tensors = list(model.parameters()) + list(model.buffers())
    if (any(t.device.type != 'cpu' for t in tensors)
            or any(t.is_floating_point() and t.dtype != torch.float64 for t in tensors)
            or model.atomic_numbers.tolist() != [1, 6, 7, 8, 9, 15, 16, 17, 35, 53]
            or float(model.r_max) != 4.5 or int(model.num_interactions) != 2):
        raise UnsupportedCapability('checkpoint elements/cutoff/dtype/device differ from the frozen asset')
    model.eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)  # Weights are fixed; coordinate gradients remain enabled.
    return model


def make_calculator(checkpoint=CHECKPOINT, manifest_path=None):
    """Use the maintained ASE adapter with explicit total-energy and unit settings."""
    model = load_model(checkpoint, manifest_path)
    _, calculator_type = _imports()
    calculator = calculator_type(models=model, device='cpu', default_dtype='float64',
                                 head='Default', energy_units_to_eV=1., length_units_to_A=1.)
    if calculator.head != 'Default' or calculator.model_type != 'MACE':
        raise UnsupportedCapability('calculator head/output model differs from the frozen policy')
    return calculator


class PinnedASECalculator:
    """ASE energy/force facade with a deterministic, hash-checked load recipe.

    A live PyTorch module does not have byte-stable pickle round trips. Store
    immutable asset paths instead so exact XML/force ownership remains usable.
    Deserialization and calculator initialization never download an asset.
    """
    def __init__(self, checkpoint=CHECKPOINT, manifest_path=None):
        verify_asset(checkpoint, manifest_path)
        self.checkpoint = str(Path(checkpoint).resolve())
        self.manifest_path = str(Path(manifest_path).resolve()) if manifest_path is not None else None
        self._calculator = None

    def __getstate__(self):
        checkpoint = None if self.checkpoint == str(CHECKPOINT.resolve()) and self.manifest_path is None else self.checkpoint
        return {'checkpoint': checkpoint, 'manifest_path': self.manifest_path}

    def __setstate__(self, state):
        # XML's trusted pickle reconstructs an inert recipe. Asset verification
        # occurs before weight deserialization in _engine, not inside the C++
        # XML unpickler. Bundled assets resolve in the current installation.
        self.checkpoint = str(CHECKPOINT.resolve()) if state['checkpoint'] is None else state['checkpoint']
        self.manifest_path = state['manifest_path']
        self._calculator = None

    def _engine(self):
        if self._calculator is None:
            self._calculator = make_calculator(self.checkpoint, self.manifest_path)
        return self._calculator

    def get_potential_energy(self, atoms=None, force_consistent=False):
        return self._engine().get_potential_energy(atoms, force_consistent=force_consistent)

    def get_forces(self, atoms=None):
        return self._engine().get_forces(atoms)


def model_spec():
    """Candidate metadata, not a claim of chemical or gate acceptance."""
    return ModelSpec('mace-off23-small', CHECKPOINT_SHA256, 'energy', ELEMENTS,
                     'neutral_singlet', 'local', 'float64')
