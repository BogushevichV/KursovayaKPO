from PySide6.QtWidgets import QMessageBox, QComboBox, QTableWidget
from DataBase.Database_Manager import DatabaseManager


class SaveData(DatabaseManager):
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        super().__init__(dbname, user, password, host, port)


    def save_data(self, group_name, course, semester, subject_name, table_widget):
        if not self._validate_input(group_name, course, semester, subject_name, table_widget):
            return False

        try:
            cursor = None
            # Создаем таблицы, если они не существуют
            self._create_tables(cursor)

            # Получаем или создаем группу
            group_id = self._get_or_create_group(cursor, group_name)

            # Получаем или создаем предмет
            subject_id = self._get_or_create_subject(cursor, subject_name)

            # Получаем или создаем запись об экзамене
            exam_id = self._get_or_create_exam(cursor, group_id, subject_id, course, semester)

            # Сохраняем студентов и их оценки
            self._save_students_data(cursor, exam_id, table_widget, group_id)

            return True

        except Exception as e:
            error_msg = f"Ошибка при сохранении: {str(e)}"
            QMessageBox.critical(None, "Ошибка", error_msg)
            return False

    @staticmethod
    def _create_tables(cursor):
        try:
            # Создание всех существующих таблиц

            # CREATE TABLE IF NOT EXISTS ...

            print("Таблицы успешно созданы/проверены")

        except Exception as e:
            raise Exception(f"Ошибка при создании таблиц: {str(e)}")

    @staticmethod
    def _get_or_create_group(cursor, group_name):
        try:
            # Пытаемся найти существующую группу
            """SELECT id FROM groups ..."""

            result = False

            # Если не нашли:

            # Создаем новую группу

            """INSERT INTO groups ..."""

        except Exception as e:
            raise Exception(f"Ошибка при работе с группой: {str(e)}")

    @staticmethod
    def _get_or_create_subject(cursor, subject_name):
        try:
            # Пытаемся найти существующий предмет
            """SELECT id FROM subjects..."""

            result = False

            # Если не нашли:

            # Создаем новый предмет
            """INSERT INTO subjects... """

        except Exception as e:
            raise Exception(f"Ошибка при работе с предметом: {str(e)}")

    @staticmethod
    def _get_or_create_exam(cursor, group_id, subject_id, course, semester):
        try:
            # Пытаемся найти существующий экзамен
            """SELECT id FROM exams..."""

            result = False

            # Если не нашли:

            # Создаем новую запись об экзамене
            """INSERT INTO exams..."""

        except Exception as e:
            raise Exception(f"Ошибка при работе с экзаменом: {str(e)}")

    def _save_students_data(self, cursor, exam_id, table_widget, group_id):
        for row in range(table_widget.rowCount() - 1):
            try:
                student_name = table_widget.item(row, 0).text()
                gradebook_number = table_widget.item(row, 1).text()
                grade_value = self._get_grade_value(table_widget, row)

                # Получаем или создаем студента с привязкой к группе
                student_id = self._get_or_create_student(
                    cursor, student_name, gradebook_number, group_id
                )

                # Сохраняем/обновляем оценку
                self._upsert_grade(cursor, student_id, exam_id, grade_value)

            except Exception as e:
                print(f"Ошибка сохранения данных студента {student_name}: {str(e)}")
                raise

    @staticmethod
    def _get_or_create_student(cursor, student_name, gradebook_number, group_id):
        try:
            # Пытаемся найти существующего студента в этой группе
            """SELECT id FROM students..."""

            result = False

            # Если не нашли:

            # Создаем нового студента с привязкой к группе
            """INSERT INTO students..."""

        except Exception as e:
            raise Exception(f"Ошибка при работе со студентом: {str(e)}")

    @staticmethod
    def _upsert_grade(cursor, student_id, exam_id, grade_value):
        try:
            # Сначала пытаемся обновить существующую запись
            """ UPDATE grades ..."""

            rowcount = 0

            # Если ни одна запись не была обновлена, создаем новую
            if rowcount == 0:
                """INSERT INTO grades... """

        except Exception as e:
            raise Exception(f"Ошибка при сохранении оценки: {str(e)}")

    @staticmethod
    def _validate_input(group_name, course, semester, subject_name, table_widget):
        if not group_name:
            QMessageBox.warning(None, "Ошибка", "Введите название группы!")
            return False

        if not course:
            QMessageBox.warning(None, "Ошибка", "Введите курс!")
            return False

        if not semester:
            QMessageBox.warning(None, "Ошибка", "Введите семестр!")
            return False

        if not subject_name:
            QMessageBox.warning(None, "Ошибка", "Введите название предмета!")
            return False

        if not isinstance(table_widget, QTableWidget) or table_widget.rowCount() == 0:
            QMessageBox.warning(None, "Ошибка", "Нет данных для сохранения!")
            return False

        return True

    @staticmethod
    def _get_grade_value(table_widget, row):
        cell_widget = table_widget.cellWidget(row, 2)

        if isinstance(cell_widget, QComboBox):
            return cell_widget.currentText()

        grade_item = table_widget.item(row, 2)
        return grade_item.text() if grade_item else ""
