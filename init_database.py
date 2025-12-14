"""
Одноразовая программа для создания базы данных и первого администратора
Запускать только один раз для инициализации БД
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

# Добавляем путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем PasswordHasher из проекта
try:
    from Server.password_hasher import PasswordHasher
    print("✓ Используется PasswordHasher из проекта")
except ImportError as e:
    print(f"✗ ОШИБКА: Не удалось импортировать PasswordHasher: {e}")
    print("Убедитесь, что файл DataBase/password_hasher.py существует")
    sys.exit(1)

# Конфигурация БД
try:
    from Server.config import DB_CONFIG
except ImportError:
    # Запрашиваем пароль у пользователя
    import getpass
    print("\n⚠ Файл конфигурации не найден. Введите данные для подключения:")
    db_password = getpass.getpass("Пароль PostgreSQL (по умолчанию для пользователя postgres): ")

    DB_CONFIG = {
        'dbname': 'ExaminationReport',
        'user': 'postgres',
        'password': db_password if db_password else '02032006',
        'host': '127.0.0.1',
        'port': '5432'
    }


def test_connection():
    """Тестирует подключение к PostgreSQL"""
    print("Тестирование подключения к PostgreSQL...")
    conn_params = DB_CONFIG.copy()
    conn_params['dbname'] = 'postgres'

    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✓ Подключение успешно!")
        print(f"✓ Версия PostgreSQL: {version[:50]}...")
        cursor.close()
        conn.close()
        return True
    except psycopg2.OperationalError as e:
        print(f"✗ Ошибка подключения!")
        print(f"  Причина: {e}")
        print("\nВозможные решения:")
        print("  1. Проверьте, что PostgreSQL запущен")
        print("  2. Проверьте логин и пароль")
        print("  3. Проверьте хост и порт")
        print(f"\nТекущие настройки:")
        print(f"  Хост: {DB_CONFIG['host']}")
        print(f"  Порт: {DB_CONFIG['port']}")
        print(f"  Пользователь: {DB_CONFIG['user']}")
        return False
    except Exception as e:
        print(f"✗ Неожиданная ошибка: {e}")
        return False


def create_database():
    """Создает базу данных, если её нет"""
    conn_params = DB_CONFIG.copy()
    conn_params['dbname'] = 'postgres'

    try:
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Проверяем существование БД
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_CONFIG['dbname'],)
        )

        if cursor.fetchone():
            print(f"✓ База данных '{DB_CONFIG['dbname']}' уже существует.")
        else:
            cursor.execute(f'CREATE DATABASE "{DB_CONFIG["dbname"]}"')
            print(f"✓ База данных '{DB_CONFIG['dbname']}' успешно создана.")

        cursor.close()
        conn.close()
        return True

    except psycopg2.errors.InsufficientPrivilege:
        print(f"✗ Недостаточно прав для создания базы данных.")
        print(f"  Пользователь '{DB_CONFIG['user']}' должен иметь права CREATEDB.")
        return False
    except Exception as e:
        print(f"✗ Ошибка при создании базы данных: {e}")
        return False


def create_tables():
    """Создает необходимые таблицы в БД"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Создаем таблицу admins
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                login VARCHAR(50) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Таблица 'admins' создана.")

        # Создаем таблицу users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                login VARCHAR(50) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Таблица 'users' создана.")

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"✗ Ошибка при создании таблиц: {e}")
        return False


def create_admin(login: str, password: str, email: str):
    """Создает администратора"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Проверяем существующих администраторов
        cursor.execute("SELECT COUNT(*) FROM admins")
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"\nВ базе данных уже есть {count} администратор(ов).")
            response = input("Создать еще одного администратора? (y/n): ")
            if response.lower() != 'y':
                print("Создание администратора отменено.")
                cursor.close()
                conn.close()
                return False

        # Генерируем соль и хеш
        salt = PasswordHasher.generate_salt()
        password_hash = PasswordHasher.hash_password(password, salt)

        # Вставляем администратора
        cursor.execute("""
            INSERT INTO admins (login, password_hash, salt, email)
            VALUES (%s, %s, %s, %s)
        """, (login, password_hash, salt, email))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✓ Администратор '{login}' успешно создан!")
        return True

    except psycopg2.errors.UniqueViolation:
        print(f"✗ Администратор с логином '{login}' или email '{email}' уже существует.")
        return False
    except Exception as e:
        print(f"✗ Ошибка при создании администратора: {e}")
        return False


def main():
    """Основная функция инициализации"""
    print("=" * 80)
    print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
    print("=" * 80)
    print()

    # Тест подключения
    print("Шаг 0: Тестирование подключения...")
    if not test_connection():
        print("\n❌ Невозможно продолжить без подключения к PostgreSQL.")
        return
    print()

    # Создание БД
    print("Шаг 1: Создание базы данных...")
    if not create_database():
        print("\n❌ Ошибка: не удалось создать базу данных.")
        return
    print()

    # Создание таблиц
    print("Шаг 2: Создание таблиц...")
    if not create_tables():
        print("\n❌ Ошибка: не удалось создать таблицы.")
        return
    print()

    # Создание администратора
    print("Шаг 3: Создание администратора...")
    print("Введите данные для администратора:")

    login = input("Логин: ").strip()
    if not login:
        print("✗ Ошибка: логин не может быть пустым.")
        return

    password = input("Пароль: ").strip()
    if not password:
        print("✗ Ошибка: пароль не может быть пустым.")
        return

    if len(password) < 6:
        print("⚠ Предупреждение: пароль слишком короткий (рекомендуется минимум 6 символов).")
        response = input("Продолжить? (y/n): ")
        if response.lower() != 'y':
            return

    email = input("Email: ").strip()
    if not email or '@' not in email:
        print("✗ Ошибка: введите корректный email.")
        return

    if not create_admin(login, password, email):
        print("\n❌ Ошибка: не удалось создать администратора.")
        return

    print()
    print("=" * 80)
    print("✓ ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 80)
    print()
    print(f"База данных: {DB_CONFIG['dbname']}")
    print(f"Хост: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"Создан администратор: {login} ({email})")
    print()
    print("Теперь вы можете запустить сервер: python Server/db_server.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Инициализация прервана пользователем.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()