"""Original, procedural humanoid export templates under the project MIT license.

Coordinates/proportions and contact proxies are authored here, not extracted
from Adobe/Epic/Unity characters. Names are interoperability identifiers only.
Canonical coordinates are metres, Y up, Z forward. No model files are bundled.
"""
from copy import deepcopy

VERSION = 1
KEYS = ('mixamo', 'ue5', 'unity')
BODY = ('Hips', 'LeftUpLeg', 'RightUpLeg', 'Spine', 'LeftLeg', 'RightLeg',
        'Spine1', 'LeftFoot', 'RightFoot', 'Spine2', 'LeftToeBase', 'RightToeBase',
        'Neck', 'LeftShoulder', 'RightShoulder', 'Head', 'LeftArm', 'RightArm',
        'LeftForeArm', 'RightForeArm', 'LeftHand', 'RightHand')
PARENTS = (-1, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 12, 13, 14, 16, 17, 18, 19)
REST = ((0, 1.02, 0), (.10, 1.00, 0), (-.10, 1.00, 0), (0, 1.14, 0),
        (.10, .56, .02), (-.10, .56, .02), (0, 1.27, 0), (.10, .10, 0),
        (-.10, .10, 0), (0, 1.40, 0), (.10, .035, .16), (-.10, .035, .16),
        (0, 1.52, 0), (.12, 1.45, 0), (-.12, 1.45, 0), (0, 1.64, 0),
        (.23, 1.45, 0), (-.23, 1.45, 0), (.50, 1.45, 0), (-.50, 1.45, 0),
        (.74, 1.45, 0), (-.74, 1.45, 0))
UE5_BODY = ('pelvis', 'thigh_l', 'thigh_r', 'spine_01', 'calf_l', 'calf_r',
            'spine_03', 'foot_l', 'foot_r', 'spine_05', 'ball_l', 'ball_r',
            'neck_01', 'clavicle_l', 'clavicle_r', 'head', 'upperarm_l',
            'upperarm_r', 'lowerarm_l', 'lowerarm_r', 'hand_l', 'hand_r')
UNITY_BODY = ('Hips', 'LeftUpperLeg', 'RightUpperLeg', 'Spine', 'LeftLowerLeg',
              'RightLowerLeg', 'Chest', 'LeftFoot', 'RightFoot', 'UpperChest',
              'LeftToes', 'RightToes', 'Neck', 'LeftShoulder', 'RightShoulder',
              'Head', 'LeftUpperArm', 'RightUpperArm', 'LeftLowerArm',
              'RightLowerArm', 'LeftHand', 'RightHand')


def definition(key):
    if key not in KEYS:
        raise ValueError('Unknown built-in export skeleton: '+str(key))
    names = tuple('mixamorig:'+name for name in BODY) if key == 'mixamo' else UE5_BODY if key == 'ue5' else UNITY_BODY
    bones = []
    children = {i: [] for i in range(22)}
    for i, parent in enumerate(PARENTS):
        if parent >= 0:
            children[parent].append(i)
    for i, name in enumerate(names):
        tail = REST[children[i][0]] if children[i] else tuple(REST[i][j]+(0, .08, 0)[j] for j in range(3))
        if i == 0:
            tail = REST[3]
        if i in (10, 11):
            tail = (REST[i][0], REST[i][1], REST[i][2]+.08)
        if i in (20, 21):
            tail = (REST[i][0]+(.09 if i == 20 else -.09), REST[i][1], REST[i][2])
        bones.append(dict(name=name, parent=names[PARENTS[i]] if PARENTS[i] >= 0 else None,
                          head=REST[i], tail=tail))
    if key != 'mixamo':
        root = 'root' if key == 'ue5' else 'Root'
        bones.insert(0, dict(name=root, parent=None, head=(0, 0, 0), tail=(0, .10, 0)))
        next(b for b in bones if b['name'] == names[0])['parent'] = root
    if key == 'ue5':
        for name, parent, head, tail, child in (
                ('spine_02', 'spine_01', (0, 1.205, 0), REST[6], 'spine_03'),
                ('spine_04', 'spine_03', (0, 1.335, 0), REST[9], 'spine_05'),
                ('neck_02', 'neck_01', (0, 1.58, 0), REST[15], 'head')):
            bones.append(dict(name=name, parent=parent, head=head, tail=tail))
            next(b for b in bones if b['name'] == parent)['tail'] = head
            next(b for b in bones if b['name'] == child)['parent'] = name
    fingers = {}
    for side, hand in (('Left', 20), ('Right', 21)):
        sign = 1 if side == 'Left' else -1
        for finger, spread in (('Thumb', .055), ('Index', .027), ('Middle', .007), ('Ring', -.014), ('Pinky', -.033)):
            parent = names[hand]
            for segment in range(1, 4):
                source = f'{side}Hand{finger}{segment}'
                if key == 'mixamo':
                    name = 'mixamorig:'+source
                elif key == 'ue5':
                    name = f'{finger.lower()}_{segment:02d}_{side[0].lower()}'
                else:
                    name = side+('Little' if finger == 'Pinky' else finger)+('Proximal', 'Intermediate', 'Distal')[segment-1]
                x = .78 + (segment-1)*.03
                head = (sign*x, 1.45, spread)
                tail = (sign*(x+.03), 1.45, spread)
                bones.append(dict(name=name, parent=parent, head=head, tail=tail))
                parent = name
                fingers[source] = name
    return deepcopy(dict(key=key, version=VERSION, units='metres', body_names=names,
                         bones=bones, finger_mapping=fingers, vendor_asset=False))
