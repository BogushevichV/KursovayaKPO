"""
Тесты для API сервера базы данных
"""
import pytest
import os
import sys

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Server.main import app
from Server.config import SERVER_CONFIG, DB_CONFIG
from Server.db_handlers import ServerAccountManager
from Server.password_hasher import PasswordHasher


@pytest.fixture(scope='module')
def client():
    """Создает тестовый клиент Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='module')
def base_url():
    """Базовый URL для тестов"""
    return f"http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}"


@pytest.fixture(scope='function')
def test_admin():
    """Создает тестового администратора и удаляет его после теста"""
    account_manager = ServerAccountManager(**DB_CONFIG)
    
    # Генерируем уникальный логин для теста
    import random
    import string
    test_login = f"test_admin_{''.join(random.choices(string.ascii_lowercase, k=6))}"
    test_password = "test_password_123"
    test_email = f"{test_login}@test.com"
    
    # Создаем тестового администратора
    try:
        account_manager.create_account("admin", test_login, test_password, test_email)
    except Exception:
        pass  # Может уже существовать
    
    yield {
        'login': test_login,
        'password': test_password,
        'email': test_email
    }
    
    # Удаляем тестового администратора после теста
    try:
        account_manager.delete_account("admin", test_login)
    except Exception:
        pass


@pytest.fixture(scope='function')
def test_user():
    """Создает тестового пользователя и удаляет его после теста"""
    account_manager = ServerAccountManager(**DB_CONFIG)
    
    # Генерируем уникальный логин для теста
    import random
    import string
    test_login = f"test_user_{''.join(random.choices(string.ascii_lowercase, k=6))}"
    test_password = "test_password_123"
    test_email = f"{test_login}@test.com"
    
    # Создаем тестового пользователя
    try:
        account_manager.create_account("user", test_login, test_password, test_email)
    except Exception:
        pass  # Может уже существовать
    
    yield {
        'login': test_login,
        'password': test_password,
        'email': test_email
    }
    
    # Удаляем тестового пользователя после теста
    try:
        account_manager.delete_account("user", test_login)
    except Exception:
        pass


class TestHealthCheck:
    """Тесты для health check endpoint"""
    
    def test_health_check(self, client):
        """Тест проверки работоспособности сервера"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'message' in data


