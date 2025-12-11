import os
from datetime import datetime
from typing import Any, Optional
import json


class DatabaseLogger:
    """Класс для журналирования всех действий с базой данных"""
    
    def __init__(self, log_dir: str = "logs", log_file_prefix: str = "db_server"):
        """
        Инициализация логгера
        
        Args:
            log_dir: Директория для хранения логов
            log_file_prefix: Префикс имени файла лога
        """
        self.log_dir = log_dir
        self.log_file_prefix = log_file_prefix
        self.log_file = None
        self.log_file_path = None
        
        # Создаем директорию для логов, если её нет
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Инициализируем новый файл лога при запуске
        self._init_log_file()
    
    def _init_log_file(self):
        """Создает новый файл лога с именем, включающим дату"""
        # Формат: db_server-2024-01-15_14-30-25.log
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.log_file_prefix}-{timestamp}.log"
        self.log_file_path = os.path.join(self.log_dir, filename)
        
        # Открываем файл для записи
        self.log_file = open(self.log_file_path, 'w', encoding='utf-8')
        
        # Записываем информацию о запуске сервера
        self._write_log("SERVER_START", {
            "message": "Сервер запущен",
            "log_file": self.log_file_path
        })
    
    def _get_timestamp(self) -> str:
        """Возвращает текущую дату и время в формате строки"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    def _write_log(self, action: str, data: dict):
        """
        Записывает лог в файл
        
        Args:
            action: Тип действия
            data: Данные для записи
        """
        if self.log_file is None:
            return
        
        log_entry = {
            "timestamp": self._get_timestamp(),
            "action": action,
            "data": data
        }
        
        # Записываем в формате JSON для удобства чтения
        log_line = json.dumps(log_entry, ensure_ascii=False, indent=2)
        self.log_file.write(log_line + "\n" + "-" * 80 + "\n")
        self.log_file.flush()  # Сразу записываем в файл
    
    def log_client_request(self, method: str, endpoint: str, params: dict, body: Optional[dict] = None):
        """
        Логирует запрос от клиента
        
        Args:
            method: HTTP метод (GET, POST, etc.)
            endpoint: Эндпоинт API
            params: Параметры запроса
            body: Тело запроса (если есть)
        """
        self._write_log("CLIENT_REQUEST", {
            "method": method,
            "endpoint": endpoint,
            "params": params,
            "body": body
        })
    
    def log_db_query(self, query: str, params: Optional[tuple] = None):
        """
        Логирует SQL запрос к базе данных
        
        Args:
            query: SQL запрос
            params: Параметры запроса
        """
        self._write_log("DB_QUERY", {
            "query": query,
            "params": params
        })
    
    def log_db_result(self, result: Any, rowcount: Optional[int] = None):
        """
        Логирует результат запроса к базе данных
        
        Args:
            result: Результат запроса
            rowcount: Количество затронутых строк (если применимо)
        """
        # Преобразуем результат в сериализуемый формат
        if isinstance(result, (list, tuple)):
            # Для списков кортежей (результаты SELECT)
            serializable_result = [list(row) if isinstance(row, tuple) else row for row in result]
        else:
            serializable_result = result
        
        self._write_log("DB_RESULT", {
            "result": serializable_result,
            "rowcount": rowcount,
            "result_type": type(result).__name__
        })
    
    def log_server_response(self, status_code: int, response_data: Any):
        """
        Логирует ответ сервера клиенту
        
        Args:
            status_code: HTTP статус код
            response_data: Данные ответа
        """
        self._write_log("SERVER_RESPONSE", {
            "status_code": status_code,
            "response": response_data
        })
    
    def log_error(self, error: Exception, context: Optional[str] = None):
        """
        Логирует ошибку
        
        Args:
            error: Объект исключения
            context: Дополнительный контекст ошибки
        """
        self._write_log("ERROR", {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        })
    
    def close(self):
        """Закрывает файл лога"""
        if self.log_file:
            self._write_log("SERVER_STOP", {
                "message": "Сервер остановлен"
            })
            self.log_file.close()
            self.log_file = None






