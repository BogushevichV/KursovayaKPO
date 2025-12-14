import smtplib
import re
from email.mime.text import MIMEText
from email.utils import formatdate
import sys
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout, QHBoxLayout,
                               QMessageBox, QGridLayout, QSizePolicy,
                               QScrollArea)
from PySide6.QtCore import Qt
from Client.Front.Styles.Admin_Window_Styles import BUTTON_STYLE, form_style, LOGIN_FORM_STYLE

# Добавляем путь для импорта конфига
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Client.Back.client_requests import DatabaseServerClient
from Client.Source.config import SERVER_URL

email_regex = re.compile(
    r'^[a-zA-Zа-яА-ЯёЁ0-9._%+-]+@[a-zA-Zа-яА-ЯёЁ0-9.-]+\.[a-zA-Zа-яА-ЯёЁ]{2,}$'
)

def is_valid_email(email):
    return bool(email_regex.match(email))

class AdminWindow(QMainWindow):
    def __init__(self, db_authenticator, account_manager, welcome_window, parent=None, signals=None):
        super().__init__(parent)
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

        self.showMaximized()

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
        # >>>>>>>>>>> Потом убрать
        self.login_input.setText("login")
        self.password_input.setText("123")
        # >>>>>>>>>>>>

        self.login_button.clicked.connect(self.check_credentials)
        self.login_button.setStyleSheet(BUTTON_STYLE)
        self.login_button.setFixedWidth(200)  # Фиксированная ширина кнопки

        self.login_input.returnPressed.connect(self.check_credentials)
        self.password_input.returnPressed.connect(self.check_credentials)

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
        self.back_button.setStyleSheet(BUTTON_STYLE)
        self.back_button.clicked.connect(self.return_to_welcome)

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.addStretch()
        button_layout.addWidget(self.back_button)

        self.main_layout.addWidget(button_container)

    def create_grid_left(self, admins, users):
        # Блок Управление Учетными Записями

        if not self.grid_left_widget is None:
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
        self.add_admin_button.clicked.connect(self.add_new_admin)

        self.send_admin_button.setText(self.tr("Отправить данные на почту"))
        self.send_admin_button.setStyleSheet(BUTTON_STYLE)
        self.send_admin_button.clicked.connect(self.send_admin_data)

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
        self.del_admin_button.clicked.connect(self.delete_admin)

        self.del_admin_sect = create_section(self.tr("Удалить Админа"), (0, 0, 0, 0), [
            self.del_admin_login_label, self.del_admin_login_input,
            self.del_admin_button
        ])

        grid_left_layout.addWidget(self.del_admin_sect, 2, 1, 1, 1)

        admin_list, admin_list_layout = create_section(self.tr("Список Админов"), (0, 30, 30, 0), is_list=True)
        grid_left_layout.addWidget(admin_list, 2, 2, 1, 1)

        create_list(admin_list, admin_list_layout, admins, self.del_admin_login_input)

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
        self.add_user_button.clicked.connect(self.add_new_user)

        self.send_button.setText(self.tr("Отправить данные на почту"))
        self.send_button.setStyleSheet(BUTTON_STYLE)
        self.send_button.clicked.connect(self.send_user_data)

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
        self.del_user_button.clicked.connect(self.delete_user)

        self.del_user_sect = create_section(self.tr("Удалить Пользователя"), (0, 0, 0, 0), [
            self.del_user_login_label, self.del_user_login_input,
            self.del_user_button
        ])

        grid_left_layout.addWidget(self.del_user_sect, 4, 1, 1, 1)

        user_list, user_list_layout = create_section(self.tr("Список Пользователей"), (0, 30, 30, 0), is_list=True)
        grid_left_layout.addWidget(user_list, 4, 2, 1, 1)

        create_list(user_list, user_list_layout, users, self.del_user_login_input)

    def create_grid_right(self, subjects, groups, exams, students):
        # Блок Управления записями БД

        if not self.grid_right_widget is None:
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
        self.del_subject_button.clicked.connect(self.delete_subject)

        self.del_subject_sect = create_section(self.tr("Удалить Предмет"), (30, 0, 0, 30), [
            self.del_subject_label, self.del_subject_input, self.del_subject_button
        ])

        grid_right_layout.addWidget(self.del_subject_sect, 2, 0, 1, 1)

        subject_list, subject_list_layout = create_section(self.tr("Список Предметов"), (0, 30, 30, 0), is_list=True)
        grid_right_layout.addWidget(subject_list, 2, 1, 1, 1)

        create_list(subject_list, subject_list_layout, subjects, self.del_subject_input)

        title = QLabel(self.tr("Группы"))
        title.setStyleSheet("font-size: 20px; margin: 5px; font-weight: bold; color: black;")
        grid_right_layout.addWidget(title, 3, 0, 1, 2)

        self.del_group_label.setText(self.tr("Номер группы:"))
        self.del_group_input.setPlaceholderText(self.tr("Введите номер группы"))
        self.del_group_input.setFixedHeight(35)

        self.del_group_button.setText(self.tr("Удалить группу"))
        self.del_group_button.setStyleSheet(BUTTON_STYLE)
        self.del_group_button.clicked.connect(self.delete_group)

        self.del_group_sect = create_section(self.tr("Удалить Группу"), (30, 0, 0, 30), [
            self.del_group_label, self.del_group_input, self.del_group_button
        ])

        grid_right_layout.addWidget(self.del_group_sect, 4, 0, 1, 1)

        group_list, group_list_layout = create_section(self.tr("Список Групп"), (0, 30, 30, 0), is_list=True)
        grid_right_layout.addWidget(group_list, 4, 1, 1, 1)

        create_list(group_list, group_list_layout, groups, self.del_group_input)

        title = QLabel(self.tr("Экзамены"))
        title.setStyleSheet("font-size: 20px; margin: 5px; font-weight: bold; color: black;")
        grid_right_layout.addWidget(title, 5, 0, 1, 2)

        self.del_exam_label.setText(self.tr("ID экзамена:"))
        self.del_exam_input.setPlaceholderText(self.tr("Введите ID экзамена"))
        self.del_exam_input.setFixedHeight(35)

        self.del_exam_button.setText(self.tr("Удалить экзамен"))
        self.del_exam_button.setStyleSheet(BUTTON_STYLE)
        self.del_exam_button.clicked.connect(self.delete_exam)

        self.del_exam_sect = create_section(self.tr("Удалить Экзамен"), (30, 0, 0, 30), [
            self.del_exam_label, self.del_exam_input, self.del_exam_button
        ])

        grid_right_layout.addWidget(self.del_exam_sect, 6, 0, 1, 1)

        exam_list, exam_list_layout = create_section(self.tr("Список Экзаменов"), (0, 30, 30, 0), is_list=True)
        grid_right_layout.addWidget(exam_list, 6, 1, 1, 1)

        create_list(exam_list, exam_list_layout, exams, self.del_exam_input)

        title = QLabel(self.tr("Студенты"))
        title.setStyleSheet("font-size: 20px; margin: 5px; font-weight: bold; color: black;")
        grid_right_layout.addWidget(title, 7, 0, 1, 2)

        self.del_student_label.setText(self.tr("ID студента:"))
        self.del_student_input.setPlaceholderText(self.tr("Введите ID студента"))
        self.del_student_input.setFixedHeight(35)

        self.del_student_button.setText(self.tr("Удалить студента"))
        self.del_student_button.setStyleSheet(BUTTON_STYLE)
        self.del_student_button.clicked.connect(self.delete_student)

        self.del_student_sect = create_section(self.tr("Удалить Студента"), (30, 0, 0, 30), [
            self.del_student_label, self.del_student_input, self.del_student_button
        ])

        grid_right_layout.addWidget(self.del_student_sect, 8, 0, 1, 1)

        student_list, student_list_layout = create_section(self.tr("Список Студентов"), (0, 30, 30, 0), is_list=True)
        grid_right_layout.addWidget(student_list, 8, 1, 1, 1)

        create_list(student_list, student_list_layout, students, self.del_student_input)

    def send_admin_data(self):
        login = self.admin_login_input.text()
        password = self.admin_password_input.text()
        email = self.admin_email_input.text()

        if not all([login, password, email]):
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Все поля должны быть заполнены!"))
            return

        if not is_valid_email(email):
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Введите корректный email!"))
            return

        try:
            # Формируем сообщение
            email_body = (
                f"Ваши административные данные:\n\n"
                f"Логин: {login}\n"
                f"Пароль: {password}\n\n"
                f"Сохраните эти данные в надежном месте."
            )

            if self.send_email(email, "Ваши данные администратора", email_body):
                QMessageBox.information(
                    self,
                    self.tr("Успех"),
                    self.tr(f"Данные администратора отправлены на {email}")
                )

            else:
                QMessageBox.warning(
                    self,
                    self.tr("Ошибка"),
                    self.tr("Не удалось отправить данные на указанный email")
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Ошибка"),
                self.tr(f"Произошла ошибка при отправке данных:\n{str(e)}")
            )

    def delete_subject(self):
        subject_name = self.del_subject_input.text()
        if not subject_name:
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Введите название предмета"))
            return

        # Подтверждение удаления
        reply = QMessageBox.question(
            self,
            self.tr("Подтверждение удаления"),
            self.tr(
                f'Вы уверены, что хотите удалить предмет "{subject_name}" и все связанные данные (экзамены, оценки)?'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            success = self.db_client.delete_subject(subject_name)
            
            if success:
                QMessageBox.information(
                    self,
                    self.tr("Успех"),
                    self.tr(f"Предмет '{subject_name}' и все связанные данные успешно удалены!")
                )

                subjects = []
                groups = []
                exams = []
                students = []

                self.create_grid_right(subjects, groups, exams, students)
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Ошибка"),
                    self.tr(f"Предмет '{subject_name}' не найден")
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Ошибка базы данных"),
                self.tr(f"Произошла ошибка при удалении предмета:\n{str(e)}")
            )

    def delete_group(self):
        group_name = self.del_group_input.text()
        if not group_name:
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Введите номер группы"))
            return

        reply = QMessageBox.question(
            self,
            self.tr('Подтверждение удаления'),
            self.tr(f'Вы уверены, что хотите удалить группу "{group_name}" и всех её студентов?'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            success = self.db_client.delete_group(group_name)
            
            if success:
                QMessageBox.information(
                    self,
                    self.tr("Успех"),
                    self.tr(f"Группа '{group_name}' и все связанные данные успешно удалены!")
                )
                # Получаем эти обновлённые списки
                subjects = []
                groups = []
                exams = []
                students = []

                self.create_grid_right(subjects, groups, exams, students)
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Ошибка"),
                    self.tr(f"Группа '{group_name}' не найдена")
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Ошибка базы данных"),
                self.tr(f"Произошла ошибка при удалении группы:\n{str(e)}")
            )

    def delete_exam(self):
        exam_id = self.del_exam_input.text()
        if not exam_id:
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Введите ID экзамена"))
            return

        reply = QMessageBox.question(
            self,
            self.tr('Подтверждение удаления'),
            self.tr(f'Вы уверены, что хотите удалить экзамен с ID {exam_id} и все оценки по нему?'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # Преобразуем exam_id в int
            try:
                exam_id_int = int(exam_id)
            except ValueError:
                QMessageBox.warning(self, self.tr("Ошибка"), self.tr("ID экзамена должен быть числом"))
                return

            # Отправляем запрос на сервер для удаления экзамена
            success = self.db_client.delete_exam(exam_id_int)
            
            if success:
                QMessageBox.information(
                    self,
                    self.tr("Успех"),
                    self.tr(f"Экзамен с ID {exam_id} и все оценки по нему успешно удалены!")
                )
                # Получаем эти обновлённые списки
                subjects = []
                groups = []
                exams = []
                students = []

                self.create_grid_right(subjects, groups, exams, students)
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Ошибка"),
                    self.tr(f"Экзамен с ID {exam_id} не найден")
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Ошибка базы данных"),
                self.tr(f"Произошла ошибка при удалении экзамена:\n{str(e)}")
            )

    def delete_student(self):
        student_id = self.del_student_input.text()
        if not student_id:
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Введите ID студента"))
            return

        reply = QMessageBox.question(
            self,
            self.tr("Подтверждение удаления"),
            self.tr(f"Вы уверены, что хотите удалить студента с ID {student_id} и все его оценки?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            try:
                student_id_int = int(student_id)
            except ValueError:
                QMessageBox.warning(self, self.tr("Ошибка"), self.tr("ID студента должен быть числом"))
                return


            success = self.db_client.delete_student(student_id_int)      
            if success:
                QMessageBox.information(
                    self,
                    self.tr("Успех"),
                    self.tr(f"Студент с ID {student_id} и все его оценки успешно удалены!")
                )

                # Получаем эти обновлённые списки
                subjects = []
                groups = []
                exams = []
                students = []

                self.create_grid_right(subjects, groups, exams, students)
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Ошибка"),
                    self.tr(f"Студент с ID {student_id} не найден")
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Ошибка базы данных"),
                self.tr(f"Произошла ошибка при удалении студента:\n{str(e)}")
            )

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Date'] = formatdate(localtime=True)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.smtp_username, [to_email], msg.as_string())
            return True
        except smtplib.SMTPAuthenticationError:
            print("Ошибка аутентификации SMTP")
            return False
        except smtplib.SMTPException as e:
            print(f"Ошибка SMTP: {e}")
            return False
        except Exception as e:
            print(f"Общая ошибка при отправке email: {e}")
            return False

    def add_new_admin(self):
        login = self.admin_login_input.text()
        password = self.admin_password_input.text()
        email = self.admin_email_input.text()

        if not all([login, password, email]):
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Все поля должны быть заполнены!"))
            return

        if not is_valid_email(email):
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Введите корректный email!"))
            return

        try:
            success = self.account_manager.create_account("admin", login, password, email)
            if success:
                # Формируем и отправляем письмо с данными
                email_body = (
                    f"Данные для входа в административную панель:\n\n"
                    f"Логин: {login}\n"
                    f"Пароль: {password}\n\n"
                    f"Сохраните эти данные в надежном месте."
                )

                if self.send_email(email, "Ваши административные данные", email_body):
                    QMessageBox.information(
                        self,
                        self.tr("Успех"),
                        self.tr(f"Администратор {login} успешно добавлен!\nДанные для входа отправлены на {email}")
                    )

                else:
                    QMessageBox.warning(
                        self,
                        self.tr("Ошибка отправки"),
                        self.tr(f"Администратор {login} добавлен, но не удалось отправить данные на email!")
                    )

                    # Получаем эти обновлённые списки

                    admins = [
                    ]

                    users = [
                    ]

                    self.create_grid_left(admins, users)
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Ошибка"),
                    self.tr("Не удалось добавить администратора. Возможно, такой логин уже существует.")
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Ошибка базы данных"),
                self.tr(f"Произошла ошибка при добавлении администратора:\n{str(e)}")
            )

    def add_new_user(self):
        login = self.user_login_input.text()
        password = self.user_password_input.text()
        email = self.user_email_input.text()

        if not all([login, password, email]):
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Все поля должны быть заполнены!"))
            return

        if not is_valid_email(email):
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Введите корректный email!"))
            return

        try:
            success = self.account_manager.create_account("user", login, password, email)
            if success:
                QMessageBox.information(
                    self,
                    self.tr("Успех"),
                    self.tr(f"Пользователь {login} успешно добавлен!")
                )

                # Получаем эти обновлённые списки

                admins = [
                ]

                users = [
                ]

                self.create_grid_left(admins, users)
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Ошибка"),
                    self.tr("Не удалось добавить пользователя. Возможно, такой логин уже существует.")
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Ошибка базы данных"),
                self.tr(f"Произошла ошибка при добавлении пользователя:\n{str(e)}")
            )

    def send_user_data(self):
        login = self.user_login_input.text()
        password = self.user_password_input.text()
        email = self.user_email_input.text()

        if not all([login, password, email]):
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Все поля должны быть заполнены!"))
            return

        if not is_valid_email(email):
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Введите корректный email!"))
            return

        try:
            # Формируем сообщение
            email_body = (
                f"Ваши данные для входа в систему:\n\n"
                f"Логин: {login}\n"
                f"Пароль: {password}\n\n"
                f"Сохраните эти данные в надежном месте."
            )

            if self.send_email(email, "Ваши данные для входа", email_body):
                QMessageBox.information(
                    self,
                    self.tr("Успех"),
                    self.tr(f"Данные для входа отправлены на {email}")
                )

            else:
                QMessageBox.warning(
                    self,
                    self.tr("Ошибка"),
                    self.tr("Не удалось отправить данные на указанный email")
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Ошибка"),
                self.tr(f"Произошла ошибка при отправке данных:\n{str(e)}")
            )

    def check_credentials(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if not login or not password:
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Введите логин и пароль"))
            return

        try:
            is_authenticated = self.db_auth.authenticate_admin(login, password)

            admins = [
                ("login", "someemail@gmail.com"),
                ("ivan", "sjkfhsdjf@gmail.com"),
                ("slava", "skdfhsh@gmail.com"),
                ("kirill", "psdhuf@gmail.com"),
                ("vadim", "siduhfs@gmail.com")
            ]

            users = [
                ("login", "someemail@gmail.com"),
                ("ivan", "sjkfhsdjf@gmail.com"),
                ("slava", "skdfhsh@gmail.com"),
                ("kirill", "psdhuf@gmail.com"),
                ("vadim", "siduhfs@gmail.com")
            ]

            subjects = [
                ("Subj_1",),
                ("Subj_2",),
                ("Subj_3",),
                ("Subj_4",)
            ]

            groups = [
                ("123123",),
                ("234234",),
                ("123123",),
                ("234234",)
            ]

            exams = [
                ("1231",),
                ("2234",),
                ("1223",),
                ("2344",)
            ]

            students = [
                ("1231", "ФИО_1"),
                ("2234", "ФИО_2"),
                ("1223", "ФИО_3"),
                ("2344", "ФИО_4")
            ]

            if is_authenticated:
                self.setup_admin_panel(admins, users, subjects, groups, exams, students)
            else:
                self.handle_failed_login()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Ошибка аутентификации"),
                self.tr(f"Произошла ошибка при проверке учетных данных:\n{str(e)}")
            )

    def handle_failed_login(self):
        self.login_attempts -= 1
        if self.login_attempts > 0:
            QMessageBox.warning(
                self,
                self.tr("Ошибка входа"),
                self.tr(f"Неверные данные! Осталось попыток: {self.login_attempts}")
            )

        else:
            QMessageBox.critical(
                self,
                self.tr("Доступ запрещен"),
                self.tr("Превышено количество попыток входа!")
            )
            self.close()

    def delete_user(self):
        login = self.del_user_login_input.text()
        if not login:
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Введите логин пользователя"))
            return

        try:
            success = self.account_manager.delete_account("user", login)
            if success:
                QMessageBox.information(
                    self,
                    self.tr("Успех"),
                    self.tr(f"Пользователь {login} успешно удален!")
                )

                # Получаем эти обновлённые списки

                admins = [
                ]

                users = [
                ]

                self.create_grid_left(admins, users)
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Ошибка"),
                    self.tr(f"Пользователь {login} не найден или не удален.")
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Ошибка базы данных"),
                self.tr(f"Произошла ошибка при удалении пользователя:\n{str(e)}")
            )

    def delete_admin(self):
        login = self.del_admin_login_input.text()
        if not login:
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Введите логин администратора"))
            return

        try:
            success = self.account_manager.delete_account("admin", login)
            if success:
                QMessageBox.information(
                    self,
                    self.tr("Успех"),
                    self.tr(f"Администратор {login} успешно удален!")
                )

                # Получаем эти обновлённые списки

                admins = [
                ]

                users = [
                ]

                self.create_grid_left(admins, users)
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Ошибка"),
                    self.tr(f"Администратор {login} не найден или не удален.")
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Ошибка базы данных"),
                self.tr(f"Произошла ошибка при удалении администратора:\n{str(e)}")
            )

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
        self.left_panel.setTitle(self.tr("Добавить Админа"))
        self.center_left_panel.setTitle(self.tr("Добавить Пользователя"))
        self.right_panel.setTitle(self.tr("Управление Учетными Записями"))
        self.del_admin_sect.setTitle(self.tr("Управление Учетными Записями"))

    def _clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


