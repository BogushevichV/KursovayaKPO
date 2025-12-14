Разработка
==========

Технологический стек
--------------------

### Клиентская часть:
- **Python 3.9+** - основной язык программирования
- **PySide6** - фреймворк для создания графического интерфейса (альтернатива PyQt)
- **Qt Framework** - кроссплатформенный фреймворк для GUI (используется через PySide6)
- **Qt Linguist** - инструмент для интернационализации и локализации
- **openpyxl** - работа с Excel файлами
- **python-docx** - генерация Word документов
- **requests** - HTTP клиент для общения с сервером

### Серверная часть:
- **Flask** - микро-фреймворк для создания REST API
- **Flask-CORS** - обработка CORS для кросс-доменных запросов
- **psycopg2** - адаптер PostgreSQL для Python
- **hashlib** - криптографическое хеширование паролей

### База данных:
- **PostgreSQL 13+** - реляционная СУБД
- **Схема БД** - кастомная схема для управления учебными ведомостями

### Инструменты разработки:
- **pytest** - фреймворк для тестирования
- **pytest-qt** - тестирование Qt приложений
- **Sphinx** - генерация документации
- **Git** - система контроля версий
- **GitHub Actions** - CI/CD пайплайн

Архитектурные паттерны
----------------------

### 1. Клиент-серверная архитектура (Client-Server)
Проект использует классическую клиент-серверную модель с четким разделением ответственности:

- **Клиент** отвечает за:
  - Пользовательский интерфейс (GUI)
  - Валидацию ввода данных на стороне клиента
  - Отображение данных в удобном формате
  - Локализацию интерфейса

- **Сервер** отвечает за:
  - Безопасное хранение данных в БД
  - Бизнес-логику приложения
  - Аутентификацию и авторизацию
  - Централизованное управление данными

### 2. REST API (Representational State Transfer)
Сервер предоставляет RESTful API с использованием следующих принципов:

- **Stateless** - каждый запрос содержит всю необходимую информацию
- **Ресурсо-ориентированность** - эндпоинты соответствуют сущностям (/api/users, /api/grades)
- **Стандартные HTTP методы**:
  - GET - получение данных
  - POST - создание новых данных
  - PUT/PATCH - обновление данных
  - DELETE - удаление данных

- **JSON формат** - все данные передаются в формате JSON

.. code-block:: text

   ### 3. Многоуровневая архитектура (N-Tier Architecture)
   Проект разделен на логические уровни:
   ┌─────────────────────────────────────────┐
   │ Presentation Layer (GUI) │ ← PySide6 Windows
   ├─────────────────────────────────────────┤
   │ Business Logic Layer │ ← Client Business Logic
   ├─────────────────────────────────────────┤
   │ Data Access Layer (Client) │ ← HTTP API Client
   ├─────────────────────────────────────────┤
   │ REST API Layer (Server) │ ← Flask Endpoints
   ├─────────────────────────────────────────┤
   │ Business Logic Layer (Server) │ ← Server Business Logic
   ├─────────────────────────────────────────┤
   │ Data Access Layer (Database) │ ← PostgreSQL + psycopg2
   └─────────────────────────────────────────┘

### 4. Стратегия (Strategy Pattern)
Используется для различных алгоритмов аутентификации:

class Authenticator:
    def authenticate(self, login: str, password: str) -> bool:
        pass

class AdminAuthenticator(Authenticator):
    def authenticate(self, login: str, password: str) -> bool:
        # Специфичная логика аутентификации администратора
        pass

class UserAuthenticator(Authenticator):
    def authenticate(self, login: str, password: str) -> bool:
        # Специфичная логика аутентификации пользователя
        pass
5. Фасад (Facade Pattern)
DatabaseServerClient выступает в роли фасада, скрывающего сложность HTTP запросов:

class DatabaseServerClient:
    def save_data(self, group_name: str, course: str, ...) -> bool:
        # Инкапсулирует логику HTTP запросов, сериализацию JSON,
        # обработку ошибок и повторные попытки
        pass
