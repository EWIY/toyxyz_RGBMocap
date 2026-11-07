"""A local source library; importing still creates a separate project asset."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import os
from pathlib import Path
import stat
from threading import Condition

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QComboBox

EXTENSIONS = frozenset(('.fbx', '.vrm', '.pmx'))


def _linked(path: Path) -> bool:
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400))


def library_folder(root: Path) -> Path:
    """Do not follow a library redirected to an unrelated folder."""
    root = Path(root).absolute()
    if root.exists() or root.is_symlink():
        if _linked(root) or not root.is_dir():
            raise ValueError('Character library must be a regular folder.')
    return root


def library_file(root: Path, relative: str) -> Path:
    root = library_folder(root)
    name = Path(relative)
    if name.is_absolute() or name.drive or '..' in name.parts or name.suffix.lower() not in EXTENSIONS:
        raise ValueError('Choose an FBX, VRM or PMX inside the character library.')
    path = root
    for part in name.parts:
        path = path / part
        if _linked(path):
            raise ValueError('Character library links are not supported.')
    path.resolve().relative_to(root.resolve())
    if not path.is_file():
        raise ValueError('Character library file is no longer available.')
    return path


@dataclass(frozen=True)
class LibraryEntry:
    relative: str
    label: str


def scan_library(root: Path, cancelled=lambda: False) -> list[LibraryEntry]:
    root = library_folder(root)
    if not root.exists():
        return []
    files = []
    pending = [root]
    while pending and not cancelled():
        folder = pending.pop()
        # Recheck at traversal time, too: a folder can change after discovery.
        if _linked(folder):
            continue
        with os.scandir(folder) as entries:
            for entry in entries:
                if cancelled():
                    return []
                path = Path(entry.path)
                try:
                    if _linked(path):
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        pending.append(path)
                    elif entry.is_file(follow_symlinks=False) and path.suffix.lower() in EXTENSIONS:
                        files.append(path.relative_to(root))
                except FileNotFoundError:
                    continue  # Files being moved by the user are picked up next time.
    counts = Counter(path.stem.casefold() for path in files)
    return [LibraryEntry(path.as_posix(), path.stem if counts[path.stem.casefold()] == 1 else
                         f'{path.stem} ({path.as_posix()})')
            for path in sorted(files, key=lambda p: (p.stem.casefold(), p.as_posix().casefold()))]


class LibraryIndex(QThread):
    ready = Signal(object)
    failed = Signal(str)

    def __init__(self, root: Path, parent=None):
        super().__init__(parent)
        self.root = Path(root)
        self.condition = Condition()
        self.pending = True
        self.stopping = False

    def request(self):
        with self.condition:
            self.pending = True
            self.condition.notify()

    def run(self):
        while True:
            with self.condition:
                self.condition.wait_for(lambda: self.pending or self.stopping)
                if self.stopping:
                    return
                self.pending = False
            try:
                entries = scan_library(self.root, lambda: self.stopping)
                if not self.stopping:
                    self.ready.emit(entries)
            except (OSError, ValueError) as error:
                if not self.stopping:
                    self.ready.emit([])
                    self.failed.emit(str(error))

    def close(self):
        with self.condition:
            self.stopping = True
            self.condition.notify()
        self.wait()


class LibraryCombo(QComboBox):
    opening = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # User file names must survive language switching verbatim.
        self.setProperty('rgb_i18n_dynamic_items', True)
        self.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(10)
        self.setMinimumWidth(0)
        self.setMaxVisibleItems(16)

    def showPopup(self):
        self.opening.emit()
        super().showPopup()

    def wheelEvent(self, event):
        # Scrolling beside People must not accidentally import a character.
        event.ignore()
