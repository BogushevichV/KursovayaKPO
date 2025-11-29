from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                               QPushButton, QVBoxLayout, QHBoxLayout, QComboBox)
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt, Signal, QCoreApplication, QTranslator


class WelcomeWindow(QMainWindow):
    user_login_requested = Signal()
    admin_login_requested = Signal()
    language_changed = Signal(str)  # добавили сигнал

    def __init__(self, current_lang="ru", signals=None):
        super().__init__()

        self.signals = signals

        self.setWindowTitle("Exam Report")
        self.setFixedSize(700, 500)
        self.setStyleSheet("background-color: white;")

        # === Центральный виджет и основной макет ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # === Выпадающий список выбора языка ===
        self.language_box = QComboBox()
        self.language_box.addItem("Русский", "ru")
        self.language_box.addItem("English", "en")
        self.language_box.addItem("中文 (Chinese)", "zh")
        index = self.language_box.findData(current_lang)

        if index == -1:
            index = 0

        self.language_box.setCurrentIndex(index)

        self.language_box.currentIndexChanged.connect(self._emit_language_change)

        if self.signals:
            self.signals.language_changed.connect(self.retranslateUi)

        # Стиль, как у кнопок
        combo_style = """
            QComboBox {
                min-width: 150px;
                min-height: 36px;
                font-size: 16px;
                border-radius: 5px;
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                padding-left: 10px;
            }
            QComboBox:hover {
                background-color: #388038;
            }
            QComboBox::drop-down {
                width: 25px;
                border: none;
                background-color: transparent;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                border-radius: 5px;
                selection-background-color: #4CAF50;
                selection-color: white;
            }
        """
        self.language_box.setStyleSheet(combo_style)

        # Правый верхний угол
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()
        lang_layout.addWidget(self.language_box)

        main_layout.addLayout(lang_layout)

        # === Приветствие ===
        self.welcome_label = QLabel(self.tr("Добро пожаловать!"))
        self.welcome_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # === Картинка ===
        self.image_label = QLabel()
        pixmap = QPixmap("WelcomeIcon.png")

        if pixmap.isNull():
            pixmap = QPixmap(400, 200)
            pixmap.fill(Qt.GlobalColor.lightGray)
            painter = QPainter(pixmap)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Welcome Image")
            painter.end()

        self.image_label.setPixmap(pixmap.scaled(500, 280, Qt.AspectRatioMode.KeepAspectRatio))
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # === Кнопки ===
        self.user_button = QPushButton(self.tr("Войти как пользователь"))
        self.admin_button = QPushButton(self.tr("Войти как администратор"))

        button_style = """
            QPushButton {
                min-width: 200px;
                min-height: 40px;
                font-size: 16px;
                border-radius: 5px;
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
            }
            QPushButton:hover {
                background-color: #388038;
            }
        """
        self.user_button.setStyleSheet(button_style)
        self.admin_button.setStyleSheet(button_style + "background-color: #ff6666; border: 2px solid #e65c5c;")

        self.user_button.clicked.connect(self._handle_user_login)
        self.admin_button.clicked.connect(self._handle_admin_login)

        # === Макет кнопок ===
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.user_button)
        buttons_layout.addWidget(self.admin_button)
        buttons_layout.setSpacing(30)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # === Добавляем всё ===
        main_layout.addWidget(self.welcome_label)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.image_label)
        main_layout.addSpacing(30)
        main_layout.addLayout(buttons_layout)

        # === Переводчик ===
        self.translator = QTranslator()
        self.current_lang = "ru"

    # === Остальные методы ===
    def _handle_user_login(self):
        self.user_login_requested.emit()
        self.close()

    def _handle_admin_login(self):
        self.admin_login_requested.emit()
        self.close()

    def _emit_language_change(self):
        lang_code = self.language_box.currentData()
        self.language_changed.emit(lang_code)


    def retranslateUi(self):
        self.welcome_label.setText(self.tr("Добро пожаловать!"))
        self.user_button.setText(self.tr("Войти как пользователь"))
        self.admin_button.setText(self.tr("Войти как администратор"))

