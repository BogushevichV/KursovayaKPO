from Client.Back.client_requests import DatabaseServerClient
from typing import List, Optional


class ReportManager:
    """Менеджер отчетов через сервер БД"""
    
    def __init__(self, server_url: str = "http://localhost:5000", **kwargs):
        """Инициализация менеджера отчетов"""
        self.client = DatabaseServerClient(server_url)

    def find_group_students(self, group_number: str) -> Optional[List[tuple]]:
        """Поиск студентов группы через сервер"""
        try:
            print(f"Ищу студентов группы {group_number}...")
            
            students = self.client.find_group_students(group_number)
            
            if students:
                # Преобразуем список в список кортежей, если нужно
                if isinstance(students, list) and len(students) > 0:
                    if not isinstance(students[0], tuple):
                        students = [tuple(s) if isinstance(s, (list, tuple)) else (s,) for s in students]
                
                print(f"Найдено {len(students)} студентов в группе {group_number}")
                return students
            else:
                print(f"Студенты в группе {group_number} не найдены")
                return []
        except Exception as e:
            print(f"Error fetching students for group {group_number}: {str(e)}")
            return None

    def find_subject_grades(self, subject_name: str, group_number: str,
                            course: str, semester: str) -> Optional[List[tuple]]:
        """Поиск оценок по предмету через сервер"""
        try:
            print(f"Ищу предмет {subject_name} для группы {group_number}...")
            
            grades = self.client.find_subject_grades(subject_name, group_number, course, semester)
            
            if grades:
                # Преобразуем список в список кортежей, если нужно
                if isinstance(grades, list) and len(grades) > 0:
                    if not isinstance(grades[0], tuple):
                        grades = [tuple(g) if isinstance(g, (list, tuple)) else (g,) for g in grades]
                
                print(f"Найдено {len(grades)} записей оценок для предмета {subject_name}")
                return grades
            else:
                print(f"Оценки для предмета {subject_name} не найдены")
                return []
        except Exception as e:
            print(f"Error fetching grades for subject {subject_name}: {str(e)}")
            return None