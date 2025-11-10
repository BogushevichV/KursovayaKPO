from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox)

from Examination_Report_App import GradeBookApp

class UserWindow(QMainWindow):
    def __init__(self, db_authenticator, welcome_window, parent=None):
        super().__init__(parent)
        self.grade_book = None
        self.login_button = None
        self.password_input = None
        self.password_label = None
        self.login_input = None
        self.login_label = None
        self.setObjectName("window")
        self.setStyleSheet("#window{background-color: White;}")
        self.db_auth = db_authenticator
        self.welcome_window = welcome_window
        self.login_attempts = 5
        self.initUI()

    def initUI(self):
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

        self.setWindowTitle("Вход пользователя")
        self.setFixedSize(400, 300)

        # Основной контейнер
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрирование по вертикали

        # Контейнер формы
        form_container = QWidget()
        form_container.setFixedSize(350, 250)  # Чуть меньше основного окна
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(30, 30, 30, 30)  # Внутренние отступы

        # Настройка элементов
        self.login_label = QLabel("Логин пользователя:")
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.setFixedHeight(35)

        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(35)

        # >>>>>>>>>>> Потом убрать
        self.login_input.setText("user")
        self.password_input.setText("123")
        # >>>>>>>>>>>>

        self.login_button = QPushButton("Войти")
        self.login_button.setStyleSheet(button_style)
        self.login_button.clicked.connect(self.check_credentials)


        self.login_input.returnPressed.connect(self.check_credentials)
        self.password_input.returnPressed.connect(self.check_credentials)

        # Добавление элементов в форму
        form_layout.addWidget(self.login_label)
        form_layout.addWidget(self.login_input)
        form_layout.addWidget(self.password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Добавляем форму в основной контейнер
        main_layout.addWidget(form_container)

        # Установка objectName для стилизации
        self.login_label.setObjectName("login_label")
        self.password_label.setObjectName("password_label")
        self.login_input.setObjectName("login_input")
        self.password_input.setObjectName("password_input")
        form_container.setObjectName("form_container")

        # Стилизация
        form_container.setStyleSheet("""
            QWidget#form_container {
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #dee2e6;
            }
            QLineEdit {
                color: black;
                background-color: white;
                padding: 5px 10px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            QLabel {
                color: black;
                background: transparent;
                border: none;
                font-size: 14px;
            }
        """)

    def check_credentials(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        try:
            is_authenticated = self.db_auth.authenticate_user(login, password)

            if is_authenticated:
                self.open_grade_book()
            else:
                self.handle_failed_login()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка аутентификации",
                f"Произошла ошибка при проверке учетных данных:\n{str(e)}"
            )

    def open_grade_book(self):
        """Открывает окно с журналом успеваемости"""
        self.grade_book = GradeBookApp()
        self.grade_book.set_welcome_window(self.welcome_window)  # Передаем welcome_window
        self.hide()  # Скрываем текущее окно
        self.grade_book.show()

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.welcome_window:
            self.welcome_window.show()
        event.accept()

    def handle_failed_login(self):
        self.login_attempts -= 1
        if self.login_attempts > 0:
            QMessageBox.warning(
                self,
                "Ошибка входа",
                f"Неверные данные! Осталось попыток: {self.login_attempts}"
            )
        else:
            QMessageBox.critical(
                self,
                "Доступ запрещен",
                "Превышено количество попыток входа!"
            )
            self.close()