6. Наблюдатель (Observer Pattern)
Широко используется в Qt для связи между компонентами:

class WelcomeWindow(QMainWindow):
    user_login_requested = Signal()  # Сигнал при нажатии кнопки
    admin_login_requested = Signal()

    def _handle_user_login(self):
        self.user_login_requested.emit()  # Уведомление подписчиков
7. Делегат (Delegate Pattern)
Для кастомного ввода данных в таблицах:

class GradeItemDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        # Создание кастомного редактора для ячеек с оценками
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator(1, 10))
        return editor
8. Dependency Injection
Внедрение зависимостей через конструкторы:

class AdminWindow(QMainWindow):
    def __init__(self, db_authenticator, account_manager, welcome_window):
        self.db_auth = db_authenticator  # Внедренная зависимость
        self.account_manager = account_manager
        self.welcome_window = welcome_window
9. Репозиторий (Repository Pattern)
Абстракция доступа к данным на сервере:

class ServerDBAuthenticator:
    def authenticate_admin(self, login: str, password: str) -> bool:
        # Абстрагирует доступ к таблице администраторов
        query = "SELECT password_hash, salt FROM admins WHERE login = %s"
        # ...
### 10. Пассивная модель представления (Passive View)

В GUI используется пассивная модель представления для улучшения тестируемости:

- **View (Окна)** - только отображает данные и передает пользовательский ввод
- **Presenter (Логика окон)** - обрабатывает бизнес-логику, связывает View и Model
- **Model (Данные)** - хранятся на сервере, обрабатываются через API

Модульная структура проекта:

### Клиентские модули

**`welcome_window.py`** - Точка входа в приложение:
    - Отображение стартового окна
    - Выбор языка интерфейса
    - Навигация к окнам пользователя/администратора

**`user_window.py`** - Аутентификация пользователя:
    - Ввод учетных данных
    - Валидация ввода
    - Обработка ошибок аутентификации
    - Открытие основного приложения

**`admin_window.py`** - Панель администратора:
    - Управление учетными записями
    - Управление данными БД
    - Отправка email с учетными данными
    - Расширенная аутентификация с ограничением попыток

**`examination_report_app.py`** - Основное рабочее окно:
    - Создание и редактирование ведомостей
    - Импорт данных из Excel
    - Поиск и фильтрация данных
    - Генерация Word документов
    - Валидация и сохранение данных

**`client_requests.py`** - HTTP клиент для API:
    - Инкапсуляция логики HTTP запросов
    - Обработка ошибок сети
    - Сериализация/десериализация JSON
    - Управление сессиями

### Серверные модули

**`main.py`** (Flask app) - REST API сервер:
    - Маршрутизация HTTP запросов
    - Валидация входящих данных
    - Обработка ошибок и исключений
    - Логирование всех операций

**`db_handlers.py`** - Обработчики базы данных:
    - Абстракция доступа к БД
    - Бизнес-логика работы с данными
    - Транзакционное выполнение запросов
    - Безопасность (SQL инъекции)

**`server_db_saver.py`** - Сохранение данных:
    - Комплексная логика сохранения связанных данных
    - Управление транзакциями
    - Обработка зависимостей между сущностями

**`logger.py`** - Система логирования:
    - Структурированное логирование в JSON формате
    - Логирование всех операций с БД
    - Аудит действий пользователей
    - Ротация лог-файлов

**`password_hasher.py`** - Криптографические операции:
    - Генерация криптографически безопасной соли
    - Хеширование паролей с использованием SHA256
    - Верификация паролей

### Общие модули

**`config.py`** - Конфигурация приложения:
    - Централизованное хранение настроек
    - Поддержка разных окружений (dev/prod)
    - Безопасное хранение секретов

**`translations/`** - Интернационализация:
    - Поддержка русского, английского, китайского языков
    - Динамическая смена языка
    - Локализация дат, чисел и форматов

Стиль написания кода
---------------------

1. Соглашения об именовании
Классы - PascalCase (верблюжий регистр с заглавной буквы):

