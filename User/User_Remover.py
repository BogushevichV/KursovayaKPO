'''
Класс удаления пользователей
(пока без подключения к БД)
В дальнейшем реализовать методы:
- для подключения к БД (аналогично методу из DBAuthenticator)
- закрытия соединения
Доделать:
- удаление пользователя из таблицы (remove_user)
'''

class UserRemover:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None


    def remove_user(self, login: str) -> bool:
        try:
            # DELETE FROM users...
            print("Пользователь удалён")
            return True
        except Exception as e:
            print(f"Ошибка при удалении пользователя: {e}")
            return False
