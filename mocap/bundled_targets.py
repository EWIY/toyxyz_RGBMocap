"""Prepare the hash-pinned official Epic template resource off the GUI thread."""
from pathlib import Path
from .paths import ROOT
from .storage import sha256

MANNY_FILE = 'assets/export_skeletons/ue5_manny/SKM_Manny_Simple.fbx'
MANNY_SHA256 = 'e512a2fa10ade6189d8d2ba64b5016e11ab2cfd17eee656fa30618d8dc9dbc87'
MANNY_BYTES = 2887824


def available(key):
    """Cheap source-presence check for selectors; full hashing happens in workers."""
    if key != 'ue5':
        return False
    path = ROOT / MANNY_FILE
    return path.is_file() and path.stat().st_size == MANNY_BYTES


def source(key):
    if key != 'ue5':
        raise ValueError('No bundled official resource for: ' + str(key))
    path = ROOT / MANNY_FILE
    if not available(key) or sha256(path) != MANNY_SHA256:
        raise RuntimeError('Bundled Manny is missing or changed. Restore the verified source resource.')
    return path


def prepare(key, *, root=None):
    """Called from a worker, reusing complete user registration before import."""
    from .official_targets import installed
    root = Path(root) if root is not None else ROOT
    existing = installed(key, verify=True, root=root)
    if existing is not None:
        return existing
    filename = source(key)
    from tools.setup_official_target import register
    try:
        return register(key, filename, data_root=root)
    except FileExistsError:
        # A second sequential worker may have registered it in the meantime.
        existing = installed(key, verify=True, root=root)
        if existing is None:
            raise
        return existing
