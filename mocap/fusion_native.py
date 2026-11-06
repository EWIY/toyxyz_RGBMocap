"""Native SMPL-H fusion and preview publication in the Flow runtime."""
import argparse
import copy
import json
import os
from pathlib import Path
import shutil

from .storage import atomic_json


def build(project, kind, emit):
    import numpy as np
    import torch
    from scipy.spatial.transform import Rotation
    from .flow_backend import activate, load_tensor, validate_motion
    activate()
    from flowhmr.core.math.geometry import rot6d_to_rotation_matrix, rotation_matrix_to_rot6d
    from .fusion import VERSION, REGIONS, blend_rotations, saved_options, input_identity
    from .motion_tools import RESULTS, result_is_current
    from .result_artifacts import file_stat
    from .correction_settings import correction_options
    from .foot_contacts import contact_revision
    state = json.loads((project/'project.json').read_text(encoding='utf-8'))
    refs = json.loads((project/'fusion_sources.json').read_text(encoding='utf-8'))['sources']
    flow, gv = [(project/refs[m]).resolve() for m in ('flowhmr', 'gvhmr')]
    settings = saved_options(project)
    for source in (flow, gv):
        if not result_is_current(source, kind):
            raise ValueError('Fusion source changed; retry Reconstruct 3D.')
    stamps = [file_stat(p/RESULTS[kind][0]) for p in (flow, gv)]
    params = load_tensor(flow/RESULTS[kind][0])
    validate_motion(params, state['frames'])
    guide = torch.load(gv/RESULTS[kind][0], map_location='cpu', weights_only=False)['smpl_params_global']
    n = state['frames']
    body = guide['body_pose'].detach().cpu().numpy().reshape(n, 21, 3)
    root = guide['global_orient'].detach().cpu().numpy().reshape(n, 1, 3)
    donor = Rotation.from_rotvec(np.concatenate((root, body), axis=1).reshape(-1, 3)).as_matrix().reshape(n, 22, 3, 3)
    original = rot6d_to_rotation_matrix(params['rot6d']).detach().cpu().numpy()[0]
    result = blend_rotations(original.astype(np.float64), donor, settings)
    fused = copy.deepcopy(params)
    chosen = [j for region in settings['regions'] for j in REGIONS[region]] if settings['weight'] else []
    if chosen:
        rotations = torch.from_numpy(result[:, chosen].copy()).to(dtype=params['rot6d'].dtype)
        fused['rot6d'][0, :, chosen, :] = rotation_matrix_to_rot6d(rotations)
    protected = [j for j in range(52) if j not in chosen]
    if not torch.equal(fused['rot6d'][:, :, protected], params['rot6d'][:, :, protected]):
        raise ValueError('Fusion changed a protected bone.')
    if not torch.equal(fused['trans'], params['trans']) or not torch.equal(fused['shapes'], params['shapes']):
        raise ValueError('Fusion changed FlowHMR root translation or body shape.')
    validate_motion(fused, n)
    temporary = project/(kind+'.fusion-partial.pt')
    try:
        torch.save(fused, temporary)
        os.replace(temporary, project/RESULTS[kind][0])
    finally:
        temporary.unlink(missing_ok=True)
    if kind.startswith('corrected_'):
        for suffix in ('correction.json', 'contacts.npz'):
            shutil.copy2(flow/(kind+'_'+suffix), project/(kind+'_'+suffix))
        from .foot_contacts import contact_revision, state_path
        contact_path=state_path(project,'initial')
        if contact_path.exists():
            contact=json.loads(contact_path.read_text(encoding='utf-8'))
            contact['sources']={'hmr4d_results.pt':file_stat(project/'hmr4d_results.pt')}
            atomic_json(contact_path,contact)
        report=json.loads((project/(kind+'_correction.json')).read_text(encoding='utf-8'))
        report.update(output_stat=file_stat(project/RESULTS[kind][0]),contact_revision=contact_revision(project,'initial'))
        atomic_json(project/(kind+'_correction.json'),report)
        atomic_json(project/(kind+'_sources.json'),{'hmr4d_results.pt':file_stat(project/'hmr4d_results.pt')})
    if any(file_stat(p/RESULTS[kind][0]) != stamp for p, stamp in zip((flow, gv), stamps)):
        raise ValueError('Source motion changed while blending; retry.')
    atomic_json(project/(kind+'_fusion.json'), dict(version=VERSION, options=settings,
        identity=input_identity(project), correction=correction_options(state.get('correction', {})),
        sources=[dict(model=m, project=refs[m], stat=s, identity=input_identity(p)) for m, s, p in zip(('flowhmr', 'gvhmr'), stamps, (flow,gv))],
        contact_revision=contact_revision(project,'initial'),
        output=file_stat(project/RESULTS[kind][0]), protected_local_exact=True,
        root_translation_exact=True, shape_exact=True, frames=n, fps=state['fps']))
    # Native meshes and all exports remain bound to the Flow body shape.
    state['source_representation'] = 'smplh'
    state['fusion_options'] = settings
    atomic_json(project/'project.json', state)
    return flow


def main(argv, emit):
    parser = argparse.ArgumentParser()
    parser.add_argument('stage')
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--result', choices=('initial', 'corrected_initial'), required=True)
    args = parser.parse_args(argv)
    project = args.project.resolve()
    from .compute_policy import configure_worker_cpu
    configure_worker_cpu('flow_export')
    import torch
    torch.set_num_threads(4)
    from .fusion import current
    from .result_artifacts import artifacts_current
    from .mixamo_data import current as preview_current
    kinds = ['initial'] + (['corrected_initial'] if args.result == 'corrected_initial' else [])
    todo = [kind for kind in kinds if not current(project, kind)]
    if todo:
        atomic_json(project/'fusion_pending.json', dict(kinds=todo))
        for kind in todo:
            emit('progress', current=0, total=0, message='Fuse '+kind+' torso, neck and head')
            build(project, kind, emit)
        (project/'fusion_pending.json').unlink()
    from .flow_backend import activate
    activate()
    from .flow_export import prepare
    for kind in kinds:
        if not artifacts_current(project, kind) or not preview_current(project, kind):
            prepare(project, emit, kind)
            path=project/(kind+'_mixamo.json')
            metadata=json.loads(path.read_text(encoding='utf-8'))
            metadata['source_model']='fusion'
            metadata['fusion_options']=json.loads((project/(kind+'_fusion.json')).read_text(encoding='utf-8'))['options']
            atomic_json(path,metadata)
    path=project/'export.json'
    metadata=json.loads(path.read_text(encoding='utf-8'))
    metadata.update(source='FlowHMR + GVHMR Fusion / native SMPL-H',result_kind=args.result)
    atomic_json(path,metadata)
    from .fusion_scene import publish_camera
    publish_camera(project)
    emit('complete', stage='fusion_native', output=str(project/'motion.bvh'))
    return 0
