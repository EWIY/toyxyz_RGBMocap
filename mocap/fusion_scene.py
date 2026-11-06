"""Reuse Flow's physical placement; guidance never moves the scene roots."""
import json
from pathlib import Path
from .storage import atomic_json


def publish_camera(project):
    from .scene_camera import VERSION, camera_sources, validate_transform
    refs = json.loads((project/'fusion_sources.json').read_text(encoding='utf-8'))['sources']
    flow = (project/refs['flowhmr']).resolve()
    from .scene_camera import read_camera
    camera=read_camera(flow)
    if camera is None:
        import numpy as np
        from .flow_placement import current
        from .flow_origin import camera_center
        from .models import BY_KEY
        from .result_artifacts import file_stat
        if not current(flow):raise ValueError('FlowHMR placement is not current.')
        world=json.loads((flow/'flow_world.json').read_text(encoding='utf-8'))
        from .people_store import root_for, load_people
        from .scene_camera import take_projects
        root=root_for(flow)
        with np.load(root/'flow_camera.npz',allow_pickle=False) as data:r=data['camera_RT_yup'][0,:3,:3].copy()
        height=world['camera_height']
        people=load_people(root) if (root/'people.json').exists() else None
        if people:
            estimates={}
            for ident,take in take_projects(root,people):
                if not current(take):raise ValueError('Source FlowHMR people have different placement generations.')
                saved=json.loads((take/'flow_world.json').read_text(encoding='utf-8'))
                estimates.setdefault(ident,[]).append(saved['camera_height'])
            if estimates:height=float(np.median([np.median(v) for v in estimates.values()]))
        matrix=np.eye(4);matrix[:3,:3]=r@np.asarray(world['scene_basis']).T
        origin=world.get('scene_origin',[0.,0.,0.])
        matrix[:3,3]=-matrix[:3,:3]@camera_center(height,origin)
        matrix=np.round(matrix,10)
        camera=dict(version=VERSION,world_to_camera=matrix.tolist(),K=world['intrinsics'],
                    model=file_stat(BY_KEY['smplh'].path),placement_version=world['context']['version'],
                    camera_height=height,scene_origin=origin,htd_compatible=False)
    validate_transform(camera['world_to_camera'])
    camera.update(source_model='fusion', sources=camera_sources(project), method='FlowHMR placement; selective GVHMR orientation guidance')
    atomic_json(project/'scene_camera.json', camera)


def load_camera(project, group=None, cancelled=lambda:False):
    """Read the Flow trajectory using fusion's own committed camera reference."""
    import numpy as np
    from .camera_tracks import record, load_array, valid_rotations
    from .scene_camera import read_camera, validate_transform
    from .result_artifacts import file_stat
    from .people_store import root_for
    from .flow_camera import saved_interval
    from .fusion import current
    if not current(project,'initial'):raise ValueError('Fusion settings or sources changed. Reconstruct 3D.')
    refs=json.loads((project/'fusion_sources.json').read_text(encoding='utf-8'))['sources']
    flow=(project/refs['flowhmr']).resolve();root=root_for(flow)
    paths=[project/'project.json',project/'fusion_sources.json',project/'scene_camera.json',
           flow/'flow_world.json',root/'flow_camera.npz',root/'project.json']
    dependencies={str(p):file_stat(p) for p in paths}
    camera=read_camera(project)
    if camera is None:raise ValueError('Fusion camera is stale. Prepare Preview.')
    base=validate_transform(camera['world_to_camera'])
    if group is not None:
        from .scene_export import context
        placement=context(group,project)
        base=base@np.linalg.inv(np.asarray(placement['transform']))
        dependencies[str(group/'people_scene.json')]=file_stat(group/'people_scene.json')
    meta=json.loads((root/'project.json').read_text(encoding='utf-8'))
    raw=load_array(root/'flow_camera.npz','camera_RT_yup');r=raw[:,:3,:3];valid_rotations(r)
    rotations=r@r[0].T@base[:3,:3]
    centers=-np.einsum('tji,tj->ti',r,raw[:,:3,3])
    displacement=(centers-centers[0])@(base[:3,:3].T@r[0]).T
    matrices=np.tile(np.eye(4),(len(r),1,1));matrices[:,:3,:3]=rotations
    center=-base[:3,:3].T@base[:3,3]
    matrices[:,:3,3]=-np.einsum('tij,j->ti',rotations,center)
    note='FlowHMR camera and placement retained by fusion; camera movement scale is approximate.'
    items=[record('Camera 1',camera['K'],[meta['width'],meta['height']],matrices,meta['start'],meta['fps'],note,displacement)]
    if cancelled():return None
    if any(file_stat(Path(p))!=stamp for p,stamp in dependencies.items()):raise ValueError('Fusion camera inputs changed while loading.')
    return dict(cameras=items,model='fusion',project=str(project),note=note,warning='',
                static_camera=saved_interval(flow,json.loads((flow/'project.json').read_text(encoding='utf-8')))==-1,camera_sources=dependencies)


def prepare_cameras(root, rows=None):
    import numpy as np
    from .scene_camera import VERSION, take_projects, read_camera
    from .people_store import load_people, media_receipt
    from .fusion import current
    root = Path(root)
    rows = rows if rows is not None else take_projects(root, load_people(root))
    usable = []
    for ident, project in rows:
        if current(project, 'initial'):
            publish_camera(project)
            camera = read_camera(project)
            if camera is None:
                raise ValueError('Fusion needs the matching FlowHMR scene camera. Reconstruct 3D to prepare it.')
            usable.append((ident, project, camera))
    path = root/'people_scene.json'
    if usable:
        ident, project, camera = min(usable, key=lambda row: (row[0], str(row[1])))
        for _, _, other in usable:
            if not np.allclose(camera['world_to_camera'], other['world_to_camera'], rtol=0, atol=1e-7):
                raise ValueError('Flow source takes do not share one scene placement. Reconstruct matching people together.')
        atomic_json(path, dict(version=VERSION, input=media_receipt(root), anchor=project.relative_to(root).as_posix(),
            anchor_id=ident, sources=camera['sources'], world_to_camera=camera['world_to_camera'],
            floor=0., K=camera['K'], camera_mode='shared_rotation', scale=1.,
            placement_version=camera.get('placement_version', 3), camera_height=camera.get('camera_height', 0),
            scene_origin=camera.get('scene_origin', [0., 0., 0.])))
    return path


def resolve_floor(root, options):
    """Reuse the Flow plane, since fusion preserves every lower-body transform."""
    import numpy as np
    from .scene_floor import inputs, VERSION, signature
    from .people_store import root_for
    context=inputs(root)
    heights=[]
    for row in context['actors']:
        project=root/row['project']
        refs=json.loads((project/'fusion_sources.json').read_text(encoding='utf-8'))['sources']
        flow=(project/refs['flowhmr']).resolve()
        path=root_for(flow)/'scene_floor_resolved.json'
        if path.exists():heights.append(float(json.loads(path.read_text(encoding='utf-8'))['floor']))
        else:
            path=flow/'corrected_initial_correction.json'
            if path.exists():heights.append(float(json.loads(path.read_text(encoding='utf-8')).get('floor',0)))
    height=float(np.median(heights)) if options['auto_floor'] and heights else float(options['floor'])
    record=dict(version=VERSION,options=options,inputs=context,floor=height,samples=0,warning='',
                signature=signature(options,context,height),method='Unchanged FlowHMR lower body and source floor')
    atomic_json(root/'scene_floor_resolved.json',record)
    return record
