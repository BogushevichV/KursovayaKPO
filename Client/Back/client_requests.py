import requests
from typing import Optional, Dict, Any
import sys
import os

# Добавляем путь для импорта конфига
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from Client.Source.config import REQUEST_TIMEOUT
except ImportError:
    # Если конфиг не найден, используем значение по умолчанию
    REQUEST_TIMEOUT = 30


class DatabaseServerClient:
    """Клиент для отправки HTTP запросов к серверу БД"""
    
    def __init__(self, server_url: str = "http://localhost:5000", timeout: int = None):
        """Инициализация клиента"""
        self.server_url = server_url.rstrip('/')
        self.timeout = timeout or REQUEST_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Выполняет HTTP запрос к серверу"""
        url = f"{self.server_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=data, timeout=self.timeout)
            else:
                response = self.session.request(method, url, json=data, timeout=self.timeout)
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Не удалось подключиться к серверу: {self.server_url}")
        except requests.exceptions.HTTPError as e:
            error_msg = "Ошибка сервера"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', str(e))
            except:
                error_msg = str(e)
            raise Exception(f"{error_msg}")
        except Exception as e:
            raise Exception(f"Ошибка при выполнении запроса: {str(e)}")
    
    def health_check(self) -> bool:
        """Проверка работоспособности сервера"""
        try:
            response = self._make_request('GET', '/api/health')
            return response.get('status') == 'ok'
        except:
            return False
    
    def authenticate_admin(self, login: str, password: str) -> bool:
        """Аутентификация администратора"""
        data = {
            "login": login,
            "password": password
        }
        response = self._make_request('POST', '/api/auth/admin', data)
        return response.get('success', False)
    
    def authenticate_user(self, login: str, password: str) -> bool:
        """Аутентификация пользователя"""
        data = {
            "login": login,
            "password": password
        }
        response = self._make_request('POST', '/api/auth/user', data)
        return response.get('success', False)
    
    def create_user(self, login: str, password: str, email: str, **extra_fields) -> bool:
        """Создание пользователя"""
        data = {
            "login": login,
            "password": password,
            "email": email,
            "extra_fields": extra_fields
        }
        response = self._make_request('POST', '/api/user/create', data)
        return response.get('success', False)
    
    def remove_user(self, login: str) -> bool:
        """Удаление пользователя"""
        data = {"login": login}
        response = self._make_request('POST', '/api/user/remove', data)
        return response.get('success', False)
    
    def create_admin(self, login: str, password: str, email: str, **extra_fields) -> bool:
        """Создание администратора"""
        data = {
            "login": login,
            "password": password,
            "email": email,
            "extra_fields": extra_fields
        }
        response = self._make_request('POST', '/api/admin/create', data)
        return response.get('success', False)
    
    def remove_admin(self, login: str) -> bool:
        """Удаление администратора"""
        data = {"login": login}
        response = self._make_request('POST', '/api/admin/remove', data)
        return response.get('success', False)
    
    def find_group_students(self, group_number: str) -> Optional[list]:
        """Поиск студентов группы"""
        data = {"group_number": group_number}
        response = self._make_request('POST', '/api/report/find_group_students', data)
        if response.get('success'):
            return response.get('data')
        return None
    
    def find_subject_grades(self, subject_name: str, group_number: str, 
                           course: str, semester: str) -> Optional[list]:
        """Поиск оценок по предмету"""
        data = {
            "subject_name": subject_name,
            "group_number": group_number,
            "course": course,
            "semester": semester
        }
        response = self._make_request('POST', '/api/report/find_subject_grades', data)
        if response.get('success'):
            return response.get('data')
        return None
    
    def save_data(self, group_name: str, course: str, semester: str, 
                  subject_name: str, students_data: list) -> bool:
        """Сохранение данных студентов и их оценок (автоматически сохраняется на сервере)"""
        data = {
            "group_name": group_name,
            "course": course,
            "semester": semester,
            "subject_name": subject_name,
            "students_data": students_data
        }
        response = self._make_request('POST', '/api/data/save', data)
        return response.get('success', False)

