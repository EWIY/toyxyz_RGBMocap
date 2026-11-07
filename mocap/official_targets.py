"""Local import receipts for bundled Epic and separately acquired official targets."""
import hashlib
import json
from pathlib import Path
from .paths import ROOT

REQUIRED = ('import.json', 'complete.json', 'mixamo-rig.json',
            'mixamo-rest.blend', 'mixamo-canonical.npz', 'mixamo-contact-geometry.npz')


def installed(key, *, verify=False, root=None):
    root = Path(root) if root is not None else ROOT
    registry = root / 'config/official-export-targets.json'
    if not registry.is_file():
        return None
    data = json.loads(registry.read_text(encoding='utf-8'))
    row = data.get('targets', {}).get(key)
    if row is None:
        return None
    asset = Path(row['asset'])
    asset = (asset if asset.is_absolute() else root / asset).resolve()
    base = (root / 'character_work/official_targets').resolve()
    if not asset.is_relative_to(base):
        raise ValueError('Official target must remain inside character_work/official_targets.')
    if not all((asset / name).is_file() for name in REQUIRED):
        raise RuntimeError('Installed official target is incomplete: ' + key)
    if verify:
        if not set(REQUIRED).issubset(row.get('files', {})):
            raise RuntimeError('Official target receipt is incomplete: ' + key)
        for name, expected in row['files'].items():
            path = (asset / name).resolve()
            if not path.is_relative_to(asset) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise RuntimeError('Installed official target changed; prepare it again: ' + key)
    return asset


def available():
    try:
        return all(installed(key) is not None for key in ('mixamo', 'ue5', 'unity'))
    except (OSError, ValueError, KeyError, TypeError, RuntimeError):
        return False


def ready(key):
    """Imported target presence for GUI status; export workers verify hashes."""
    try:
        return installed(key) is not None
    except (OSError, ValueError, KeyError, TypeError, RuntimeError):
        return False
