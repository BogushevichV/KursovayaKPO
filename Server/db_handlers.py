"""
Серверные обработчики для работы с БД напрямую
Эти классы используются только на сервере и работают напрямую с PostgreSQL
"""
import psycopg2
from psycopg2 import sql
from Server.db_manager import DatabaseManager
from Server.password_hasher import PasswordHasher


class ServerDBAuthenticator(DatabaseManager):
    """Серверная версия аутентификатора - работает напрямую с БД"""
    
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        super().__init__(dbname, user, password, host, port)

    def __authenticate(self, table: str, login: str, password: str) -> bool:
        try:
            print(f"[DEBUG] Начало аутентификации для '{login}' в таблице '{table}'")
            self.connect()
            print(f"[DEBUG] Подключение к БД установлено")
            
            cursor = self.connection.cursor()
            try:
                query = sql.SQL("""
                    SELECT password_hash, salt
                    FROM {table}
                    WHERE login = %s
                """).format(table=sql.Identifier(table))

                print(f"[DEBUG] Выполняю SQL запрос для логина: {login}")
                cursor.execute(query, (login,))
                record = cursor.fetchone()

                if not record:
                    print(f"[DEBUG] Пользователь '{login}' не найден в таблице '{table}'")
                    return False

                stored_hash, stored_salt = record
                print(f"[DEBUG] Пользователь найден. Проверяю пароль...")
                print(f"[DEBUG] Salt (первые 10 символов): {stored_salt[:10]}...")
                print(f"[DEBUG] Hash (первые 10 символов): {stored_hash[:10]}...")
                
                is_valid = PasswordHasher.verify_password(password, stored_hash, stored_salt)
                
                if not is_valid:
                    print(f"[DEBUG] Неверный пароль для пользователя '{login}'")
                    # Для отладки - показываем что сравнивается
                    test_hash = PasswordHasher.hash_password(password, stored_salt)
                    print(f"[DEBUG] Введенный пароль хеш (первые 20 символов): {test_hash[:20]}...")
                    print(f"[DEBUG] Сохраненный хеш (первые 20 символов): {stored_hash[:20]}...")
                    print(f"[DEBUG] Хеши совпадают: {test_hash == stored_hash}")
                else:
                    print(f"[DEBUG] Пароль верный! Аутентификация успешна.")
                
                return is_valid
            finally:
                cursor.close()
        except Exception as e:
            print(f"[ERROR] Ошибка при аутентификации: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.close()
            print(f"[DEBUG] Подключение закрыто")

    def authenticate_admin(self, login: str, password: str) -> bool:
        return self.__authenticate('admins', login, password)

    def authenticate_user(self, login: str, password: str) -> bool:
        return self.__authenticate('users', login, password)


class ServerAccountManager(DatabaseManager):
    """Серверная версия менеджера аккаунтов - работает напрямую с БД"""
    
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        super().__init__(dbname, user, password, host, port)

    def create_account(self, account_type: str, login: str, password: str, email: str, **extra_fields) -> bool:
        """
        Создание аккаунта (пользователя или администратора)
        
        Args:
            account_type: Тип аккаунта - 'user' или 'admin'
            login: Логин пользователя
            password: Пароль пользователя
            email: Email пользователя
            **extra_fields: Дополнительные поля
        
        Returns:
            True если аккаунт успешно создан, False в противном случае
        """
        if account_type not in ['user', 'admin']:
            raise ValueError(f"Неизвестный тип аккаунта: {account_type}. Используйте 'user' или 'admin'")
        
        table_name = f"{account_type}s"
        
        print(f"[DEBUG] Начало создания аккаунта '{login}' в таблице '{table_name}'")
        salt = PasswordHasher.generate_salt()
        hashed_password = PasswordHasher.hash_password(password, salt)
        print(f"[DEBUG] Сгенерирован salt (первые 10 символов): {salt[:10]}...")
        print(f"[DEBUG] Сгенерирован hash (первые 10 символов): {hashed_password[:10]}...")

        try:
            self.connect()
            print(f"[DEBUG] Подключение к БД установлено")
            
            cursor = self.connection.cursor()
            try:
                columns = ["login", "password_hash", "salt", "email"] + list(extra_fields.keys())
                values = [login, hashed_password, salt, email] + list(extra_fields.values())

                insert_query = sql.SQL("""
                    INSERT INTO {table} ({fields})
                    VALUES ({placeholders})
                """).format(
                    table=sql.Identifier(table_name),
                    fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
                    placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
                )

                print(f"[DEBUG] Выполняю INSERT запрос...")
                cursor.execute(insert_query, values)
                print(f"[DEBUG] INSERT выполнен успешно, делаю commit...")
            finally:
                cursor.close()
            
            self.commit()
            print(f"[DEBUG] Commit выполнен. Аккаунт '{login}' успешно создан в таблице '{table_name}'")
            return True
        except psycopg2.errors.UniqueViolation as e:
            # Определяем, что именно нарушило уникальность
            error_detail = str(e)
            if 'login' in error_detail.lower() or 'login' in str(e.pgcode):
                error_msg = f"Администратор с логином '{login}' уже существует"
            elif 'email' in error_detail.lower() or 'email' in str(e.pgcode):
                error_msg = f"Администратор с email '{email}' уже существует"
            else:
                error_msg = f"Запись с логином '{login}' или email '{email}' уже существует в {table_name}"
            
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Детали: {e}")
            self.rollback()
            raise ValueError(error_msg)  # Пробрасываем исключение для более детальной обработки
        except Exception as e:
            error_msg = f"Ошибка при создании записи в {table_name}: {e}"
            print(f"[ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            self.rollback()
            return False
        finally:
            self.close()
            print(f"[DEBUG] Подключение закрыто")

    def delete_account(self, account_type: str, login: str) -> bool:
        """Удаление аккаунта (пользователя или администратора)"""
        if account_type not in ['user', 'admin']:
            raise ValueError(f"Неизвестный тип аккаунта: {account_type}. Используйте 'user' или 'admin'")
        
        table_name = f"{account_type}s"
        
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                delete_query = sql.SQL("""
                    DELETE FROM {table}
                    WHERE login = %s
                """).format(table=sql.Identifier(table_name))

                cursor.execute(delete_query, (login,))
                if cursor.rowcount == 0:
                    self.rollback()
                    return False

            self.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении пользователя из {table_name}: {e}")
            self.rollback()
            return False
        finally:
            self.close()


class ServerReportManager(DatabaseManager):
    """Серверная версия менеджера отчетов - работает напрямую с БД"""
    
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        super().__init__(dbname, user, password, host, port)

    def find_group_students(self, group_number: str):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                query = """
                    SELECT s.id, s.student_name, s.gradebook_number
                    FROM students s
                    INNER JOIN groups g ON s.group_id = g.id
                    WHERE g.group_name = %s
                    ORDER BY s.student_name
                """
                cursor.execute(query, (group_number,))
                students = cursor.fetchall()
                result = [
                    {
                        'id': row[0],
                        'student_name': row[1],
                        'gradebook_number': row[2]
                    }
                    for row in students
                ]
            return result
        except Exception as e:
            print(f"Error fetching students for group {group_number}: {str(e)}")
            return None
        finally:
            self.close()

    def find_subject_grades(self, subject_name: str, group_number: str, course: str, semester: str):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                query = """
                    SELECT s.student_name, s.gradebook_number, g.grade_value
                    FROM grades g
                    INNER JOIN students s ON g.student_id = s.id
                    INNER JOIN exams e ON g.exam_id = e.id
                    INNER JOIN groups gr ON e.group_id = gr.id
                    INNER JOIN subjects sub ON e.subject_id = sub.id
                    WHERE sub.subject_name = %s
                      AND gr.group_name = %s
                      AND e.course = %s
                      AND e.semester = %s
                    ORDER BY s.student_name
                """
                cursor.execute(query, (subject_name, group_number, course, semester))
                grades = cursor.fetchall()
                # Преобразуем в список словарей для удобства
                result = [
                    {
                        'student_name': row[0],
                        'gradebook_number': row[1],
                        'grade_value': row[2]
                    }
                    for row in grades
                ]
            return result
        except Exception as e:
            print(f"Error fetching grades for subject {subject_name}: {str(e)}")
            return None
        finally:
            self.close()

    def get_all_subjects(self):
        """Получить все предметы"""
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                query = """
                    SELECT subject_name
                    FROM subjects
                    ORDER BY subject_name
                """
                cursor.execute(query)
                subjects = cursor.fetchall()
                # Преобразуем в список кортежей для совместимости с UI
                result = [(row[0],) for row in subjects]
            return result
        except Exception as e:
            print(f"Error fetching all subjects: {str(e)}")
            return []
        finally:
            self.close()

    def get_all_groups(self):
        """Получить все группы"""
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                query = """
                    SELECT group_name
                    FROM groups
                    ORDER BY group_name
                """
                cursor.execute(query)
                groups = cursor.fetchall()
                # Преобразуем в список кортежей для совместимости с UI
                result = [(row[0],) for row in groups]
            return result
        except Exception as e:
            print(f"Error fetching all groups: {str(e)}")
            return []
        finally:
            self.close()

    def get_all_exams(self):
        """Получить все экзамены"""
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                query = """
                    SELECT 
                        e.id,
                        g.group_name,
                        s.subject_name,
                        e.course,
                        e.semester
                    FROM exams e
                    INNER JOIN groups g ON e.group_id = g.id
                    INNER JOIN subjects s ON e.subject_id = s.id
                    ORDER BY e.id
                """
                cursor.execute(query)
                exams = cursor.fetchall()
                # Формируем человекочитаемое описание экзамена
                result = [
                    (
                        str(row[0]),
                        f"{row[1]} • {row[2]} • курс {row[3]}, семестр {row[4]}"
                    )
                    for row in exams
                ]
            return result
        except Exception as e:
            print(f"Error fetching all exams: {str(e)}")
            return []
        finally:
            self.close()

    def get_all_students(self):
        """Получить всех студентов"""
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                query = """
                    SELECT s.gradebook_number, s.student_name
                    FROM students s
                    ORDER BY s.student_name
                """
                cursor.execute(query)
                students = cursor.fetchall()
                # Преобразуем в список кортежей для совместимости с UI
                result = [(row[0], row[1]) for row in students]
            return result
        except Exception as e:
            print(f"Error fetching all students: {str(e)}")
            return []
        finally:
            self.close()

    def get_all_users(self):
        """Получить всех пользователей (логин и email)"""
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                query = """
                    SELECT login, email
                    FROM users
                    ORDER BY login
                """
                cursor.execute(query)
                users = cursor.fetchall()
                result = [(row[0], row[1]) for row in users]
            return result
        except Exception as e:
            print(f"Error fetching all users: {str(e)}")
            return []
        finally:
            self.close()

    def get_all_admins(self):
        """Получить всех администраторов (логин и email)"""
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                query = """
                    SELECT login, email
                    FROM admins
                    ORDER BY login
                """
                cursor.execute(query)
                admins = cursor.fetchall()
                result = [(row[0], row[1]) for row in admins]
            return result
        except Exception as e:
            print(f"Error fetching all admins: {str(e)}")
            return []
        finally:
            self.close()

