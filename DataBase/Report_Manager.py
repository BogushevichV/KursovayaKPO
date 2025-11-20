from DataBase.Database_Manager import DatabaseManager
from typing import List, Dict, Optional

# При необходимости переименовать
class ReportManager(DatabaseManager):
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        super().__init__(dbname, user, password, host, port)

    def find_group_students(self, group_number: str) -> Optional[List[tuple]]:
        if not self.connect():
            return None

        try:
            with self.connection.cursor() as cursor:

                # FROM students ...

                students = []
                print(f"Найдено {len(students)} студентов в группе {group_number}")
                return students
        except Exception as e:
            print(f"Error fetching students for group {group_number}: {str(e)}")
            return None
