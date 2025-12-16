import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QMessageBox, QComboBox, QTableWidgetItem

from User.Examination_Report_App import GradeBookApp


@pytest.fixture
def gradebook(qtbot):
    """Создаёт тестируемое окно."""
    window = GradeBookApp()
    qtbot.addWidget(window)
    return window


# ----------------------------------------------------------------------
# UI ОБЩЕЕ
# ----------------------------------------------------------------------
def test_initial_ui_state(gradebook):
    """Проверяем, что элементы формы созданы."""
    assert gradebook.group_input is not None
    assert gradebook.subject_input is not None
    assert gradebook.table.columnCount() == 3
    assert gradebook.table.rowCount() == 1   # одна пустая строка


def test_buttons_exist(gradebook):
    assert gradebook.btn_import.text() != ""
    assert gradebook.btn_save.text() != ""
    assert gradebook.btn_find_subject.text() != ""
    assert gradebook.btn_clear.text() != ""
    assert gradebook.btn_create_report.text() != ""


# ----------------------------------------------------------------------
# EMPTY ROW LOGIC
# ----------------------------------------------------------------------
def test_adds_new_empty_row_when_editing_last(gradebook, qtbot):
    """Если последняя строка заполнена — добавляется новая."""
    gradebook.table.item(0, 0).setText("Иванов И.И.")
    gradebook.table.item(0, 1).setText("12345")
    gradebook.table.item(0, 2).setText("9")

    gradebook.handle_item_changed(gradebook.table.item(0, 0))

    assert gradebook.table.rowCount() == 2


def test_removes_extra_empty_rows(gradebook):
    """В конце должен быть только один пустой ряд."""
    gradebook.table.setRowCount(3)

    # делаем строки пустыми
    for r in range(3):
        for c in range(3):
            gradebook.table.setItem(r, c, QTableWidgetItem(""))

    gradebook._check_empty_rows()

    assert gradebook.table.rowCount() == 1


# ----------------------------------------------------------------------
# SWITCH MODE GRADE <-> PASS_FAIL
# ----------------------------------------------------------------------
def test_switch_to_pass_fail(gradebook):
    gradebook.switch_to_pass_fail()

    assert gradebook.grade_mode == "pass_fail"
    assert isinstance(gradebook.table.cellWidget(0, 2), QComboBox)


def test_switch_to_grades(gradebook):
    gradebook.switch_to_grades()

    assert gradebook.grade_mode == "grade"
    assert isinstance(gradebook.table.item(0, 2), QTableWidgetItem)


# ----------------------------------------------------------------------
# КНОПКА "Очистить"
# ----------------------------------------------------------------------
def test_clear_table(gradebook):
    gradebook.table.insertRow(1)
    gradebook.clear_table()

    assert gradebook.table.rowCount() == 1
    assert gradebook.table.item(0, 0).text() == ""


# ----------------------------------------------------------------------
# import_from_excel
# ----------------------------------------------------------------------
def test_import_from_excel(gradebook, monkeypatch):
    """ExcelImporter замокан — UI должен загрузить строки."""
    fake_data = [
        {"name": "Иванов И.И.", "gradebook": "111"},
        {"name": "Петров П.П.", "gradebook": "222"},
    ]

    monkeypatch.setattr("User.Examination_Report_App.ExcelImporter.import_from_excel", lambda *a: fake_data)

    gradebook.import_from_excel()

    assert gradebook.table.rowCount() == 3  # + пустая строка
    assert gradebook.table.item(0, 0).text() == "Иванов И.И."
    assert gradebook.table.item(1, 1).text() == "222"


# ----------------------------------------------------------------------
# ЛОГИКА create_exam_report (валидация)
# ----------------------------------------------------------------------
def test_create_exam_report_missing_required_field(gradebook, monkeypatch):
    """Если не заполнено обязательное поле — предупреждение."""
    gradebook.group_input.setText("")  # обязательное поле

    messages = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: messages.append(True))

    gradebook.create_exam_report()

    assert messages, "Ожидалось предупреждение о незаполненном поле"


def test_create_exam_report_success(gradebook, monkeypatch):
    """Если все поля заполнены — функция проходит дальше (ошибок нет)."""

    # Заполняем обязательные поля
    gradebook.statement_number_input.setText("10")
    gradebook.group_input.setText("121")
    gradebook.course_input.setText("2")
    gradebook.subject_input.setText("Математика")

    # Заглушка QMessageBox (он не должен вызываться)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: (_ for _ in ()).throw(Exception("warning_called")))

    try:
        gradebook.create_exam_report()
    except Exception as e:
        assert False, f"Не должно быть предупреждений, но было: {e}"


# ----------------------------------------------------------------------
# return_to_welcome
# ----------------------------------------------------------------------
def test_return_to_welcome_ok(gradebook):
    welcome = MagicMock()
    gradebook.set_welcome_window(welcome)

    gradebook.return_to_welcome()

    welcome.show.assert_called_once()


def test_return_to_welcome_no_welcome_window(gradebook, monkeypatch):
    """Если welcome_window нет — показывается QMessageBox."""
    gradebook.welcome_window = None

    messages = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: messages.append(True))

    gradebook.return_to_welcome()

    assert messages


# ----------------------------------------------------------------------
# get_full_faculty_name
# ----------------------------------------------------------------------
def test_get_full_faculty_name(gradebook):
    assert gradebook.get_full_faculty_name("АТФ") == gradebook.faculty_full[0]
    assert gradebook.get_full_faculty_name("НЕСУЩ") == "НЕСУЩ"
