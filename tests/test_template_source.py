"""Official GUI selection survives language changes without legacy templates."""
import unittest
from PySide6.QtWidgets import QApplication
from mocap.gui import MainWindow
from mocap import i18n
from mocap.export_targets_ui import ExportTargetsDialog

class TemplateSourceTests(unittest.TestCase):
    def test_gui_offers_only_official_targets_in_both_languages(self):
        app=QApplication.instance() or QApplication([])
        window=MainWindow()
        try:
            i18n.install(window)
            self.assertEqual(window.output_template.currentData(),'auto')
            self.assertFalse(window.output_template.isEnabled())
            self.assertEqual([window.output_template.itemData(i) for i in range(window.output_template.count())],['auto','official'])
            window.output_skeleton.setCurrentIndex(window.output_skeleton.findData('ue5'))
            self.assertTrue(window.output_template.isEnabled())
            window.output_template.setCurrentIndex(window.output_template.findData('official'))
            for language in ('zh','en'):
                i18n.apply_language(window,language)
                self.assertEqual(window.output_template.currentData(),'official')
            dialog=ExportTargetsDialog(window)
            self.assertEqual(dialog.table.rowCount(),3)
            self.assertEqual(set(dialog.import_buttons),{'mixamo','ue5','unity'})
            dialog.deleteLater()
            window.output_skeleton.setCurrentIndex(window.output_skeleton.findData('native'))
            self.assertFalse(window.output_template.isEnabled())
        finally:
            i18n._CURRENT='en';window.close();app.processEvents()
