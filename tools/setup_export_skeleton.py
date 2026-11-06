"""Register a user-owned humanoid FBX as an optional bone-only export target.

Run after install.cmd using runtime/python.exe. No characters are downloaded or
distributed. Existing registered targets and the source FBX are never replaced.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mocap.rig_export import PRESET_FILES, SKELETONS, preset_ready


def register(skeleton, filename):
    if skeleton not in SKELETONS:
        raise ValueError('Unsupported target skeleton.')
    filename = Path(filename).resolve(strict=True)
    if filename.suffix.lower() != '.fbx' or not filename.is_file():
        raise ValueError('Select your own licensed humanoid FBX character with a mesh.')
    python = ROOT / 'runtime/python.exe'
    if not python.is_file():
        raise RuntimeError('Run install.cmd before preparing an export target.')
    presets = ROOT / 'character_work/presets'
    presets.mkdir(parents=True, exist_ok=True)
    target = presets / skeleton
    if target.exists():
        raise FileExistsError('Existing target was preserved: ' + str(target))
    ident = uuid.uuid4().hex
    staging = presets / ('.import-' + ident)
    request = presets / ('.request-' + ident + '.json')
    request.write_text(json.dumps(dict(mode='import', file=str(filename), output=str(staging), id=skeleton)), encoding='utf-8')
    try:
        subprocess.run([str(python), '-I', '-X', 'utf8', '-B', str(ROOT / 'worker_boot.py'),
                        'character', '--request', str(request)], cwd=ROOT, check=True,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if not all((staging / name).is_file() for name in PRESET_FILES):
            raise RuntimeError('Import did not produce the required export-target files. Staging was preserved: ' + str(staging))
        info = json.loads((staging / 'import.json').read_text(encoding='utf-8'))
        if info['kind'] != 'mixamo':
            raise ValueError('Export targets must use the supported FBX humanoid mapping.')
        staging.rename(target)
    finally:
        request.unlink(missing_ok=True)
    if not preset_ready(skeleton):
        raise RuntimeError('Target registration is incomplete.')
    print('Registered ' + skeleton + '. Restart RGBMoCap to enable this export target.')
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skeleton', choices=SKELETONS, required=True)
    parser.add_argument('--file', type=Path, required=True)
    args = parser.parse_args()
    register(args.skeleton, args.file)


if __name__ == '__main__':
    main()
