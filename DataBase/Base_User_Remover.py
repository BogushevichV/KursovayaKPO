from psycopg2 import sql

from DataBase.Database_Manager import DatabaseManager

class BaseUserRemover(DatabaseManager):
    def __init__(self, table_name: str, dbname: str, user: str, password: str, host: str, port: str = "5432"):
        self.table_name = table_name
        super().__init__(dbname, user, password, host, port)

    def remove_account(self, login: str) -> bool:
        if not self.table_name:
            raise ValueError("Subclasses must define table_name")

        try:
            self.connect()
            with self.connection.cursor() as cursor:
                delete_query = sql.SQL("""
                    DELETE FROM {table}
                    WHERE login = %s
                """).format(table=sql.Identifier(self.table_name))

                cursor.execute(delete_query, (login,))
                if cursor.rowcount == 0:
                    print(f" Запись с логином '{login}' не найдена в таблице {self.table_name}")
                    self.rollback()
                    return False

            self.commit()
            print(f"Пользователь '{login}' успешно удалён из таблицы {self.table_name}")
            return True
        except Exception as e:
            print(f"Ошибка при удалении пользователя из {self.table_name}: {e}")
            self.rollback()
            return False
        finally:
            self.close()