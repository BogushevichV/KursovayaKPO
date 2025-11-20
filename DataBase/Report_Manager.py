from DataBase.Database_Manager import DatabaseManager
from typing import List, Dict, Optional

# При необходимости переименовать
class ReportManager(DatabaseManager):
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        super().__init__(dbname, user, password, host, port)

    def find_group_students(self, group_number: str) -> Optional[List[tuple]]:
        try:
            print(f"Ищу студентов группы {group_number}...")

            # FROM students ...

            students = [
                ("Сеченов Дмитрий Сергеевич", "107011231"),
                ("Захаров Харитон Радеонович", "107011232"),
                ("Нечаев Сергей Алексеевич", "107011233"),
            ]

            print(f"Найдено {len(students)} студентов в группе {group_number}")
            return students
        except Exception as e:
            print(f"Error fetching students for group {group_number}: {str(e)}")
            return None

    def find_subject_grades(self, subject_name: str, group_number: str,
                            course: str, semester: str) -> Optional[List[tuple]]:

        try:
            print(f"Ищу предмет {subject_name} для группы {group_number}...")

            """
                SELECT ...
                FROM students
                JOIN grades 
                JOIN exams
            """

            grades = [
                ("Сеченов Дмитрий Сергеевич", "107011231", "10"),
                ("Захаров Харитон Радеонович", "107011232", "9"),
                ("Нечаев Сергей Алексеевич", "107011233", "10"),
            ]

            print(f"Найдено {len(grades)} записей оценок для предмета {subject_name}")
            return grades
        except Exception as e:
            print(f"Error fetching grades for subject {subject_name}: {str(e)}")
            return None