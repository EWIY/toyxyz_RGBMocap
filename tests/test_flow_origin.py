"""Scene-coordinate regressions using synthetic geometry, without body models."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy.spatial.transform import Rotation
from mocap.flow_origin import (INPUTS, camera_center, horizontal_origin,
                               identity, rebase_saved_camera, reference)


class SceneOriginTests(unittest.TestCase):
    def test_horizontal_origin_preserves_height_and_relative_displacements(self):
        rotation = Rotation.from_euler('y', 31, degrees=True).as_matrix()
        pelvis = np.array([2., 1.7, -4.])
        offset = np.array([.5, .2, 1.])
        origin = horizontal_origin(pelvis, rotation, offset)
        placed = rotation@pelvis + offset
        np.testing.assert_allclose(placed-origin, [0, placed[1], 0], atol=1e-12)
        points = np.array([[2, 1, 3], [4, 2, 1], [-2, 0, 9.]])
        np.testing.assert_allclose(np.diff(points-origin, axis=0), np.diff(points,axis=0))

    def test_camera_projection_is_unchanged_when_camera_and_people_rebase(self):
        rotation = Rotation.from_euler('xyz', [5, 20, 2], degrees=True).as_matrix()
        origin = np.array([4., 0, -7.])
        center = np.array([0., 1.8, 0])
        points = np.array([[2., .8, 5.], [-1., 1.4, 6.]])
        rebased_center = camera_center(center[1], origin)
        np.testing.assert_allclose((points-center)@rotation.T,
                                   ((points-origin)-rebased_center)@rotation.T, atol=1e-12)

    def test_saved_orbit_view_rebases_once_and_keeps_original_input(self):
        camera = dict(scene_center=[3, 1, 4], target=[1, 2, 3], distance=5.)
        original = copy.deepcopy(camera)
        origin = np.array([2., 0, 8.])
        first = rebase_saved_camera(camera, origin)
        self.assertEqual(rebase_saved_camera(first, origin), first)
        np.testing.assert_allclose(first['target'], [-1, 2, -5])
        second = rebase_saved_camera(first, [3, 0, 2])
        np.testing.assert_allclose(second['target'], [-2, 2, 1])
        self.assertEqual(camera, original)

    def test_invalid_origins_are_rejected(self):
        for bad in ([0, 1, 0], [float('nan'), 0, 0], [1, 2]):
            with self.assertRaises(ValueError):
                camera_center(1.8, bad)
            with self.assertRaises(ValueError):
                rebase_saved_camera({}, bad)
        with self.assertRaises(ValueError):
            horizontal_origin([1, 2], np.eye(3), np.zeros(3))

    def test_earliest_complete_take_is_shared_and_pending_others_are_excluded(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            people = []
            projects = []
            for ident, first in [(1, 15), (2, 0)]:
                project = root/f'person_{ident}'
                project.mkdir()
                for name in INPUTS:
                    (project/name).write_bytes(b'synthetic')
                (project/'project.json').write_text(json.dumps(dict(person_id=ident,person_frames=[first,first+3])),encoding='utf-8')
                projects.append(project)
                people.append(dict(id=ident,takes=[dict(first=first,project=project.name)]))
            (root/'people.json').write_text('{}')
            with patch('mocap.flow_backend.scene_root',return_value=root), patch('mocap.people_store.load_people',return_value={'people':people}):
                self.assertEqual(reference(projects[0]), projects[1])
                self.assertEqual(identity(projects[0])['project'], 'person_2')
                (projects[1]/'flowhmr_pending.json').write_text('{}')
                self.assertEqual(reference(projects[0]), projects[0])
                # A currently publishing actor is eligible before clearing its marker.
                self.assertEqual(reference(projects[1]), projects[1])


if __name__ == '__main__':
    unittest.main()
