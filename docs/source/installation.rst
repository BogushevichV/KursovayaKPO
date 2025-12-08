Установка и настройка
=====================

Предварительные требования
--------------------------

* **Python 3.9+**
* **PostgreSQL 12+**
* **pip** (менеджер пакетов Python)
* **Git** (для клонирования репозитория)

Зависимости
-----------

Файл `requirements.txt`:

.. code-block:: text

   PySide6>=6.5.0
   psycopg2-binary>=2.9.6
   openpyxl>=3.1.0

Установка
---------

1. **Клонируйте репозиторий:**

   .. code-block:: bash

      git clone https://github.com/BogushevichV/KursovayaKPO
      cd KursovayaKPO

2. **Создайте виртуальное окружение:**

   .. code-block:: bash

      python -m venv .venv

3. **Активируйте виртуальное окружение:**

   **Windows:**

   .. code-block:: bash

      .venv\Scripts\activate

   **Linux/Mac:**

   .. code-block:: bash

      source .venv/bin/activate

4. **Установите зависимости:**

   .. code-block:: bash

      pip install -r requirements.txt

Настройка базы данных
---------------------

1. **Создайте базу данных в PostgreSQL:**

   .. code-block:: sql

      CREATE DATABASE ExaminationReport;
      CREATE USER postgres WITH PASSWORD 'ваш_пароль';

2. **Настройте подключение в коде:**

   В файле `Main.py` измените параметры подключения:

   .. code-block:: python
      :linenos:
      :caption: Main.py - настройки подключения к БД
      :emphasize-lines: 3-8

      def init_db_connections(self):
          db_params = {
              'dbname': "ExaminationReport",
              'user': "postgres",
              'password': "ваш_пароль",  # ← измените здесь
              'host': "127.0.0.1",
              'port': "5432"
          }

3. **Создайте таблицы по схеме:**

   Используйте схему из файла `db_schema.txt`.

Запуск
------

.. code-block:: bash

   python Main.py

Проверка установки
------------------

После запуска вы должны увидеть стартовое окно:

.. figure:: /_static/screenshots/welcome_window.png
   :width: 600px
   :align: center
   :alt: Стартовое окно приложения

   Стартовое окно Exam Report

Устранение проблем
------------------

**Проблема:** Не удается подключиться к PostgreSQL

**Решение:**
1. Проверьте, запущен ли сервер PostgreSQL
2. Проверьте правильность логина и пароля
3. Убедитесь, что база данных существует

**Проблема:** Ошибка импорта модулей PySide6

**Решение:**
1. Переустановите PySide6: `pip install --force-reinstall PySide6`
2. Проверьте версию Python (должна быть 3.9+)