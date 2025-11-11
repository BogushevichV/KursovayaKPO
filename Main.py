from Welcome_Window import WelcomeWindow
from Admin.Admin_Window import AdminWindow

from DataBase.DB_Validation import DBAuthenticator

from Admin.Admin_Creator import AdminCreator
from Admin.Admin_Remover import AdminRemover
from User.User_Creator import UserCreator
from User.User_Remover import UserRemover

from PySide6.QtWidgets import QApplication, QMessageBox
from User.User_Window import UserWindow
import sys


class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.welcome_window = WelcomeWindow()
        self.admin_window = None
        self.db_auth = None
        self.user_creator = None
        self.user_remover = None
        self.admin_creator = None
        self.admin_remover = None
        self.user_window = None

        # Подключаем сигналы
        self.welcome_window.user_login_requested.connect(lambda: self.show_user_window(self.welcome_window))
        self.welcome_window.admin_login_requested.connect(lambda: self.show_admin_window(self.welcome_window))
        self.welcome_window.show()

    def init_db_connections(self):
        db_params = {
            'dbname': "ExaminationReport",
            'user': "postgres",
            'password': "",
            'host': "127.0.0.1",
            'port': "5432"
        }

        try:
            self.db_auth = DBAuthenticator(**db_params)
            self.user_creator = UserCreator(**db_params)
            self.user_remover = UserRemover(**db_params)
            self.admin_creator = AdminCreator(**db_params)
            self.admin_remover = AdminRemover(**db_params)
            return True
        except Exception as e:
            QMessageBox.critical(
                None,
                "Ошибка подключения",
                f"Не удалось подключиться к базе данных:\n{str(e)}"
            )
            return False

    def show_user_window(self, welcome_window):
        if not self.init_db_connections():
            return

        if self.user_window is None:
            self.user_window = UserWindow(self.db_auth, welcome_window)  # Передаем welcome_window

        welcome_window.hide()  # Скрываем welcome_window
        self.user_window.show()

    def show_admin_window(self, welcome_window):
        if not self.init_db_connections():
            return

        # Всегда создаем новое окно администратора
        self.admin_window = AdminWindow(
            self.db_auth,
            self.user_creator,
            self.admin_creator,
            self.user_remover,
            self.admin_remover,
            welcome_window  # Передаем текущее окно приветствия
        )

        welcome_window.hide()
        self.admin_window.show()

    def cleanup(self):
        self.admin_window = None
        if hasattr(self, 'user_creator') and self.user_creator:
            self.user_creator.close()

    def run(self):
        try:
            sys.exit(self.app.exec())
        finally:
            self.cleanup()


if __name__ == "__main__":
    application = Application()
    application.run()
