import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import psycopg2
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout, QHBoxLayout,
                               QMessageBox)
from PySide6.QtCore import Qt


class AdminWindow(QMainWindow):
    def __init__(self, db_authenticator, user_creator, admin_creator,
                 user_remover, admin_remover, welcome_window,parent=None, signals=None):
        super().__init__(parent)
        self.back_button = None
        self.signals = signals
        self.db_auth = db_authenticator
        self.user_creator = user_creator
        self.admin_creator = admin_creator
        self.user_remover = user_remover
        self.admin_remover = admin_remover
        self.welcome_window = welcome_window
        self.login_attempts = 5

        # Настройки SMTP (замените на свои)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = "examinationreportbntu@gmail.com"
        self.smtp_password = "quqv ypik iktl illl"

        self._init_ui_elements()
        self.setWindowTitle(self.tr("Панель администратора"))
        self.setFixedSize(1400, 650)
        self.setStyleSheet("background-color: White;")

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
        self.login_button.clicked.connect(self.check_credentials)
        self.login_button.setStyleSheet(button_style)
        self.login_button.setFixedWidth(200)  # Фиксированная ширина кнопки

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
        form_container.setStyleSheet("""
            QLineEdit#login_input, QLineEdit#password_input, QWidget#form_container {
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #dee2e6;
            }
            QLabel#login_label, QLabel#password_label {
                background-color: #f8f9fa;
            }
        """)

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

    def setup_admin_panel(self):
        self._clear_layout()

        # Стиль для кнопок
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

        # Стиль для форм
        form_style = """
                    QWidget {
                        background-color: #f8f9fa;
                        border-radius: 10px;
                        border: 1px solid #dee2e6;
                    }
                    QLineEdit {
                        padding: 5px 10px;
                        border: 1px solid #ced4da;
                        border-radius: 4px;
                        font-size: 14px;
                    }
                    QLabel {
                        background: transparent;
                        border: none;
                        font-size: 14px;
                    }
                """

        # Универсальный метод создания секции
        def create_section(title_text, widgets):
            container = QWidget()
            container.setStyleSheet(form_style)
            layout = QVBoxLayout(container)
            layout.setSpacing(10)
            layout.setContentsMargins(20, 20, 20, 20)

            title = QLabel(title_text)
            title.setStyleSheet("font-size: 16px; font-weight: bold;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)

            for widget in widgets:
                layout.addWidget(widget)

            layout.addStretch()
            return container

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
        self.add_admin_button.setStyleSheet(button_style)
        self.add_admin_button.clicked.connect(self.add_new_admin)

        self.send_admin_button.setText(self.tr("Отправить данные на почту"))
        self.send_admin_button.setStyleSheet(button_style)
        self.send_admin_button.clicked.connect(self.send_admin_data)

        left_panel = create_section("Добавить Админа", [
            self.admin_login_label, self.admin_login_input,
            self.admin_password_label, self.admin_password_input,
            self.admin_email_label, self.admin_email_input,
            self.add_admin_button, self.send_admin_button
        ])

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
        self.add_user_button.setStyleSheet(button_style)
        self.add_user_button.clicked.connect(self.add_new_user)

        self.send_button.setText(self.tr("Отправить данные на почту"))
        self.send_button.setStyleSheet(button_style)
        self.send_button.clicked.connect(self.send_user_data)

        center_left_panel = create_section("Добавить Пользователя", [
            self.user_login_label, self.user_login_input,
            self.user_password_label, self.user_password_input,
            self.user_email_label, self.user_email_input,
            self.add_user_button, self.send_button
        ])

        # Настройка виджетов для удаления
        self.del_user_login_label.setText(self.tr("Логин пользователя:"))
        self.del_user_login_input.setPlaceholderText(self.tr("Введите логин"))
        self.del_user_login_input.setFixedHeight(35)

        self.del_user_button.setText(self.tr("Удалить пользователя"))
        self.del_user_button.setStyleSheet(button_style)
        self.del_user_button.clicked.connect(self.delete_user)

        self.del_admin_login_label.setText(self.tr("Логин администратора:"))
        self.del_admin_login_input.setPlaceholderText(self.tr("Введите логин"))
        self.del_admin_login_input.setFixedHeight(35)

        self.del_admin_button.setText(self.tr("Удалить администратора"))
        self.del_admin_button.setStyleSheet(button_style)
        self.del_admin_button.clicked.connect(self.delete_admin)

        center_right_panel = create_section("Управление Учетными Записями", [
            self.del_user_login_label, self.del_user_login_input,
            self.del_user_button,
            self.del_admin_login_label, self.del_admin_login_input,
            self.del_admin_button
        ])

        # Настройка виджетов для управления БД
        self.del_subject_label.setText(self.tr("Название предмета:"))
        self.del_subject_input.setPlaceholderText(self.tr("Введите название предмета"))
        self.del_subject_input.setFixedHeight(35)

        self.del_subject_button.setText(self.tr("Удалить предмет"))
        self.del_subject_button.setStyleSheet(button_style)
        self.del_subject_button.clicked.connect(self.delete_subject)

        self.del_group_label.setText(self.tr("Номер группы:"))
        self.del_group_input.setPlaceholderText(self.tr("Введите номер группы"))
        self.del_group_input.setFixedHeight(35)

        self.del_group_button.setText(self.tr("Удалить группу"))
        self.del_group_button.setStyleSheet(button_style)
        self.del_group_button.clicked.connect(self.delete_group)

        self.del_exam_label.setText(self.tr("ID экзамена:"))
        self.del_exam_input.setPlaceholderText(self.tr("Введите ID экзамена"))
        self.del_exam_input.setFixedHeight(35)

        self.del_exam_button.setText(self.tr("Удалить экзамен"))
        self.del_exam_button.setStyleSheet(button_style)
        self.del_exam_button.clicked.connect(self.delete_exam)

        self.del_student_label.setText(self.tr("ID студента:"))
        self.del_student_input.setPlaceholderText(self.tr("Введите ID студента"))
        self.del_student_input.setFixedHeight(35)

        self.del_student_button.setText(self.tr("Удалить студента"))
        self.del_student_button.setStyleSheet(button_style)
        self.del_student_button.clicked.connect(self.delete_student)

        right_panel = create_section("Управление записями БД", [
            self.del_subject_label, self.del_subject_input, self.del_subject_button,
            self.del_group_label, self.del_group_input, self.del_group_button,
            self.del_exam_label, self.del_exam_input, self.del_exam_button,
            self.del_student_label, self.del_student_input, self.del_student_button
        ])

        # Добавляем все панели в главный layout
        self.main_layout.addWidget(left_panel, 1)
        self.main_layout.addWidget(center_left_panel, 1)
        self.main_layout.addWidget(center_right_panel, 1)
        self.main_layout.addWidget(right_panel, 1)

        # Кнопка Назад
        self.back_button = QPushButton(self.tr("Назад"))
        self.back_button.setFixedSize(100, 30)
        self.back_button.setStyleSheet(button_style)
        self.back_button.clicked.connect(self.return_to_welcome)

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.addStretch()
        button_layout.addWidget(self.back_button)

        self.main_layout.addWidget(button_container)

    def send_admin_data(self):
        login = self.admin_login_input.text()
        password = self.admin_password_input.text()
        email = self.admin_email_input.text()

        if not all([login, password, email]):
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Ошибка", "Введите корректный email!")
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
                    "Успех",
                    f"Данные администратора отправлены на {email}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Не удалось отправить данные на указанный email"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Произошла ошибка при отправке данных:\n{str(e)}"
            )

    def delete_subject(self):
        subject_name = self.del_subject_input.text()
        if not subject_name:
            QMessageBox.warning(self, "Ошибка", "Введите название предмета")
            return

        # Подтверждение удаления
        reply = QMessageBox.question(
            self,
            'Подтверждение удаления',
            f'Вы уверены, что хотите удалить предмет "{subject_name}" и все связанные данные (экзамены, оценки)?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            conn = psycopg2.connect(
                dbname="ExaminationReport",
                user="postgres",
                password="",
                host="127.0.0.1",
                port="5432"
            )
            cursor = conn.cursor()

            # 1. Находим ID предмета
            cursor.execute("SELECT id FROM subjects WHERE subject_name = %s", (subject_name,))
            subject_id = cursor.fetchone()

            if not subject_id:
                QMessageBox.warning(self, "Ошибка", f"Предмет '{subject_name}' не найден")
                return

            subject_id = subject_id[0]

            # 2. Удаляем оценки, связанные с экзаменами по этому предмету
            cursor.execute("""
                DELETE FROM grades 
                WHERE exam_id IN (
                    SELECT id FROM exams WHERE subject_id = %s
                )
            """, (subject_id,))

            # 3. Удаляем экзамены по этому предмету
            cursor.execute("DELETE FROM exams WHERE subject_id = %s", (subject_id,))

            # 4. Удаляем сам предмет
            cursor.execute("DELETE FROM subjects WHERE id = %s", (subject_id,))

            conn.commit()

            QMessageBox.information(
                self,
                "Успех",
                f"Предмет '{subject_name}' и все связанные данные успешно удалены!"
            )
            self.del_subject_input.clear()

        except psycopg2.Error as e:
            conn.rollback()
            QMessageBox.critical(
                self,
                "Ошибка базы данных",
                f"Произошла ошибка при удалении предмета:\n{str(e)}"
            )
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_group(self):
        group_name = self.del_group_input.text()
        if not group_name:
            QMessageBox.warning(self, "Ошибка", "Введите номер группы")
            return

        reply = QMessageBox.question(
            self,
            'Подтверждение удаления',
            f'Вы уверены, что хотите удалить группу "{group_name}" и всех её студентов?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            conn = psycopg2.connect(
                dbname="ExaminationReport",
                user="postgres",
                password="",
                host="127.0.0.1",
                port="5432"
            )
            cursor = conn.cursor()

            # 1. Находим ID группы
            cursor.execute("SELECT id FROM groups WHERE group_name = %s", (group_name,))
            group_id = cursor.fetchone()

            if not group_id:
                QMessageBox.warning(self, "Ошибка", f"Группа '{group_name}' не найдена")
                return

            group_id = group_id[0]

            # 2. Удаляем оценки студентов этой группы
            cursor.execute("""
                DELETE FROM grades 
                WHERE student_id IN (
                    SELECT id FROM students WHERE group_id = %s
                )
            """, (group_id,))

            # 3. Удаляем студентов группы
            cursor.execute("DELETE FROM students WHERE group_id = %s", (group_id,))

            # 4. Удаляем экзамены группы
            cursor.execute("DELETE FROM exams WHERE group_id = %s", (group_id,))

            # 5. Удаляем саму группу
            cursor.execute("DELETE FROM groups WHERE id = %s", (group_id,))

            conn.commit()

            QMessageBox.information(
                self,
                "Успех",
                f"Группа '{group_name}' и все связанные данные успешно удалены!"
            )
            self.del_group_input.clear()

        except psycopg2.Error as e:
            conn.rollback()
            QMessageBox.critical(
                self,
                "Ошибка базы данных",
                f"Произошла ошибка при удалении группы:\n{str(e)}"
            )
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_exam(self):
        exam_id = self.del_exam_input.text()
        if not exam_id:
            QMessageBox.warning(self, "Ошибка", "Введите ID экзамена")
            return

        reply = QMessageBox.question(
            self,
            'Подтверждение удаления',
            f'Вы уверены, что хотите удалить экзамен с ID {exam_id} и все оценки по нему?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            conn = psycopg2.connect(
                dbname="ExaminationReport",
                user="postgres",
                password="",
                host="127.0.0.1",
                port="5432"
            )
            cursor = conn.cursor()

            # 1. Проверяем существование экзамена
            cursor.execute("SELECT id FROM exams WHERE id = %s", (exam_id,))
            if not cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", f"Экзамен с ID {exam_id} не найден")
                return

            # 2. Удаляем оценки по этому экзамену
            cursor.execute("DELETE FROM grades WHERE exam_id = %s", (exam_id,))

            # 3. Удаляем сам экзамен
            cursor.execute("DELETE FROM exams WHERE id = %s", (exam_id,))

            conn.commit()

            QMessageBox.information(
                self,
                "Успех",
                f"Экзамен с ID {exam_id} и все оценки по нему успешно удалены!"
            )
            self.del_exam_input.clear()

        except psycopg2.Error as e:
            conn.rollback()
            QMessageBox.critical(
                self,
                "Ошибка базы данных",
                f"Произошла ошибка при удалении экзамена:\n{str(e)}"
            )
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_student(self):
        student_id = self.del_student_input.text()
        if not student_id:
            QMessageBox.warning(self, "Ошибка", "Введите ID студента")
            return

        reply = QMessageBox.question(
            self,
            'Подтверждение удаления',
            f'Вы уверены, что хотите удалить студента с ID {student_id} и все его оценки?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            conn = psycopg2.connect(
                dbname="ExaminationReport",
                user="postgres",
                password="",
                host="127.0.0.1",
                port="5432"
            )
            cursor = conn.cursor()

            # 1. Проверяем существование студента
            cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
            if not cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", f"Студент с ID {student_id} не найден")
                return

            # 2. Удаляем оценки студента
            cursor.execute("DELETE FROM grades WHERE student_id = %s", (student_id,))

            # 3. Удаляем самого студента
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))

            conn.commit()

            QMessageBox.information(
                self,
                "Успех",
                f"Студент с ID {student_id} и все его оценки успешно удалены!"
            )
            self.del_student_input.clear()

        except psycopg2.Error as e:
            conn.rollback()
            QMessageBox.critical(
                self,
                "Ошибка базы данных",
                f"Произошла ошибка при удалении студента:\n{str(e)}"
            )
        finally:
            if 'conn' in locals():
                conn.close()

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
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Ошибка", "Введите корректный email!")
            return

        try:
            success = self.admin_creator.create_admin(login, password, email)
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
                        "Успех",
                        f"Администратор {login} успешно добавлен!\n"
                        f"Данные для входа отправлены на {email}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Ошибка отправки",
                        f"Администратор {login} добавлен, но не удалось отправить данные на email!"
                    )

                # Очищаем поля
                self.admin_login_input.clear()
                self.admin_password_input.clear()
                self.admin_email_input.clear()
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Не удалось добавить администратора. Возможно, такой логин уже существует."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка базы данных",
                f"Произошла ошибка при добавлении администратора:\n{str(e)}"
            )

    def add_new_user(self):
        login = self.user_login_input.text()
        password = self.user_password_input.text()
        email = self.user_email_input.text()

        if not all([login, password, email]):
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Ошибка", "Введите корректный email!")
            return

        try:
            success = self.user_creator.create_user(login, password, email)
            if success:
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Пользователь {login} успешно добавлен!"
                )
                self.user_login_input.clear()
                self.user_password_input.clear()
                self.user_email_input.clear()
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Не удалось добавить пользователя. Возможно, такой логин уже существует."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка базы данных",
                f"Произошла ошибка при добавлении пользователя:\n{str(e)}"
            )

    def send_user_data(self):
        login = self.user_login_input.text()
        password = self.user_password_input.text()
        email = self.user_email_input.text()

        if not all([login, password, email]):
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Ошибка", "Введите корректный email!")
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
                    "Успех",
                    f"Данные для входа отправлены на {email}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Не удалось отправить данные на указанный email"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Произошла ошибка при отправке данных:\n{str(e)}"
            )

    def check_credentials(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        try:
            is_authenticated = self.db_auth.authenticate_admin(login, password)

            if is_authenticated:
                self.setup_admin_panel()
            else:
                self.handle_failed_login()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка аутентификации",
                f"Произошла ошибка при проверке учетных данных:\n{str(e)}"
            )

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

    def delete_user(self):
        login = self.del_user_login_input.text()
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин пользователя")
            return

        try:
            success = self.user_remover.remove_user(login)
            if success:
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Пользователь {login} успешно удален!"
                )
                self.del_user_login_input.clear()
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Пользователь {login} не найден или не удален."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка базы данных",
                f"Произошла ошибка при удалении пользователя:\n{str(e)}"
            )

    def delete_admin(self):
        login = self.del_admin_login_input.text()
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин администратора")
            return

        try:
            success = self.admin_remover.remove_admin(login)
            if success:
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Администратор {login} успешно удален!"
                )
                self.del_admin_login_input.clear()
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Администратор {login} не найден или не удален."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка базы данных",
                f"Произошла ошибка при удалении администратора:\n{str(e)}"
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

    def _clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
