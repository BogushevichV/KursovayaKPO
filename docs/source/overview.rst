Обзор системы
=============

Архитектура
-----------

.. code-block:: text

    Exam Report/
    ├── Main.py                          # Точка входа
    ├── Welcome_Window.py               # Стартовое окно
    ├── Grade_Item_Delegate.py
    ├── Excel_Importer.py
    ├── DataBase/                       # Модули работы с БД
    |   ├── Base_User_Creator.py
    |   ├── Base_User_Remover.py
    │   ├── Database_Manager.py
    │   ├── Database_Saver.py
    │   ├── DB_Validation.py
    |   ├── Password_Hasher.py
    │   └── Report_Manager.py
    ├── User/                           # Пользовательская система
    |   ├── Create_Examination_Report.py      # Создание отчетов
    |   ├── Examination_Report_App.py  # Основное приложение
    │   ├── User_Window.py
    │   ├── User_Creator.py
    │   └── User_Remover.py
    ├── Admin/                          # Административная часть
    │   ├── Admin_Window.py
    │   ├── Admin_Creator.py
    │   └── Admin_Remover.py
    ├── translations/                   # Многоязычная поддержка
    ├── tests/                          # Тесты
    └── docs/                          # Документация

Основные функции
----------------

1. **Создание экзаменационных ведомостей**
2. **Управление пользователями** (админы/пользователи)
3. **Импорт данных из Excel** (Excel_Importer.py)
4. **Многоязычный интерфейс** (русский, английский, китайский)
5. **Безопасное хранение паролей** (Password_Hasher.py)
6. **Валидация данных** (DB_Validation.py)

Технологии
----------

* **Язык:** Python 3.x
* **GUI:** PySide6 (Qt для Python)
* **База данных:** PostgreSQL
* **Документация:** Sphinx
* **Международная поддержка:** Qt Linguist

Точка входа
-----------

Основной запуск приложения осуществляется через файл `Main.py`:

.. literalinclude:: ../../Main.py
   :language: python
   :linenos:
   :lines: 1-30
   :caption: Начало файла Main.py

Ключевые особенности реализации:

1. **Использование сигналов (Signals)**: Для связи между окнами
2. **Настройки (QSettings)**: Для сохранения языка и других параметров
3. **Динамическая загрузка переводов**: Поддержка 3 языков
4. **Разделение на модули**: Четкая архитектура проекта