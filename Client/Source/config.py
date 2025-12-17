"""
Конфигурация клиентского приложения
"""
import os

# URL сервера базы данных
# На Windows `localhost` иногда даёт заметную задержку из-за резолвинга (IPv6/hosts/DNS),
# поэтому по умолчанию используем 127.0.0.1.
SERVER_URL = os.getenv('SERVER_URL', 'http://127.0.0.1:5000')

# Таймаут для HTTP запросов (в секундах)
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))






