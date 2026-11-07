"""Import an official-resource skinned FBX into a verified local export slot.

Acquire the character from the publisher first. This tool checks the supported
hierarchy and records the selected bytes; it cannot authenticate their publisher
or grant permission to redistribute them. Existing asset versions are preserved.
"""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mocap.official_targets import REQUIRED, installed
from mocap.rig_export import SKELETONS, TARGET_SOURCES
from mocap.storage import atomic_json, sha256


@contextmanager
def registry_lock(root):
    """Serialize registry changes; OS releases the lock if an import is stopped."""
    path = root / 'config/official-targets.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as stream:
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def import_target(filename, output, skeleton):
    python = ROOT / 'runtime/python.exe'
    if not python.is_file():
        raise RuntimeError('Run install.cmd before preparing an official target.')
    request = output.with_suffix('.request.json')
    atomic_json(request, dict(mode='import', file=str(filename), output=str(output), id=skeleton))
    try:
        subprocess.run([str(python), '-I', '-X', 'utf8', '-B', str(ROOT / 'worker_boot.py'),
                        'character', '--request', str(request)], cwd=ROOT, check=True,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    finally:
        request.unlink(missing_ok=True)


def validate_target(folder, key):
    if not all((folder / name).is_file() for name in REQUIRED):
        raise RuntimeError('Official target import is incomplete; diagnostic files were preserved.')
    info = json.loads((folder / 'import.json').read_text(encoding='utf-8'))
    rig = json.loads((folder / 'mixamo-rig.json').read_text(encoding='utf-8'))
    if info.get('kind') != 'mixamo' or not rig.get('meshes') or len(rig.get('finger_mapping', {})) != 30:
        raise ValueError('The official target needs one supported FBX body, a skinned mesh and all 30 finger segments.')
    finger = rig['finger_mapping'].get('LeftHandIndex1', '').split(':')[-1]
    expected = dict(mixamo='LeftHandIndex1', ue5='index_01_l', unity='LeftIndexProximal')
    if finger != expected[key]:
        raise ValueError('The selected FBX does not match the requested official target hierarchy: ' + key)
    bones = {bone['name'].split(':')[-1] for bone in rig['bones']}
    if key == 'ue5' and not {'spine_05', 'neck_02'}.issubset(bones):
        raise ValueError('Use the UE5 Manny/Quinn hierarchy with five spine and two neck segments.')


def register(skeleton, filename, *, replace=False, data_root=None):
    if skeleton not in SKELETONS:
        raise ValueError('Unsupported official target slot.')
    filename = Path(filename).resolve(strict=True)
    if filename.suffix.lower() != '.fbx' or not filename.is_file():
        raise ValueError('Select the official character FBX with its skinned mesh.')
    source_hash = sha256(filename)
    root = Path(data_root) if data_root is not None else ROOT
    registry = root / 'config/official-export-targets.json'
    with registry_lock(root):
        data = json.loads(registry.read_text(encoding='utf-8')) if registry.exists() else dict(schema=1, targets={})
        if skeleton in data['targets'] and not replace:
            raise FileExistsError('Existing official target was preserved. Use --replace to register a new version.')
        base = root / 'character_work/official_targets' / skeleton
        base.mkdir(parents=True, exist_ok=True)
        version = uuid.uuid4().hex
        staging = base / ('.import-' + version)
        target = base / version
        import_target(filename, staging, skeleton)
        validate_target(staging, skeleton)
        if sha256(filename) != source_hash:
            raise RuntimeError('Source FBX changed during import. Existing registration was preserved.')
        hashes = {}
        for path in staging.rglob('*'):
            if path.is_symlink() or not path.resolve().is_relative_to(staging.resolve()):
                raise ValueError('Imported target contains an external link.')
            if path.is_file():
                hashes[path.relative_to(staging).as_posix()] = sha256(path)
        staging.rename(target)
        row = dict(label=TARGET_SOURCES[skeleton][0], asset=target.relative_to(root).as_posix(),
                   source_file=str(filename), source_sha256=source_hash,
                   url=TARGET_SOURCES[skeleton][1], files=hashes)
        # Publish only after the import, family and source-byte checks succeed.
        candidate = dict(data, targets=dict(data['targets'], **{skeleton: row}))
        if registry.exists():
            atomic_json(registry.with_name('official-export-targets.previous.json'), data)
        atomic_json(registry, candidate)
        if installed(skeleton, verify=True, root=root) != target.resolve():
            raise RuntimeError('Official target registration did not validate.')
    print('Registered ' + TARGET_SOURCES[skeleton][0] + '. Original skin retained; old asset versions preserved.', flush=True)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skeleton', choices=SKELETONS, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--file', type=Path)
    source.add_argument('--bundled', action='store_true', help='Prepare the included official Epic Manny resource (UE5 only).')
    parser.add_argument('--replace', action='store_true', help='Register a new version while retaining the previous asset files.')
    args = parser.parse_args()
    if args.bundled:
        if args.skeleton != 'ue5':
            parser.error('--bundled is only available for ue5.')
        from mocap.bundled_targets import source as bundled_source
        filename = bundled_source(args.skeleton)
    else:
        filename = args.file
    register(args.skeleton, filename, replace=args.replace)


if __name__ == '__main__':
    main()
