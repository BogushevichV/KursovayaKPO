import smtplib
import re

from email.mime.text import MIMEText
from email.utils import formatdate
from PySide6.QtWidgets import QMessageBox

from Client.Front.admin_lists_widgets import create_list

email_regex = re.compile(
    r'^[a-zA-Zа-яА-ЯёЁ0-9._%+-]+@[a-zA-Zа-яА-ЯёЁ0-9.-]+\.[a-zA-Zа-яА-ЯёЁ]{2,}$'
)

def is_valid_email(email):
    return bool(email_regex.match(email))

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

            if send_email(self, email, "Ваши административные данные", email_body):
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

                admins = self.db_client.get_all_admins()

                self.admin_scroll_list.deleteLater()
                self.admin_scroll_list = create_list(self.admin_list, self.admin_list_layout, admins,
                                                     self.del_admin_login_input)
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
            users = self.db_client.get_all_users()

            self.user_scroll_list.deleteLater()
            self.user_scroll_list = create_list(self.user_list, self.user_list_layout, users,
                                                 self.del_user_login_input)

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

            users = self.db_client.get_all_users()

            self.user_scroll_list.deleteLater()
            self.user_scroll_list = create_list(self.user_list, self.user_list_layout, users,
                                                self.del_user_login_input)

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

            admins = self.db_client.get_all_admins()

            self.admin_scroll_list.deleteLater()
            self.admin_scroll_list = create_list(self.admin_list, self.admin_list_layout, admins,
                                                 self.del_admin_login_input)
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

            subjects = self.db_client.get_all_subjects()
            exams = self.db_client.get_all_exams()

            self.subject_scroll_list.deleteLater()
            self.subject_scroll_list = create_list(self.subject_list, self.subject_list_layout, subjects,
                                                self.del_subject_input)
            self.exams_scroll_list.deleteLater()
            self.exams_scroll_list = create_list(self.exam_list, self.exam_list_layout, exams,
                                                self.del_exam_input)

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
            groups = self.db_client.get_all_groups()
            exams = self.db_client.get_all_exams()
            students = self.db_client.get_all_students()

            self.group_scroll_list.deleteLater()
            self.group_scroll_list = create_list(self.group_list, self.group_list_layout, groups,
                                                   self.del_group_input)
            self.exam_scroll_list.deleteLater()
            self.exam_scroll_list = create_list(self.exam_list, self.exam_list_layout, exams,
                                                 self.del_exam_input)
            self.student_scroll_list.deleteLater()
            self.student_scroll_list = create_list(self.student_list, self.student_list_layout, students,
                                                 self.del_student_input)

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
            exams = self.db_client.get_all_exams()

            self.exam_scroll_list.deleteLater()
            self.exam_scroll_list = create_list(self.exam_list, self.exam_list_layout, exams,
                                                 self.del_exam_input)

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
            students = self.db_client.get_all_students()

            self.student_scroll_list.deleteLater()
            self.student_scroll_list = create_list(self.student_list, self.student_list_layout, students,
                                                   self.del_student_input)
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

        admins = self.db_client.get_all_admins()

        users = self.db_client.get_all_users()

        subjects = self.db_client.get_all_subjects()

        groups = self.db_client.get_all_groups()

        exams = self.db_client.get_all_exams()

        students = self.db_client.get_all_students()

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