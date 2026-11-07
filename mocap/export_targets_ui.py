"""Import and status for separately acquired official-resource export targets."""
import codecs
import os
from pathlib import Path

from PySide6.QtCore import QProcess, QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QDialog, QFileDialog, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from .i18n import t
from .paths import ROOT
from .rig_export import TARGET_SOURCES, skeleton_available


def refresh_choices(window):
    combo = window.output_skeleton
    for index in range(combo.count()):
        key = combo.itemData(index)
        if key == 'native':
            continue
        item = combo.model().item(index)
        available = skeleton_available(key)
        item.setEnabled(available)
        item.setToolTip('' if available else t('Official target is not installed. See File > Export Skeleton Targets.'))


class ExportTargetsDialog(QDialog):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.process = None
        self.killer = None
        self.close_when_stopped = False
        self.setWindowTitle(t('Export Skeleton Targets'))
        self.resize(740, 360)
        layout = QVBoxLayout(self)
        note = QLabel(t('Acquire official X Bot, Manny Simple or DefaultMale from the linked publisher, then import its skinned FBX here. Files stay local. Import checks hierarchy and integrity; it cannot authenticate publisher ownership. Native capture remains available without these targets.'))
        note.setWordWrap(True)
        layout.addWidget(note)
        self.table = QTableWidget(len(TARGET_SOURCES), 3)
        self.table.setHorizontalHeaderLabels([t('Output Skeleton'), t('Status'), t('Action')])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 210)
        self.table.setColumnWidth(1, 110)
        self.import_buttons = {}
        for row, (key, (label, url)) in enumerate(TARGET_SOURCES.items()):
            self.table.setItem(row, 0, QTableWidgetItem(t(label)))
            self.table.setItem(row, 1, QTableWidgetItem())
            cell = QWidget()
            buttons = QHBoxLayout(cell)
            buttons.setContentsMargins(2, 2, 2, 2)
            official = QPushButton(t('Official Source'))
            official.clicked.connect(lambda checked=False, link=url: QDesktopServices.openUrl(QUrl(link)))
            buttons.addWidget(official)
            imported = QPushButton(t('Import official FBX...'))
            imported.clicked.connect(lambda checked=False, target=key: self.import_target(target))
            buttons.addWidget(imported)
            self.import_buttons[key] = imported
            self.table.setCellWidget(row, 2, cell)
        layout.addWidget(self.table)
        self.status = QLabel(t('Enable Include target mesh to keep the original skin in the exported animation. Select one character at a time for comparison in the shared viewport. See docs/OFFICIAL_EXPORT_TARGETS.md for setup and preview steps.'))
        self.status.setWordWrap(True)
        self.status.setTextFormat(Qt.PlainText)
        layout.addWidget(self.status)
        buttons = QHBoxLayout()
        self.cancel = QPushButton(t('Cancel'))
        self.cancel.setEnabled(False)
        self.cancel.clicked.connect(self.cancel_import)
        buttons.addWidget(self.cancel)
        buttons.addStretch()
        close = QPushButton(t('Close'))
        close.clicked.connect(self.reject)
        buttons.addWidget(close)
        layout.addLayout(buttons)
        self.refresh()

    def refresh(self):
        for row, key in enumerate(TARGET_SOURCES):
            available = skeleton_available(key)
            self.table.item(row, 1).setText(t('Official target' if available else 'Not installed'))
            self.import_buttons[key].setEnabled(self.process is None and not available)
        self.cancel.setEnabled(self.process is not None)
        refresh_choices(self.window)

    def import_target(self, key):
        if self.process is not None:
            return
        filename, _ = QFileDialog.getOpenFileName(self, t('Import {target} target FBX', target=t(TARGET_SOURCES[key][0])), '', 'FBX (*.fbx)')
        if not filename:
            return
        self.target_key = key
        self.tail = ''
        self.decoder = codecs.getincrementaldecoder('utf-8')('replace')
        process = QProcess(self)
        self.process = process
        process.setProcessChannelMode(QProcess.MergedChannels)
        process.setWorkingDirectory(str(ROOT))
        process.readyReadStandardOutput.connect(self.read_output)
        process.errorOccurred.connect(self.process_error)
        process.finished.connect(self.finished)
        self.status.setText(t('Preparing {target} export target...', target=t(TARGET_SOURCES[key][0])))
        process.start(str(ROOT/'runtime/python.exe'), ['-I', '-X', 'utf8', '-B', str(ROOT/'tools/setup_official_target.py'), '--skeleton', key, '--file', filename, '--replace'])
        self.refresh()

    def read_output(self):
        if self.process is None:
            return
        self.tail = (self.tail + self.decoder.decode(bytes(self.process.readAllStandardOutput())))[-8192:]

    def process_error(self, error):
        if error == QProcess.FailedToStart:
            self.status.setText(t('Cannot start target import. Run install.cmd first.'))
            process = self.process
            self.process = None
            process.deleteLater()
            self.refresh()
            if self.close_when_stopped:
                super().reject()

    def finished(self, code, exit_status):
        if self.process is None:
            return
        self.read_output()
        self.tail += self.decoder.decode(b'', final=True)
        success = code == 0 and skeleton_available(self.target_key)
        self.status.setText(t('Export target ready. Select it under Output Skeleton.') if success else
                           t('Target import did not complete. Existing targets were preserved.\n{details}', details=self.tail[-2000:]))
        process = self.process
        self.process = None
        process.deleteLater()
        self.refresh()
        if self.close_when_stopped:
            super().reject()

    def cancel_import(self):
        if self.process is None:
            return
        self.cancel.setEnabled(False)
        self.status.setText(t('Stopping...'))
        if os.name == 'nt' and self.process.processId():
            helper = QProcess(self)
            self.killer = helper
            helper.finished.connect(helper.deleteLater)
            helper.start(str(Path(os.environ['SystemRoot'])/'System32/taskkill.exe'), ['/PID', str(self.process.processId()), '/T', '/F'])
        else:
            self.process.kill()

    def reject(self):
        if self.process is not None:
            self.close_when_stopped = True
            self.cancel_import()
            return
        super().reject()

    def closeEvent(self, event):
        if self.process is not None:
            event.ignore()
            self.reject()
        else:
            super().closeEvent(event)


def show(window):
    if window.busy or getattr(window, 'character_process', None) is not None:
        window.status.setText(t('Finish the current task before preparing export targets.'))
        return
    dialog = ExportTargetsDialog(window)
    try:
        dialog.exec()
    finally:
        dialog.deleteLater()
