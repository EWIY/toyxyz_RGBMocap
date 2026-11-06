"""One fixed horizontal origin for a FlowHMR scene, shared by actors and camera."""
from pathlib import Path
import json
import numpy as np
from .result_artifacts import file_stat

INPUTS=('flow_prediction.pt','flow_placement.json','flow_camera.npz','tracking.npz')

def reference(project):
    from .flow_backend import scene_root
    from .people_store import load_people,safe_child
    project=Path(project);root=scene_root(project);rows=[]
    people=load_people(root) if (root/'people.json').exists() else None
    if people:
        for person in people['people']:
            for take in person.get('takes',[]):
                path=safe_child(root,take['project'])
                if all((path/name).is_file() for name in INPUTS) and not (path/'flowhmr_pending.json').exists():
                    rows.append((int(take['first']),int(person['id']),path.relative_to(root).as_posix(),path))
    # The currently publishing actor is eligible before its pending marker clears.
    if all((project/name).is_file() for name in INPUTS):
        state=json.loads((project/'project.json').read_text(encoding='utf-8'))
        rows.append((int(state.get('person_frames',[0])[0]),int(state.get('person_id',0)),project.relative_to(root).as_posix(),project))
    if len(rows)>4097:raise ValueError('Too many FlowHMR takes for scene-origin selection')
    if not rows:raise ValueError('No complete FlowHMR source is available for the scene origin')
    return min(rows,key=lambda row:row[:3])[-1]

def identity(project):
    from .flow_backend import scene_root
    anchor=reference(project);root=scene_root(project)
    state=json.loads((anchor/'project.json').read_text(encoding='utf-8'))
    return dict(project=anchor.relative_to(root).as_posix(),first_frame=state.get('person_frames',[0])[0],
                inputs={name:file_stat(anchor/name) for name in INPUTS})

def horizontal_origin(pelvis,rotation,offset):
    pelvis=np.asarray(pelvis,float);rotation=np.asarray(rotation,float);offset=np.asarray(offset,float)
    if pelvis.shape!=(3,) or rotation.shape!=(3,3) or offset.shape!=(3,) or not all(np.isfinite(x).all() for x in (pelvis,rotation,offset)):
        raise ValueError('Invalid FlowHMR scene-origin inputs')
    origin=rotation@pelvis+offset;origin[1]=0.
    return origin

def rebase_saved_camera(camera,origin):
    """Translate a saved orbit view once into the displayed scene's coordinates."""
    origin=np.asarray(origin,float)
    previous=np.asarray(camera.get('scene_origin',[0.,0.,0.]),float)
    if any(x.shape!=(3,) or not np.isfinite(x).all() or abs(x[1])>1e-9 for x in (origin,previous)):
        raise ValueError('Invalid saved FlowHMR camera origin')
    result=dict(camera)
    for key in ('scene_center','target'):
        if key in result:result[key]=(np.asarray(result[key],float)+previous-origin).tolist()
    result['scene_origin']=origin.tolist()
    return result

def camera_center(height,origin):
    origin=np.asarray(origin,float)
    if origin.shape!=(3,) or not np.isfinite(origin).all() or abs(origin[1])>1e-9 or not np.isfinite(height):
        raise ValueError('Invalid horizontal FlowHMR scene origin')
    return np.array([0.,float(height),0.])-origin
