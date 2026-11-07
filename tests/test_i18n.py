"""Presentation regressions with offscreen Qt and synthetic local settings."""
import json
import os
from pathlib import Path
import string
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication,QComboBox,QDoubleSpinBox,QLabel,QVBoxLayout,QDialog
from mocap import i18n
from mocap.tooltips import plain_tooltip,tooltip_text


class LanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        i18n._CURRENT='en'

    def tearDown(self):
        i18n._CURRENT='en'

    def test_preferences_default_to_english_but_remember_explicit_chinese(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(i18n,'SETTINGS',Path(folder)/'language.json'),patch.dict(os.environ,{},clear=False):
            os.environ.pop('RGBMOCAP_LANG',None)
            self.assertEqual(i18n._load(),'en')
            for value in ['[]','null','{','{"language":[]}','{"language":"invalid"}']:
                i18n.SETTINGS.write_text(value,encoding='utf-8')
                self.assertEqual(i18n._load(),'en')
            i18n._save('zh')
            self.assertEqual(i18n._load(),'zh')
            os.environ['RGBMOCAP_LANG']='en'
            self.assertEqual(i18n._load(),'en')

    def test_translation_format_fields_match_the_source(self):
        formatter=string.Formatter()
        fields=lambda value:sorted((name,spec,conversion) for _,name,spec,conversion in formatter.parse(value) if name is not None)
        for source,translated in i18n.ZH.items():
            with self.subTest(source=source):self.assertEqual(fields(source),fields(translated))

    def test_switch_preserves_option_data_numeric_values_and_exact_english(self):
        dialog=QDialog();layout=QVBoxLayout(dialog)
        label=QLabel('Frame All');layout.addWidget(label)
        phrase="Show each person's name above their mesh. Rename people by right-clicking the People list. Display only."
        label.setToolTip(tooltip_text(phrase))
        combo=QComboBox();combo.addItem('Automatic','auto');combo.addItem('Low Memory','low_memory');combo.setCurrentIndex(1);layout.addWidget(combo)
        number=QDoubleSpinBox();number.setRange(-10,10);number.setValue(1.25);layout.addWidget(number)
        selection=QSignalSpy(combo.currentIndexChanged);edited=QSignalSpy(number.valueChanged)
        i18n.apply_language(dialog,'zh',refresh=False)
        self.assertEqual(combo.currentData(),'low_memory');self.assertEqual(number.value(),1.25)
        self.assertIn('人物名称',plain_tooltip(label.toolTip()))
        i18n.apply_language(dialog,'en',refresh=False)
        self.assertEqual(label.text(),'Frame All')
        self.assertEqual(plain_tooltip(label.toolTip()),phrase)
        self.assertEqual(selection.count(),0);self.assertEqual(edited.count(),0)
        dialog.close()

    def test_formatted_labels_created_in_english_translate_later_without_changing_paths(self):
        original=i18n.t('Webcam slot {value0}',value0=3)
        i18n._CURRENT='zh'
        self.assertEqual(i18n.t(original),'摄像头插槽 3')
        path=r'D:\角色\自动\actor {take}.fbx'
        message=i18n.t('Project saved: {value0}',value0=path)
        self.assertIn(path,message)
        self.assertEqual(i18n.to_english(message),'Project saved: '+path)

    def test_new_resource_dialogs_are_localized_and_keep_native_available(self):
        from mocap.gui import MainWindow,ModelsDialog
        from mocap.export_targets_ui import ExportTargetsDialog
        unavailable=patch('mocap.official_targets.installed',return_value=None)
        unavailable.start()
        window=MainWindow()
        try:
            i18n.install(window)
            callbacks=[]
            with patch.object(sys,'excepthook',side_effect=lambda *args:callbacks.append(args)):
                window.detector_choice.setCurrentIndex(window.detector_choice.findData('yolox'))
            self.assertEqual(callbacks,[], 'Qt signal callbacks must not raise silently')
            models=ModelsDialog(window)
            self.assertIn('humanart',{model.key for model in models.models})
            i18n.apply_language(models,'zh',refresh=False)
            self.assertIn('模型管理器',models.windowTitle())
            models.close();models.deleteLater()
            targets=ExportTargetsDialog(window)
            i18n.apply_language(targets,'zh',refresh=False)
            self.assertEqual(targets.windowTitle(),'导出骨架目标管理')
            self.assertEqual(window.output_skeleton.currentData(),'native')
            self.assertTrue(window.output_skeleton.model().item(0).isEnabled())
            for index in range(1,window.output_skeleton.count()):
                self.assertEqual(window.output_skeleton.model().item(index).isEnabled(),window.output_skeleton.itemData(index)=='ue5')
            for row in range(targets.table.rowCount()):
                self.assertIn(targets.table.item(row,1).text(),('Bundled; not prepared','已内置，尚未准备') if row==1 else ('Not installed','未安装'))
            targets.close();targets.deleteLater()
            i18n.apply_language(window,'en')
            self.assertEqual(window.windowTitle(),'RGB MoCap | Motion Workspace')
        finally:
            window.close()
            self.app.processEvents()
            unavailable.stop()

    def test_latest_upstream_export_options_survive_translation_and_format_changes(self):
        from mocap.source_export_dialog import SourceExportDialog
        dialog=SourceExportDialog()
        try:
            self.assertFalse(dialog.options()['place_at_origin'])
            self.assertFalse(dialog.options()['symmetric_rest'])
            dialog.place_at_origin.setChecked(True)
            dialog.symmetric_rest.setChecked(True)
            for kind in ['fbx','bvh','blend']:
                dialog.format.setCurrentIndex(dialog.format.findData(kind))
                baseline=dialog.options()
                self.assertEqual(baseline['place_at_origin'],kind!='blend')
                self.assertEqual(baseline['symmetric_rest'],kind!='blend')
                i18n.apply_language(dialog,'zh',refresh=False)
                self.assertEqual(dialog.options(),baseline)
                self.assertEqual(dialog.place_at_origin.text(),'导出时移到原点')
                i18n.apply_language(dialog,'en',refresh=False)
                self.assertEqual(dialog.options(),baseline)
        finally:
            dialog.close()


if __name__ == '__main__':
    unittest.main()