# Класс Пользовательская прокручивающаяся область
class CustomScrollArea(QScrollArea):
    def __init__(self, root, alignment, bg=None, place=None, vert_scroll=False, horiz_scroll=False):
        super().__init__(root)
        self.setWidgetResizable(True)
        if not vert_scroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        if not horiz_scroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.elements = QWidget()
        self.setWidget(self.elements)

        if bg is not None:
            self.elements.setStyleSheet(f"background-color: {bg};")

        if alignment == 'v':
            self.layout = QVBoxLayout(self.elements)
            self.layout.setAlignment(Qt.AlignTop)
        elif alignment == 'h':
            self.layout = QHBoxLayout(self.elements)
            self.layout.setAlignment(Qt.AlignLeft)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(1)
        self.elements.setLayout(self.layout)

        # if place is None:
        #     root.layout.addWidget(self)
        # elif len(place) == 1:
        #     root.layout.insertWidget(place[0], self)
        # elif len(place) == 4:
        #     root.layout.addWidget(self, place[0], place[1], place[2], place[3])

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

# Универсальный метод создания списка
def create_list(list_widget: QWidget, list_layout: QVBoxLayout, full_list: list, input_block: QLineEdit):
    area = CustomScrollArea(list_widget, 'v', vert_scroll=True)
    area.layout.setSpacing(5)

    area.elements.setObjectName("Area")
    area.elements.setStyleSheet("#Area{ border-radius: 0px;"
                                        "border-bottom-right-radius: 30px; "
                                        "border-bottom-left-radius: 30px;}")
    list_layout.addWidget(area)

    input_block.textChanged.connect(
        lambda e: on_text_changed(full_list, input_block.text(), area))

    on_text_changed(full_list, "", area)

# Функция для привязки изменения текста поля
def on_text_changed(full_list: list, text: str, area):
    for el in area.elements.children()[1:]:
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