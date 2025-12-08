База данных
===========

Структура БД
------------

Схема базы данных (файл `db_schema.txt`):

.. literalinclude:: ../../db_schema.txt
   :language: sql
   :linenos:
   :caption: Схема базы данных

Основные таблицы:

1. **admins** - Администраторы системы
2. **users** - Пользователи (преподаватели)
3. **students** - Студенты (требуется расширение схемы)
4. **subjects** - Предметы (требуется расширение схемы)
5. **grades** - Оценки (требуется расширение схемы)

Менеджер базы данных
--------------------

Основной класс для работы с БД (`Database_Manager.py`):

.. literalinclude:: ../../DataBase/Database_Manager.py
   :language: python
   :linenos:
   :caption: Database_Manager.py - базовый класс управления БД

Пример использования:

.. code-block:: python
   :linenos:

   from DataBase.Database_Manager import DatabaseManager

   # Инициализация менеджера
   db_manager = DatabaseManager(
       dbname="ExaminationReport",
       user="postgres",
       password="ваш_пароль",
       host="127.0.0.1",
       port="5432"
   )

   # Подключение к БД
   db_manager.connect()

   # Выполнение запросов
   cursor = db_manager.connection.cursor()
   cursor.execute("SELECT * FROM admins")
   admins = cursor.fetchall()

   # Закрытие соединения
   db_manager.close()

Безопасность паролей
--------------------

Класс `Password_Hasher.py` реализует безопасное хранение паролей:

.. literalinclude:: ../../DataBase/Password_Hasher.py
   :language: python
   :linenos:
   :caption: Password_Hasher.py - хэширование паролей

Принцип работы:

1. **Генерация соли (salt):** Уникальная строка для каждого пользователя
2. **Хэширование:** SHA256(пароль + соль)
3. **Верификация:** Сравнение хэшей

Пример использования:

.. code-block:: python
   :linenos:

   from DataBase.Password_Hasher import PasswordHasher

   # Создание нового пользователя
   password = "secure_password123"
   salt = PasswordHasher.generate_salt()
   password_hash = PasswordHasher.hash_password(password, salt)

   # Сохранение в БД
   # salt и password_hash сохраняются в разные колонки

   # Проверка пароля при входе
   is_valid = PasswordHasher.verify_password(
       input_password="user_input",
       stored_hash=password_hash_from_db,
       stored_salt=salt_from_db
   )

Создание пользователей
----------------------

Классы для создания учетных записей:

**Admin_Creator.py:**
.. literalinclude:: ../../Admin/Admin_Creator.py
   :language: python
   :linenos:
   :caption: Admin_Creator.py - создание администраторов

**User_Creator.py:**
.. literalinclude:: ../../User/User_Creator.py
   :language: python
   :linenos:
   :caption: User_Creator.py - создание пользователей

Оба класса используют общий базовый класс `Base_User_Creator.py`,
что демонстрирует хорошую архитектуру с повторным использованием кода.

Менеджер отчетов
----------------

Класс `Report_Manager.py` наследуется от `Database_Manager`:

.. literalinclude:: ../../Report_Manager.py
   :language: python
   :linenos:
   :caption: Report_Manager.py - управление отчетами

Запросы к базе данных
---------------------

**Поиск студентов группы:**

.. code-block:: python
   :linenos:

   def find_group_students(self, group_number: str):
       # Реализация в Report_Manager.py
       query = """
           SELECT s.id, s.full_name, s.gradebook_number
           FROM students s
           WHERE s.group_number = %s
           ORDER BY s.full_name
       """
       cursor = self.connection.cursor()
       cursor.execute(query, (group_number,))
       return cursor.fetchall()

**Поиск оценок по предмету:**

.. code-block:: python
   :linenos:

   def find_subject_grades(self, subject_name: str, group_number: str,
                          course: str, semester: str):
       query = """
           SELECT s.full_name, s.gradebook_number, g.grade
           FROM students s
           JOIN grades g ON s.id = g.student_id
           JOIN exams e ON g.exam_id = e.id
           WHERE s.group_number = %s
             AND e.subject_name = %s
             AND e.course = %s
             AND e.semester = %s
       """
       cursor = self.connection.cursor()
       cursor.execute(query, (group_number, subject_name, course, semester))
       return cursor.fetchall()

Миграции базы данных
--------------------

Для добавления новых таблиц:

1. **Расширьте схему** в `db_schema.txt`
2. **Добавьте методы** в `Database_Manager.py` или `Report_Manager.py`
3. **Протестируйте** подключение и запросы

Пример добавления таблицы студентов:

.. code-block:: sql

   CREATE TABLE students (
       id SERIAL PRIMARY KEY,
       full_name VARCHAR(100) NOT NULL,
       gradebook_number VARCHAR(20) UNIQUE NOT NULL,
       group_number VARCHAR(10) NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );