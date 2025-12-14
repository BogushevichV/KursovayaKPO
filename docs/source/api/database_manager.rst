DatabaseManager
===============

.. automodule:: DataBase.Database_Manager
   :members:
   :undoc-members:
   :show-inheritance:

Описание
--------

Базовый класс для управления подключением к PostgreSQL базе данных.

Инициализация
-------------

.. code-block:: python

   db_manager = DatabaseManager(
       dbname="ExaminationReport",
       user="postgres",
       password="password123",
       host="localhost",
       port="5432"
   )

Методы
------

.. py:method:: DatabaseManager.connect()

   Устанавливает соединение с базой данных.

   **Возвращает:** None

   **Исключения:**
   - `psycopg2.OperationalError` - если не удается подключиться

.. py:method:: DatabaseManager.close()

   Закрывает соединение с базой данных.

   **Возвращает:** None

.. py:method:: DatabaseManager.commit()

   Фиксирует транзакцию.

   **Возвращает:** None

.. py:method:: DatabaseManager.rollback()

   Откатывает транзакцию.

   **Возвращает:** None

Пример использования
--------------------

.. code-block:: python

   from DataBase.Database_Manager import DatabaseManager

   # Создание экземпляра
   db = DatabaseManager(
       dbname="test_db",
       user="postgres",
       password="secret",
       host="localhost",
       port="5432"
   )

   try:
       # Подключение
       db.connect()

       # Выполнение запроса
       cursor = db.connection.cursor()
       cursor.execute("SELECT version()")
       version = cursor.fetchone()
       print(f"PostgreSQL version: {version}")

       # Фиксация изменений
       db.commit()

   except Exception as e:
       # Откат при ошибке
       db.rollback()
       print(f"Error: {e}")

   finally:
       # Закрытие соединения
       db.close()