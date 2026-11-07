"""Rest-relative finger rotations in physical finger/palm frames, not bone tails."""
import numpy as np


def unit(vector):
    vector=np.asarray(vector,dtype=float)
    length=float(np.linalg.norm(vector))
    if not np.isfinite(length) or length<1e-8:
        raise ValueError('Degenerate anatomical finger reference.')
    return vector/length


def frame(direction,palm_normal):
    along=unit(direction)
    normal=unit(np.asarray(palm_normal)-along*np.dot(along,palm_normal))
    return np.column_stack((along,normal,np.cross(along,normal)))


def palm_normal(points,side):
    wrist=points[side+'Hand']
    forward=points[side+'HandMiddle1']-wrist
    across=points[side+'HandIndex1']-points[side+'HandPinky1']
    return unit(np.cross(forward,across))


def anatomical_rest(rest,ends,parents,basis):
    """Undo BVH export's per-parent offset basis before measuring anatomy."""
    points=np.asarray(rest,dtype=float).copy()
    for j,parent in enumerate(parents):
        if parent>=0:
            points[j]=points[parent]+basis[parent]@(rest[j]-rest[parent])
    tips=np.einsum('nij,nj->ni',basis,ends)
    return points,tips


def transfer(native,parents,finger_ids,source_axes,target_axes,hand_world):
    """Transfer each native joint's local delta, preserving target bind offsets.

    native: source world skin rotations, with identity at neutral.
    hand_world: existing solved target hand skin rotations. Body solving is untouched.
    Each basis uses the actual proximal-to-distal line and a palm-plane reference.
    """
    native=np.asarray(native,dtype=float)
    result={}
    for j in finger_ids:
        parent=int(parents[j])
        parent_target=result[parent] if parent in result else hand_world[parent]
        relative=native[:,parent].swapaxes(-1,-2)@native[:,j]
        conversion=target_axes[j]@source_axes[j].T
        delta=conversion@relative@conversion.T
        result[j]=parent_target@delta
    return result
