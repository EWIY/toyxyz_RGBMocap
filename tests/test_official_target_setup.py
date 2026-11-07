"""Registration is portable, rejects wrong families and preserves prior assets."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from mocap import official_targets, rig_export
from tools import setup_official_target as setup


class OfficialSetupTests(unittest.TestCase):
    def fixture_import(self, filename, folder, key):
        folder.mkdir()
        for name in official_targets.REQUIRED:
            (folder/name).write_bytes(b'fixture')
        (folder/'import.json').write_text(json.dumps(dict(kind='mixamo')))
        profile=dict(mixamo='LeftHandIndex1',ue5='index_01_l',unity='LeftIndexProximal')[key]
        mapping={str(i):'segment'+str(i) for i in range(29)}
        mapping['LeftHandIndex1']=profile
        (folder/'mixamo-rig.json').write_text(json.dumps(dict(finger_mapping=mapping,
            meshes=[dict(name='skin')],bones=[dict(name=n) for n in ('spine_05','neck_02')])))

    def test_registration_relocation_and_replace_keep_prior_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'first';root.mkdir();source=Path(temp)/'XBot.fbx';source.write_bytes(b'original source')
            with patch.object(setup,'ROOT',root),patch.object(setup,'import_target',side_effect=self.fixture_import):
                first=setup.register('mixamo',source)
                original=(first/'mixamo-rest.blend').read_bytes()
                self.assertEqual(official_targets.installed('mixamo',verify=True,root=root),first)
                with self.assertRaises(FileExistsError):setup.register('mixamo',source)
                second=setup.register('mixamo',source,replace=True)
                self.assertNotEqual(first,second)
                self.assertEqual((first/'mixamo-rest.blend').read_bytes(),original)
                self.assertTrue((root/'config/official-export-targets.previous.json').is_file())
            renamed=Path(temp)/'moved';root.rename(renamed)
            with patch.object(rig_export,'ROOT',renamed):
                self.assertEqual(rig_export.target_asset('mixamo'),renamed/second.relative_to(root))
            self.assertEqual(source.read_bytes(),b'original source')

    def test_wrong_family_never_replaces_the_registry(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'XBot.fbx';source.write_bytes(b'source')
            with patch.object(setup,'ROOT',root),patch.object(setup,'import_target',side_effect=self.fixture_import):
                first=setup.register('mixamo',source)
            before=(root/'config/official-export-targets.json').read_bytes()
            def wrong(filename,folder,key):self.fixture_import(filename,folder,'unity')
            with patch.object(setup,'ROOT',root),patch.object(setup,'import_target',side_effect=wrong):
                with self.assertRaisesRegex(ValueError,'hierarchy'):setup.register('mixamo',source,replace=True)
            self.assertEqual((root/'config/official-export-targets.json').read_bytes(),before)
            self.assertTrue(first.is_dir())

    def test_incomplete_receipt_cannot_bypass_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);asset=root/'character_work/official_targets/mixamo/v1';asset.mkdir(parents=True)
            for name in official_targets.REQUIRED:(asset/name).write_bytes(b'fixture')
            (root/'config').mkdir()
            (root/'config/official-export-targets.json').write_text(json.dumps(dict(targets=dict(mixamo=dict(asset=asset.relative_to(root).as_posix(),files={})))))
            with self.assertRaisesRegex(RuntimeError,'receipt is incomplete'):official_targets.installed('mixamo',verify=True,root=root)
