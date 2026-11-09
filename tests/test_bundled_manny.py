"""Fresh-clone availability, integrity and first-use import of the official asset."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from mocap import bundled_targets,official_targets,rig_export
from tools import setup_official_target as setup
import test_official_target_setup as setup_fixtures


class BundledMannyTests(unittest.TestCase):
    def test_only_ue_is_bundled_and_manifest_matches_packaged_bytes(self):
        self.assertTrue(bundled_targets.available('ue5'))
        self.assertFalse(bundled_targets.available('mixamo'))
        self.assertFalse(bundled_targets.available('unity'))
        file=bundled_targets.source('ue5')
        self.assertEqual(file.relative_to(bundled_targets.ROOT).as_posix(),
                         'character_library/UE5/SKM_Manny_Simple.fbx')
        self.assertFalse((bundled_targets.ROOT/'assets/export_skeletons/ue5_manny/SKM_Manny_Simple.fbx').exists())
        resources=json.loads((bundled_targets.ROOT/'installer/source-resources.json').read_text())
        row=next(r for r in resources['files'] if r['path']==bundled_targets.MANNY_FILE)
        self.assertEqual(row['sha256'],bundled_targets.MANNY_SHA256)
        self.assertEqual(file.stat().st_size,row['bytes'])

    def test_changed_resource_is_rejected_before_import(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);target=root/bundled_targets.MANNY_FILE;target.parent.mkdir(parents=True)
            target.write_bytes(b'0'*bundled_targets.MANNY_BYTES)
            with patch.object(bundled_targets,'ROOT',root),patch.object(setup,'register') as register:
                self.assertTrue(bundled_targets.available('ue5'))
                with self.assertRaisesRegex(RuntimeError,'missing or changed'):bundled_targets.prepare('ue5',root=root)
                register.assert_not_called()

    def test_first_export_prepares_once_then_reuses_and_relocates(self):
        fixture=setup_fixtures.OfficialSetupTests().fixture_import
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'install';root.mkdir()
            with patch.object(rig_export,'ROOT',root),patch.object(setup,'import_target',side_effect=fixture) as importer:
                self.assertTrue(rig_export.skeleton_available('ue5'))
                target=rig_export.target_asset('ue5')
                self.assertEqual(rig_export.target_asset('ue5'),target)
                self.assertEqual(importer.call_count,1)
                self.assertEqual(official_targets.installed('ue5',verify=True,root=root),target)
                self.assertFalse(rig_export.skeleton_available('mixamo'))
                self.assertFalse(rig_export.skeleton_available('unity'))
            moved=root.with_name('moved');root.rename(moved)
            with patch.object(rig_export,'ROOT',moved),patch.object(setup,'import_target') as importer:
                self.assertEqual(rig_export.target_asset('ue5'),moved/target.relative_to(root))
                importer.assert_not_called()
