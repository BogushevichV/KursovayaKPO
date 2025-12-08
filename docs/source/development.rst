Разработка
==========

Структура проекта
-----------------

### Основные модули и их ответственность:

1. **Main.py** - Точка входа, управление жизненным циклом приложения
2. **Welcome_Window.py** - Стартовое окно, выбор языка
3. **DataBase/Database_Manager.py** - Базовое управление подключением к БД
4. **DataBase/Password_Hasher.py** - Безопасность паролей
5. **Report_Manager.py** - Бизнес-логика отчетов (наследник DatabaseManager)
6. **Excel_Importer.py** - Импорт данных из Excel
7. **Grade_Item_Delegate.py** - Кастомные виджеты для ввода оценок

### Архитектурные паттерны:

1. **Наследование:** `ReportManager` наследует `DatabaseManager`
2. **Композиция:** `Admin_Creator` использует `BaseUserCreator`
3. **Сигналы и слоты:** Связь между окнами через Qt сигналы
4. **Разделение ответственности:** Каждый модуль отвечает за свою задачу

Добавление новых функций
------------------------

### Пример: Добавление экспорта в PDF

1. **Создайте новый модуль:** `PDF_Exporter.py`
2. **Реализуйте функциональность:**

   .. code-block:: python

      class PDFExporter:
          def export_statement(self, statement_data, filename):
              # Реализация генерации PDF
              pass

3. **Интегрируйте в основное приложение:**

   .. code-block:: python

      # В Examination_Report_App.py
      from PDF_Exporter import PDFExporter

      def export_to_pdf(self):
          exporter = PDFExporter()
          exporter.export_statement(self.get_statement_data(), "statement.pdf")

4. **Добавьте кнопку в интерфейс**

Тестирование
------------

### Структура тестов:

.. code-block:: text

    tests/
    ├── test_database.py      # Тесты работы с БД
    ├── test_password.py      # Тесты безопасности
    ├── test_import.py        # Тесты импорта
    └── test_ui.py           # Тесты интерфейса

### Пример теста для PasswordHasher:

.. code-block:: python
   :linenos:

   import pytest
   from DataBase.Password_Hasher import PasswordHasher

   class TestPasswordHasher:

       def setup_method(self):
           self.hasher = PasswordHasher

       def test_generate_salt_length(self):
           """Тест длины генерируемой соли."""
           salt = self.hasher.generate_salt()
           assert len(salt) == 32
           salt_custom = self.hasher.generate_salt(64)
           assert len(salt_custom) == 64

       def test_hash_consistency(self):
           """Тест консистентности хэширования."""
           password = "test_password"
           salt = "test_salt"

           hash1 = self.hasher.hash_password(password, salt)
           hash2 = self.hasher.hash_password(password, salt)

           assert hash1 == hash2
           assert len(hash1) == 64  # Длина SHA256 хэша

       def test_verify_password(self):
           """Тест верификации пароля."""
           password = "secure123"
           salt = self.hasher.generate_salt()
           hashed = self.hasher.hash_password(password, salt)

           # Правильный пароль
           assert self.hasher.verify_password(password, hashed, salt) == True

           # Неправильный пароль
           assert self.hasher.verify_password("wrong", hashed, salt) == False

       def test_salt_uniqueness(self):
           """Тест уникальности солей."""
           salt1 = self.hasher.generate_salt()
           salt2 = self.hasher.generate_salt()

           assert salt1 != salt2

### Запуск тестов:

.. code-block:: bash

   # Все тесты
   pytest tests/

   # Конкретный тест
   pytest tests/test_password.py -v

   # С покрытием кода
   pytest --cov=DataBase tests/test_password.py

Стиль кода
----------

### Рекомендации:

1. **Именование:**
   - Классы: `CamelCase` (например, `DatabaseManager`)
   - Функции/методы: `snake_case` (например, `connect_to_database`)
   - Константы: `UPPER_CASE` (например, `MAX_LOGIN_ATTEMPTS`)

2. **Docstrings:** Используйте Google-style docstrings:

   .. code-block:: python

      class DatabaseManager:
          """Менеджер для работы с базой данных.

          Attributes:
              dbname (str): Название базы данных.
              user (str): Имя пользователя БД.
              password (str): Пароль пользователя.
              host (str): Хост базы данных.
              port (str): Порт подключения.
              connection: Соединение с БД.
          """

          def connect(self):
              """Устанавливает соединение с базой данных.

              Returns:
                  bool: True если подключение успешно, False в противном случае.

              Raises:
                  DatabaseError: Если не удается подключиться.
              """
              # реализация

3. **Типизация:** Используйте type hints:

   .. code-block:: python

      def create_user(self, login: str, password: str, email: str) -> bool:
          """Создает нового пользователя.

          Args:
              login: Логин пользователя.
              password: Пароль пользователя.
              email: Email пользователя.

          Returns:
              True если пользователь создан успешно.
          """

Отладка
-------

### Логирование:

Добавьте логирование в `Database_Manager.py`:

.. code-block:: python

   import logging

   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   logger = logging.getLogger(__name__)

   class DatabaseManager:
       def connect(self):
           try:
               logger.info(f"Connecting to database {self.dbname}")
               self.connection = psycopg2.connect(...)
               logger.info("Connection established successfully")
           except psycopg2.Error as e:
               logger.error(f"Failed to connect to database: {e}")
               raise

### Отладка Qt приложения:

.. code-block:: python

   # Включение отладки сти