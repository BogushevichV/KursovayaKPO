import sys
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout, QHBoxLayout,
                               QGridLayout, QSizePolicy)
from PySide6.QtCore import Qt
from Client.Front.Styles.Admin_Window_Styles import BUTTON_STYLE, BACK_BUTTON_STYLE, form_style, LOGIN_FORM_STYLE
from Client.Front.admin_lists_widgets import create_list
from Client.Back.admin_controller import (send_admin_data, delete_subject, delete_group,
                                          delete_exam, delete_student, add_new_admin,
                                          add_new_user, send_user_data, check_credentials,
                                          delete_user, delete_admin)

# Добавляем путь для импорта конфига
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Client.Back.client_requests import DatabaseServerClient
from Client.Source.config import SERVER_URL

class AdminWindow(QMainWindow):
    def __init__(self, db_authenticator, account_manager, welcome_window, parent=None, signals=None):
        super().__init__(parent)

        self.admin_scroll_list = None
        self.user_scroll_list = None
        self.subject_scroll_list = None
        self.group_scroll_list = None
        self.exam_scroll_list = None
        self.student_scroll_list = None

        self.admin_list = None
        self.user_list = None
        self.subject_list = None
        self.group_list = None
        self.exam_list = None
        self.student_list = None

        self.admin_list_layout = None
        self.user_list_layout = None
        self.subject_list_layout = None
        self.group_list_layout = None
        self.exam_list_layout = None
        self.student_list_layout = None

        self.grid_left_widget = None
        self.grid_right_widget = None

        self.add_admin_sect = None
        self.del_admin_sect = None
        self.add_user_sect = None
        self.del_user_sect = None

        self.del_subject_sect = None
        self.del_group_sect = None
        self.del_exam_sect = None
        self.del_student_sect = None

        self.back_button = None
        self.signals = signals
        self.db_auth = db_authenticator
        self.account_manager = account_manager
        self.welcome_window = welcome_window
        self.login_attempts = 5
        # Клиент для запросов к серверу для операций удаления
        self.db_client = DatabaseServerClient(server_url=SERVER_URL)

        # Настройки SMTP (замените на свои)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = "examinationreportbntu@gmail.com"
        self.smtp_password = "quqv ypik iktl illl"

        self._init_ui_elements()
        self.setWindowTitle(self.tr("Панель администратора"))
        self.setObjectName("window")
        self.setStyleSheet("#window{background-color: White;}")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.del_subject_label = QLabel()
        self.del_subject_input = QLineEdit()
        self.del_subject_button = QPushButton()

        self.del_group_label = QLabel()
        self.del_group_input = QLineEdit()
        self.del_group_button = QPushButton()

        self.del_exam_label = QLabel()
        self.del_exam_input = QLineEdit()
        self.del_exam_button = QPushButton()

        self.del_student_label = QLabel()
        self.del_student_input = QLineEdit()
        self.del_student_button = QPushButton()

        self.setup_login_ui()

        if self.signals:
            self.signals.language_changed.connect(self.retranslateUi)

    def _init_ui_elements(self):
        # Для авторизации
        self.login_label = QLabel()
        self.login_input = QLineEdit()
        self.password_label = QLabel()
        self.password_input = QLineEdit()
        self.login_button = QPushButton()

        # Для добавления администратора
        self.admin_login_label = QLabel()
        self.admin_login_input = QLineEdit()
        self.admin_password_label = QLabel()
        self.admin_password_input = QLineEdit()
        self.admin_email_label = QLabel()
        self.admin_email_input = QLineEdit()
        self.add_admin_button = QPushButton()
        self.send_admin_button = QPushButton()

        # Для добавления пользователя
        self.user_login_label = QLabel()
        self.user_login_input = QLineEdit()
        self.user_password_label = QLabel()
        self.user_password_input = QLineEdit()
        self.user_email_label = QLabel()
        self.user_email_input = QLineEdit()
        self.add_user_button = QPushButton()
        self.send_button = QPushButton()

        # Для удаления
        self.del_user_login_label = QLabel()
        self.del_user_login_input = QLineEdit()
        self.del_user_button = QPushButton()
        self.del_admin_login_label = QLabel()
        self.del_admin_login_input = QLineEdit()
        self.del_admin_button = QPushButton()

        # Управление записями БД
        self.del_subject_label = QLabel()
        self.del_subject_input = QLineEdit()
        self.del_subject_button = QPushButton()

        self.del_group_label = QLabel()
        self.del_group_input = QLineEdit()
        self.del_group_button = QPushButton()

        self.del_exam_label = QLabel()
        self.del_exam_input = QLineEdit()
        self.del_exam_button = QPushButton()

        self.del_student_label = QLabel()
        self.del_student_input = QLineEdit()
        self.del_student_button = QPushButton()

    def setup_login_ui(self):
        self._clear_layout()

        # Создаем основной контейнер с вертикальным выравниванием
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрирование по вертикали

        # Создаем контейнер для формы входа
        form_container = QWidget()
        form_container.setFixedSize(400, 300)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(30, 30, 30, 30)  # Добавляем отступы вокруг формы

        # Настройка элементов
        self.login_label.setText(self.tr("Логин администратора:"))
        self.password_label.setText(self.tr("Пароль:"))

        self.login_input.setPlaceholderText(self.tr("Введите логин"))
        self.login_input.setFixedHeight(35)  # Фиксированная высота
        self.password_input.setPlaceholderText(self.tr("Введите пароль"))
        self.password_input.setFixedHeight(35)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button.setText(self.tr("Войти"))

        self.login_button.clicked.connect(lambda e: check_credentials(self))
        self.login_button.setStyleSheet(BUTTON_STYLE)
        self.login_button.setFixedWidth(200)  # Фиксированная ширина кнопки

        self.login_input.returnPressed.connect(lambda e: check_credentials(self))
        self.password_input.returnPressed.connect(lambda e: check_credentials(self))

        # Добавляем элементы в форму
        form_layout.addWidget(self.login_label)
        form_layout.addWidget(self.login_input)
        form_layout.addWidget(self.password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_button, alignment=Qt.AlignmentFlag.AlignHCenter)  # Кнопка по центру

        # Добавляем форму в основной контейнер
        main_layout.addWidget(form_container)

        # Добавляем основной контейнер в центральный виджет
        self.main_layout.addWidget(main_container)

        self.login_label.setObjectName("login_label")
        self.password_label.setObjectName("password_label")
        self.login_input.setObjectName("login_input")
        self.password_input.setObjectName("password_input")
        form_container.setObjectName("form_container")

        # Стилизация для лучшего визуального восприятия
        form_container.setStyleSheet(LOGIN_FORM_STYLE)

    def return_to_welcome(self):
        """Возврат на начальное окно"""
        if self.welcome_window:
            self.welcome_window.show()
            self.deleteLater()  # Помечаем окно для удаления

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.welcome_window and self.welcome_window.isHidden():
            self.welcome_window.show()
        event.accept()

    def setup_admin_panel(self, admins, users, subjects, groups, exams, students):
        self._clear_layout()

        self.create_grid_left(admins, users)
        self.create_grid_right(subjects, groups, exams, students)

        # Кнопка Назад
        self.back_button = QPushButton(self.tr("Назад"))
        self.back_button.setFixedSize(100, 30)
        self.back_button.setStyleSheet(BACK_BUTTON_STYLE)
        self.back_button.clicked.connect(self.return_to_welcome)
        self.back_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        filler = QWidget()
        filler.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(filler)

        self.main_layout.insertWidget(0, button_container)

        self.showMaximized()

    def create_grid_left(self, admins, users):

        print("Создали Левую часть")
        # Блок Управление Учетными Записями

        if not self.grid_left_widget is None:
            print("Удалили Левую часть")
            self.grid_left_widget.deleteLater()

        self.grid_left_widget = QWidget()
        self.grid_left_widget.setObjectName("LeftGrid")
        self.grid_left_widget.setStyleSheet("#LeftGrid{background-color: #d4d4d4; border-radius: 30px;}")
        grid_left_layout = QGridLayout(self.grid_left_widget)

        title_left = QLabel(self.tr("Управление Учетными Записями"))
        title_left.setStyleSheet("font-size: 30px; font-weight: bold; color: black;")
        title_left.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_left_layout.addWidget(title_left, 0, 0, 1, 3)

        self.main_layout.insertWidget(0, self.grid_left_widget, 3)

        title = QLabel(self.tr("Администраторы"))
        title.setStyleSheet("font-size: 20px; margin: 5px; font-weight: bold; color: black;")
        grid_left_layout.addWidget(title, 1, 0, 1, 3)

        # Настройка виджетов для добавления администратора
        self.admin_login_label.setText(self.tr("Логин администратора:"))
        self.admin_login_input.setPlaceholderText(self.tr("Введите логин"))
        self.admin_login_input.setFixedHeight(35)
        self.admin_password_label.setText(self.tr("Пароль администратора:"))
        self.admin_password_input.setPlaceholderText(self.tr("Введите пароль"))
        self.admin_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.admin_password_input.setFixedHeight(35)
        self.admin_email_label.setText(self.tr("Электронная почта:"))
        self.admin_email_input.setPlaceholderText(self.tr("Введите электронную почту"))
        self.admin_email_input.setFixedHeight(35)

        # Кнопки добавления администратора
        self.add_admin_button.setText(self.tr("Добавить администратора"))
        self.add_admin_button.setStyleSheet(BUTTON_STYLE)
        self.add_admin_button.clicked.connect(lambda e: add_new_admin(self))

        self.send_admin_button.setText(self.tr("Отправить данные на почту"))
        self.send_admin_button.setStyleSheet(BUTTON_STYLE)
        self.send_admin_button.clicked.connect(lambda e: send_admin_data(self))

        self.add_admin_sect = create_section(self.tr("Добавить Админа"), (30, 0, 0, 30), [
            self.admin_login_label, self.admin_login_input,
            self.admin_password_label, self.admin_password_input,
            self.admin_email_label, self.admin_email_input,
            self.add_admin_button, self.send_admin_button
        ])

        grid_left_layout.addWidget(self.add_admin_sect, 2, 0, 1, 1)

        # Настройка виджетов для удаления администратора
        self.del_admin_login_label.setText(self.tr("Логин администратора:"))
        self.del_admin_login_input.setPlaceholderText(self.tr("Введите логин"))
        self.del_admin_login_input.setFixedHeight(35)

        self.del_admin_button.setText(self.tr("Удалить администратора"))
        self.del_admin_button.setStyleSheet(BUTTON_STYLE)
        self.del_admin_button.clicked.connect(lambda e: delete_admin(self))

        self.del_admin_sect = create_section(self.tr("Удалить Админа"), (0, 0, 0, 0), [
            self.del_admin_login_label, self.del_admin_login_input,
            self.del_admin_button
        ])

        grid_left_layout.addWidget(self.del_admin_sect, 2, 1, 1, 1)

        self.admin_list, self.admin_list_layout = create_section(self.tr("Список Админов"), (0, 30, 30, 0), is_list=True)
        grid_left_layout.addWidget(self.admin_list, 2, 2, 1, 1)

        self.admin_scroll_list = create_list(self.admin_list, self.admin_list_layout, admins, self.del_admin_login_input)

        title = QLabel(self.tr("Пользователи"))
        title.setStyleSheet("font-size: 20px; margin: 5px; font-weight: bold; color: black;")
        grid_left_layout.addWidget(title, 3, 0, 1, 3)

        # Настройка виджетов для добавления пользователя
        self.user_login_label.setText(self.tr("Логин пользователя:"))
        self.user_login_input.setPlaceholderText(self.tr("Введите логин"))
        self.user_login_input.setFixedHeight(35)
        self.user_password_label.setText(self.tr("Пароль пользователя:"))
        self.user_password_input.setPlaceholderText(self.tr("Введите пароль"))
        self.user_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.user_password_input.setFixedHeight(35)
        self.user_email_label.setText(self.tr("Электронная почта:"))
        self.user_email_input.setPlaceholderText(self.tr("Введите электронную почту"))
        self.user_email_input.setFixedHeight(35)

        # Кнопки добавления пользователя
        self.add_user_button.setText(self.tr("Добавить пользователя"))
        self.add_user_button.setStyleSheet(BUTTON_STYLE)
        self.add_user_button.clicked.connect(lambda e: add_new_user(self))

        self.send_button.setText(self.tr("Отправить данные на почту"))
        self.send_button.setStyleSheet(BUTTON_STYLE)
        self.send_button.clicked.connect(lambda e: send_user_data(self))

        self.add_user_sect = create_section(self.tr("Добавить Пользователя"), (30, 0, 0, 30), [
            self.user_login_label, self.user_login_input,
            self.user_password_label, self.user_password_input,
            self.user_email_label, self.user_email_input,
            self.add_user_button, self.send_button
        ])

        grid_left_layout.addWidget(self.add_user_sect, 4, 0, 1, 1)

        # Настройка виджетов для удаления пользователя
        self.del_user_login_label.setText(self.tr("Логин пользователя:"))
        self.del_user_login_input.setPlaceholderText(self.tr("Введите логин"))
        self.del_user_login_input.setFixedHeight(35)

        self.del_user_button.setText(self.tr("Удалить пользователя"))
        self.del_user_button.setStyleSheet(BUTTON_STYLE)
        self.del_user_button.clicked.connect(lambda: delete_user(self))

        self.del_user_sect = create_section(self.tr("Удалить Пользователя"), (0, 0, 0, 0), [
            self.del_user_login_label, self.del_user_login_input,
            self.del_user_button
        ])

        grid_left_layout.addWidget(self.del_user_sect, 4, 1, 1, 1)

        self.user_list, self.user_list_layout = create_section(self.tr("Список Пользователей"), (0, 30, 30, 0), is_list=True)
        grid_left_layout.addWidget(self.user_list, 4, 2, 1, 1)

        self.user_scroll_list = create_list(self.user_list, self.user_list_layout, users, self.del_user_login_input)

    def create_grid_right(self, subjects, groups, exams, students):
        print("Создали Правую часть")
        # Блок Управления записями БД

        if not self.grid_right_widget is None:
            print("Удалили Правую часть")

            self.grid_right_widget.deleteLater()

        self.grid_right_widget = QWidget()
        self.grid_right_widget.setObjectName("RightGrid")
        self.grid_right_widget.setStyleSheet("#RightGrid{background-color: #d4d4d4; border-radius: 30px;}")
        grid_right_layout = QGridLayout(self.grid_right_widget)

        self.main_layout.insertWidget(1, self.grid_right_widget, 2)

        title_right = QLabel(self.tr("Управление записями БД"))
        title_right.setStyleSheet("font-size: 30px; font-weight: bold; color: black;")
        title_right.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_right_layout.addWidget(title_right, 0, 0, 1, 2)

        title = QLabel(self.tr("Предметы"))
        title.setStyleSheet("font-size: 20px; margin: 5px; font-weight: bold; color: black;")
        grid_right_layout.addWidget(title, 1, 0, 1, 2)

        self.del_subject_label.setText(self.tr("Название предмета:"))
        self.del_subject_input.setPlaceholderText(self.tr("Введите название предмета"))
        self.del_subject_input.setFixedHeight(35)

        self.del_subject_button.setText(self.tr("Удалить предмет"))
        self.del_subject_button.setStyleSheet(BUTTON_STYLE)
        self.del_subject_button.clicked.connect(lambda e: delete_subject(self))

        self.del_subject_sect = create_section(self.tr("Удалить Предмет"), (30, 0, 0, 30), [
            self.del_subject_label, self.del_subject_input, self.del_subject_button
        ])

        grid_right_layout.addWidget(self.del_subject_sect, 2, 0, 1, 1)

        self.subject_list, self.subject_list_layout = create_section(self.tr("Список Предметов"), (0, 30, 30, 0), is_list=True)
        grid_right_layout.addWidget(self.subject_list, 2, 1, 1, 1)

        self.subject_scroll_list = create_list(self.subject_list, self.subject_list_layout, subjects, self.del_subject_input)

        title = QLabel(self.tr("Группы"))
        title.setStyleSheet("font-size: 20px; margin: 5px; font-weight: bold; color: black;")
        grid_right_layout.addWidget(title, 3, 0, 1, 2)

        self.del_group_label.setText(self.tr("Номер группы:"))
        self.del_group_input.setPlaceholderText(self.tr("Введите номер группы"))
        self.del_group_input.setFixedHeight(35)

        self.del_group_button.setText(self.tr("Удалить группу"))
        self.del_group_button.setStyleSheet(BUTTON_STYLE)
        self.del_group_button.clicked.connect(lambda e: delete_group(self))

        self.del_group_sect = create_section(self.tr("Удалить Группу"), (30, 0, 0, 30), [
            self.del_group_label, self.del_group_input, self.del_group_button
        ])

        grid_right_layout.addWidget(self.del_group_sect, 4, 0, 1, 1)

        self.group_list, self.group_list_layout = create_section(self.tr("Список Групп"), (0, 30, 30, 0), is_list=True)
        grid_right_layout.addWidget(self.group_list, 4, 1, 1, 1)

        self.group_scroll_list = create_list(self.group_list, self.group_list_layout, groups, self.del_group_input)

        title = QLabel(self.tr("Экзамены"))
        title.setStyleSheet("font-size: 20px; margin: 5px; font-weight: bold; color: black;")
        grid_right_layout.addWidget(title, 5, 0, 1, 2)

        self.del_exam_label.setText(self.tr("ID экзамена:"))
        self.del_exam_input.setPlaceholderText(self.tr("Введите ID экзамена"))
        self.del_exam_input.setFixedHeight(35)

        self.del_exam_button.setText(self.tr("Удалить экзамен"))
        self.del_exam_button.setStyleSheet(BUTTON_STYLE)
        self.del_exam_button.clicked.connect(lambda e: delete_exam(self))

        self.del_exam_sect = create_section(self.tr("Удалить Экзамен"), (30, 0, 0, 30), [
            self.del_exam_label, self.del_exam_input, self.del_exam_button
        ])

        grid_right_layout.addWidget(self.del_exam_sect, 6, 0, 1, 1)

        self.exam_list, self.exam_list_layout = create_section(self.tr("Список Экзаменов"), (0, 30, 30, 0), is_list=True)
        grid_right_layout.addWidget(self.exam_list, 6, 1, 1, 1)

        self.exam_scroll_list = create_list(self.exam_list, self.exam_list_layout, exams, self.del_exam_input)

        title = QLabel(self.tr("Студенты"))
        title.setStyleSheet("font-size: 20px; margin: 5px; font-weight: bold; color: black;")
        grid_right_layout.addWidget(title, 7, 0, 1, 2)

        self.del_student_label.setText(self.tr("ID студента:"))
        self.del_student_input.setPlaceholderText(self.tr("Введите ID студента"))
        self.del_student_input.setFixedHeight(35)

        self.del_student_button.setText(self.tr("Удалить студента"))
        self.del_student_button.setStyleSheet(BUTTON_STYLE)
        self.del_student_button.clicked.connect(lambda e: delete_student(self))

        self.del_student_sect = create_section(self.tr("Удалить Студента"), (30, 0, 0, 30), [
            self.del_student_label, self.del_student_input, self.del_student_button
        ])

        grid_right_layout.addWidget(self.del_student_sect, 8, 0, 1, 1)

        self.student_list, self.student_list_layout = create_section(self.tr("Список Студентов"), (0, 30, 30, 0), is_list=True)
        grid_right_layout.addWidget(self.student_list, 8, 1, 1, 1)

        self.student_scroll_list = create_list(self.student_list, self.student_list_layout, students, self.del_student_input)

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Панель администратора"))
        self.login_label.setText(self.tr("Логин администратора:"))
        self.password_label.setText(self.tr("Пароль:"))
        self.login_input.setPlaceholderText(self.tr("Введите логин"))
        self.password_input.setPlaceholderText(self.tr("Введите пароль"))
        self.login_button.setText(self.tr("Войти"))
        self.admin_login_label.setText(self.tr("Логин администратора:"))
        self.admin_login_input.setPlaceholderText(self.tr("Введите логин"))
        self.admin_password_label.setText(self.tr("Пароль администратора:"))
        self.admin_password_input.setPlaceholderText(self.tr("Введите пароль"))
        self.admin_email_label.setText(self.tr("Электронная почта:"))
        self.admin_email_input.setPlaceholderText(self.tr("Введите электронную почту"))
        self.add_admin_button.setText(self.tr("Добавить администратора"))
        self.send_admin_button.setText(self.tr("Отправить данные на почту"))
        self.user_login_label.setText(self.tr("Логин пользователя:"))
        self.user_login_input.setPlaceholderText(self.tr("Введите логин"))
        self.user_password_label.setText(self.tr("Пароль пользователя:"))
        self.user_password_input.setPlaceholderText(self.tr("Введите пароль"))
        self.user_email_label.setText(self.tr("Электронная почта:"))
        self.user_email_input.setPlaceholderText(self.tr("Введите электронную почту"))
        self.add_user_button.setText(self.tr("Добавить пользователя"))
        self.send_button.setText(self.tr("Отправить данные на почту"))
        self.del_user_login_label.setText(self.tr("Логин пользователя:"))
        self.del_user_login_input.setPlaceholderText(self.tr("Введите логин"))
        self.del_user_button.setText(self.tr("Удалить пользователя"))
        self.del_admin_login_label.setText(self.tr("Логин администратора:"))
        self.del_admin_login_input.setPlaceholderText(self.tr("Введите логин"))
        self.del_admin_button.setText(self.tr("Удалить администратора"))
        self.del_subject_label.setText(self.tr("Название предмета:"))
        self.del_subject_input.setPlaceholderText(self.tr("Введите название предмета"))
        self.del_subject_button.setText(self.tr("Удалить предмет"))
        self.del_group_label.setText(self.tr("Номер группы:"))
        self.del_group_input.setPlaceholderText(self.tr("Введите номер группы"))
        self.del_group_button.setText(self.tr("Удалить группу"))
        self.del_exam_label.setText(self.tr("ID экзамена:"))
        self.del_exam_input.setPlaceholderText(self.tr("Введите ID экзамена"))
        self.del_exam_button.setText(self.tr("Удалить экзамен"))
        self.del_student_label.setText(self.tr("ID студента:"))
        self.del_student_input.setPlaceholderText(self.tr("Введите ID студента"))
        self.del_student_button.setText(self.tr("Удалить студента"))
        self.back_button = QPushButton(self.tr("Назад"))
        self.del_admin_sect.setTitle(self.tr("Управление Учетными Записями"))

    def _clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

# Универсальный метод создания секции
def create_section(title_text, radius, widgets=None, is_list=False):
    container = QWidget()
    container.setStyleSheet(form_style(radius))
    layout = QVBoxLayout(container)
    layout.setSpacing(10)
    layout.setContentsMargins(20, 20, 20, 20)

    title = QLabel(title_text)
    title.setStyleSheet("font-size: 16px; font-weight: bold;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)

    if not is_list:
        for widget in widgets:
            layout.addWidget(widget)

        layout.addStretch()
        container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        return container
    else:
        return container, layout
