"""Audit the indexed source tree and its manifest before publishing this fork.

Uses only Python's standard library and Git. It never installs software, runs
models, reads credentials or deletes user data. Run from any working directory.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'SOURCE_MANIFEST.json'
FORBIDDEN_TOP = {'models', 'projects', 'cache', 'character_work', 'character_scenes', 'character_library',
                 '.setup', '.cache', '.bootstrap', '.runtime', 'build', 'dist',
                 'releases', 'temp', 'config', 'validation-output', '_tmp', '_audit'}
LIBRARY_FILES = frozenset(('character_library/README.md',
                           'character_library/UE5/SKM_Manny_Simple.fbx'))
PAYLOAD_SUFFIXES = {'.pt', '.pth', '.ckpt', '.safetensors', '.onnx', '.npz', '.npy',
                    '.pkl', '.fbx', '.bvh', '.blend', '.vrm', '.pmx', '.vmd', '.pmd',
                    '.vpd', '.pmm', '.mp4', '.avi', '.mov', '.mkv', '.webm', '.exe',
                    '.dll', '.pyd', '.pyc', '.pyo', '.whl', '.zip', '.7z', '.log'}
SOURCE_DOCS = ('README.md', 'README.zh-CN.md', 'README.upstream.md',
               'docs/FORK_GUIDE.md', 'docs/PUBLISHING.md', 'docs/FORK_VALIDATION.md',
               'docs/OFFICIAL_EXPORT_TARGETS.md', 'assets/export_skeletons/README.md',
               'docs/CHARACTER_LIBRARY.md', 'character_library/README.md',
               'assets/export_skeletons/ue5_manny/NOTICE.md')
FEATURE_FILES = {
    'bilingual interface': ('mocap/i18n.py','mocap/i18n_zh.py','mocap/i18n_help_zh.py'),
    'Fusion': ('mocap/fusion.py','mocap/fusion_pipeline.py','mocap/fusion_native.py','mocap/fusion_scene.py','mocap/fusion_ui.py'),
    'shared scene origin': ('mocap/flow_origin.py',),
    'HumanArt': ('mocap/yolox_humanart.py','mocap/detectors.py'),
    'official skeleton export': ('mocap/official_targets.py','mocap/rig_export.py','mocap/export_targets_ui.py','mocap/retarget/blender_fingers.py','mocap/retarget/finger_transport.py','mocap/retarget/blender_materials.py','tools/setup_official_target.py'),
    'bundled official Manny': ('mocap/bundled_targets.py','mocap/export_paths.py','character_library/UE5/SKM_Manny_Simple.fbx','assets/export_skeletons/ue5_manny/PROVENANCE.json','assets/export_skeletons/ue5_manny/LICENSE.txt','assets/export_skeletons/ue5_manny/NOTICE.md'),
    'stability': ('mocap/wheel_guard.py',),
    'character library': ('character_library/README.md','mocap/character_library.py','mocap/character_ui.py','mocap/people_ui.py','docs/CHARACTER_LIBRARY.md'),
}
OFFICIAL_VGGT = 'c02da418b18bb01d0392598d3f6147366bcde1bb70fd08a5e3bf7925b0667934'


def git(*args):
    return subprocess.check_output(['git', '-c', 'safe.directory='+ROOT.as_posix(),
                                    '-C', str(ROOT), *args])


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024**2), b''):
            digest.update(data)
    return digest.hexdigest()


def indexed_files():
    if git('ls-files', '--unmerged', '-z'):
        raise ValueError('Resolve and stage all merge conflicts before publishing.')
    return sorted(set(name for name in git('ls-files', '--cached', '-z').decode('utf-8').split('\0') if name))


def audit(names):
    errors = []
    for feature, required in FEATURE_FILES.items():
        for name in required:
            if name not in names:
                errors.append('Missing tracked '+feature+' source: '+name)
    resources = {row['path']: row for row in json.loads((ROOT/'installer/source-resources.json').read_text(encoding='utf-8'))['files']}
    auxiliary = {row['path'] for row in json.loads((ROOT/'installer/external-assets.json').read_text(encoding='utf-8'))['files']}
    rows = []
    exceptions = []
    for name in names:
        relative = Path(name)
        path = ROOT/relative
        if relative.is_absolute() or '..' in relative.parts or not path.is_file():
            errors.append('Invalid or missing indexed file: '+name)
            continue
        info = path.lstat()
        if path.is_symlink() or getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0):
            errors.append('Source links are not publishable: '+name)
            continue
        first = relative.parts[0]
        if (first in FORBIDDEN_TOP and name not in LIBRARY_FILES) or first.startswith(('runtime', '.venv')) or '__pycache__' in relative.parts:
            errors.append('Private/generated directory is indexed: '+name)
        if name.startswith(('assets/rigs/', 'tools/bin/')) or name in auxiliary:
            errors.append('Locally acquired/generated asset is indexed: '+name)
        if re.search(r'\.bak(?:-|$)|\.(?:orig|rej)$', name, re.I) or path.name.startswith('.env') or path.suffix.lower() in {'.pem', '.key'}:
            errors.append('Backup or credential file is indexed: '+name)
        checksum = sha(path)
        if path.suffix.lower() in PAYLOAD_SUFFIXES:
            allowed = resources.get(name)
            if not allowed or allowed['bytes'] != info.st_size or allowed['sha256'] != checksum:
                errors.append('Unapproved binary/model/media payload: '+name)
            else:
                exceptions.append(name)
        if info.st_size >= 95*1024**2:
            errors.append('File approaches GitHub blob size limit: '+name)
        if path.suffix == '.py':
            try:
                tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=name)
                if name.startswith('mocap/'):
                    for node in ast.walk(tree):
                        if not isinstance(node, ast.ImportFrom) or not node.module:
                            continue
                        if node.level:
                            parts = list(relative.parent.parts)
                            if node.level > 1:
                                parts = parts[:-(node.level-1)]
                            parts += node.module.split('.')
                        elif node.module.startswith('mocap.'):
                            parts = node.module.split('.')
                        else:
                            continue
                        module = ROOT.joinpath(*parts)
                        if not module.with_suffix('.py').is_file() and not (module/'__init__.py').is_file():
                            errors.append(f'Missing application import at {name}:{node.lineno}: {node.module}')
            except (SyntaxError, UnicodeError) as exc:
                errors.append(str(exc))
        if path.suffix.lower() in {'.py', '.md', '.txt', '.json', '.cmd', '.ps1', '.yml', '.yaml'} and info.st_size < 4*1024**2:
            text = path.read_text(encoding='utf-8-sig', errors='replace')
            if re.search(r'[AC]:[\\/]+(?:cu130-comfy|Users[\\/]+EWIY)', text, re.I):
                errors.append('Developer-specific absolute path: '+name)
            if re.search(r'gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{70,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', text):
                errors.append('Possible secret material: '+name)
            if re.search(r'^<<<<<<< (?:ours|theirs|HEAD)$|^>>>>>>> (?:ours|theirs|[0-9a-f]{7,40})$', text, re.M):
                errors.append('Unresolved merge marker: '+name)
        if name != 'SOURCE_MANIFEST.json':
            rows.append(dict(path=name, bytes=info.st_size, sha256=checksum))
    for name in SOURCE_DOCS:
        path = ROOT/name
        if not path.is_file():
            errors.append('Missing fork documentation: '+name)
            continue
        for match in re.finditer(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)', path.read_text(encoding='utf-8')):
            link = match.group(1).strip('<>')
            if link.startswith(('#', 'http:', 'https:', 'mailto:')):
                continue
            local = unquote(link.split('#',1)[0])
            if local and not (path.parent/local).exists():
                errors.append(f'Broken relative documentation link: {name} -> {local}')
    lock = json.loads((ROOT/'installer/runtime-lock.json').read_text(encoding='utf-8'))
    if lock['registry_sha256'] != sha(ROOT/'mocap/runtime_registry.py'):
        errors.append('Runtime registry/lock hash mismatch.')
    if lock.get('models_included') is not False:
        errors.append('The runtime lock must exclude model weights.')
    for group in lock['groups']:
        for package in group['packages']:
            if package.get('url') and not package['url'].startswith('https://'):
                errors.append('Non-HTTPS runtime package: '+package['name'])
            if not re.fullmatch('[0-9a-f]{64}', package['sha256']):
                errors.append('Missing runtime package hash: '+package['name'])
    model_tree = ast.parse((ROOT/'mocap/models.py').read_text(encoding='utf-8'))
    vggt = [node for node in ast.walk(model_tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='Model' and node.args and isinstance(node.args[0],ast.Constant) and node.args[0].value=='flow_vggt']
    if len(vggt) != 1 or not any(kw.arg=='expected_sha256' and isinstance(kw.value,ast.Constant) and kw.value.value==OFFICIAL_VGGT for kw in vggt[0].keywords):
        errors.append('VGGT must retain the official upstream model checksum.')
    return rows, exceptions, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-manifest', action='store_true', help='Refresh the source-only manifest from the reviewed Git index.')
    args = parser.parse_args()
    names = indexed_files()
    rows, exceptions, errors = audit(names)
    if not errors and args.write_manifest:
        upstream = git('rev-parse', 'upstream/main').decode().strip()
        document = dict(schema=1, date='2026-11-07', purpose='Fork source with approved Epic Manny; no AI model weights, installed runtimes, caches or private characters/projects',
                        version='git-source-fork', upstream=dict(url='https://github.com/toyxyz/toyxyz_RGBMocap', commit=upstream), files=rows)
        MANIFEST.write_text(json.dumps(document,indent=2)+'\n', encoding='utf-8')
    elif not errors:
        expected = json.loads(MANIFEST.read_text(encoding='utf-8'))['files']
        if rows != expected:
            errors.append('SOURCE_MANIFEST.json differs from the indexed source tree. Review changes, stage source files, then run --write-manifest.')
    print(json.dumps(dict(files=len(names), source_bytes=sum(row['bytes'] for row in rows), approved_resources=exceptions, errors=errors),indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
