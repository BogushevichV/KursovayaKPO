from Client.Front.welcome_window import WelcomeWindow
from Client.Front.admin_window import AdminWindow
from Client.Front.user_window import UserWindow

from Client.Back.account_validation import Authenticator
from Client.Back.account_manager import AccountManager

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QSettings, QTranslator, QCoreApplication, QObject, Signal
from Client.Source.config import SERVER_URL
import sys
import os


def resource_path(relative_path):
    """Получить абсолютный путь к ресурсу, работает для разработки и для PyInstaller/Inno Setup"""
    try:
        # PyInstaller создает временную папку в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


class AppSignals(QObject):
    language_changed = Signal(str)


class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.signals = AppSignals()
        self.welcome_window = WelcomeWindow()
        self.admin_window = None
        self.db_auth = None
        self.account_manager = None
        self.user_window = None

        # === 1. Настройки приложения ===
        self.settings = QSettings("MyCompany", "ExamRecordApp")

        # === 2. Переводчик (один на всё приложение) ===
        self.translator = QTranslator()
        self.current_lang = self.settings.value("language", "ru")  # читаем сохранённый язык (по умолчанию русский)

        # Загружаем перевод, если не русский
        if self.current_lang != "ru":
            self.load_language(self.current_lang)

        # === 3. Окно приветствия ===
        self.welcome_window = WelcomeWindow(self.current_lang, self.signals)
        self.welcome_window.language_changed.connect(self.on_language_changed)

        # Подключаем сигналы
        self.welcome_window.user_login_requested.connect(lambda: self.show_user_window(self.welcome_window))
        self.welcome_window.admin_login_requested.connect(lambda: self.show_admin_window(self.welcome_window))
        self.welcome_window.show()

    # === 4. Метод загрузки перевода ===
    def load_language(self, lang_code):
        self.translator = QTranslator()

        # Пробуем разные пути к файлам переводов
        translation_paths = [
            resource_path(f"../Client/Source/translations/{lang_code}.qm"),
            resource_path(f"translations/{lang_code}.qm"),
            f"translations/{lang_code}.qm",
            f"{lang_code}.qm",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), f"../Client/Source/translations/{lang_code}.qm"),
        ]

        loaded = False
        for path in translation_paths:
            if os.path.exists(path):
                print(f"Пытаемся загрузить перевод из: {path}")
                if self.translator.load(path):
                    QCoreApplication.installTranslator(self.translator)
                    self.current_lang = lang_code
                    self.settings.setValue("language", lang_code)
                    self.signals.language_changed.emit(lang_code)
                    loaded = True
                    print(f"✅ Перевод успешно загружен из: {path}")
                    break
                else:
                    print(f"❌ Не удалось загрузить перевод из: {path}")

        if not loaded:
            print(f"⚠ Не удалось загрузить перевод для языка {lang_code}")
            for path in translation_paths:
                print(f"  Проверял: {path}")

    def on_language_changed(self, new_lang):
        """При смене языка из WelcomeWindow"""
        self.load_language(new_lang)
        if hasattr(self.welcome_window, 'retranslateUi'):
            self.welcome_window.retranslateUi()

    def init_db_connections(self):
        """Инициализация подключений к серверу БД через HTTP API"""
        try:
            # Инициализируем классы для работы через сервер
            # Все классы используют HTTP запросы к серверу (не прямые подключения к БД)
            self.db_auth = Authenticator(server_url=SERVER_URL)
            self.account_manager = AccountManager(server_url=SERVER_URL)

            # Проверяем доступность сервера
            if not self.db_auth.client.health_check():
                raise ConnectionError("Сервер БД недоступен")

            return True
        except Exception as e:
            QMessageBox.critical(
                None,
                "Ошибка подключения",
                f"Не удалось подключиться к серверу базы данных:\n{str(e)}\n\n"
                f"URL сервера: {SERVER_URL}\n\n"
                f"Убедитесь, что сервер запущен на другом компьютере."
            )
            return False

    def show_user_window(self, welcome_window):
        if not self.init_db_connections():
            return

        if self.user_window is None:
            self.user_window = UserWindow(self.db_auth, welcome_window, signals=self.signals)  # Передаем welcome_window

        welcome_window.hide()  # Скрываем welcome_window
        self.user_window.show()

    def show_admin_window(self, welcome_window):
        if not self.init_db_connections():
            return

        # Всегда создаем новое окно администратора
        self.admin_window = AdminWindow(
            self.db_auth,
            self.account_manager,
            welcome_window,
            signals=self.signals
        )

        welcome_window.hide()
        self.admin_window.show()

    def cleanup(self):
        self.admin_window = None

    def run(self):
        try:
            sys.exit(self.app.exec())
        finally:
            self.cleanup()


if __name__ == "__main__":
    application = Application()
    application.run()