class DatabaseManager:
class PasswordHasher:
class WelcomeWindow:
Методы и функции - snake_case (нижний регистр с подчеркиваниями):

def connect_to_database():
def validate_user_input():
def calculate_average_grade():
Переменные и атрибуты - snake_case:

student_name = "Иванов И.И."
gradebook_number = "12345"
is_authenticated = True
Константы - UPPER_CASE (верхний регистр с подчеркиваниями):

MAX_LOGIN_ATTEMPTS = 5
DEFAULT_SERVER_URL = "http://localhost:5000"
VALID_GRADES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
Private члены класса - _leading_underscore:

class DatabaseManager:
    def __init__(self):
        self._connection = None  # Внутренняя переменная
        self._logger = self._setup_logger()

    def _setup_logger(self):  # Внутренний метод
        pass
2. Аннотации типов (Type Hints)
Проект активно использует аннотации типов для улучшения читаемости и поддержки IDE:

from typing import Optional, List, Dict, Tuple, Any

def authenticate_user(login: str, password: str) -> bool:
    """
    Args:
        login: Логин пользователя
        password: Пароль пользователя

    Returns:
        True если аутентификация успешна, иначе False
    """
    pass

def get_student_grades(group_number: str, subject: str) -> Optional[List[Tuple[str, str]]]:
    """
    Args:
        group_number: Номер группы
        subject: Название предмета

    Returns:
        Список кортежей (имя студента, оценка) или None при ошибке
    """
    pass
3. Docstrings в Google стиле
Все публичные методы и классы документированы с использованием Google-стиля:

class DatabaseManager:
    """Менеджер для работы с базой данных.

    Attributes:
        dbname (str): Название базы данных.
        user (str): Имя пользователя БД.
        host (str): Хост базы данных.
        port (int): Порт подключения.
        connection (psycopg2.connection): Соединение с БД.
    """

    def connect(self) -> bool:
        """Устанавливает соединение с базой данных.

        Returns:
            bool: True если подключение успешно, False в противном случае.

        Raises:
            DatabaseError: Если не удается подключиться к БД.
            ConnectionError: Если хост недоступен.
        """
        pass
4. Структура файлов и импортов
Порядок импортов:

Стандартные библиотеки Python

Сторонние библиотеки

Локальные модули проекта

import os
import sys
from datetime import datetime
from typing import Optional, List

from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

from Client.Back.client_requests import DatabaseServerClient
from Client.Back.account_validation import Authenticator
Разделение кода по логическим блокам:

# 1. Импорты
# 2. Константы
# 3. Классы и функции
# 4. Точка входа (если есть)
5. Обработка ошибок и исключений
Используется структурированная обработка ошибок с конкретными типами исключений:

try:
    result = self.client.authenticate_admin(login, password)
    if result:
        print(f"Аутентификация успешна для администратора '{login}'")
    else:
        print(f"Аутентификация не удалась для администратора '{login}'")
    return result
except ConnectionError as e:
    logger.error(f"Сервер недоступен: {e}")
    show_network_error_message()
    return False
except ValueError as e:
    logger.error(f"Неверные данные: {e}")
    return False
except Exception as e:
    logger.error(f"Неожиданная ошибка: {e}")
    return False
6. Логирование
Используется структурированное логирование с разными уровнями:

import logging

logger = logging.getLogger(__name__)

def save_data(self, data: dict) -> bool:
    logger.debug(f"Начало сохранения данных: {data}")

    try:
        # Логика сохранения
        logger.info(f"Данные успешно сохранены: {len(data)} записей")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных: {e}", exc_info=True)
        return False
7. Форматирование кода
Проект использует Black-совместимое форматирование:

Длина строки: 100 символов

Двойные кавычки для строк

4 пробела для отступов

Пустые строки для разделения логических блоков

