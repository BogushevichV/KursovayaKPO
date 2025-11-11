'''
Класс удаления админов
(пока без подключения к БД)
В дальнейшем реализовать методы:
- для подключения к БД (аналогично методу из DBAuthenticator)
- закрытия соединения
Доделать:
- удаление админа из таблицы (remove_admin)
'''


class AdminRemover:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def remove_admin(self, login: str) -> bool:
        try:
            # DELETE FROM admins... WHERE login = %s",
            print("Админ удалён")
            return True
        except Exception as e:
            print(f"Ошибка при удалении администратора: {e}")
            return False