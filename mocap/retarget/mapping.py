import numpy as np
A = np.array([[1.0, 0, 0], [0, 0, -1], [0, 1, 0]])
NAMES = ['Hips', 'LeftUpLeg', 'RightUpLeg', 'Spine', 'LeftLeg', 'RightLeg', 'Spine1', 'LeftFoot', 'RightFoot', 'Spine2', 'LeftToeBase', 'RightToeBase', 'Neck', 'LeftShoulder', 'RightShoulder', 'Head', 'LeftArm', 'RightArm', 'LeftForeArm', 'RightForeArm', 'LeftHand', 'RightHand']
PARENTS = np.array([-1, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 12, 13, 14, 16, 17, 18, 19])
VRM = ['hips', 'leftUpperLeg', 'rightUpperLeg', 'spine', 'leftLowerLeg', 'rightLowerLeg', 'chest', 'leftFoot', 'rightFoot', 'upperChest', 'leftToes', 'rightToes', 'neck', 'leftShoulder', 'rightShoulder', 'head', 'leftUpperArm', 'rightUpperArm', 'leftLowerArm', 'rightLowerArm', 'leftHand', 'rightHand']
PMX = ['下半身', '足.L', '足.R', '上半身', 'ひざ.L', 'ひざ.R', '上半身1', '足首.L', '足首.R', '上半身2', 'つま先.L', 'つま先.R', '首', '肩.L', '肩.R', '頭', '腕.L', '腕.R', 'ひじ.L', 'ひじ.R', '手首.L', '手首.R']

def body_trajectory_root(parents, mapped):
    """Use the body's existing root; independent control trees may coexist."""
    roots = set()
    for name in mapped:
        seen = set()
        while True:
            if name not in parents or name in seen:
                raise ValueError('Invalid humanoid bone hierarchy.')
            seen.add(name)
            parent = parents[name]
            if parent is None:
                roots.add(name)
                break
            name = parent
    if len(roots) != 1:
        raise ValueError('The mapped humanoid body must share one hierarchy root.')
    return next(iter(roots))

# Standard humanoid rigs that can act as export targets. Each entry maps the
# canonical Mixamo body name to names used by that skeleton family.
ALIASES = {
    'ue5': {
        'Hips': ('pelvis',), 'Spine': ('spine_01',), 'Spine1': ('spine_02',),
        'Spine2': ('spine_03',), 'Neck': ('neck_01',), 'Head': ('head',),
        'LeftShoulder': ('clavicle_l',), 'RightShoulder': ('clavicle_r',),
        'LeftArm': ('upperarm_l',), 'RightArm': ('upperarm_r',),
        'LeftForeArm': ('lowerarm_l',), 'RightForeArm': ('lowerarm_r',),
        'LeftHand': ('hand_l',), 'RightHand': ('hand_r',),
        'LeftUpLeg': ('thigh_l',), 'RightUpLeg': ('thigh_r',),
        'LeftLeg': ('calf_l',), 'RightLeg': ('calf_r',),
        'LeftFoot': ('foot_l',), 'RightFoot': ('foot_r',),
        'LeftToeBase': ('ball_l',), 'RightToeBase': ('ball_r',),
    },
    'unity': {
        'Hips': ('Hips', 'Hip', 'Hips_Joint_01'),
        'Spine': ('Spine', 'Ribs'),
        'Spine1': ('Chest', 'Spine1'),
        'Spine2': ('UpperChest', 'Spine2'),
        'Neck': ('Neck',), 'Head': ('Head',),
        'LeftShoulder': ('LeftShoulder', 'Left_Shoulder_Joint_01'),
        'RightShoulder': ('RightShoulder', 'Right_Shoulder_Joint_01'),
        'LeftArm': ('LeftUpperArm', 'Left_Upper_Arm_Joint_01'),
        'RightArm': ('RightUpperArm', 'Right_Upper_Arm_Joint_01'),
        'LeftForeArm': ('LeftLowerArm', 'Left_Forearm_Joint_01'),
        'RightForeArm': ('RightLowerArm', 'Right_Forearm_Joint_01'),
        'LeftHand': ('LeftHand', 'Left_Wrist_Joint_01'),
        'RightHand': ('RightHand', 'Right_Wrist_Joint_01'),
        'LeftUpLeg': ('LeftUpperLeg', 'Left_Thigh_Joint_01'),
        'RightUpLeg': ('RightUpperLeg', 'Right_Thigh_Joint_01'),
        'LeftLeg': ('LeftLowerLeg', 'Left_Knee_Joint_01'),
        'RightLeg': ('RightLowerLeg', 'Right_Knee_Joint_01'),
        'LeftFoot': ('LeftFoot', 'Left_Ankle_Joint_01'),
        'RightFoot': ('RightFoot', 'Right_Ankle_Joint_01'),
        'LeftToeBase': ('LeftToes', 'Left_Toe_Joint_01'),
        'RightToeBase': ('RightToes', 'Right_Toe_Joint_01'),
    },
}


def body_mapping(kind,bones,semantic):
    names=set(bones)
    if kind=='mixamo':
        suffix={}
        for name in names:
            suffix.setdefault(name.split(':')[-1],[]).append(name)
        families=[None,'ue5','unity']
        last_missing=[]
        for family in families:
            mapping=[]
            for n in NAMES:
                candidates=(n,) if family is None else ALIASES[family].get(n,(n,))
                # Manny/Quinn have five spine and two neck segments. Map the
                # canonical chest to the actual upper chest, not spine_03.
                if family == 'ue5' and 'spine_05' in suffix:
                    candidates={'Spine1':('spine_03',), 'Spine2':('spine_05',),
                                'Neck':('neck_02',)}.get(n,candidates)
                hits=[]
                for candidate in candidates:
                    hits.extend(suffix.get(candidate,[]))
                mapping.append(hits)
            missing=[n for n,v in zip(NAMES,mapping) if len(v)!=1]
            if not missing:
                chosen=[v[0] for v in mapping]
                if len(set(chosen))==22:return chosen
            last_missing=missing
        raise ValueError('Expected a Mixamo, UE5 or Unity humanoid rig. Missing or ambiguous bones: '+', '.join(last_missing))
    mapping=[semantic.get(n) for n in VRM] if kind=='vrm' else PMX
    missing=[NAMES[i] for i,n in enumerate(mapping) if n not in names]
    if missing:raise ValueError('Unsupported humanoid mapping (manual mapping is not available yet): '+', '.join(missing))
    if len(set(mapping))!=22:raise ValueError('Humanoid bones must have distinct mappings')
    return mapping


def finger_mapping(bones):
    """Keep real publisher finger names; do not rename the target hierarchy."""
    suffix = {}
    for name in bones:
        suffix.setdefault(name.split(':')[-1], []).append(name)
    result = {}
    for side, short in (('Left', 'l'), ('Right', 'r')):
        for finger in ('Thumb', 'Index', 'Middle', 'Ring', 'Pinky'):
            for number, segment in enumerate(('Proximal', 'Intermediate', 'Distal'), 1):
                canonical = f'{side}Hand{finger}{number}'
                candidates = (canonical, f'{finger.lower()}_{number:02d}_{short}',
                              f'{side}{finger}{segment}')
                hits = [name for candidate in candidates for name in suffix.get(candidate, [])]
                if len(hits) == 1:
                    result[canonical] = hits[0]
    return result
