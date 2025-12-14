from Server.db_manager import DatabaseManager


class ServerDatabaseSaver(DatabaseManager):
    """Серверная версия Database_Saver - работает напрямую с БД и автоматически сохраняет изменения"""
    
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        super().__init__(dbname, user, password, host, port)
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Создает таблицы, если они не существуют"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            
            # Создаем таблицу groups
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    id SERIAL PRIMARY KEY,
                    group_name VARCHAR(50) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Создаем таблицу subjects
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id SERIAL PRIMARY KEY,
                    subject_name VARCHAR(200) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Создаем таблицу students
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    student_name VARCHAR(200) NOT NULL,
                    gradebook_number VARCHAR(50) NOT NULL,
                    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(gradebook_number, group_id)
                )
            """)
            
            # Создаем таблицу exams
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exams (
                    id SERIAL PRIMARY KEY,
                    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
                    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
                    course VARCHAR(10) NOT NULL,
                    semester VARCHAR(10) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(group_id, subject_id, course, semester)
                )
            """)
            
            # Создаем таблицу grades
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grades (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                    exam_id INTEGER REFERENCES exams(id) ON DELETE CASCADE,
                    grade_value VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(student_id, exam_id)
                )
            """)
            
            self.commit()
            cursor.close()
            print("[DEBUG] Таблицы проверены/созданы")
        except Exception as e:
            print(f"[ERROR] Ошибка при создании таблиц: {e}")
            self.rollback()
            raise
        finally:
            self.close()
    
    def save_data(self, group_name: str, course: str, semester: str, subject_name: str, students_data: list) -> bool:
        """Сохранение данных студентов и их оценок"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            
            # Получаем или создаем группу
            group_id = self._get_or_create_group(cursor, group_name)
            
            # Получаем или создаем предмет
            subject_id = self._get_or_create_subject(cursor, subject_name)
            
            # Получаем или создаем запись об экзамене
            exam_id = self._get_or_create_exam(cursor, group_id, subject_id, course, semester)
            
            # Сохраняем студентов и их оценки
            self._save_students_data(cursor, exam_id, students_data, group_id)
            
            # Автоматическое сохранение при изменениях
            self.commit()
            print(f"[DEBUG] Данные успешно сохранены для группы '{group_name}', предмет '{subject_name}'")
            return True
            
        except Exception as e:
            error_msg = f"Ошибка при сохранении: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.rollback()
            return False
        finally:
            cursor.close()
            self.close()
    
    def _get_or_create_group(self, cursor, group_name: str) -> int:
        """Получает или создает группу"""
        try:
            cursor.execute("SELECT id FROM groups WHERE group_name = %s", (group_name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            cursor.execute("INSERT INTO groups (group_name) VALUES (%s) RETURNING id", (group_name,))
            group_id = cursor.fetchone()[0]
            print(f"[DEBUG] Создана группа '{group_name}' с ID {group_id}")
            return group_id
        except Exception as e:
            raise Exception(f"Ошибка при работе с группой: {e}")
    
    def _get_or_create_subject(self, cursor, subject_name: str) -> int:
        """Получает или создает предмет"""
        try:
            cursor.execute("SELECT id FROM subjects WHERE subject_name = %s", (subject_name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            cursor.execute("INSERT INTO subjects (subject_name) VALUES (%s) RETURNING id", (subject_name,))
            subject_id = cursor.fetchone()[0]
            print(f"[DEBUG] Создан предмет '{subject_name}' с ID {subject_id}")
            return subject_id
        except Exception as e:
            raise Exception(f"Ошибка при работе с предметом: {e}")
    
    def _get_or_create_exam(self, cursor, group_id: int, subject_id: int, course: str, semester: str) -> int:
        """Получает или создает запись об экзамене"""
        try:
            cursor.execute("""
                SELECT id FROM exams 
                WHERE group_id = %s AND subject_id = %s AND course = %s AND semester = %s
            """, (group_id, subject_id, course, semester))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            cursor.execute("""
                INSERT INTO exams (group_id, subject_id, course, semester) 
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (group_id, subject_id, course, semester))
            exam_id = cursor.fetchone()[0]
            print(f"[DEBUG] Создан экзамен с ID {exam_id}")
            return exam_id
        except Exception as e:
            raise Exception(f"Ошибка при работе с экзаменом: {e}")
    
    def _save_students_data(self, cursor, exam_id: int, students_data: list, group_id: int):
        """Сохраняет данные студентов и их оценки"""
        for student_data in students_data:
            try:
                student_name = student_data.get('name', '').strip()
                gradebook_number = student_data.get('gradebook', '').strip()
                grade_value = student_data.get('grade', '').strip()
                
                if not student_name or not gradebook_number:
                    continue  # Пропускаем пустые записи
                
                # Получаем или создаем студента
                student_id = self._get_or_create_student(cursor, student_name, gradebook_number, group_id)
                
                # Сохраняем/обновляем оценку
                self._upsert_grade(cursor, student_id, exam_id, grade_value)
                
            except Exception as e:
                print(f"[ERROR] Ошибка сохранения данных студента {student_name}: {str(e)}")
                raise
    
    def _get_or_create_student(self, cursor, student_name: str, gradebook_number: str, group_id: int) -> int:
        """Получает или создает студента"""
        try:
            cursor.execute("""
                SELECT id FROM students 
                WHERE gradebook_number = %s AND group_id = %s
            """, (gradebook_number, group_id))
            result = cursor.fetchone()
            
            if result:
                # Обновляем имя студента, если оно изменилось
                cursor.execute("""
                    UPDATE students SET student_name = %s 
                    WHERE id = %s AND student_name != %s
                """, (student_name, result[0], student_name))
                return result[0]
            
            cursor.execute("""
                INSERT INTO students (student_name, gradebook_number, group_id) 
                VALUES (%s, %s, %s) RETURNING id
            """, (student_name, gradebook_number, group_id))
            student_id = cursor.fetchone()[0]
            print(f"[DEBUG] Создан студент '{student_name}' с ID {student_id}")
            return student_id
        except Exception as e:
            raise Exception(f"Ошибка при работе со студентом: {e}")
    
    def _upsert_grade(self, cursor, student_id: int, exam_id: int, grade_value: str):
        """Сохраняет или обновляет оценку"""
        try:
            # Сначала пытаемся обновить существующую запись
            cursor.execute("""
                UPDATE grades 
                SET grade_value = %s, updated_at = CURRENT_TIMESTAMP
                WHERE student_id = %s AND exam_id = %s
            """, (grade_value, student_id, exam_id))
            
            # Если ни одна запись не была обновлена, создаем новую
            if cursor.rowcount == 0:
                cursor.execute("""
                    INSERT INTO grades (student_id, exam_id, grade_value) 
                    VALUES (%s, %s, %s)
                """, (student_id, exam_id, grade_value))
                print(f"[DEBUG] Создана оценка для студента {student_id}, экзамен {exam_id}")
            else:
                print(f"[DEBUG] Обновлена оценка для студента {student_id}, экзамен {exam_id}")
        except Exception as e:
            raise Exception(f"Ошибка при сохранении оценки: {e}")

