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
                ("Нечаев Сергей Алексеевич", "1070112310"),
                ("Фелатова Лариса Андреевна", "1070112311"),
                ("Таненбаум Эндрю Стюарт", "1070112312"),
                ("Неелова Анна Аркадьевна", "1070112313"),
                ("Петров Виктор Васильевич", "1070112314"),
                ("Сеченов Дмитрий Сергеевич", "1070112315"),
                ("Муравьёва Зинаида Петровна", "1070112316"),
                ("Захаров Харитон Радеонович", "1070112317"),
                ("Терешкова Валентина Владимировна", "1070112318"),
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
                ("Нечаев Сергей Алексеевич", "1070112310", "5"),
                ("Фелатова Лариса Андреевна", "1070112311", "9"),
                ("Таненбаум Эндрю Стюарт", "1070112312", "10"),
                ("Неелова Анна Аркадьевна", "1070112313", "8"),
                ("Петров Виктор Васильевич", "1070112314", "10"),
                ("Сеченов Дмитрий Сергеевич", "1070112315", "7"),
                ("Муравьёва Зинаида Петровна", "1070112316", "9"),
                ("Захаров Харитон Радеонович", "1070112317", "5"),
                ("Терешкова Валентина Владимировна", "1070112318", "10"),
            ]

            print(f"Найдено {len(grades)} записей оценок для предмета {subject_name}")
            return grades
        except Exception as e:
            print(f"Error fetching grades for subject {subject_name}: {str(e)}")
            return None