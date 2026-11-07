"""Anatomical adapters for UE mannequin and Unity sample finger hierarchies."""
import numpy as np
from .finger_transport import anatomical_rest,frame,palm_normal,transfer
from .mapping import A


def profile(rig):
    name=rig.get('finger_mapping',{}).get('LeftHandIndex1','').split(':')[-1]
    return 'ue5' if name=='index_01_l' else 'unity' if name=='LeftIndexProximal' else None


def rotations(rig,arm,source_frames,source_asset,source_names,target_world):
    mapping=rig['finger_mapping'];source_names=list(source_names)
    ids=list(range(22,len(source_names)))
    if len(ids)!=30 or any(source_names[j] not in mapping for j in ids):
        raise ValueError('UE/Unity finger retarget requires all 30 mapped source phalanges.')
    basis=np.asarray(source_asset['export_basis'],float)
    if basis.shape!=(len(source_names),3,3):raise ValueError('Missing source export-basis metadata.')
    native=np.asarray(source_frames[:,:,:3,:3],float)@basis.swapaxes(-1,-2)
    if np.max(abs(native.swapaxes(-1,-2)@native-np.eye(3)))>2e-4:
        raise ValueError('Invalid source finger rotations.')
    source_rest,source_ends=anatomical_rest(np.asarray(source_asset['rest'],float),
        np.asarray(source_asset['ends'],float),source_asset['parents'],basis)
    source_points={name:source_rest[i] for i,name in enumerate(source_names)}
    # All calculations use RGBMoCap Y-up world space. Imported bone display
    # tails are deliberately never used as anatomical directions.
    target_points={name:np.asarray(arm.matrix_world@arm.data.bones[target].head_local)@A
                   for name,target in mapping.items()}
    for side,index in (('Left',20),('Right',21)):
        target_points[side+'Hand']=np.asarray(arm.matrix_world@arm.data.bones[target_world['names'][index]].head_local)@A
    target_rest_rotation={}
    for name in mapping:
        raw=np.asarray(arm.matrix_world@arm.data.bones[mapping[name]].matrix_local)[:3,:3]
        u,_,v=np.linalg.svd(raw);target_rest_rotation[name]=A.T@(u@v)
    sa={};ta={};directions={}
    for side in ('Left','Right'):
        source_normal=palm_normal(source_points,side);target_normal=palm_normal(target_points,side)
        for finger in ('Thumb','Index','Middle','Ring','Pinky'):
            for number in (1,2,3):
                name=f'{side}Hand{finger}{number}';j=source_names.index(name)
                next_name=f'{side}Hand{finger}{number+1}'
                sd=source_points[next_name]-source_points[name] if number<3 else source_ends[j]
                bone=arm.data.bones[mapping[name]]
                if number<3:td=target_points[next_name]-target_points[name]
                elif len(bone.children)==1:
                    td=np.asarray(arm.matrix_world@bone.children[0].head_local)@A-target_points[name]
                else:
                    # UE distal bones have no anatomical endpoint node. Carry
                    # the previous segment's local anatomical axis through
                    # the authored distal rest frame, rather than its Y tail.
                    previous=f'{side}Hand{finger}2'
                    td=target_rest_rotation[name]@target_rest_rotation[previous].T@directions[previous]
                directions[name]=td;sa[j]=frame(sd,source_normal);ta[j]=frame(td,target_normal)
    result=transfer(native,source_asset['parents'],ids,sa,ta,
                    {20:target_world['world'][:,20],21:target_world['world'][:,21]})
    return {mapping[source_names[j]]:rotation for j,rotation in result.items()}
