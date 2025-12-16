import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QMessageBox
from Admin.Admin_Window import AdminWindow


@pytest.fixture
def admin_window(qtbot):
    """Создаёт окно с замоканным backend."""
    window = AdminWindow(
        db_authenticator=MagicMock(),
        user_creator=MagicMock(),
        admin_creator=MagicMock(),
        user_remover=MagicMock(),
        admin_remover=MagicMock(),
        welcome_window=MagicMock(),
        signals=None
    )
    qtbot.addWidget(window)
    return window


# -------------------------------------------------------------------
# LOGIN UI
# -------------------------------------------------------------------
def test_login_ui_initial_visible(admin_window):
    """Проверка, что окно открывается на форме логина."""
    assert admin_window.login_label.text() != ""
    assert admin_window.login_input.isVisible()
    assert admin_window.password_input.isVisible()
    assert admin_window.login_button.isVisible()


def test_login_success_opens_admin_panel(admin_window, qtbot):
    """Успешный вход переключает UI на админ-панель."""
    admin_window.db_auth.authenticate_admin.return_value = True

    admin_window.login_input.setText("admin")
    admin_window.password_input.setText("123")

    admin_window.check_credentials()

    # Проверяем, что панель администратора появилась
    assert admin_window.left_panel is not None
    assert admin_window.left_panel.isVisible()


def test_login_failed_shows_warning(admin_window, qtbot, monkeypatch):
    """Ошибка входа вызывает QMessageBox.warning."""
    admin_window.db_auth.authenticate_admin.return_value = False

    messages = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: messages.append(True))

    admin_window.login_input.setText("bad")
    admin_window.password_input.setText("wrong")

    admin_window.check_credentials()

    assert messages, "Ожидалось всплывающее предупреждение"


# -------------------------------------------------------------------
# ADD USER
# -------------------------------------------------------------------
def test_add_user_empty_fields(admin_window, monkeypatch):
    """Пустые поля → предупреждение."""
    admin_window.setup_admin_panel()

    admin_window.user_creator.create_user.return_value = True

    admin_window.user_login_input.setText("")
    admin_window.user_password_input.setText("")
    admin_window.user_email_input.setText("")

    messages = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: messages.append(True))

    admin_window.add_new_user()

    assert messages


def test_add_user_success(admin_window, monkeypatch):
    """Проверка успешного добавления пользователя."""
    admin_window.setup_admin_panel()

    admin_window.user_creator.create_user.return_value = True

    admin_window.user_login_input.setText("user1")
    admin_window.user_password_input.setText("pass")
    admin_window.user_email_input.setText("email@test.com")

    messages = []
    monkeypatch.setattr(QMessageBox, "information", lambda *a: messages.append(True))

    admin_window.add_new_user()

    assert messages
    assert admin_window.user_login_input.text() == ""


# -------------------------------------------------------------------
# DELETE USER
# -------------------------------------------------------------------
def test_delete_user_success(admin_window, monkeypatch):
    admin_window.setup_admin_panel()

    admin_window.user_remover.remove_user.return_value = True
    admin_window.del_user_login_input.setText("userX")

    messages = []
    monkeypatch.setattr(QMessageBox, "information", lambda *a: messages.append(True))

    admin_window.delete_user()
    assert messages


def test_delete_user_not_found(admin_window, monkeypatch):
    admin_window.setup_admin_panel()

    admin_window.user_remover.remove_user.return_value = False
    admin_window.del_user_login_input.setText("ghost")

    messages = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: messages.append(True))

    admin_window.delete_user()
    assert messages


# -------------------------------------------------------------------
# SEND EMAIL (МОК)
# -------------------------------------------------------------------
def test_send_email_called(admin_window):
    """send_email вызывается фронтом — реальный SMTP не используется."""
    admin_window.send_email = MagicMock(return_value=True)
    admin_window.setup_admin_panel()

    admin_window.admin_login_input.setText("newadmin")
    admin_window.admin_password_input.setText("123")
    admin_window.admin_email_input.setText("test@test.com")

    admin_window.add_admin_button.click()

    admin_window.send_email.assert_called_once()
