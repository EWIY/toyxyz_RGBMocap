"""Finger bind offsets and roll are independent of imported display axes."""
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from mocap.retarget.finger_transport import anatomical_rest,frame,transfer
from mocap.retarget.blender_fingers import profile

class FingerTransportTests(unittest.TestCase):
    def test_export_rest_directions_are_decoded_before_measuring_anatomy(self):
        physical=np.array([[0.,1,0],[.2,1,0],[.3,1,.02],[.4,1,.04]])
        parents=np.array([-1,0,1,2]);basis=Rotation.from_euler('z',[0,90,145,-20],degrees=True).as_matrix()
        exported=physical.copy()
        for j in range(1,4):exported[j]=exported[parents[j]]+basis[parents[j]].T@(physical[j]-physical[parents[j]])
        tips=np.tile([.02,0,.01],(4,1));encoded_tips=np.einsum('nji,nj->ni',basis,tips)
        decoded,decoded_tips=anatomical_rest(exported,encoded_tips,parents,basis)
        np.testing.assert_allclose(decoded,physical,atol=1e-12)
        np.testing.assert_allclose(decoded_tips,tips,atol=1e-12)

    def test_neutral_pose_has_no_spurious_finger_rotation(self):
        native=np.tile(np.eye(3),(4,4,1,1));parents=np.array([-1,0,1,2])
        source={j:frame([1,.1*j,0],[0,0,1]) for j in (1,2,3)}
        target={j:frame([.1,1,.05*j],[1,0,0]) for j in (1,2,3)}
        hand=Rotation.from_rotvec([.3,.1,-.2]).as_matrix()
        output=transfer(native,parents,[1,2,3],source,target,{0:np.tile(hand,(4,1,1))})
        for value in output.values():np.testing.assert_allclose(value,np.tile(hand,(4,1,1)),atol=1e-12)

    def test_curl_is_transported_in_anatomical_plane_without_rest_offset(self):
        native=np.tile(np.eye(3),(1,4,1,1));parents=np.array([-1,0,1,2])
        bend=Rotation.from_rotvec([0,0,.4]).as_matrix()
        for j in (1,2,3):native[:,j]=native[:,j-1]@bend
        sa={j:frame([1,0,0],[0,1,0]) for j in (1,2,3)}
        ta={j:frame([0,1,0],[0,0,1]) for j in (1,2,3)}
        output=transfer(native,parents,[1,2,3],sa,ta,{0:native[:,0]})
        basis=ta[1]@sa[1].T
        for j in (1,2,3):np.testing.assert_allclose(output[j][0],basis@native[0,j]@basis.T,atol=1e-12)

    def test_mixamo_keeps_its_existing_adapter(self):
        self.assertIsNone(profile(dict(finger_mapping={'LeftHandIndex1':'mixamorig:LeftHandIndex1'})))
        self.assertEqual(profile(dict(finger_mapping={'LeftHandIndex1':'index_01_l'})),'ue5')
        self.assertEqual(profile(dict(finger_mapping={'LeftHandIndex1':'LeftIndexProximal'})),'unity')
