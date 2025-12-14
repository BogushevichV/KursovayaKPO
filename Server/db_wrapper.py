from Server.logger import DatabaseLogger
from psycopg2 import sql


class LoggedCursor:
    """Обертка для cursor с логированием всех SQL запросов"""
    
    def __init__(self, original_cursor, logger: DatabaseLogger):
        self._cursor = original_cursor
        self.logger = logger
    
    def __getattr__(self, name):
        """Проксирует все атрибуты к оригинальному cursor"""
        return getattr(self._cursor, name)
    
    def __enter__(self):
        """Поддержка context manager (with statement)"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка context manager (with statement)"""
        if hasattr(self._cursor, '__exit__'):
            return self._cursor.__exit__(exc_type, exc_val, exc_tb)
        return False
    
    def execute(self, query, params=None):
        """Перехватывает execute и логирует запрос"""
        # Преобразуем sql.SQL объект в строку для логирования
        try:
            if isinstance(query, (sql.SQL, sql.Composed)):
                # Для sql.SQL объектов нужно использовать connection для преобразования
                query_str = query.as_string(self._cursor.connection)
            else:
                query_str = str(query)
        except Exception:
            # Если не удалось преобразовать, используем строковое представление
            query_str = str(query)
        
        # Логируем запрос
        self.logger.log_db_query(query_str, params)
        
        # Выполняем запрос
        result = self._cursor.execute(query, params)
        
        return result
    
    def fetchone(self):
        """Перехватывает fetchone и логирует результат"""
        result = self._cursor.fetchone()
        self.logger.log_db_result(result, rowcount=1 if result else 0)
        return result
    
    def fetchall(self):
        """Перехватывает fetchall и логирует результат"""
        result = self._cursor.fetchall()
        self.logger.log_db_result(result, rowcount=len(result) if result else 0)
        return result


class LoggedConnection:
    """Обертка для connection с логированием cursor"""
    def __init__(self, original_connection, logger: DatabaseLogger):
        self._connection = original_connection
        self.logger = logger
    
    def __getattr__(self, name):
        """Проксирует все атрибуты к оригинальному connection, кроме cursor"""
        if name == 'cursor':
            return self._logged_cursor
        return getattr(self._connection, name)
    
    def _logged_cursor(self, *args, **kwargs):
        """Создает cursor с логированием"""
        cursor_instance = self._connection.cursor(*args, **kwargs)
        return LoggedCursor(cursor_instance, self.logger)


def patch_database_manager_for_logging(manager_instance, logger: DatabaseLogger):
    """Патчит методы DatabaseManager для логирования SQL запросов"""
    if not hasattr(manager_instance, 'connect'):
        return  # Если нет метода connect, пропускаем
    
    original_connect = manager_instance.connect
    
    def logged_connect():
        """Обертка для connect с логированием cursor"""
        original_connect()
        
        if manager_instance.connection is None:
            return
        
        # Оборачиваем connection в LoggedConnection
        manager_instance.connection = LoggedConnection(manager_instance.connection, logger)
    
    # Заменяем метод connect
    manager_instance.connect = logged_connect

