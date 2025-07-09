from pyqt_compat.QtCore import Qt
from pyqt_compat.QtGui import QKeySequence, QContextMenuEvent, QTextCursor, QKeyEvent
from pyqt_compat.QtWidgets import QPlainTextEdit, QMenu, QInputDialog

from pyqt_compat import is_qt6, QT_STRONG_FOCUS, QT_KEY_F, QT_KEY_MODIFIER_CONTROL, QT_KEY_F3

if is_qt6:
    from pyqt_compat.QtGui import QAction
else:
    from pyqt_compat.QtWidgets import QAction


class ScreenTextViewer(QPlainTextEdit):

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.find_text = ""
        self.setFocusPolicy(QT_STRONG_FOCUS)

    def contextMenuEvent(self, e: QContextMenuEvent) -> None:
        menu = QMenu()

        action_find = QAction("&Find", self)
        action_find.setStatusTip("Find text")
        action_find.triggered.connect(self.on_find)
        menu.addAction(action_find)

        menu.exec(e.globalPos())

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == QT_KEY_F and e.modifiers() == QT_KEY_MODIFIER_CONTROL:
            self.on_find()
        elif e.key() == QT_KEY_F3:
            text_cursor = self.find(self.find_text)
            if text_cursor:
                self.moveCursor(QTextCursor.MoveOperation.WordRight,
                                QTextCursor.MoveMode.KeepAnchor)
        else:
            super().keyPressEvent(e)

    def on_find(self):
        text_to_find, ok = QInputDialog.getText(self.parentWidget(),
                                                'Find text',
                                                'Enter the text to find')
        if ok and text_to_find:
            self.find_text = text_to_find
            text_cursor = self.find(text_to_find)

            if text_cursor:
                self.moveCursor(QTextCursor.MoveOperation.WordRight,
                                QTextCursor.MoveMode.KeepAnchor)
