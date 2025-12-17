from flask import Flask
from flask_cors import CORS
import sys
import os
import atexit

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Server.SystemUtils.logger import DatabaseLogger
from Server.DBUtils.db_wrapper import patch_database_manager_for_logging
from Server.DBUtils.db_handlers import (
    ServerDBAuthenticator,
    ServerAccountManager,
    ServerReportManager
)
from Server.DBUtils.server_db_saver import ServerDatabaseSaver
from Server.Source.config import DB_CONFIG, SERVER_CONFIG, LOG_CONFIG
from Server.SystemUtils.docker_manager import DockerManager
from Server.SystemUtils.middleware import setup_middleware
from Server.Routes import register_all_routes
from Server.Source.utils import print_endpoints


def initialize_database_managers(logger):
    print("Инициализация подключений к БД...")
    print(f"Параметры БД: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, "
          f"dbname={DB_CONFIG['dbname']}, user={DB_CONFIG['user']}")

    try:
        db_auth = ServerDBAuthenticator(**DB_CONFIG)
        account_manager = ServerAccountManager(**DB_CONFIG)
        report_manager = ServerReportManager(**DB_CONFIG)
        database_saver = ServerDatabaseSaver(**DB_CONFIG)

        # Тестируем подключение
        print("Тестирование подключения к БД...")
        db_auth.connect()
        if db_auth.connection:
            print("✓ Подключение к БД успешно!")
            db_auth.close()
        else:
            print("✗ Не удалось подключиться к БД")

        # Патчим все менеджеры для логирования SQL запросов
        patch_database_manager_for_logging(db_auth, logger)
        patch_database_manager_for_logging(account_manager, logger)
        patch_database_manager_for_logging(report_manager, logger)
        patch_database_manager_for_logging(database_saver, logger)
        print("✓ Все менеджеры инициализированы и патчены для логирования")

        return db_auth, account_manager, report_manager, database_saver

    except Exception as e:
        print(f"✗ КРИТИЧЕСКАЯ ОШИБКА при инициализации БД: {e}")
        import traceback
        traceback.print_exc()
        print("\nПроверьте:")
        print("  1. PostgreSQL запущен")
        print("  2. Параметры подключения в Server/config.py правильные")
        print("  3. База данных создана (запустите init_database.py)")
        raise


def create_app():
    app = Flask(__name__)
    CORS(app)

    return app


def main():
    """Главная функция запуска сервера"""

    # 1. Инициализация Docker
    docker_manager = DockerManager(container_name='exam_pg')
    if not docker_manager.initialize():
        print("Не удалось запустить Docker. Завершение работы.")
        sys.exit(1)

    # Регистрируем остановку контейнера при завершении
    atexit.register(docker_manager.cleanup)

    print("=" * 80)
    print("ИНИЦИАЛИЗАЦИЯ СЕРВЕРА")
    print("=" * 80 + "\n")

    # 2. Создание Flask приложения
    app = create_app()

    # 3. Инициализация логгера
    logger = DatabaseLogger(
        log_dir=LOG_CONFIG['log_dir'],
        log_file_prefix=LOG_CONFIG['log_file_prefix']
    )
    atexit.register(logger.close)

    # 4. Инициализация менеджеров БД
    db_auth, account_manager, report_manager, database_saver = initialize_database_managers(logger)

    # 5. Настройка middleware
    setup_middleware(app, logger)

    # 6. Регистрация маршрутов
    register_all_routes(app, db_auth, account_manager, report_manager, database_saver, logger)

    # 7. Вывод информации о сервере
    print("\n" + "=" * 80)
    print("СЕРВЕР ГОТОВ К РАБОТЕ")
    print("=" * 80)
    print(f"Docker контейнер: {docker_manager.container_name}")
    print(f"Логи записываются в: {logger.log_file_path}")
    print("=" * 80)
    print_endpoints()
    print("\n" + "=" * 80)

    # 8. Запуск сервера
    try:
        app.run(
            host=SERVER_CONFIG['host'],
            port=SERVER_CONFIG['port'],
            debug=SERVER_CONFIG['debug']
        )
    except KeyboardInterrupt:
        print("\n\nЗавершение работы сервера...")
    finally:
        docker_manager.cleanup()


if __name__ == '__main__':
    main()