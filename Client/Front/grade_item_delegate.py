from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (QLineEdit, QStyledItemDelegate)


class GradeItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.validator = QIntValidator(1, 10)

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(self.validator)
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor.setMaxLength(2)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        editor.setText(str(value) if value else "")

    def setModelData(self, editor, model, index):
        text = editor.text()
        if text:
            model.setData(index, int(text), Qt.ItemDataRole.EditRole)
        else:
            model.setData(index, None, Qt.ItemDataRole.EditRole)
