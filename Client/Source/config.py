"""
Конфигурация клиентского приложения
"""
import os

# URL сервера базы данных
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

# Таймаут для HTTP запросов (в секундах)
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))






