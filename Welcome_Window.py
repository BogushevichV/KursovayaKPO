from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                               QPushButton, QVBoxLayout, QHBoxLayout)
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt, Signal


class WelcomeWindow(QMainWindow):
    user_login_requested = Signal()
    admin_login_requested = Signal()

    def __init__(self):
        super().__init__()

        # Настройка главного окна
        self.setWindowTitle("Exam Record")
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: White;")

        # Создаем центральный виджет и основной макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Приветственная фраза
        welcome_label = QLabel("Добро пожаловать!")
        welcome_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Загрузка и отображение картинки
        image_label = QLabel()
        pixmap = QPixmap("WelcomeIcon.png")  # Укажите путь к вашему изображению

        # Если изображение не загружено, используем заглушку
        if pixmap.isNull():
            pixmap = QPixmap(400, 200)
            pixmap.fill(Qt.GlobalColor.lightGray)
            text_painter = QPainter(pixmap)
            text_painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Welcome Image")
            text_painter.end()

        image_label.setPixmap(pixmap.scaled(500, 280, Qt.AspectRatioMode.KeepAspectRatio))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Создаем кнопки
        user_button = QPushButton("Войти как пользователь")
        admin_button = QPushButton("Войти как администратор")

        # Настройка стилей кнопок
        button_style = """
            QPushButton {
                min-width: 200px;
                min-height: 40px;
                font-size: 16px;
                border-radius: 5px;
                background-color: #4CAF50;  /* Зеленый */
                color: white;
                border: 2px solid #45a049;
            }
            QPushButton:hover {
                background-color: #388038;
            }
        """
        user_button.setStyleSheet(button_style)
        admin_button.setStyleSheet(button_style + "background-color: #ffcccc;")

        # Подключаем обработчики нажатий
        user_button.clicked.connect(self._handle_user_login)
        admin_button.clicked.connect(self._handle_admin_login)

        # Горизонтальный макет для кнопок
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(user_button)
        buttons_layout.addWidget(admin_button)
        buttons_layout.setSpacing(30)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Добавляем все элементы в основной макет
        main_layout.addWidget(welcome_label)
        main_layout.addSpacing(20)
        main_layout.addWidget(image_label)
        main_layout.addSpacing(30)
        main_layout.addLayout(buttons_layout)

    def _handle_user_login(self):
        self.user_login_requested.emit()
        self.close()

    def _handle_admin_login(self):
        self.admin_login_requested.emit()
        self.close()
