from psycopg2 import sql

from DataBase.Database_Manager import DatabaseManager
from DataBase.Password_Hasher import PasswordHasher

class DBAuthenticator(DatabaseManager):
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        super().__init__(dbname, user, password, host, port)

    def __authenticate(self, table: str, login: str, password: str) -> bool:
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                query = sql.SQL("""
                    SELECT password_hash, salt
                    FROM {table}
                    WHERE login = %s
                """).format(table=sql.Identifier(table))

                cursor.execute(query, (login,))
                record = cursor.fetchone()

                if not record:
                    print(f"Пользователь '{login}' не найден")
                    return False

                stored_hash, stored_salt = record
                if PasswordHasher.verify_password(password, stored_hash, stored_salt):
                    print(f"Аутентификация успешна для '{login}'")
                    return True
                else:
                    print(f"Неверный пароль для '{login}'")
                    return False
        except Exception as e:
            print(f"Ошибка при аутентификации: {e}")
            return False
        finally:
            self.close()

    def authenticate_admin(self, login: str, password: str) -> bool:
        return self.__authenticate('admins', login, password)

    def authenticate_user(self, login: str, password: str) -> bool:
        return self.__authenticate('users', login, password)
