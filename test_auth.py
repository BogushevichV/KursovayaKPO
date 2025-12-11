"""
Тестовый скрипт для проверки аутентификации
Проверяет подключение к БД и аутентификацию пользователя test с паролем 123
"""
import psycopg2
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Server.config import DB_CONFIG
from Server.password_hasher import PasswordHasher

def test_connection():
    """Тестирует подключение к БД"""
    print("Тестирование подключения к БД...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"✓ Подключение успешно!")
        return conn
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return None

def check_admin(conn, login="test"):
    """Проверяет данные администратора в БД"""
    print(f"\nПроверка администратора '{login}' в БД...")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT login, password_hash, salt, email FROM admins WHERE login = %s", (login,))
        record = cursor.fetchone()
        
        if not record:
            print(f"✗ Администратор '{login}' не найден в БД")
            return None
        
        db_login, db_hash, db_salt, db_email = record
        print(f"✓ Найден администратор:")
        print(f"  Логин: {db_login}")
        print(f"  Email: {db_email}")
        print(f"  Salt (первые 20 символов): {db_salt[:20]}...")
        print(f"  Hash (первые 20 символов): {db_hash[:20]}...")
        
        return {
            'login': db_login,
            'hash': db_hash,
            'salt': db_salt,
            'email': db_email
        }
    except Exception as e:
        print(f"✗ Ошибка при проверке: {e}")
        return None

def test_password_verification(password, stored_hash, stored_salt):
    """Тестирует верификацию пароля"""
    print(f"\nТестирование верификации пароля...")
    print(f"Введенный пароль: {password}")
    
    # Генерируем хеш с тем же солью
    test_hash = PasswordHasher.hash_password(password, stored_salt)
    
    print(f"Тестовый хеш (первые 20 символов): {test_hash[:20]}...")
    print(f"Сохраненный хеш (первые 20 символов): {stored_hash[:20]}...")
    
    # Проверяем через verify_password
    is_valid = PasswordHasher.verify_password(password, stored_hash, stored_salt)
    
    print(f"Результат verify_password: {is_valid}")
    print(f"Хеши совпадают: {test_hash == stored_hash}")
    
    return is_valid

def main():
    print("=" * 80)
    print("ТЕСТ АУТЕНТИФИКАЦИИ")
    print("=" * 80)
    print()
    
    # Тест подключения
    conn = test_connection()
    if not conn:
        return
    
    # Проверка администратора
    admin_data = check_admin(conn, "test")
    if not admin_data:
        print("\nПопробуйте создать администратора через init_database.py")
        conn.close()
        return
    
    # Тест верификации пароля
    password = "123"
    is_valid = test_password_verification(
        password,
        admin_data['hash'],
        admin_data['salt']
    )
    
    print()
    print("=" * 80)
    if is_valid:
        print("✓ ПАРОЛЬ ВЕРНЫЙ - аутентификация должна работать!")
    else:
        print("✗ ПАРОЛЬ НЕВЕРНЫЙ - проверьте пароль в БД")
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nТест прерван.")
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()






