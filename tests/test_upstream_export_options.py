"""Keep the new upstream export-only origin distinct from shared scene origin."""
import unittest
import numpy as np
from mocap.export_options import centered_transform


class ExportOriginTests(unittest.TestCase):
    def test_one_offset_per_actor_keeps_travel_and_height_across_takes(self):
        origins={}
        transform=np.eye(4)
        first=centered_transform(transform,[5,1.8,-3],origins,'actor-a')
        later=centered_transform(transform,[7,1.9,-1],origins,'actor-a')
        np.testing.assert_allclose(first[:3,3],[-5,0,3])
        np.testing.assert_array_equal(first,later)
        np.testing.assert_allclose(later[:3,:3]@np.array([7,1.9,-1])+later[:3,3],[2,1.9,2])
        other=centered_transform(transform,[20,1.6,8],origins,'actor-b')
        np.testing.assert_allclose(other[:3,3],[-20,0,-8])
        np.testing.assert_array_equal(transform,np.eye(4))


if __name__=='__main__':unittest.main()
