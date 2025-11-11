'''
Класс добавления админов
(пока без подключения к БД)
В дальнейшем реализовать методы:
- для подключения к БД (аналогично методу из DBAuthenticator)
- закрытия соединения
Доделать:
- добавление админа в таблицу (create_admin)
'''

from DataBase.Password_Hasher import PasswordHasher

class AdminCreator:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def create_admin(self, login: str, password: str, email: str) -> bool:
        salt = PasswordHasher.generate_salt()
        hashed_password = PasswordHasher.hash_password(password, salt)

        try:
            # INSERT INTO admins...
            print("Админ добавлен")
            return True
        except Exception as e:
            print(f"Ошибка при создании администратора: {e}")
            return False
