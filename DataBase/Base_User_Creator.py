import psycopg2
from psycopg2 import sql

from DataBase.Password_Hasher import PasswordHasher
from DataBase.Database_Manager import DatabaseManager

class BaseUserCreator(DatabaseManager):
    def __init__(self, table_name: str, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        self.table_name = table_name
        super().__init__(dbname, user, password, host, port)

    def create_account(self, login: str, password: str, email: str, **extra_fields) -> bool:
        if not self.table_name:
            raise ValueError("Subclasses must define table_name")

        salt = PasswordHasher.generate_salt()
        hashed_password = PasswordHasher.hash_password(password, salt)

        try:
            self.connect()
            with self.connection.cursor() as cursor:
                columns = ["login", "password_hash", "salt", "email"] + list(extra_fields.keys())
                values = [login, hashed_password, salt, email] + list(extra_fields.values())

                insert_query = sql.SQL("""
                    INSERT INTO {table} ({fields})
                    VALUES ({placeholders})
                """).format(
                    table=sql.Identifier(self.table_name),
                    fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
                    placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
                )

                cursor.execute(insert_query, values)
            self.commit()
            print(f"Запись успешно добавлена в таблицу {self.table_name}")
            return True
        except psycopg2.errors.UniqueViolation:
            print(f"Ошибка: запись с таким логином или email уже существует в {self.table_name}")
            self.rollback()
            return False
        except Exception as e:
            print(f"Ошибка при создании записи в {self.table_name}: {e}")
            self.rollback()
            return False
        finally:
            self.close()