class TestAdminAuthentication:
    """Тесты для аутентификации администратора"""
    
    def test_authenticate_admin_success(self, client, test_admin):
        """Тест успешной аутентификации администратора"""
        response = client.post('/api/auth/admin', json={
            'login': test_admin['login'],
            'password': test_admin['password']
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_authenticate_admin_wrong_password(self, client, test_admin):
        """Тест аутентификации с неверным паролем"""
        response = client.post('/api/auth/admin', json={
            'login': test_admin['login'],
            'password': 'wrong_password'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is False
    
    def test_authenticate_admin_nonexistent(self, client):
        """Тест аутентификации несуществующего администратора"""
        response = client.post('/api/auth/admin', json={
            'login': 'nonexistent_admin_12345',
            'password': 'password'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is False
    
    def test_authenticate_admin_missing_fields(self, client):
        """Тест аутентификации с отсутствующими полями"""
        response = client.post('/api/auth/admin', json={
            'login': 'test'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data


class TestUserAuthentication:
    """Тесты для аутентификации пользователя"""
    
    def test_authenticate_user_success(self, client, test_user):
        """Тест успешной аутентификации пользователя"""
        response = client.post('/api/auth/user', json={
            'login': test_user['login'],
            'password': test_user['password']
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_authenticate_user_wrong_password(self, client, test_user):
        """Тест аутентификации с неверным паролем"""
        response = client.post('/api/auth/user', json={
            'login': test_user['login'],
            'password': 'wrong_password'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is False
    
    def test_authenticate_user_missing_fields(self, client):
        """Тест аутентификации с отсутствующими полями"""
        response = client.post('/api/auth/user', json={
            'login': 'test'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestAdminManagement:
    """Тесты для управления администраторами"""
    
    def test_create_admin_success(self, client):
        """Тест успешного создания администратора"""
        import random
        import string
        test_login = f"test_admin_{''.join(random.choices(string.ascii_lowercase, k=8))}"
        test_password = "test_password_123"
        test_email = f"{test_login}@test.com"
        
        response = client.post('/api/admin/create', json={
            'login': test_login,
            'password': test_password,
            'email': test_email
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Удаляем созданного администратора
        account_manager = ServerAccountManager(**DB_CONFIG)
        try:
            account_manager.delete_account("admin", test_login)
        except Exception:
            pass
    
    def test_create_admin_duplicate_login(self, client, test_admin):
        """Тест создания администратора с существующим логином"""
        response = client.post('/api/admin/create', json={
            'login': test_admin['login'],
            'password': 'password123',
            'email': 'different@test.com'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_create_admin_duplicate_email(self, client, test_admin):
        """Тест создания администратора с существующим email"""
        import random
        import string
        test_login = f"test_admin_{''.join(random.choices(string.ascii_lowercase, k=8))}"
        
        response = client.post('/api/admin/create', json={
            'login': test_login,
            'password': 'password123',
            'email': test_admin['email']
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_create_admin_missing_fields(self, client):
        """Тест создания администратора с отсутствующими полями"""
        response = client.post('/api/admin/create', json={
            'login': 'test',
            'password': 'password'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_delete_admin_success(self, client):
        """Тест успешного удаления администратора"""
        account_manager = ServerAccountManager(**DB_CONFIG)
        
        # Создаем администратора для удаления
        import random
        import string
        test_login = f"test_admin_{''.join(random.choices(string.ascii_lowercase, k=8))}"
        test_password = "test_password_123"
        test_email = f"{test_login}@test.com"
        
        try:
            account_manager.create_account("admin", test_login, test_password, test_email)
        except Exception:
            pass
        
        response = client.post('/api/admin/remove', json={
            'login': test_login
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_delete_admin_nonexistent(self, client):
        """Тест удаления несуществующего администратора"""
        response = client.post('/api/admin/remove', json={
            'login': 'nonexistent_admin_12345'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is False
    
    def test_delete_admin_missing_login(self, client):
        """Тест удаления администратора без указания логина"""
        response = client.post('/api/admin/remove', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestUserManagement:
    """Тесты для управления пользователями"""
    
    def test_create_user_success(self, client):
        """Тест успешного создания пользователя"""
        import random
        import string
        test_login = f"test_user_{''.join(random.choices(string.ascii_lowercase, k=8))}"
        test_password = "test_password_123"
        test_email = f"{test_login}@test.com"
        
        response = client.post('/api/user/create', json={
            'login': test_login,
            'password': test_password,
            'email': test_email
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Удаляем созданного пользователя
        account_manager = ServerAccountManager(**DB_CONFIG)
        try:
            account_manager.delete_account("user", test_login)
        except Exception:
            pass
    
    def test_create_user_duplicate_login(self, client, test_user):
        """Тест создания пользователя с существующим логином"""
        response = client.post('/api/user/create', json={
            'login': test_user['login'],
            'password': 'password123',
            'email': 'different@test.com'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_delete_user_success(self, client):
        """Тест успешного удаления пользователя"""
        account_manager = ServerAccountManager(**DB_CONFIG)
        
        # Создаем пользователя для удаления
        import random
        import string
        test_login = f"test_user_{''.join(random.choices(string.ascii_lowercase, k=8))}"
        test_password = "test_password_123"
        test_email = f"{test_login}@test.com"
        
        try:
            account_manager.create_account("user", test_login, test_password, test_email)
        except Exception:
            pass
        
        response = client.post('/api/user/remove', json={
            'login': test_login
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestDataSaving:
    """Тесты для сохранения данных"""
    
    def test_save_data_success(self, client):
        """Тест успешного сохранения данных"""
        students_data = [
            {'name': 'Иванов И.И.', 'gradebook': '12345', 'grade': '8'},
            {'name': 'Петров П.П.', 'gradebook': '12346', 'grade': '9'}
        ]
        
        response = client.post('/api/data/save', json={
            'group_name': 'TEST_GROUP_123',
            'course': '1',
            'semester': '1',
            'subject_name': 'TEST_SUBJECT_123',
            'students_data': students_data
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_save_data_missing_fields(self, client):
        """Тест сохранения данных с отсутствующими полями"""
        response = client.post('/api/data/save', json={
            'group_name': 'TEST_GROUP',
            'course': '1'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_save_data_invalid_students_data(self, client):
        """Тест сохранения данных с невалидными данными студентов"""
        response = client.post('/api/data/save', json={
            'group_name': 'TEST_GROUP',
            'course': '1',
            'semester': '1',
            'subject_name': 'TEST_SUBJECT',
            'students_data': 'not_a_list'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestReportEndpoints:
    """Тесты для endpoints отчетов"""
    
    def test_find_group_students(self, client):
        """Тест поиска студентов группы"""
        response = client.post('/api/report/find_group_students', json={
            'group_number': 'TEST_GROUP'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
    
    def test_find_group_students_missing_field(self, client):
        """Тест поиска студентов группы без указания номера группы"""
        response = client.post('/api/report/find_group_students', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_find_subject_grades(self, client):
        """Тест поиска оценок по предмету"""
        response = client.post('/api/report/find_subject_grades', json={
            'subject_name': 'TEST_SUBJECT',
            'group_number': 'TEST_GROUP',
            'course': '1',
            'semester': '1'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
    
    def test_find_subject_grades_missing_fields(self, client):
        """Тест поиска оценок с отсутствующими полями"""
        response = client.post('/api/report/find_subject_grades', json={
            'subject_name': 'TEST_SUBJECT'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestErrorHandling:
    """Тесты для обработки ошибок"""
    
    def test_404_not_found(self, client):
        """Тест обработки 404 ошибки"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_invalid_json(self, client):
        """Тест обработки невалидного JSON"""
        # Отправляем невалидный JSON
        response = client.post('/api/admin/create', 
                              data='invalid json',
                              content_type='application/json')
        # Сервер должен вернуть 400 с понятным сообщением об ошибке
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

