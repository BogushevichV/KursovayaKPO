import sys
import re
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout, QHBoxLayout,
                               QGridLayout, QSizePolicy, QScrollArea)
from PySide6.QtCore import Qt

# Универсальный метод создания списка
def create_list(list_widget: QWidget, list_layout: QVBoxLayout, full_list: list, input_block: QLineEdit):
    area = CustomScrollArea(list_widget)
    area.layout.setSpacing(5)

    area.elements.setObjectName("Area")
    area.elements.setStyleSheet("#Area{ border-radius: 0px;"
                                        "border-bottom-right-radius: 30px; "
                                        "border-bottom-left-radius: 30px;}")
    list_layout.addWidget(area)

    input_block.textChanged.connect(
        lambda e: on_text_changed(full_list, input_block.text(), area))

    on_text_changed(full_list, "", area)
    return area

# Функция для привязки изменения текста поля
def on_text_changed(full_list: list, text: str, area):
    if area is not None:
        for el in area.elements.children()[1:]:
            if el is not None:
                el.deleteLater()

    for elem in full_list:
        if re.search(text, elem[0]):
            block = QWidget()
            block.setStyleSheet("font-size: 15px; font-weight: bold; background-color: #daf3e6; "
                                        "border-bottom-left-radius: 15px; border-top-left-radius: 15px;")
            block_layout = QHBoxLayout(block)
            area.layout.addWidget(block)

            item_left = QLabel(elem[0])
            item_left.setStyleSheet("color: green; margin: 0 0 0 5;")
            block_layout.addWidget(item_left)

            if len(elem) > 1:
                item_right = QLabel(elem[1])
                item_right.setStyleSheet("color: gray; margin: 0 0 0 50;")
                block_layout.addWidget(item_right)

            block_layout.addStretch()


# Класс Пользовательская прокручивающаяся область
class CustomScrollArea(QScrollArea):
    def __init__(self, root):
        super().__init__(root)
        self.setWidgetResizable(True)

        self.elements = QWidget()
        self.setWidget(self.elements)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.layout = QVBoxLayout(self.elements)
        self.layout.setAlignment(Qt.AlignTop)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(1)
        self.elements.setLayout(self.layout)