'''
Класс добавления пользователей
(пока без подключения к БД)
В дальнейшем реализовать методы:
- для подключения к БД (аналогично методу из DBAuthenticator)
- закрытия соединения
- хеширование паролей
Доделать:
- добавление пользователя в таблицу (create_user)
'''

class UserCreator:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def create_user(self, login: str, password: str, email: str) -> bool:

        try:
            # INSERT INTO users...
            print("Пользователь добавлен")
            return True
        except Exception as e:
            print(f"Ошибка при создании пользователя: {e}")
            return False
