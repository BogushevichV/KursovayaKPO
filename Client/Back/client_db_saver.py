from Client.Back.client_requests import DatabaseServerClient


class SaveData:
    """Клиентская версия Database_Saver - отправляет данные на сервер через API"""
    
    def __init__(self, server_url: str = "http://localhost:5000", **kwargs):
        """Инициализация клиента для сохранения данных"""
        self.client = DatabaseServerClient(server_url)
    
    def save_data(self, group_name: str, course: str, semester: str, 
                  subject_name: str, table_widget) -> bool:
        """Сохранение данных студентов и их оценок через сервер"""
        if not self._validate_input(group_name, course, semester, subject_name, table_widget):
            return False
        
        try:
            # Преобразуем данные из таблицы в список словарей
            students_data = self._extract_students_data(table_widget)
            
            # Отправляем данные на сервер (автоматически сохраняется на сервере)
            result = self.client.save_data(group_name, course, semester, subject_name, students_data)
            
            if result:
                print(f"Данные успешно сохранены для группы '{group_name}', предмет '{subject_name}'")
            else:
                print(f"Ошибка: не удалось сохранить данные для группы '{group_name}'")
            
            return result
        except Exception as e:
            error_msg = f"Ошибка при сохранении: {str(e)}"
            print(error_msg)
            return False
    
    def _extract_students_data(self, table_widget) -> list:
        """Извлекает данные студентов из таблицы"""
        students_data = []
        
        for row in range(table_widget.rowCount() - 1):  # Исключаем последнюю пустую строку
            try:
                name_item = table_widget.item(row, 0)
                gradebook_item = table_widget.item(row, 1)
                grade_item = table_widget.item(row, 2)
                
                if not name_item or not gradebook_item:
                    continue  # Пропускаем пустые строки
                
                student_name = name_item.text().strip()
                gradebook_number = gradebook_item.text().strip()
                
                if not student_name or not gradebook_number:
                    continue  # Пропускаем строки с пустыми данными
                
                # Получаем значение оценки
                grade_value = self._get_grade_value(table_widget, row)
                
                students_data.append({
                    'name': student_name,
                    'gradebook': gradebook_number,
                    'grade': grade_value
                })
            except Exception as e:
                print(f"Ошибка при извлечении данных студента из строки {row}: {str(e)}")
                continue
        
        return students_data
    
    @staticmethod
    def _get_grade_value(table_widget, row: int) -> str:
        """Получает значение оценки из ячейки"""
        from PySide6.QtWidgets import QComboBox
        
        cell_widget = table_widget.cellWidget(row, 2)
        
        if isinstance(cell_widget, QComboBox):
            return cell_widget.currentText()
        
        grade_item = table_widget.item(row, 2)
        return grade_item.text() if grade_item else ""
    
    @staticmethod
    def _validate_input(group_name: str, course: str, semester: str, 
                        subject_name: str, table_widget) -> bool:
        """Валидация входных данных"""
        if not group_name:
            print("Ошибка: Введите название группы!")
            return False
        
        if not course:
            print("Ошибка: Введите курс!")
            return False
        
        if not semester:
            print("Ошибка: Введите семестр!")
            return False
        
        if not subject_name:
            print("Ошибка: Введите название предмета!")
            return False
        
        if table_widget is None or table_widget.rowCount() == 0:
            print("Ошибка: Нет данных для сохранения!")
            return False
        
        return True
