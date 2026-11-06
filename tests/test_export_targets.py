"""Export-target preparation never requires a bundled vendor character."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mocap import rig_export
from mocap.retarget.mapping import ALIASES, NAMES, body_mapping
from tools import setup_export_skeleton as setup


class ExportTargetTests(unittest.TestCase):
    def test_source_only_clone_has_optional_targets_and_safe_default(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(rig_export,'ROOT',Path(folder)):
            for key in rig_export.SKELETONS:
                self.assertFalse(rig_export.preset_ready(key))
            self.assertFalse(rig_export.preset_ready('../../outside'))
            for key in rig_export.SKELETONS:
                self.assertTrue(rig_export.skeleton_available(key))
            self.assertFalse(rig_export.skeleton_available('../../outside'))

    def test_all_registered_artifacts_are_required(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(rig_export,'ROOT',Path(folder)):
            target=Path(folder)/'character_work/presets/ue5'
            target.mkdir(parents=True)
            for name in rig_export.PRESET_FILES:
                (target/name).write_bytes(b'synthetic target')
            self.assertTrue(rig_export.preset_ready('ue5'))
            (target/'mixamo-canonical.npz').unlink()
            self.assertFalse(rig_export.preset_ready('ue5'))

    def test_mapping_accepts_three_explicit_families_and_rejects_ambiguity(self):
        self.assertEqual(body_mapping('mixamo',NAMES,{}),NAMES)
        for family in ['ue5','unity']:
            names=[ALIASES[family].get(name,(name,))[0] for name in NAMES]
            self.assertEqual(body_mapping('mixamo',names,{}),names)
        with self.assertRaises(ValueError):
            body_mapping('mixamo',['a:'+name for name in NAMES]+['b:Hips'],{})

    def test_user_import_is_staged_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'runtime').mkdir()
            (root/'runtime/python.exe').write_bytes(b'interpreter fixture')
            source=root/'my-character.fbx'
            source.write_bytes(b'licensed user fixture')
            def import_worker(command,**kwargs):
                request=json.loads(Path(command[-1]).read_text(encoding='utf-8'))
                target=Path(request['output'])
                target.mkdir()
                for name in rig_export.PRESET_FILES:
                    (target/name).write_bytes(b'fixture')
                (target/'import.json').write_text('{"kind":"mixamo"}',encoding='utf-8')
            with patch.object(setup,'ROOT',root),patch.object(rig_export,'ROOT',root),patch.object(setup.subprocess,'run',side_effect=import_worker):
                target=setup.register('ue5',source)
                self.assertTrue(rig_export.preset_ready('ue5'))
                self.assertEqual(source.read_bytes(),b'licensed user fixture')
                sentinel=target/'keep.txt';sentinel.write_text('keep')
                with self.assertRaises(FileExistsError):
                    setup.register('ue5',source)
                self.assertEqual(sentinel.read_text(),'keep')

    def test_missing_vendor_target_uses_builtin_and_invalid_key_never_starts_retarget(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(rig_export,'ROOT',Path(folder)),patch.object(rig_export,'_character') as worker:
            request=Path(folder)/'job.json'
            request.write_text(json.dumps(dict(project=folder,result='initial',skeleton='../outside',target=str(Path(folder)/'out.fbx'))))
            with self.assertRaises(ValueError):
                rig_export.run(request,lambda *args,**kwargs:None)
            worker.assert_not_called()
            with patch('mocap.builtin_targets.prepare',return_value=Path(folder)/'generated') as prepare:
                self.assertEqual(rig_export.target_asset('ue5'),Path(folder)/'generated')
                prepare.assert_called_once_with('ue5')


if __name__ == '__main__':
    unittest.main()
