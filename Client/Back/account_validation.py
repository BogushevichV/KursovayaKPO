from Client.Back.client_requests import DatabaseServerClient


class Authenticator:
    """Класс для аутентификации через сервер"""
    
    def __init__(self, server_url: str = "http://localhost:5000", **kwargs):
        """Инициализация аутентификатора"""
        self.client = DatabaseServerClient(server_url)

    def authenticate_admin(self, login: str, password: str) -> bool:
        """Аутентификация администратора через сервер"""
        try:
            result = self.client.authenticate_admin(login, password)
            if result:
                print(f"Аутентификация успешна для администратора '{login}'")
            else:
                print(f"Аутентификация не удалась для администратора '{login}'")
            return result
        except Exception as e:
            print(f"Ошибка при аутентификации администратора: {e}")
            return False

    def authenticate_user(self, login: str, password: str) -> bool:
        """Аутентификация пользователя через сервер"""
        try:
            result = self.client.authenticate_user(login, password)
            if result:
                print(f"Аутентификация успешна для пользователя '{login}'")
            else:
                print(f"Аутентификация не удалась для пользователя '{login}'")
            return result
        except Exception as e:
            print(f"Ошибка при аутентификации пользователя: {e}")
            return False
