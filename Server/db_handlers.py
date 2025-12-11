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
                query = sql.SQL("""
                    SELECT full_name, gradebook_number
                    FROM students
                    WHERE group_id = (
                        SELECT id FROM groups WHERE group_name = %s
                    )
                """)
                cursor.execute(query, (group_number,))
                students = cursor.fetchall()
                print(f"[DEBUG] Найдено {len(students)} студентов в группе {group_number}")
            return students
        except Exception as e:
            print(f"Error fetching students for group {group_number}: {str(e)}")
            return None
        finally:
            self.close()

    def find_subject_grades(self, subject_name: str, group_number: str, course: str, semester: str):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                query = sql.SQL("""
                    SELECT s.full_name, s.gradebook_number, g.grade_value
                    FROM students AS s
                    JOIN grades AS g ON s.id = g.student_id
                    JOIN exams AS e ON g.exam_id = e.id
                    WHERE e.group_id = (
                        SELECT id FROM groups WHERE group_name = %s
                    )
                    AND e.subject_id = (
                        SELECT id FROM subjects WHERE subject_name = %s
                    )
                    AND e.course = %s
                    AND e.semester = %s
                """)
                cursor.execute(query, (group_number, subject_name, course, semester))
                grades = cursor.fetchall()
                print(f"[DEBUG] Найдено {len(grades)} записей оценок для предмета {subject_name}")
            return grades
        except Exception as e:
            print(f"Error fetching grades for subject {subject_name}: {str(e)}")
            return None
        finally:
            self.close()

    def get_report_data(self, subject_name: str, group_number: str):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                # Получаем данные о студентах и оценках
                cursor.execute("""
                    SELECT 
                        st.full_name, 
                        st.gradebook_number, 
                        gr.grade_value
                    FROM students st
                    JOIN groups g ON st.group_id = g.id
                    LEFT JOIN grades gr ON st.id = gr.student_id
                    LEFT JOIN exams e ON gr.exam_id = e.id AND e.subject_id = (
                        SELECT id FROM subjects WHERE subject_name = %s
                    )
                    WHERE g.group_name = %s
                    ORDER BY st.full_name
                """, (subject_name, group_number))

                students = cursor.fetchall()

                # Получаем статистику по оценкам
                cursor.execute("""
                    SELECT 
                        gr.grade_value,
                        COUNT(*) as count
                    FROM grades gr
                    JOIN students st ON gr.student_id = st.id
                    JOIN groups g ON st.group_id = g.id
                    JOIN exams e ON gr.exam_id = e.id
                    JOIN subjects s ON e.subject_id = s.id
                    WHERE g.group_name = %s AND s.subject_name = %s
                    GROUP BY gr.grade_value
                """, (group_number, subject_name))

                grade_stats = {str(grade): count for grade, count in cursor.fetchall()}

                # Получаем статистику по оценкам (адаптировано для зачетов/экзаменов)
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN gr.grade_value IS NULL THEN 'не явился'
                            WHEN gr.grade_value = '' THEN 'не явился'
                            WHEN gr.grade_value::text ~ '^[0-9]+$' THEN 'экзамен'
                            ELSE 'зачет'
                        END as result_type,
                        COUNT(*) as count
                    FROM students st
                    JOIN groups g ON st.group_id = g.id
                    LEFT JOIN grades gr ON st.id = gr.student_id
                    LEFT JOIN exams e ON gr.exam_id = e.id AND e.subject_id = (
                        SELECT id FROM subjects WHERE subject_name = %s
                    )
                    WHERE g.group_name = %s
                    GROUP BY result_type
                """, (subject_name, group_number))

                attendance_stats = {result: count for result, count in cursor.fetchall()}
            return students, grade_stats, attendance_stats
        except Exception as e:
            print(f"Error fetching data for report: {str(e)}")
            return None
        finally:
            self.close()
