"""Local official overrides preserve private targets and reject damaged assets."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from mocap import official_targets,rig_export
from mocap.retarget.mapping import ALIASES,NAMES,body_mapping,finger_mapping

class OfficialTargetsTests(unittest.TestCase):
    def test_hidden_selected_source_still_drives_shared_follow_camera(self):
        import numpy as np
        from mocap.viewport import MotionView
        project=Path.cwd().resolve()
        take=SimpleNamespace(frame_at=lambda seconds:12)
        view=SimpleNamespace(live_active=False,scene_center=np.array([0.,1.,0.]),pan=np.zeros(3),
            follow=True,people_scene=SimpleNamespace(by_project={project:take}),
            path=project/'preview.json',scene_time=.4,scene_actors=lambda:[],
            scene_joint_points=lambda take,frame:np.array([[2.,.9,3.]]))
        np.testing.assert_allclose(MotionView.target(view),[2.,1.,3.])
        view.follow=False
        view.joints=None
        np.testing.assert_allclose(MotionView.target(view),[0.,1.,0.])
    def fixture(self, root):
        target=root/'character_work/official_targets/mixamo/version'
        target.mkdir(parents=True)
        for name in official_targets.REQUIRED:(target/name).write_bytes(b'official fixture')
        hashes={name:hashlib.sha256((target/name).read_bytes()).hexdigest() for name in official_targets.REQUIRED}
        (root/'config').mkdir()
        (root/'config/official-export-targets.json').write_text(json.dumps(dict(targets=dict(mixamo=dict(asset=str(target),files=hashes)))))
        return target

    def test_installed_official_is_the_only_export_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);target=self.fixture(root)
            with patch.object(rig_export,'ROOT',root):
                for source in ('auto','official','builtin'):
                    self.assertEqual(rig_export.target_asset('mixamo',source),target)
                with self.assertRaises(ValueError):rig_export.target_asset('mixamo','custom')

    def test_corrupt_official_never_silently_falls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);target=self.fixture(root)
            (target/'mixamo-rest.blend').write_bytes(b'changed')
            with patch.object(rig_export,'ROOT',root):
                with self.assertRaisesRegex(RuntimeError,'target changed'):rig_export.target_asset('mixamo')

    def test_manny_chest_and_neck_use_actual_upper_segments(self):
        names=[ALIASES['ue5'].get(name,(name,))[0] for name in NAMES]+['spine_04','spine_05','neck_02']
        mapped=body_mapping('mixamo',names,{})
        self.assertEqual([mapped[i] for i in (3,6,9,12)],['spine_01','spine_03','spine_05','neck_02'])
        self.assertEqual(len(set(mapped)),22)

    def test_all_thirty_real_publisher_fingers_map_without_renaming(self):
        for family in ('ue5','unity','mixamo'):
            names=[]
            for side,short in (('Left','l'),('Right','r')):
                for finger in ('Thumb','Index','Middle','Ring','Pinky'):
                    for number,segment in enumerate(('Proximal','Intermediate','Distal'),1):
                        names.append(f'{finger.lower()}_{number:02d}_{short}' if family=='ue5' else f'{side}{finger}{segment}' if family=='unity' else f'mixamorig:{side}Hand{finger}{number}')
            mapped=finger_mapping(names)
            self.assertEqual(len(mapped),30)
            self.assertEqual(set(mapped.values()),set(names))
