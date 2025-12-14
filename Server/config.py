"""
Конфигурация сервера базы данных
"""
import os

# Параметры подключения к PostgreSQL
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'ExaminationReport'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '02032006'),
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': os.getenv('DB_PORT', '5432')
}

# Параметры сервера Flask
SERVER_CONFIG = {
    'host': os.getenv('SERVER_HOST', '0.0.0.0'),
    'port': int(os.getenv('SERVER_PORT', '5000')),
    'debug': os.getenv('DEBUG', 'False').lower() == 'true'
}

# Параметры логирования
LOG_CONFIG = {
    'log_dir': os.getenv('LOG_DIR', 'logs'),
    'log_file_prefix': os.getenv('LOG_PREFIX', 'db_server')
}






