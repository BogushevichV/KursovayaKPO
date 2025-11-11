import openpyxl
from PySide6.QtWidgets import QFileDialog, QMessageBox


class ExcelImporter:
    @staticmethod
    def import_from_excel(parent_window):
        file_path, _ = QFileDialog.getOpenFileName(
            parent_window,
            "Выберите файл Excel",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if not file_path:
            return None

        try:
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active

            data = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if row[0] and row[1]:  # Проверяем, что есть ФИО и номер зачётки
                    data.append({
                        'name': row[0],
                        'gradebook': row[1]
                    })

            return data

        except Exception as e:
            QMessageBox.critical(
                parent_window,
                "Ошибка импорта",
                f"Не удалось загрузить данные из файла:\n{str(e)}"
            )
            return None
