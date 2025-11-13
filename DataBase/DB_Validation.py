'''
Класс аутентификации админов и пользователей
(пока заглушка)
В дальнейшем реализовать методы:
- для подключения к БД
- закрытия соединения
- хеширование паролей
Доделать:
- аутентификацию админа (authenticate_admin)
- аутентификацию пользователя (authenticate_user)
'''

# new

class DBAuthenticator:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def authenticate_admin(self, login: str, password: str) -> bool:
        try:
            result = login == "login"

            if result:
                return password == "123"

            return False
        except Exception as e:
            print(f"Ошибка при аутентификации администратора: {e}")
            return False

    def authenticate_user(self, username: str, password: str) -> bool:
        try:
            result = username == "user"

            if result:
                return password == "123"

            return False
        except Exception as e:
            print(f"Ошибка при аутентификации пользователя: {e}")
            return False
