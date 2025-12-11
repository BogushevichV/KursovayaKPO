import psycopg2

class DatabaseManager:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def connect(self):
        if self.connection is None or self.connection.closed:
            print("connecting to database...")
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )

    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()

    def commit(self):
        if self.connection:
            self.connection.commit()

    def rollback(self):
        if self.connection:
            self.connection.rollback()

