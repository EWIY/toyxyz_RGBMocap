"""Original template topology, cache authenticity and private-target precedence."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from mocap import builtin_skeletons as templates, builtin_targets as cache, rig_export


class BuiltinSkeletonTests(unittest.TestCase):
    def test_templates_have_distinct_valid_hierarchies_and_all_fingers(self):
        for key in templates.KEYS:
            spec = templates.definition(key)
            bones = {bone['name']:bone for bone in spec['bones']}
            self.assertEqual(len(bones),len(spec['bones']))
            self.assertEqual(len(spec['body_names']),22)
            self.assertEqual(len(spec['finger_mapping']),30)
            self.assertFalse(spec['vendor_asset'])
            self.assertTrue(all(name in bones for name in spec['body_names']))
            self.assertTrue(all(name in bones for name in spec['finger_mapping'].values()))
            for bone in bones.values():
                self.assertGreater(np.linalg.norm(np.subtract(bone['head'],bone['tail'])),.001)
                seen = {bone['name']}
                parent = bone['parent']
                while parent:
                    self.assertIn(parent,bones)
                    self.assertNotIn(parent,seen)
                    seen.add(parent)
                    parent = bones[parent]['parent']
        ue = templates.definition('ue5')
        self.assertIn('spine_05',{b['name'] for b in ue['bones']})
        self.assertIn('neck_02',{b['name'] for b in ue['bones']})
        with self.assertRaises(ValueError):
            templates.definition('../unknown')

    def test_generated_cache_is_verified_reused_and_corruption_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(cache,'HOME',Path(folder)),patch.object(cache,'signature',return_value='a'*64):
            def build(mode,out,key):
                self.assertEqual(mode,'builtin')
                for name in cache.FILES:
                    (out/name).write_bytes(('original fixture '+key).encode())
            with patch('mocap.retarget.worker.invoke',side_effect=build) as invoke:
                first=cache.prepare('mixamo')
                self.assertEqual(cache.prepare('mixamo'),first)
                self.assertEqual(invoke.call_count,1)
                (first/'mixamo-rest.blend').write_bytes(b'corrupted')
                second=cache.prepare('mixamo')
                self.assertEqual(first,second)
                self.assertEqual(invoke.call_count,2)
                preserved=list(first.parent.glob(first.name+'.invalid-*'))
                self.assertEqual(len(preserved),1)
                self.assertEqual((preserved[0]/'mixamo-rest.blend').read_bytes(),b'corrupted')

    def test_registered_targets_take_precedence_without_being_changed(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(rig_export,'ROOT',Path(folder)),patch('mocap.builtin_targets.prepare') as generate:
            target=Path(folder)/'character_work/presets/unity'
            target.mkdir(parents=True)
            for name in rig_export.PRESET_FILES:
                (target/name).write_bytes(b'private fixture')
            self.assertEqual(rig_export.target_asset('unity'),target)
            generate.assert_not_called()
            self.assertEqual((target/'mixamo-rest.blend').read_bytes(),b'private fixture')


if __name__ == '__main__':
    unittest.main()
