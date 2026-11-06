"""Isolated, resumable FlowHMR + GVHMR orchestration.

Existing model results are read-only. Missing inference/correction is performed
in this model's private source projects, using each engine's own worker runtime.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

from .storage import atomic_json
from .fusion import options, input_identity


def manifest(project):
    return json.loads((Path(project)/'project.json').read_text(encoding='utf-8'))


def write_record(path, value):
    try:
        if json.loads(path.read_text(encoding='utf-8')) == value:
            return
    except (OSError, ValueError):
        pass
    atomic_json(path, value)


def matching(a, b):
    """Only identical source timing and actor identity can share a prediction."""
    if not a.get('source_sha256') or a.get('source_sha256') != b.get('source_sha256'):
        return False
    if any(a.get(k) != b.get(k) for k in ('start', 'end', 'frames', 'fps', 'width', 'height')):
        return False
    if a.get('person_id') is not None:
        if any(a.get(k) != b.get(k) for k in ('person_id', 'person_frames', 'person_fingerprint')):
            return False
    return True


def same_tracking(a, b):
    import numpy as np
    try:
        with np.load(a/'tracking.npz', allow_pickle=False) as x, np.load(b/'tracking.npz', allow_pickle=False) as y:
            return set(x.files) == set(y.files) and all(np.array_equal(x[k], y[k]) for k in x.files)
    except (OSError, ValueError, KeyError):
        return False


_MEDIA_HASHES = {}


def same_media(a, b):
    """Frame-grid identity includes the actual prepared video, not just its name."""
    from .result_artifacts import file_stat
    from .storage import sha256
    def digest(project):
        path=project/'input.mp4'
        key=(str(path.resolve()),*file_stat(path))
        if key not in _MEDIA_HASHES:
            if len(_MEDIA_HASHES)>=256:_MEDIA_HASHES.clear()
            _MEDIA_HASHES[key]=sha256(path)
        return _MEDIA_HASHES[key]
    try:return digest(a)==digest(b)
    except OSError:return False


def candidates(project, model):
    from .project_workspace import root_for as workspace_root
    from .people_store import root_for
    state = manifest(project)
    roots = [root_for(project)/'_fusion_sources'/model]
    workspace = workspace_root(project, state)
    if workspace:
        roots.insert(0, workspace/model)
    seen = set()
    for root in roots:
        # Bounded layout scan, never search unrelated projects or other videos.
        files = [root/'project.json', *root.glob('clips/*/project.json'),
                 *root.glob('people/*/person_*/takes/*/project.json'),
                 *root.glob('clips/*/people/*/person_*/takes/*/project.json')]
        if len(files) > 4096:
            raise ValueError('Too many candidate takes. Trim the project before fusion.')
        for file in files:
            if not file.is_file() or file.parent in seen:
                continue
            seen.add(file.parent)
            try:
                other = manifest(file.parent)
                if other.get('pipeline', {}).get('model') == model and matching(state, other):
                    yield file.parent
            except (OSError, ValueError, KeyError):
                continue


def reuse_tracking(project):
    """Use the already selected actor's exact observations before a new tracker."""
    tracking = project/'tracking.npz'
    if tracking.is_file() and tracking.stat().st_mtime_ns >= (project/'input.mp4').stat().st_mtime_ns:
        return True
    matches = [p for p in candidates(project, 'flowhmr') if same_media(project,p)]
    if not matches:
        return False
    first = matches[0]
    # Multiple detections are only interchangeable when all observations agree.
    if not all(same_tracking(first, p) for p in matches[1:]):
        return False
    if tracking.is_file() and not same_tracking(project, first):
        return False
    # Reuse has validated identical media and observations. A new destination
    # needs a fresh write time: copy2 preserves an older source timestamp and
    # makes the GUI reject the otherwise valid tracking as stale.
    for name in ('tracking.npz', 'camera.pt'):
        if (first/name).is_file():
            shutil.copyfile(first/name, project/name)
    return (project/'tracking.npz').is_file()


def copy_file(source, target):
    if not source.is_file():
        return
    from .result_artifacts import file_stat
    if target.is_file() and file_stat(source) == file_stat(target):
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name+'.fusion-copy')
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def clone_files(source, target):
    """Copy inference inputs/receipts, not large derived preview generations."""
    target.mkdir(parents=True, exist_ok=True)
    for file in source.iterdir():
        if not file.is_file() or file.name == 'project.json':
            continue
        if ('_flow-' in file.name or '_rig' in file.name or '_mixamo' in file.name or
                '_mesh' in file.name or file.suffix in ('.bvh', '.fbx', '.blend', '.log')):
            continue
        copy_file(file, target/file.name)


