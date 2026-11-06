"""Export the active motion result on a preset engine skeleton."""

import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

from .paths import ROOT

SKELETONS = ('mixamo', 'ue5', 'unity')
TARGET_SOURCES = {
    'mixamo': ('Mixamo Humanoid', 'https://www.mixamo.com/'),
    'ue5': ('UE5 Mannequin', 'https://dev.epicgames.com/documentation/en-us/unreal-engine/third-person-template-in-unreal-engine'),
    'unity': ('Unity Humanoid', 'https://unity3d.jp/unity-chan_contents/index.php?lang=en'),
}
PRESET_FILES = ('import.json', 'complete.json', 'mixamo-rig.json',
                'mixamo-rest.blend', 'mixamo-canonical.npz', 'mixamo-contact-geometry.npz')


def preset_ready(skeleton):
    """Private user-imported targets are optional, never shipped with source."""
    return skeleton in SKELETONS and all(
        (ROOT / 'character_work' / 'presets' / skeleton / name).is_file()
        for name in PRESET_FILES)


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
    presets = ROOT / "character_work" / "presets"
    asset = presets / skeleton
    if not preset_ready(skeleton):
        raise RuntimeError(f"Export target {skeleton} is not registered. Run tools/setup_export_skeleton.py with your own licensed FBX character; see docs/FORK_GUIDE.md.")
    work = ROOT / 'cache' / 'rig-export' / ('job-' + uuid.uuid4().hex)
    work.mkdir(parents=True)
    emit("progress", current=0, total=2, message=f"Retarget to {skeleton}")
    retarget = work / "retarget.json"
    retarget.write_text(json.dumps({
        "mode": "retarget", "id": skeleton, "asset": str(asset),
        "output": str(work / "animation"), "animation": str(work / "animation"),
        "result": result, "source_name": "RGBMoCap " + skeleton,
        "takes": [{"project": str(project), "start": 0}],
    }), encoding="utf-8")
    _character(retarget)
    complete = json.loads((work / "animation" / "complete.json").read_text(encoding="utf-8"))
    emit("progress", current=1, total=2, message=f"Export {target.name}")
    export = work / "export.json"
    export.write_text(json.dumps({
        "mode": "export", "output": str(work / "export"),
        "animation": str(work / "animation"), "takes": complete["takes"],
        "files": [str(target)], "format": "fbx", "include_mesh": False,
        "source_name": "RGBMoCap " + skeleton,
    }), encoding="utf-8")
    _character(export)
    emit("progress", current=2, total=2, message="Skeleton FBX written")
    return str(target)
