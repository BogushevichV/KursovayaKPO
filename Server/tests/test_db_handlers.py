import pytest
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Server.db_handlers import ServerDBAuthenticator, ServerAccountManager
from Server.config import DB_CONFIG
from Server.password_hasher import PasswordHasher


@pytest.fixture(scope='function')
def test_admin_credentials():
    """Генерирует уникальные учетные данные для тестового администратора"""
    import random
    import string
    login = f"test_admin_{''.join(random.choices(string.ascii_lowercase, k=8))}"
    password = "test_password_123"
    email = f"{login}@test.com"
    return {'login': login, 'password': password, 'email': email}


@pytest.fixture(scope='function')
def test_user_credentials():
    """Генерирует уникальные учетные данные для тестового пользователя"""
    import random
    import string
    login = f"test_user_{''.join(random.choices(string.ascii_lowercase, k=8))}"
    password = "test_password_123"
    email = f"{login}@test.com"
    return {'login': login, 'password': password, 'email': email}


class TestServerDBAuthenticator:
    """Тесты для ServerDBAuthenticator"""
    
    def test_authenticate_admin_success(self, test_admin_credentials):
        """Тест успешной аутентификации администратора"""
        account_manager = ServerAccountManager(**DB_CONFIG)
        auth = ServerDBAuthenticator(**DB_CONFIG)
        
        # Создаем администратора
        try:
            account_manager.create_account(
                "admin",
                test_admin_credentials['login'],
                test_admin_credentials['password'],
                test_admin_credentials['email']
            )
        except Exception:
            pass
        
        # Тестируем аутентификацию
        result = auth.authenticate_admin(
            test_admin_credentials['login'],
            test_admin_credentials['password']
        )
        assert result is True
        
        # Удаляем тестового администратора
        try:
            account_manager.delete_account("admin", test_admin_credentials['login'])
        except Exception:
            pass
    
    def test_authenticate_admin_wrong_password(self, test_admin_credentials):
        """Тест аутентификации с неверным паролем"""
        account_manager = ServerAccountManager(**DB_CONFIG)
        auth = ServerDBAuthenticator(**DB_CONFIG)
        
        # Создаем администратора
        try:
            account_manager.create_account(
                "admin",
                test_admin_credentials['login'],
                test_admin_credentials['password'],
                test_admin_credentials['email']
            )
        except Exception:
            pass
        
        # Тестируем аутентификацию с неверным паролем
        result = auth.authenticate_admin(
            test_admin_credentials['login'],
            'wrong_password'
        )
        assert result is False
        
        # Удаляем тестового администратора
        try:
            account_manager.delete_account("admin", test_admin_credentials['login'])
        except Exception:
            pass
    
    def test_authenticate_user_success(self, test_user_credentials):
        """Тест успешной аутентификации пользователя"""
        account_manager = ServerAccountManager(**DB_CONFIG)
        auth = ServerDBAuthenticator(**DB_CONFIG)
        
        # Создаем пользователя
        try:
            account_manager.create_account(
                "user",
                test_user_credentials['login'],
                test_user_credentials['password'],
                test_user_credentials['email']
            )
        except Exception:
            pass
        
        # Тестируем аутентификацию
        result = auth.authenticate_user(
            test_user_credentials['login'],
            test_user_credentials['password']
        )
        assert result is True
        
        # Удаляем тестового пользователя
        try:
            account_manager.delete_account("user", test_user_credentials['login'])
        except Exception:
            pass