def private_source(project, model, source=None):
    from .people_store import root_for
    state = manifest(project)
    root = root_for(project, state)
    target_root = root/'_fusion_sources'/model
    target = target_root/project.relative_to(root)
    origin = source or project
    origin_root = root_for(origin)
    if source:
        target = target_root/origin.relative_to(origin_root)
    # Existing owned projects retain expensive caches between blend edits.
    if source and source.resolve() == target.resolve():
        return target
    if source:
        clone_files(origin_root, target_root)
        if origin != origin_root:
            clone_files(origin, target)
    else:
        target_root.mkdir(parents=True, exist_ok=True)
        target.mkdir(parents=True, exist_ok=True)
        for src, dst in ((root, target_root), (project, target)):
            for name in ('input.mp4', 'tracking.npz', 'camera.pt', 'people.json', 'scene_floor.json'):
                copy_file(src/name, dst/name)
    # A group's list always comes from the current fusion selection. Relative
    # paths are preserved, allowing normal engine placement and shared floors.
    copy_file(root/'people.json', target_root/'people.json')
    for src, dst in ((origin_root, target_root), (origin, target)):
        value = copy.deepcopy(manifest(src))
        value.pop('workspace_root', None)
        value.pop('storage_root', None)
        value.pop('storage', None)
        value['pipeline'] = dict(model=model, result='initial')
        value['correction'] = state.get('correction', {})
        if dst != target_root:
            value['people_root'] = os.path.relpath(target_root, dst)
        else:
            value.pop('people_root', None)
        if model == 'flowhmr' and not source:
            value['flow_options'] = dict(camera_interval=int(os.environ.get('RGB_MOCAP_FLOW_INTERVAL', '0')),
                fast_sam=True, sam_batch4=True, sam_gpu_crop=True, sam_hand_stride4=True, hamer=False)
        if not source and (dst/'project.json').is_file():
            old = manifest(dst)
            if matching(value, old):
                value['stages'] = old.get('stages', {})
        atomic_json(dst/'project.json', value)
    return target


def child(stage, project, kind, emit):
    from .runtime_registry import command
    from .paths import ROOT
    argv = command(ROOT, stage, ['--project', str(project), '--result', kind],
                   frozen=getattr(sys, 'frozen', False))
    emit('progress', current=0, total=0, message=f'Fusion · {stage} · {project.name}')
    # The desktop's existing tree cancellation and resource monitor include this
    # child. Shell-free invocation keeps filenames and user text out of commands.
    process = subprocess.Popen(argv, cwd=ROOT, env=os.environ.copy(), stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace',
                               creationflags=0x08000000 if os.name == 'nt' else 0)
    try:
        for line in process.stdout:
            if line.startswith('@@MOCAP@@'):
                try:
                    event = json.loads(line[len('@@MOCAP@@'):])
                    event_type = event.pop('type')
                except (ValueError, KeyError):
                    print(line, end='', flush=True)
                    continue
                if event_type == 'failed':
                    raise RuntimeError(f'{stage}: '+event.get('message', 'worker failed'))
                if event_type == 'complete':
                    event['batch_inner'] = True
                if event_type == 'progress':
                    event['phase'] = 'fusion:'+stage+':'+str(event.get('phase', ''))
                emit(event_type, **event)
            else:
                print(line, end='', flush=True)
        if process.wait():
            raise RuntimeError(f'Fusion dependency {stage} failed. Completed model caches were retained; retry Reconstruct 3D.')
    finally:
        if process.poll() is None:
            if os.name == 'nt':
                subprocess.run(['taskkill.exe', '/PID', str(process.pid), '/T', '/F'], capture_output=True,
                               creationflags=0x08000000)
            else:
                process.terminate()
            process.wait()
        process.stdout.close()


def sources(project, emit, runner=child):
    from .motion_tools import result_is_current
    from .people_store import root_for
    input_identity(project)  # Fail before loading models if tracking/preparation failed.
    value = {}
    for model in ('flowhmr', 'gvhmr'):
        matches = [p for p in candidates(project, model) if same_tracking(project, p) and same_media(project,p)]
        source = next((p for p in matches if result_is_current(p, 'initial')), None)
        if source:
            emit('progress', current=1, total=1, message=f'Fusion · reusing {model} capture')
        else:
            source = private_source(project, model)
            stages = ('flow_camera', 'flow_features', 'flowhmr') if model == 'flowhmr' else ('gvhmr',)
            for stage in stages:
                runner(stage, source, 'initial', emit)
            if not result_is_current(source, 'initial'):
                raise ValueError(f'{model} did not publish a valid source motion.')
        value[model] = os.path.relpath(source, project)
    record = dict(identity=input_identity(project), sources=value)
    write_record(project/'fusion_sources.json', record)
    return value


