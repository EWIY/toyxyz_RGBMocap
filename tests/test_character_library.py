"""Library discovery, stable identities and the existing project import path."""
import os
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QDialog,QVBoxLayout
from mocap import i18n
from mocap.character_library import LibraryCombo,LibraryEntry,LibraryIndex,library_file,scan_library


class DiscoveryTests(unittest.TestCase):
    def test_recursive_supported_models_and_duplicate_names(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name in ['A/Hero.fbx','B/Hero.VRM','Unique.pmx','image.png','ignored.blend']:
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'')
            entries=scan_library(root)
            self.assertEqual({e.relative for e in entries},{'A/Hero.fbx','B/Hero.VRM','Unique.pmx'})
            self.assertEqual(len({e.label for e in entries}),3)
            self.assertEqual(next(e.label for e in entries if e.relative=='Unique.pmx'),'Unique')
            self.assertEqual(scan_library(root,lambda:True),[])

    def test_missing_folder_and_path_boundaries(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'library'
            self.assertEqual(scan_library(root),[])
            root.mkdir();(root/'hero.fbx').write_bytes(b'')
            self.assertEqual(library_file(root,'hero.fbx'),root/'hero.fbx')
            for name in ('../outside.fbx',str(root/'hero.fbx'),'C:hero.fbx','hero.txt','missing.fbx'):
                with self.subTest(name=name),self.assertRaises((ValueError,OSError)):
                    library_file(root,name)

    @unittest.skipUnless(os.name=='nt','Windows junction boundary')
    def test_junction_is_not_listed_or_imported(self):
        import _winapi
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);root=base/'library';outside=base/'outside'
            root.mkdir();outside.mkdir();(outside/'external.fbx').write_bytes(b'')
            link=root/'alias';_winapi.CreateJunction(str(outside),str(link))
            try:
                self.assertEqual(scan_library(root),[])
                with self.assertRaises(ValueError):library_file(root,'alias/external.fbx')
            finally:
                # Remove only this verified junction, never recurse into its target.
                assert link.parent==root and link.name=='alias'
                link.rmdir()
            self.assertTrue((outside/'external.fbx').is_file())


class LibraryUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])

    def test_user_names_and_paths_survive_language_switch(self):
        old=i18n._CURRENT
        dialog=QDialog();layout=QVBoxLayout(dialog);combo=LibraryCombo();layout.addWidget(combo)
        combo.setPlaceholderText('Add Character...')
        combo.addItem('Automatic','English/Automatic.fbx');combo.addItem('角色 {one}','角色/角色 {one}.vrm')
        combo.setCurrentIndex(-1)
        try:
            for language in ('zh','en'):
                i18n.apply_language(dialog,language,refresh=False)
                self.assertEqual([combo.itemText(i) for i in range(2)],['Automatic','角色 {one}'])
                self.assertEqual(combo.itemData(1),'角色/角色 {one}.vrm')
                self.assertEqual(combo.currentIndex(),-1)
            self.assertEqual(combo.placeholderText(),'Add Character...')
        finally:
            i18n._CURRENT=old;dialog.close()

    def test_index_refresh_and_shutdown(self):
        from PySide6.QtTest import QSignalSpy
        def wait_for(spy,count):
            deadline=time.monotonic()+5
            while spy.count()<count and time.monotonic()<deadline:
                self.app.processEvents();time.sleep(.01)
            self.assertEqual(spy.count(),count)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);index=LibraryIndex(root);spy=QSignalSpy(index.ready)
            index.start()
            try:
                wait_for(spy,1);self.assertEqual(spy.at(0)[0],[])
                (root/'New.fbx').write_bytes(b'');index.request()
                wait_for(spy,2);self.assertEqual(spy.at(1)[0],[LibraryEntry('New.fbx','New')])
            finally:index.close()
            self.assertFalse(index.isRunning())

    def test_dropdown_import_uses_project_job_and_honours_gates(self):
        from mocap.gui import MainWindow
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);library=base/'library';library.mkdir();(library/'My Actor.fbx').write_bytes(b'fake')
            window=MainWindow()
            try:
                window.character_library_index.close()
                self.app.processEvents()
                window.workspace_root=base/'project';window.character_library_root=library
                window.character_library_ready([LibraryEntry('My Actor.fbx','My Actor')])
                index=window.character_library_combo.findData('My Actor.fbx')
                self.assertGreaterEqual(index,0)
                self.assertLess(window.people_panel.layout().indexOf(window.people_list),window.people_panel.layout().count())
                self.assertEqual(window.character_library_combo.parentWidget(),window.people_panel)
                with patch.object(window,'start_character_job') as start,patch('mocap.character_ui.QFileDialog.getOpenFileName') as picker:
                    window.add_library_character(index)
                    picker.assert_not_called();job=start.call_args.args[0]
                    self.assertEqual(job['mode'],'import');self.assertEqual(Path(job['file']),library/'My Actor.fbx')
                    self.assertTrue(Path(job['output']).is_relative_to(base/'project/characters'))
                    self.assertEqual(window.character_library_combo.currentIndex(),-1)
                    start.reset_mock();window.busy=True;window.add_library_character(index);start.assert_not_called()
                    window.busy=False;window.contact_saving=True;window.add_library_character(index);start.assert_not_called()
                    window.contact_saving=False
                    window.characters=[dict(id=str(i),name='Actor '+str(i),kind='mixamo',asset=str(i)+'/asset') for i in range(8)]
                    with patch('mocap.character_ui.QMessageBox.information') as notice:
                        window.add_library_character(index);start.assert_not_called();notice.assert_called_once()
                window.update_character_library_readiness();self.assertFalse(window.character_library_combo.isEnabled())
            finally:
                window.busy=False;window.contact_saving=False;window.characters=[]
                window.close();self.app.processEvents()

    def test_bundled_manny_is_available_without_a_user_library(self):
        from mocap.gui import MainWindow
        from mocap.character_ui import BUNDLED_MANNY
        from mocap import bundled_targets
        old=i18n._CURRENT
        with tempfile.TemporaryDirectory() as folder:
            window=MainWindow()
            try:
                window.character_library_index.close();self.app.processEvents()
                window.workspace_root=Path(folder)/'project'
                window.character_library_root=Path(folder)/'no-library'
                window.character_library_ready([])
                index=window.character_library_combo.findData(BUNDLED_MANNY)
                self.assertGreaterEqual(index,0)
                with patch.object(window,'start_character_job') as start:
                    window.add_library_character(index)
                    job=start.call_args.args[0]
                    self.assertEqual(job['bundled'],'ue5')
                    self.assertEqual(job['name'],'Epic Manny Simple')
                    self.assertEqual(Path(job['file']),bundled_targets.ROOT/bundled_targets.MANNY_FILE)
                for lang in ('zh','en'):
                    i18n.apply_language(window,lang)
                    self.assertEqual(window.character_library_combo.itemData(index),BUNDLED_MANNY)
                    self.assertEqual(window.character_library_combo.itemText(index),i18n.t('Epic Manny Simple (bundled)'))
                self.assertFalse(window.character_library_root.exists())
            finally:
                i18n._CURRENT=old;window.workspace_root=None
                window.close();self.app.processEvents()

    def test_packaged_manny_is_listed_once_and_cannot_bypass_verification(self):
        from mocap.gui import MainWindow
        from mocap.character_ui import BUNDLED_MANNY
        from mocap import bundled_targets
        window=MainWindow()
        try:
            window.character_library_index.close();self.app.processEvents()
            window.character_library_root=bundled_targets.ROOT/'character_library'
            entries=scan_library(window.character_library_root)
            relative=Path(bundled_targets.MANNY_FILE).relative_to('character_library').as_posix()
            self.assertIn(relative,[entry.relative for entry in entries])
            window.character_library_ready(entries)
            values=[window.character_library_combo.itemData(i) for i in range(window.character_library_combo.count())]
            self.assertEqual(values.count(BUNDLED_MANNY),1)
            self.assertNotIn(relative,values)
            # A missing/invalid bundled resource must not become a normal import.
            with patch.object(bundled_targets,'available',return_value=False):
                window.character_library_ready(entries)
                values=[window.character_library_combo.itemData(i) for i in range(window.character_library_combo.count())]
                self.assertNotIn(BUNDLED_MANNY,values)
                self.assertNotIn(relative,values)
        finally:
            window.close();self.app.processEvents()

    def test_same_named_model_in_custom_data_folder_stays_visible(self):
        from mocap.gui import MainWindow
        from mocap.character_ui import BUNDLED_MANNY
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'character_library'
            model=root/'UE5/SKM_Manny_Simple.fbx'
            model.parent.mkdir(parents=True);model.write_bytes(b'user character')
            window=MainWindow()
            try:
                window.character_library_index.close();self.app.processEvents()
                window.character_library_root=root
                window.character_library_ready(scan_library(root))
                self.assertGreaterEqual(window.character_library_combo.findData(BUNDLED_MANNY),0)
                self.assertGreaterEqual(window.character_library_combo.findData('UE5/SKM_Manny_Simple.fbx'),0)
                self.assertEqual(model.read_bytes(),b'user character')
            finally:
                window.close();self.app.processEvents()


class BundledImportTests(unittest.TestCase):
    def test_worker_rejects_a_substituted_bundled_path_before_blender(self):
        from mocap.retarget import worker
        from mocap import bundled_targets
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);request=root/'job.json'
            request.write_text(json.dumps(dict(mode='import',file=str(root/'wrong.fbx'),
                output=str(root/'asset'),bundled='ue5')),encoding='utf-8')
            with patch.object(worker,'invoke') as invoke:
                with self.assertRaisesRegex(ValueError,'verified resource'):
                    worker.main(['--request',str(request)])
                invoke.assert_not_called()
