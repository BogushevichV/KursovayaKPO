import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QMessageBox
from Client.Front.admin_window import AdminWindow


@pytest.fixture
def admin_window(qtbot):
    """Создаёт окно с замоканным backend."""
    window = AdminWindow(
        db_authenticator=MagicMock(),
        account_manager=MagicMock(),
        welcome_window=MagicMock(),
        signals=None
    )
    qtbot.addWidget(window)
    return window


# -------------------------------------------------------------------
# ADD USER
# -------------------------------------------------------------------
def test_add_user_empty_fields(admin_window, monkeypatch):
    """Пустые поля → предупреждение."""
    # Мокаем setup_admin_panel для теста
    admin_window.db_client = MagicMock()
    admin_window.db_client.get_all_admins.return_value = []
    admin_window.db_client.get_all_users.return_value = []
    admin_window.db_client.get_all_subjects.return_value = []
    admin_window.db_client.get_all_groups.return_value = []
    admin_window.db_client.get_all_exams.return_value = []
    admin_window.db_client.get_all_students.return_value = []

    admin_window.setup_admin_panel([], [], [], [], [], [])

    admin_window.account_manager.create_account.return_value = True

    admin_window.user_login_input.setText("")
    admin_window.user_password_input.setText("")
    admin_window.user_email_input.setText("")

    messages = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: messages.append(True))

    admin_window.add_new_user()

    assert messages


def test_add_user_success(admin_window, monkeypatch):
    """Проверка успешного добавления пользователя."""
    # Мокаем setup_admin_panel для теста
    admin_window.db_client = MagicMock()
    admin_window.db_client.get_all_admins.return_value = []
    admin_window.db_client.get_all_users.return_value = []
    admin_window.db_client.get_all_subjects.return_value = []
    admin_window.db_client.get_all_groups.return_value = []
    admin_window.db_client.get_all_exams.return_value = []
    admin_window.db_client.get_all_students.return_value = []

    admin_window.setup_admin_panel([], [], [], [], [], [])

    admin_window.account_manager.create_account.return_value = True

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
    # Мокаем setup_admin_panel для теста
    admin_window.db_client = MagicMock()
    admin_window.db_client.get_all_admins.return_value = []
    admin_window.db_client.get_all_users.return_value = []
    admin_window.db_client.get_all_subjects.return_value = []
    admin_window.db_client.get_all_groups.return_value = []
    admin_window.db_client.get_all_exams.return_value = []
    admin_window.db_client.get_all_students.return_value = []

    admin_window.setup_admin_panel([], [], [], [], [], [])

    admin_window.account_manager.delete_account.return_value = True
    admin_window.del_user_login_input.setText("userX")

    messages = []
    monkeypatch.setattr(QMessageBox, "information", lambda *a: messages.append(True))

    admin_window.delete_user()
    assert messages


def test_delete_user_not_found(admin_window, monkeypatch):
    # Мокаем setup_admin_panel для теста
    admin_window.db_client = MagicMock()
    admin_window.db_client.get_all_admins.return_value = []
    admin_window.db_client.get_all_users.return_value = []
    admin_window.db_client.get_all_subjects.return_value = []
    admin_window.db_client.get_all_groups.return_value = []
    admin_window.db_client.get_all_exams.return_value = []
    admin_window.db_client.get_all_students.return_value = []

    admin_window.setup_admin_panel([], [], [], [], [], [])

    admin_window.account_manager.delete_account.return_value = False
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

    # Мокаем setup_admin_panel для теста
    admin_window.db_client = MagicMock()
    admin_window.db_client.get_all_admins.return_value = []
    admin_window.db_client.get_all_users.return_value = []
    admin_window.db_client.get_all_subjects.return_value = []
    admin_window.db_client.get_all_groups.return_value = []
    admin_window.db_client.get_all_exams.return_value = []
    admin_window.db_client.get_all_students.return_value = []

    admin_window.setup_admin_panel([], [], [], [], [], [])

    admin_window.admin_login_input.setText("newadmin")
    admin_window.admin_password_input.setText("123")
    admin_window.admin_email_input.setText("test@test.com")

    admin_window.add_admin_button.click()

    admin_window.send_email.assert_called_once()