def load_sources(project, emit, runner=child):
    from .motion_tools import result_is_current
    try:
        record = json.loads((project/'fusion_sources.json').read_text(encoding='utf-8'))
        if record['identity'] == input_identity(project) and all(
                matching(manifest(project), manifest((project/p).resolve())) and
                same_tracking(project, (project/p).resolve()) and
                same_media(project, (project/p).resolve()) and
                result_is_current((project/p).resolve(), 'initial') for p in record['sources'].values()):
            return record['sources']
    except (OSError, ValueError, KeyError):
        pass
    return sources(project, emit, runner)


def corrected_sources(project, selected, emit, runner=child):
    from .motion_tools import result_is_current
    from .correction_settings import correction_options
    wanted = correction_options(manifest(project).get('correction', {}))
    from .foot_contacts import contact_state, read_edit, save_edit
    from .result_artifacts import file_stat
    edit = contact_state(project, 'initial')
    for model, relative in list(selected.items()):
        source = (project/relative).resolve()
        source_options = correction_options(manifest(source).get('correction', {}))
        edits_match = not edit or manifest(source).get('fusion_edit_revision') == edit.get('revision')
        if source_options == wanted and result_is_current(source, 'corrected_initial') and (model != 'flowhmr' or edits_match):
            continue
        source = private_source(project, model, source)
        state = manifest(source)
        state['correction'] = wanted
        atomic_json(source/'project.json', state)
        from .people_store import root_for
        if root_for(source) != source:
            from .scene_floor import save_config
            save_config(root_for(source), wanted)
        # Explicit foot-contact edits belong to the fusion result, and only its
        # private Flow baseline receives them before guidance is applied.
        if model == 'flowhmr' and edit:
            context=dict(frames=state['frames'],fps=state['fps'],sources={'hmr4d_results.pt':file_stat(project/'hmr4d_results.pt')})
            ranges,_,warning=read_edit(project,'initial',context)
            if warning:raise ValueError(warning)
            context['sources']={'hmr4d_results.pt':file_stat(source/'hmr4d_results.pt')}
            save_edit(source,'initial',ranges,context)
            state['fusion_edit_revision']=edit['revision']
            atomic_json(source/'project.json',state)
        runner('correct', source, 'corrected_initial', emit)
        if not result_is_current(source, 'corrected_initial'):
            raise ValueError(f'{model} correction did not produce a current result.')
        selected[model] = os.path.relpath(source, project)
    write_record(project/'fusion_sources.json', dict(identity=input_identity(project), sources=selected))
    return selected


def main(argv, emit):
    parser = argparse.ArgumentParser()
    parser.add_argument('stage')
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--result', default='auto')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args(argv)
    project = args.project.resolve()
    started = time.monotonic()
    try:
        state = manifest(project)
        if state.get('pipeline', {}).get('model') != 'fusion':
            raise ValueError('Fusion requires its own model project.')
        from .people_store import root_for
        if 'RGB_MOCAP_FUSION_OPTIONS' in os.environ:
            root = root_for(project, state)
            root_state = manifest(root)
            root_state['fusion_options'] = options(json.loads(os.environ['RGB_MOCAP_FUSION_OPTIONS']))
            atomic_json(root/'project.json', root_state)
        kind = args.result if args.result != 'auto' else state.get('pipeline', {}).get('result', 'corrected_initial')
        if kind not in ('initial', 'corrected_initial'):
            raise ValueError('Fusion supports original and corrected motion, without GVHMR refinement add-ons.')
        if args.stage == 'fusion_sources':
            load_sources(project, emit)
        else:
            from .fusion import current
            from .result_artifacts import artifacts_current
            from .mixamo_data import current as preview_current
            cached = all(current(project, k) and artifacts_current(project, k) and preview_current(project, k)
                         for k in (('initial', kind) if kind != 'initial' else (kind,)))
            if not cached or args.force:
                selected = load_sources(project, emit)
                if kind == 'corrected_initial':
                    corrected_sources(project, selected, emit)
                child('fusion_native', project, kind, emit)
            state = manifest(project)
            state['pipeline']['result'] = kind
            atomic_json(project/'project.json', state)
            from .fusion_scene import publish_camera
            publish_camera(project)
        emit('complete', stage=args.stage, output=str(project/'motion.bvh'), elapsed=time.monotonic()-started)
        return 0
    except Exception as error:
        print(traceback.format_exc(), file=sys.stderr, flush=True)
        emit('failed', message=str(error))
        return 1
