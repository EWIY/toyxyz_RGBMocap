"""FlowHMR motion with selective, heading-aligned GVHMR orientation guidance.

No model imports here: settings and cache checks also run in the GUI process.
"""
import json
from pathlib import Path

VERSION = 1
REGIONS = {'torso': (3, 6, 9), 'neck': (12,), 'head': (15,)}
PARENTS = (-1, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 12, 13, 14, 16, 17, 18, 19)


def options(value=None):
    value = value or {}
    weight = float(value.get('weight', 1.))
    if not 0 <= weight <= 1:
        raise ValueError('Fusion weight must be between 0 and 100%.')
    regions = value.get('regions', list(REGIONS))
    if not isinstance(regions, (list, tuple)) or any(r not in REGIONS for r in regions):
        raise ValueError('Unsupported fusion bone region.')
    return dict(weight=weight, regions=[r for r in REGIONS if r in regions])


def saved_options(project):
    from .people_store import root_for
    state = json.loads((Path(project)/'project.json').read_text(encoding='utf-8'))
    root = root_for(project, state)
    if root != Path(project).resolve():
        state = json.loads((root/'project.json').read_text(encoding='utf-8'))
    return options(state.get('fusion_options'))


def blend_rotations(flow, donor, settings=None):
    """Blend selected LOCAL rotations toward GV world orientations, parent first.

    One initial yaw alignment, no per-frame heading fit, time warp, smoothing,
    translation, scale or changes to unselected local rotations.
    """
    import numpy as np
    from scipy.spatial.transform import Rotation
    settings = options(settings)
    flow, donor = np.asarray(flow), np.asarray(donor)
    if flow.ndim != 4 or flow.shape[1:] != (52, 3, 3) or donor.shape != (len(flow), 22, 3, 3) or not len(flow):
        raise ValueError('Fusion requires matching FlowHMR/GVHMR frame counts and body joints.')
    if not np.isfinite(flow).all() or not np.isfinite(donor).all():
        raise ValueError('Non-finite input rotations.')
    out = flow.copy()
    weight = settings['weight']
    selected = {j for r in settings['regions'] for j in REGIONS[r]}
    if not weight or not selected:
        return out
    # A vertical forward vector has no reliable yaw. Use projected right axis.
    def yaw(root):
        forward = root[:, 2]
        return (np.arctan2(forward[0], forward[2]) if np.linalg.norm(forward[[0, 2]]) > 1e-5
                else np.arctan2(-root[2, 0], root[0, 0]))
    align = Rotation.from_euler('y', yaw(flow[0, 0])-yaw(donor[0, 0])).as_matrix()
    gv_world, world = [], []
    for j, parent in enumerate(PARENTS):
        gv_world.append(align@donor[:, j] if parent < 0 else gv_world[parent]@donor[:, j])
        if j in selected:
            goal = world[parent].swapaxes(-1, -2)@gv_world[j]
            if weight == 1:
                out[:, j] = goal
            else:
                delta = Rotation.from_matrix(flow[:, j].swapaxes(-1, -2)@goal)
                out[:, j] = flow[:, j]@Rotation.from_rotvec(delta.as_rotvec()*weight).as_matrix()
        world.append(out[:, j] if parent < 0 else world[parent]@out[:, j])
    return out


def current(project, kind, ignore_contacts=False):
    """Own receipt; never invoke Flow placement on a fused motion."""
    from .result_artifacts import file_stat
    from .motion_tools import RESULTS, result_is_current, require_supported_project
    from .correction_settings import correction_options
    project = Path(project)
    try:
        if kind not in ('initial', 'corrected_initial') or (project/'fusion_pending.json').exists():
            return False
        record = json.loads((project/(kind+'_fusion.json')).read_text(encoding='utf-8'))
        if record['version'] != VERSION or record['options'] != saved_options(project):
            return False
        if record['output'] != file_stat(project/RESULTS[kind][0]):
            return False
        state = json.loads((project/'project.json').read_text(encoding='utf-8'))
        if record['identity'] != input_identity(project, state):
            return False
        if kind.startswith('corrected_') and record['correction'] != correction_options(state.get('correction', {})):
            return False
        if kind.startswith('corrected_') and not ignore_contacts:
            from .foot_contacts import contact_revision
            if record.get('contact_revision') != contact_revision(project, 'initial'):
                return False
        refs = json.loads((project/'fusion_sources.json').read_text(encoding='utf-8'))['sources']
        for item in record['sources']:
            path = (project/item['project']).resolve()
            if item['model'] not in ('flowhmr', 'gvhmr') or require_supported_project(path).key != item['model']:
                return False
            if refs.get(item['model']) != item['project'] or item['identity'] != input_identity(path):
                return False
            if file_stat(path/RESULTS[kind][0]) != item['stat'] or not result_is_current(path, kind):
                return False
        return True
    except (OSError, ValueError, KeyError, TypeError):
        return False


def input_identity(project, state=None):
    from .result_artifacts import file_stat
    state = state or json.loads((Path(project)/'project.json').read_text(encoding='utf-8'))
    return dict(source=state.get('source_sha256'), start=state['start'], end=state['end'],
                frames=state['frames'], fps=state['fps'], person=state.get('person_id'),
                person_frames=state.get('person_frames'), person_fingerprint=state.get('person_fingerprint'),
                input=file_stat(Path(project)/'input.mp4'), tracking=file_stat(Path(project)/'tracking.npz'))