def complex_function(
    param1: str,
    param2: int,
    param3: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Пример правильно отформатированной функции."""

    if param3 is None:
        param3 = []

    result = {
        "processed": True,
        "param1_length": len(param1),
        "param2_squared": param2 ** 2,
        "items_processed": len(param3),
    }

    return result
8. Принципы SOLID
Проект следует принципам SOLID:

Single Responsibility Principle (SRP):

# Каждый класс имеет одну ответственность
class PasswordHasher:  # Только хеширование паролей
class Logger:          # Только логирование
class Authenticator:   # Только аутентификация
Open/Closed Principle (OCP):

class ReportExporter:
    def export(self, data, format_type):
        if format_type == "word":
            return self._export_to_word(data)
        elif format_type == "pdf":  # Легко добавить новый формат
            return self._export_to_pdf(data)
Liskov Substitution Principle (LSP):

class Authenticator:
    def authenticate(self, login: str, password: str) -> bool:
        pass

class AdminAuthenticator(Authenticator):  # Можно заменить базовым классом
    def authenticate(self, login: str, password: str) -> bool:
        # Специфичная логика для администраторов
        pass
Interface Segregation Principle (ISP):

# Разделенные интерфейсы вместо одного большого
class DataReader:
    def read(self) -> List[dict]:
        pass

class DataWriter:
    def write(self, data: List[dict]) -> bool:
        pass
Dependency Inversion Principle (DIP):

class ReportManager:
    def __init__(self, db_client: DatabaseClient):  # Зависимость от абстракции
        self.client = db_client
9. Шаблоны проектирования Qt
Модель-Представление (Model-View):

# QTableWidget для отображения данных
self.table = QTableWidget()
self.table.setColumnCount(3)
self.table.setHorizontalHeaderLabels(["ФИО", "Зачетка", "Оценка"])

# Делегаты для кастомного редактирования
self.table.setItemDelegateForColumn(2, GradeItemDelegate())
Сигналы и слоты (Signals and Slots):

class WelcomeWindow(QMainWindow):
    # Объявление сигналов
    user_login_requested = Signal()
    admin_login_requested = Signal()
    language_changed = Signal(str)

    def __init__(self):
        # Соединение сигналов со слотами
        self.user_button.clicked.connect(self._handle_user_login)
        self.language_box.currentIndexChanged.connect(self._emit_language_change)
10. Безопасность кода
Валидация входных данных:

def validate_input(self, login: str, password: str) -> bool:
    if not login or not password:
        return False
    if len(login) < 3 or len(login) > 50:
        return False
    if len(password) < 6:
        return False
    if "<" in login or ">" in login:  # Защита от XSS
        return False
    return True
Параметризованные SQL запросы:

# НЕПРАВИЛЬНО (уязвимо для SQL инъекций)
cursor.execute(f"SELECT * FROM users WHERE login = '{login}'")

# ПРАВИЛЬНО (безопасно)
cursor.execute("SELECT * FROM users WHERE login = %s", (login,))
Хеширование паролей:

class PasswordHasher:
    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        salted_password = password + salt
        return hashlib.sha256(salted_password.encode()).hexdigest()

Тестирование
------------

Проект использует комплексную систему тестирования, охватывающую все компоненты клиент-серверной архитектуры.
Тесты разделены на три основные категории: клиентские тесты (GUI), серверные тесты (API) и тесты бизнес-логики (DB handlers).

.. code-block:: text

   ### Структура тестов
   tests/
   ├── 📁 client/ # Тесты клиентской части
   │ ├── test_gradebook_app.py # Тесты основного приложения ведомостей
   │ ├── test_welcome_window.py # Тесты стартового окна
   │ ├── test_admin_window.py # Тесты окна администратора
   │ └── test_user_window.py # Тесты окна входа пользователя
   │
   ├── 📁 server/ # Тесты серверной части
   │ ├── test_server_api.py # Тесты API endpoints (REST)
   │ └── test_db_handlers.py # Тесты обработчиков базы данных
   │
   └── conftest.py # Общие фикстуры pytest

### Клиентские тесты (GUI)

Клиентские тесты используют `pytest-qt` для тестирования PySide6 GUI приложения. Они проверяют корректность работы
окон, взаимодействие пользователя с интерфейсом и обработку событий.

#### Тесты WelcomeWindow (`test_welcome_window.py`)

Проверяют функциональность стартового окна приложения:

- Наличие всех виджетов (метки, кнопки, выпадающий список)
- Корректность начальных текстов на русском языке
- Эмиссию сигналов при нажатии кнопок
- Загрузку и отображение изображения
- Функциональность смены языка интерфейса

**Пример теста:**

.. code-block:: python
   :linenos:

   def test_user_login_signal(qtbot, window):
       with qtbot.waitSignal(window.user_login_requested, timeout=500):
           qtbot.mouseClick(window.user_button, Qt.LeftButton)

   def test_language_change_signal(qtbot, window):
       with qtbot.waitSignal(window.language_changed, timeout=500):
           window.language_box.setCurrentIndex(1)  # переключаем язык

#### Тесты UserWindow (`test_user_window.py`)

Проверяют окно аутентификации пользователя:

- Корректную аутентификацию через API
- Обработку неверных учетных данных
- Механизм ограничения попыток входа
- Открытие основного приложения при успешной аутентификации
- Переход к окну приветствия при закрытии

**Пример теста:**

.. code-block:: python
   :linenos:

   def test_successful_login(qtbot, user_window, mock_db_authenticator, monkeypatch):
       mock_db_authenticator.should_authenticate = True

       class FakeGradeBook:
           def __init__(self):
               self.opened = True
           def show(self):
               self.was_shown = True

       monkeypatch.setattr("User.UserWindow.GradeBookApp", FakeGradeBook)

       qtbot.mouseClick(user_window.login_button, Qt.LeftButton)
       assert isinstance(user_window.grade_book, FakeGradeBook)

#### Тесты GradeBookApp (`test_gradebook_app.py`)

Проверяют основное приложение для работы с ведомостями:

- Начальное состояние UI элементов
- Логику добавления/удаления пустых строк в таблице
- Переключение между режимами оценок (числа) и зачетов (зачтено/не зачтено)
- Функциональность импорта данных из Excel
- Валидацию обязательных полей при создании отчета
- Механизм возврата к окну приветствия

**Пример теста:**

.. code-block:: python
   :linenos:

   def test_adds_new_empty_row_when_editing_last(gradebook, qtbot):
       """Если последняя строка заполнена — добавляется новая."""
       gradebook.table.item(0, 0).setText("Иванов И.И.")
       gradebook.table.item(0, 1).setText("12345")
       gradebook.table.item(0, 2).setText("9")

       gradebook.handle_item_changed(gradebook.table.item(0, 0))
       assert gradebook.table.rowCount() == 2

### Серверные тесты (API)

Серверные тесты проверяют работу REST API и обработчиков базы данных. Используется Flask test client
для имитации HTTP запросов к API endpoints.

#### Тесты API endpoints (`test_server_api.py`)

Проверяют все REST API endpoints сервера:

1. **Health check** - проверка доступности сервера
2. **Аутентификация** - авторизация администраторов и пользователей
3. **Управление учетными записями** - создание и удаление пользователей и администраторов
4. **Работа с данными** - сохранение и получение данных о студентах и оценках
5. **Обработка ошибок** - корректная обработка невалидных запросов и ошибок сервера

**Пример теста аутентификации:**

.. code-block:: python
   :linenos:

   def test_authenticate_admin_success(self, client, test_admin):
       response = client.post('/api/auth/admin', json={
           'login': test_admin['login'],
           'password': test_admin['password']
       })
       assert response.status_code == 200
       data = response.get_json()
       assert data['success'] is True

**Пример теста обработки ошибок:**

.. code-block:: python
   :linenos:

   def test_404_not_found(self, client):
       response = client.get('/api/nonexistent')
       assert response.status_code == 404
       data = response.get_json()
       assert data['success'] is False
       assert 'error' in data

#### Тесты DB handlers (`test_db_handlers.py`)

Проверяют низкоуровневую работу с базой данных:

- Корректность аутентификации через прямой доступ к БД
- Создание и удаление учетных записей
- Работу системы хэширования паролей
- Обработку edge cases (дублирование логинов, несуществующие аккаунты)

**Пример теста работы с базой данных:**

.. code-block:: python
   :linenos:

   class TestServerDBAuthenticator:
       def test_authenticate_admin_success(self, test_admin_credentials):
           account_manager = ServerAccountManager(**DB_CONFIG)
           auth = ServerDBAuthenticator(**DB_CONFIG)

           # Создаем администратора
           account_manager.create_account(
               "admin",
               test_admin_credentials['login'],
               test_admin_credentials['password'],
               test_admin_credentials['email']
           )

           # Тестируем аутентификацию
           result = auth.authenticate_admin(
               test_admin_credentials['login'],
               test_admin_credentials['password']
           )
           assert result is True

### Тестирование безопасности

Проект включает тесты для проверки безопасности системы:

1. **Хэширование паролей** - проверка использования соли и корректности верификации
2. **Валидация входных данных** - защита от SQL-инъекций и некорректных данных
3. **Ограничение попыток входа** - предотвращение brute-force атак
4. **Проверка привилегий** - разделение доступа между пользователями и администраторами

**Пример теста безопасности:**

.. code-block:: python
   :linenos:

   class TestPasswordHashing:
       def test_password_verification_success(self):
           password = "test_password_123"
           salt = PasswordHasher.generate_salt()
           hashed = PasswordHasher.hash_password(password, salt)

           assert PasswordHasher.verify_password(password, hashed, salt) is True

       def test_password_verification_failure(self):
           password = "test_password_123"
           wrong_password = "wrong_password"
           salt = PasswordHasher.generate_salt()
           hashed = PasswordHasher.hash_password(password, salt)

           assert PasswordHasher.verify_password(wrong_password, hashed, salt) is False

### Запуск тестов

#### Для клиентских тестов:

.. code-block:: bash

   # Запуск всех клиентских тестов
   pytest tests/client/ -v

   # Запуск тестов с покрытием кода
   pytest tests/client/ --cov=Client --cov-report=html

   # Запуск конкретного тестового файла
   pytest tests/client/test_gradebook_app.py -v

#### Для серверных тестов:

.. code-block:: bash

   # Запуск всех серверных тестов
   pytest tests/server/ -v

   # Запуск только тестов API
   pytest tests/server/test_server_api.py -v

   # Запуск тестов с логированием
   pytest tests/server/ -v --log-cli-level=INFO

#### Для запуска всех тестов:

.. code-block:: bash

   # Запуск всех тестов проекта
   pytest tests/ -v

   # Запуск с измерением покрытия кода
   pytest --cov=Client --cov=Server --cov-report=html tests/

   # Параллельный запуск тестов
   pytest -n auto tests/

### Фикстуры и моки

Тесты используют систему фикстур pytest для создания тестового окружения:

#### Клиентские фикстуры:

- `qtbot` - для тестирования Qt приложений
- Моки аутентификаторов и менеджеров БД
- Тестовые данные студентов и групп

#### Серверные фикстуры:

- `client` - Flask test client
- `test_admin` / `test_user` - тестовые учетные записи
- Моки подключений к базе данных

**Пример использования фикстур:**

.. code-block:: python
   :linenos:

   @pytest.fixture
   def client():
       """Создает тестовый клиент Flask"""
       app.config['TESTING'] = True
       with app.test_client() as client:
           yield client

   @pytest.fixture(scope='function')
   def test_admin():
       """Создает тестового администратора и удаляет его после теста"""
       account_manager = ServerAccountManager(**DB_CONFIG)
       test_login = f"test_admin_{random_string(6)}"

       account_manager.create_account("admin", test_login, "password", f"{test_login}@test.com")

       yield {'login': test_login, 'password': 'password'}

       account_manager.delete_account("admin", test_login)

### Интеграционные тесты

Проект поддерживает интеграционные тесты, проверяющие взаимодействие клиента и сервера:

1. **Полный цикл аутентификации** - от ввода данных в GUI до проверки в базе данных
2. **Работа с данными** - сохранение данных через клиент и проверка их наличия на сервере
3. **Обработка ошибок сети** - тестирование поведения при недоступности сервера

### Тестирование производительности

Для критических компонентов реализованы тесты производительности:

- **API endpoints** - проверка времени ответа при высокой нагрузке
- **Работа с БД** - тестирование скорости выполнения запросов
- **Генерация отчетов** - измерение времени создания Word документов

### Непрерывная интеграция

Тесты интегрированы в CI/CD pipeline через GitHub Actions. При каждом коммите автоматически запускаются:

1. Клиентские тесты
2. Серверные тесты
3. Проверка покрытия кода
4. Статический анализ кода

Конфигурация CI находится в `.github/workflows/test.yml`.

### Отчеты о тестировании

Для анализа результатов тестирования генерируются отчеты:

- **HTML отчеты покрытия кода** (через pytest-cov)
- **JUnit XML отчеты** для интеграции с CI системами
- **Визуальные отчеты** о выполнении тестов

### Рекомендации по написанию тестов

1. **Изоляция тестов:** Каждый тест должен быть независим от других
2. **Чистота данных:** Тестовые данные создаются и удаляются в рамках теста
3. **Моки зависимостей:** Внешние сервисы (SMTP, файловая система) мокаются
4. **Тестирование edge cases:** Особое внимание граничным условиям
5. **Читаемость:** Тесты должны быть понятны без дополнительных комментариев

### Пример полного тестового сценария

.. code-block:: python
   :linenos:

   def test_complete_exam_report_workflow():
       """Полный тест создания экзаменационной ведомости"""

       # 1. Аутентификация
       client = DatabaseServerClient("http://localhost:5001")
       assert client.authenticate_user("test_user", "test_pass") is True

       # 2. Создание группы и студентов
       students_data = [
           {'name': 'Иванов И.И.', 'gradebook': '12345', 'grade': '8'},
           {'name': 'Петров П.П.', 'gradebook': '12346', 'grade': '9'}
       ]

       result = client.save_data(
           group_name="Группа 101",
           course="3",
           semester="1",
           subject_name="Математика",
           students_data=students_data
       )

       assert result is True

       # 3. Получение данных для проверки
       grades = client.find_subject_grades(
           subject_name="Математика",
           group_number="Группа 101",
           course="3",
           semester="1"
       )

       assert len(grades) == 2
       assert grades[0][0] == 'Иванов И.И.'

### Тестирование многоязычной поддержки

Проект включает тесты для проверки корректности перевода интерфейса:

- Проверка текстов на всех поддерживаемых языках
- Тестирование динамической смены языка
- Проверка корректности отображения спецсимволов

### Отладка тестов

Для отладки проблемных тестов можно использовать:

.. code-block:: bash

   # Запуск теста с отладочной информацией
   pytest tests/ -v --tb=long

   # Запуск теста с остановкой на первом падении
   pytest tests/ -x

   # Запуск теста с pdb для интерактивной отладки
   pytest tests/ --pdb


Заключение
----------

Проект Exam Report System представляет собой хорошо структурированное клиент-серверное приложение,
построенное с использованием современных технологий и архитектурных паттернов.

**Ключевые особенности архитектуры:**

1. **Четкое разделение ответственности** между клиентом и сервером
2. **Масштабируемая REST API архитектура** на Flask
3. **Профессиональный GUI** на PySide6 с поддержкой интернационализации
4. **Безопасное хранение данных** с использованием PostgreSQL и хеширования паролей
5. **Комплексная система тестирования**, покрывающая все компоненты приложения

**Преимущества выбранных решений:**

- **PySide6** обеспечивает кроссплатформенность и современный UI
- **Flask** предоставляет гибкость и простоту разработки REST API
- **PostgreSQL** гарантирует надежность и производительность хранения данных
- **Pytest** позволяет создавать поддерживаемые и надежные тесты

Проект следует лучшим практикам разработки, включая принципы SOLID, использование паттернов проектирования
и поддержку качественного кода через аннотации типов и документацию.