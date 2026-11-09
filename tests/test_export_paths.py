"""Final FBXs cannot overwrite bundled, registered or runtime input files."""
import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from mocap.export_paths import destination
from mocap import rig_export,official_targets


class ExportPathTests(unittest.TestCase):
    def test_unicode_spaces_and_project_outputs_are_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);out=root/'projects/测试工程/导出 结果';out.mkdir(parents=True)
            self.assertEqual(destination(out/'动作','fbx',root=root),out/'动作.fbx')
            self.assertEqual(destination(out/'walk.FBX','fbx',root=root),out/'walk.FBX')

    def test_resources_runtime_and_cache_outputs_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for folder in ('assets','models','runtime_character','character_work','character_library','cache','.git'):
                with self.subTest(folder=folder):
                    parent=root/folder;parent.mkdir()
                    with self.assertRaisesRegex(ValueError,'protected'):destination(parent/'out.fbx','fbx',root=root)

    def test_parent_traversal_cannot_bypass_resource_boundary(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'output').mkdir();(root/'assets').mkdir()
            with self.assertRaisesRegex(ValueError,'protected'):destination(root/'output/../assets/out.fbx','fbx',root=root)

    def test_original_source_and_hardlink_alias_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'source.fbx';source.write_bytes(b'original');alias=root/'alias.fbx';os.link(source,alias)
            for path in (source,alias):
                with self.assertRaisesRegex(ValueError,'original character'):destination(path,'fbx',root=root,protected_files=[source])
            self.assertEqual(source.read_bytes(),b'original')

    def test_relative_missing_parent_wrong_suffix_and_input_cache_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);animation=root/'animation';animation.mkdir()
            for path in (Path('out.fbx'),root/'missing/out.fbx',root/'out.npz',animation/'out.fbx',animation):
                with self.subTest(path=path),self.assertRaises(ValueError):destination(path,'fbx',root=root,protected_roots=[animation])

    def test_registry_source_is_protected_before_preparation_starts(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'original.fbx';source.write_bytes(b'original');(root/'config').mkdir()
            (root/'config/official-export-targets.json').write_text(json.dumps(dict(targets=dict(ue5=dict(source_file=str(source))))))
            request=root/'request.json';request.write_text(json.dumps(dict(project=str(root),result='initial',skeleton='ue5',target=str(source))))
            with patch.object(rig_export,'ROOT',root),patch.object(rig_export,'target_asset') as prepare:
                with self.assertRaisesRegex(ValueError,'original character'):rig_export.run(request,lambda *a,**kw:None)
                prepare.assert_not_called()
            self.assertEqual(official_targets.original_files('ue5',root=root),[source])

    def test_relocated_bundle_hardlink_is_protected_with_old_or_no_receipt(self):
        from mocap.bundled_targets import MANNY_FILE
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/MANNY_FILE
            source.parent.mkdir(parents=True);source.write_bytes(b'original bundled bytes')
            alias=root/'outside-library.fbx';os.link(source,alias)
            old=root/'assets/export_skeletons/ue5_manny/SKM_Manny_Simple.fbx'
            for originals in ((),(old,)):
                with self.subTest(receipt=bool(originals)),self.assertRaisesRegex(ValueError,'original character'):
                    destination(alias,'fbx',root=root,protected_files=originals)
            self.assertEqual(source.read_bytes(),b'original bundled bytes')
