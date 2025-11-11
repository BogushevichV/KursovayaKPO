'''
Класс добавления пользователей
(пока без подключения к БД)
В дальнейшем реализовать методы:
- для подключения к БД (аналогично методу из DBAuthenticator)
- закрытия соединения
Доделать:
- добавление пользователя в таблицу (create_user)
'''

from DataBase.Password_Hasher import PasswordHasher

class UserCreator:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def create_user(self, login: str, password: str, email: str) -> bool:
        salt = PasswordHasher.generate_salt()
        hashed_password = PasswordHasher.hash_password(password, salt)

        try:
            # INSERT INTO users...
            print("Пользователь добавлен")
            return True
        except Exception as e:
            print(f"Ошибка при создании пользователя: {e}")
            return False
