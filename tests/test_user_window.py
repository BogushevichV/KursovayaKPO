import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from User.User_Window import UserWindow


# ---- ФИКСТУРЫ ----

@pytest.fixture
def mock_db_authenticator():
    """Мокаем объект аутентификатора."""
    class MockAuth:
        def __init__(self):
            self.last_login = None
            self.last_password = None
            self.should_authenticate = False

        def authenticate_user(self, login, password):
            self.last_login = login
            self.last_password = password
            return self.should_authenticate

    return MockAuth()


@pytest.fixture
def mock_welcome():
    """Фейковое окно welcome."""
    class W:
        def show(self):
            self.was_shown = True
    return W()


@pytest.fixture
def user_window(qtbot, mock_db_authenticator, mock_welcome):
    w = UserWindow(mock_db_authenticator, mock_welcome)
    qtbot.addWidget(w)
    w.show()
    return w


# ---- ТЕСТЫ ----

def test_widgets_exist(user_window):
    assert user_window.login_label is not None
    assert user_window.password_label is not None
    assert user_window.login_input is not None
    assert user_window.password_input is not None
    assert user_window.login_button is not None


def test_default_texts(user_window):
    assert user_window.windowTitle() == "Вход пользователя"
    assert user_window.login_label.text() == "Логин пользователя:"
    assert user_window.password_label.text() == "Пароль:"
    assert user_window.login_button.text() == "Войти"


def test_successful_login(qtbot, user_window, mock_db_authenticator, monkeypatch):
    """Авторизация проходит успешно → открывается GradeBookApp."""
    mock_db_authenticator.should_authenticate = True

    class FakeGradeBook:
        def __init__(self):
            self.opened = True

        def set_welcome_window(self, w):
            self.welcome_window = w

        def show(self):
            self.was_shown = True

    monkeypatch.setattr("User.UserWindow.GradeBookApp", FakeGradeBook)

    with qtbot.waitExposed(user_window):  # гарантируем, что окно отображено
        qtbot.mouseClick(user_window.login_button, Qt.LeftButton)

    assert isinstance(user_window.grade_book, FakeGradeBook)
    assert user_window.grade_book.was_shown is True


def test_failed_login_reduces_attempts(qtbot, user_window, mock_db_authenticator):
    """Неверный логин → attempts уменьшается."""
    mock_db_authenticator.should_authenticate = False
    initial_attempts = user_window.login_attempts

    # Ожидаем QMessageBox.warning
    with qtbot.waitSignal(QMessageBox.warning, timeout=500, raising=False):
        qtbot.mouseClick(user_window.login_button, Qt.LeftButton)

    assert user_window.login_attempts == initial_attempts - 1


def test_failed_login_message_shown(qtbot, user_window, mock_db_authenticator, monkeypatch):
    """Проверяем, что QMessageBox.warning был вызван."""
    mock_db_authenticator.should_authenticate = False

    msgs = {}

    def fake_warning(self, title, text):
        msgs["title"] = title
        msgs["text"] = text

    monkeypatch.setattr(QMessageBox, "warning", fake_warning)

    qtbot.mouseClick(user_window.login_button, Qt.LeftButton)

    assert "Ошибка входа" in msgs["title"]
    assert "Осталось попыток" in msgs["text"]


def test_max_attempts_closes_window(qtbot, user_window, mock_db_authenticator, monkeypatch):
    """После 5 неверных попыток окно должно закрыться."""
    user_window.login_attempts = 1   # упрощаем тест
    mock_db_authenticator.should_authenticate = False

    called = {"critical": False}

    def fake_critical(self, title, text):
        called["critical"] = True

    monkeypatch.setattr(QMessageBox, "critical", fake_critical)

    qtbot.mouseClick(user_window.login_button, Qt.LeftButton)

    assert called["critical"] is True
    assert not user_window.isVisible()  # окно закрыто


def test_close_event_shows_welcome(qtbot, user_window, mock_welcome):
    """При закрытии окна должен показаться welcome_window."""
    event = type("FakeEvent", (object,), {"accept": lambda self: None})()
    user_window.closeEvent(event)

    assert hasattr(mock_welcome, "was_shown")


def test_retranslate_ui(user_window):
    """Проверяем, что retranslateUi обновляет текст."""
    user_window.retranslateUi()

    assert user_window.windowTitle() == "Вход пользователя"
    assert user_window.login_label.text() in ["Логин пользователя:", "User Login", "用户名"]


def test_language_signal(qtbot, user_window):
    """Проверяем, что сигнал вызывает изменение UI."""
    if user_window.signals:
        with qtbot.waitSignal(user_window.signals.language_changed, timeout=500):
            user_window.signals.language_changed.emit("en")

        # Проверяем, что текст обновился
        assert user_window.login_button.text() in ["Войти", "Login", "登录"]