class TestServerAccountManager:
    """Тесты для ServerAccountManager"""
    
    def test_create_admin_success(self, test_admin_credentials):
        """Тест успешного создания администратора"""
        account_manager = ServerAccountManager(**DB_CONFIG)
        
        try:
            result = account_manager.create_account(
                "admin",
                test_admin_credentials['login'],
                test_admin_credentials['password'],
                test_admin_credentials['email']
            )
            assert result is True
            
            # Проверяем, что администратор действительно создан
            auth = ServerDBAuthenticator(**DB_CONFIG)
            assert auth.authenticate_admin(
                test_admin_credentials['login'],
                test_admin_credentials['password']
            ) is True
        finally:
            # Удаляем тестового администратора
            try:
                account_manager.delete_account("admin", test_admin_credentials['login'])
            except Exception:
                pass
    
    def test_create_admin_duplicate_login(self, test_admin_credentials):
        """Тест создания администратора с существующим логином"""
        account_manager = ServerAccountManager(**DB_CONFIG)
        
        try:
            # Создаем первого администратора
            account_manager.create_account(
                "admin",
                test_admin_credentials['login'],
                test_admin_credentials['password'],
                test_admin_credentials['email']
            )
            
            # Пытаемся создать второго с тем же логином
            with pytest.raises(ValueError):
                account_manager.create_account(
                    "admin",
                    test_admin_credentials['login'],
                    "different_password",
                    "different@test.com"
                )
        finally:
            # Удаляем тестового администратора
            try:
                account_manager.delete_account("admin", test_admin_credentials['login'])
            except Exception:
                pass
    
    def test_create_user_success(self, test_user_credentials):
        """Тест успешного создания пользователя"""
        account_manager = ServerAccountManager(**DB_CONFIG)
        
        try:
            result = account_manager.create_account(
                "user",
                test_user_credentials['login'],
                test_user_credentials['password'],
                test_user_credentials['email']
            )
            assert result is True
            
            # Проверяем, что пользователь действительно создан
            auth = ServerDBAuthenticator(**DB_CONFIG)
            assert auth.authenticate_user(
                test_user_credentials['login'],
                test_user_credentials['password']
            ) is True
        finally:
            # Удаляем тестового пользователя
            try:
                account_manager.delete_account("user", test_user_credentials['login'])
            except Exception:
                pass
    
    def test_delete_admin_success(self, test_admin_credentials):
        """Тест успешного удаления администратора"""
        account_manager = ServerAccountManager(**DB_CONFIG)
        
        # Создаем администратора
        try:
            account_manager.create_account(
                "admin",
                test_admin_credentials['login'],
                test_admin_credentials['password'],
                test_admin_credentials['email']
            )
        except Exception:
            pass
        
        # Удаляем администратора
        result = account_manager.delete_account("admin", test_admin_credentials['login'])
        assert result is True
        
        # Проверяем, что администратор действительно удален
        auth = ServerDBAuthenticator(**DB_CONFIG)
        assert auth.authenticate_admin(
            test_admin_credentials['login'],
            test_admin_credentials['password']
        ) is False
    
    def test_delete_nonexistent_admin(self):
        """Тест удаления несуществующего администратора"""
        account_manager = ServerAccountManager(**DB_CONFIG)
        result = account_manager.delete_account("admin", "nonexistent_admin_12345")
        assert result is False
    
    def test_create_account_invalid_type(self):
        """Тест создания аккаунта с невалидным типом"""
        account_manager = ServerAccountManager(**DB_CONFIG)
        
        with pytest.raises(ValueError, match="Неизвестный тип аккаунта"):
            account_manager.create_account(
                "invalid_type",
                "test",
                "password",
                "test@test.com"
            )
    
    def test_delete_account_invalid_type(self):
        """Тест удаления аккаунта с невалидным типом"""
        account_manager = ServerAccountManager(**DB_CONFIG)
        
        with pytest.raises(ValueError, match="Неизвестный тип аккаунта"):
            account_manager.delete_account("invalid_type", "test")


class TestPasswordHashing:
    """Тесты для хеширования паролей"""
    
    def test_password_hashing(self):
        """Тест хеширования пароля"""
        password = "test_password_123"
        salt = PasswordHasher.generate_salt()
        hashed = PasswordHasher.hash_password(password, salt)
        
        assert hashed != password
        assert len(hashed) > 0
        assert len(salt) > 0
    
    def test_password_verification_success(self):
        """Тест успешной проверки пароля"""
        password = "test_password_123"
        salt = PasswordHasher.generate_salt()
        hashed = PasswordHasher.hash_password(password, salt)
        
        assert PasswordHasher.verify_password(password, hashed, salt) is True
    
    def test_password_verification_failure(self):
        """Тест неудачной проверки пароля"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        salt = PasswordHasher.generate_salt()
        hashed = PasswordHasher.hash_password(password, salt)
        
        assert PasswordHasher.verify_password(wrong_password, hashed, salt) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

