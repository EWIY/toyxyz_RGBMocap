"""Keep the one bundled character publishable without exposing user libraries."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import check_fork
import check_source
import build_release


class LibraryDistributionTests(unittest.TestCase):
    def test_git_ignores_everything_except_the_exact_bundle(self):
        for name,ignored in [
            ('character_library/README.md',False),
            ('character_library/UE5/SKM_Manny_Simple.fbx',False),
            ('character_library/UE5/another.fbx',True),
            ('character_library/UE5/texture.png',True),
            ('character_library/UE5/private.json',True),
            ('character_library/UE5/nested/SKM_Manny_Simple.fbx',True),
            ('character_library/Mixamo/X Bot.fbx',True),
            ('character_library/Unity/DefaultMale.materials.json',True),
            ('character_library/notes.txt',True),
        ]:
            with self.subTest(name=name):
                result=subprocess.run(['git','check-ignore','--no-index','-q',name],cwd=ROOT)
                self.assertIn(result.returncode,(0,1))
                self.assertEqual(result.returncode==0,ignored)

    def test_fork_audit_rejects_private_library_files_even_when_indexed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            # Minimal source fixtures let the audit reach its real privacy checks.
            for name in ('installer/source-resources.json','installer/external-assets.json',
                         'installer/runtime-lock.json','mocap/runtime_registry.py','mocap/models.py'):
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/name,target)
            private=['character_library/UE5/private.json','character_library/Unity/texture.png']
            for name in private:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'{}')
            with patch.object(check_fork,'ROOT',root),patch.object(check_fork,'FEATURE_FILES',{}),patch.object(check_fork,'SOURCE_DOCS',()):
                _,_,errors=check_fork.audit(private)
            self.assertEqual(sorted(errors),sorted('Private/generated directory is indexed: '+name for name in private))

    def test_source_archive_checks_bundle_hash_and_private_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in ('README.md','LICENSE','THIRD_PARTY_NOTICES.md','docs/USER_GUIDE.md','docs/BUILD.md',
                         'installer/runtime-lock.json','installer/external-assets.json','installer/source-resources.json',
                         'mocap/runtime_registry.py',*check_fork.LIBRARY_FILES):
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
            def run():
                output=io.StringIO()
                with patch.object(check_source,'ROOT',root),patch.object(check_source,'cache_dependency_files'),contextlib.redirect_stdout(output):
                    result=check_source.main()
                return result,json.loads(output.getvalue())['errors']
            self.assertEqual(run(),(False,[]))
            private=root/'character_library/UE5/private.json';private.write_text('{}')
            result,errors=run();self.assertTrue(result)
            self.assertIn('Private character library file: character_library/UE5/private.json',errors)
            model=root/'character_library/UE5/SKM_Manny_Simple.fbx';model.write_bytes(b'invalid')
            result,errors=run();self.assertTrue(result)
            self.assertTrue(any('Generated or model payload:' in error and 'SKM_Manny_Simple.fbx' in error for error in errors))

    def test_packager_copies_only_allowlisted_library_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'source';app=Path(temp)/'app'
            for name in check_fork.LIBRARY_FILES:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'fixture')
            private=root/'character_library/UE5/private.png';private.write_bytes(b'private')
            model=(root/'character_library/UE5/SKM_Manny_Simple.fbx').resolve()
            with patch.object(build_release,'ROOT',root),patch.object(build_release,'source_resources',return_value={model}):
                build_release.stage_character_library(app)
            self.assertEqual({p.relative_to(app).as_posix() for p in app.rglob('*') if p.is_file()},set(check_fork.LIBRARY_FILES))
            self.assertEqual(private.read_bytes(),b'private')
