"""Official-only routing never resurrects removed legacy targets."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from mocap import rig_export
from mocap.retarget.mapping import ALIASES,NAMES,body_mapping

class ExportTargetTests(unittest.TestCase):
    def test_missing_official_disables_target_and_never_uses_legacy_files(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(rig_export,'ROOT',Path(tmp)):
            legacy=Path(tmp)/'character_work/presets/mixamo';legacy.mkdir(parents=True)
            (legacy/'complete.json').write_text('{}')
            self.assertFalse(rig_export.skeleton_available('mixamo'))
            self.assertFalse(rig_export.skeleton_available('../../outside'))
            with self.assertRaisesRegex(RuntimeError,'not installed'):rig_export.target_asset('mixamo')
            self.assertTrue((legacy/'complete.json').exists())

    def test_mapping_accepts_explicit_families_and_rejects_ambiguity(self):
        self.assertEqual(body_mapping('mixamo',NAMES,{}),NAMES)
        for family in ('ue5','unity'):
            names=[ALIASES[family].get(name,(name,))[0] for name in NAMES]
            self.assertEqual(body_mapping('mixamo',names,{}),names)
        with self.assertRaises(ValueError):body_mapping('mixamo',['a:'+name for name in NAMES]+['b:Hips'],{})

    def test_invalid_key_does_not_start_worker(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(rig_export,'_character') as worker:
            request=Path(tmp)/'job.json'
            request.write_text(json.dumps(dict(project=tmp,result='initial',skeleton='../outside',target=str(Path(tmp)/'out.fbx'))))
            with self.assertRaises(ValueError):rig_export.run(request,lambda *args,**kwargs:None)
            worker.assert_not_called()
