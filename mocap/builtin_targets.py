"""Prepare versioned local caches from redistributable skeleton source code."""
import hashlib
import json
from pathlib import Path
import uuid

from .builtin_skeletons import KEYS, VERSION
from .paths import ROOT, HOME

FILES = ('import.json', 'complete.json', 'mixamo-rig.json', 'mixamo-rest.blend',
         'mixamo-canonical.npz', 'mixamo-contact-geometry.npz')
SOURCES = ('mocap/builtin_skeletons.py', 'mocap/retarget/blender_builtin.py',
           'mocap/retarget/blender_geometry.py', 'mocap/retarget/mapping.py')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signature(key):
    if key not in KEYS:
        raise ValueError('Unknown built-in skeleton: '+str(key))
    values = [key, str(VERSION)] + [digest(ROOT/name) for name in SOURCES]
    return hashlib.sha256('\n'.join(values).encode()).hexdigest()


def valid(folder, key, identity):
    try:
        receipt = json.loads((folder/'template.json').read_text(encoding='utf-8'))
        return (receipt['key'] == key and receipt['signature'] == identity and
                set(receipt['files']) == set(FILES) and
                all(digest(folder/name) == receipt['files'][name] for name in FILES))
    except (OSError, ValueError, KeyError, TypeError):
        return False


def prepare(key):
    identity = signature(key)
    base = HOME/'cache/export-targets'
    target = base/(key+'-'+identity[:20])
    if valid(target, key, identity):
        return target
    base.mkdir(parents=True, exist_ok=True)
    staging = base/('.build-'+uuid.uuid4().hex)
    staging.mkdir()
    from .retarget.worker import invoke
    invoke('builtin', staging, key)
    receipt = dict(key=key,version=VERSION,signature=identity,
                   files={name:digest(staging/name) for name in FILES})
    (staging/'template.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    if not valid(staging, key, identity):
        raise RuntimeError('Built-in skeleton preparation failed validation: '+str(staging))
    # Preserve a damaged generation for inspection. Never delete a registered
    # character. Another worker may have finished the same generation meanwhile.
    if target.exists():
        if valid(target, key, identity):
            return target
        target.rename(base/(target.name+'.invalid-'+uuid.uuid4().hex))
    try:
        staging.rename(target)
    except FileExistsError:
        if not valid(target, key, identity):
            raise
    return target
