"""Export the active motion result on an installed official character skeleton."""

import json
import subprocess
import sys
import uuid
from pathlib import Path

from .paths import ROOT

SKELETONS = ('mixamo', 'ue5', 'unity')
TARGET_SOURCES = {
    'mixamo': ('Adobe X Bot (Mixamo)', 'https://www.mixamo.com/'),
    'ue5': ('Epic Manny Simple (UE5)', 'https://dev.epicgames.com/documentation/en-us/unreal-engine/third-person-template-in-unreal-engine'),
    'unity': ('Unity DefaultMale', 'https://github.com/Unity-Technologies/Standard-Assets-Characters'),
}


def skeleton_available(skeleton):
    """Only publisher-original targets registered in this installation are offered."""
    from .official_targets import installed
    if skeleton not in SKELETONS:
        return False
    try:
        return installed(skeleton, root=ROOT) is not None
    except (OSError, ValueError, KeyError, TypeError, RuntimeError):
        return False


def target_asset(skeleton, source='auto'):
    if skeleton not in SKELETONS:
        raise ValueError('Unknown export skeleton: '+str(skeleton))
    # 'builtin' is retained only as a request-format alias for old GUI jobs.
    if source not in ('auto','official','builtin'):
        raise ValueError('Unknown skeleton template source: '+str(source))
    from .official_targets import installed
    official = installed(skeleton, verify=True, root=ROOT)
    if official is None:
        raise RuntimeError('Official export target is not installed: '+skeleton+'. Open File > Export Skeleton Targets to import the official FBX. See docs/OFFICIAL_EXPORT_TARGETS.md. Native capture export remains available.')
    return official


def _character(request: Path) -> None:
    command = [sys.executable, "-I", "-X", "utf8", "-B", "worker_boot.py",
               "character", "--request", str(request)]
    subprocess.run(command, cwd=ROOT, check=True)


def run(request, emit):
    spec = json.loads(Path(request).read_text(encoding="utf-8"))
    project = Path(spec["project"])
    result = spec["result"]
    skeleton = spec["skeleton"]
    if skeleton not in SKELETONS:
        raise ValueError('Unknown export skeleton: ' + str(skeleton))
    target = Path(spec["target"])
    target_source = spec.get('target_source','auto')
    emit("progress", current=0, total=3, message=f"Prepare {skeleton} export skeleton")
    asset = target_asset(skeleton,target_source)
    work = ROOT / 'cache' / 'rig-export' / ('job-' + uuid.uuid4().hex)
    work.mkdir(parents=True)
    emit("progress", current=1, total=3, message=f"Retarget to {skeleton}")
    retarget = work / "retarget.json"
    retarget.write_text(json.dumps({
        "mode": "retarget", "id": skeleton, "asset": str(asset),
        "output": str(work / "animation"), "animation": str(work / "animation"),
        "result": result, "source_name": "RGBMoCap " + skeleton,
        "takes": [{"project": str(project), "start": 0}],
        "target_source": target_source,
    }), encoding="utf-8")
    _character(retarget)
    complete = json.loads((work / "animation" / "complete.json").read_text(encoding="utf-8"))
    emit("progress", current=2, total=3, message=f"Export {target.name}")
    export = work / "export.json"
    export.write_text(json.dumps({
        "mode": "export", "output": str(work / "export"),
        "animation": str(work / "animation"), "takes": complete["takes"],
        "files": [str(target)], "format": "fbx", "include_mesh": bool(spec.get('include_mesh', False)),
        "source_name": "RGBMoCap " + skeleton,
    }), encoding="utf-8")
    _character(export)
    emit("progress", current=3, total=3, message="Skeleton FBX written")
    return str(target)
