from flask import Flask, request, jsonify
from flask_cors import CORS
from Server.logger import DatabaseLogger
from Server.db_wrapper import patch_database_manager_for_logging
from Server.db_handlers import (
    ServerDBAuthenticator,
    ServerAccountManager,
    ServerReportManager
)
from Server.server_db_saver import ServerDatabaseSaver
from Server.config import DB_CONFIG, SERVER_CONFIG, LOG_CONFIG
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для клиентских запросов

# Инициализация логгера из конфига
logger = DatabaseLogger(
    log_dir=LOG_CONFIG['log_dir'],
    log_file_prefix=LOG_CONFIG['log_file_prefix']
)

# Инициализация серверных менеджеров БД
# Сервер использует прямые подключения к БД (не через API)
# Эти классы работают напрямую с PostgreSQL для обработки запросов от клиентов
print("Инициализация подключений к БД...")
print(f"Параметры БД: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, dbname={DB_CONFIG['dbname']}, user={DB_CONFIG['user']}")

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

except Exception as e:
    print(f"✗ КРИТИЧЕСКАЯ ОШИБКА при инициализации БД: {e}")
    import traceback
    traceback.print_exc()
    print("\nПроверьте:")
    print("  1. PostgreSQL запущен")
    print("  2. Параметры подключения в Server/config.py правильные")
    print("  3. База данных создана (запустите init_database.py)")
    raise


def safe_get_json():
    """Безопасное получение JSON из запроса с обработкой ошибок"""
    try:
        return request.get_json()
    except Exception as e:
        logger.log_error(e, context="json_parsing_error")
        return None


@app.before_request
def log_request():
    """Логирует каждый входящий запрос"""
    try:
        body = request.get_json(silent=True)
    except Exception:
        body = None
    logger.log_client_request(
        method=request.method,
        endpoint=request.path,
        params=dict(request.args),
        body=body
    )


@app.after_request
def log_response(response):
    """Логирует каждый исходящий ответ"""
    # Получаем данные ответа
    try:
        response_data = response.get_json()
    except:
        response_data = response.get_data(as_text=True)

    logger.log_server_response(
        status_code=response.status_code,
        response_data=response_data
    )
    return response


@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности сервера"""
    return jsonify({"status": "ok", "message": "Сервер работает"})


@app.route('/api/auth/admin', methods=['POST'])
def authenticate_admin():
    """Аутентификация администратора"""
    try:
        data = safe_get_json()
        if data is None:
            return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
        if 'login' not in data or 'password' not in data:
            return jsonify({"success": False, "error": "Необходимы login и password"}), 400

        login = data['login']
        password = data['password']

        # Выполняем аутентификацию (внутри метода уже есть SQL запрос)
        result = db_auth.authenticate_admin(login, password)

        if not result:
            logger.log_error(
                Exception(f"Аутентификация не удалась для admin: {login}"),
                context="authenticate_admin"
            )

        return jsonify({"success": result})

    except Exception as e:
        error_msg = str(e)
        logger.log_error(e, context="authenticate_admin")
        print(f"Ошибка при аутентификации администратора: {error_msg}")
        return jsonify({"success": False, "error": error_msg}), 500


@app.route('/api/auth/user', methods=['POST'])
def authenticate_user():
    """Аутентификация пользователя"""
    try:
        data = safe_get_json()
        if data is None:
            return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
        if 'login' not in data or 'password' not in data:
            return jsonify({"success": False, "error": "Необходимы login и password"}), 400

        login = data['login']
        password = data['password']

        # Выполняем аутентификацию (внутри метода уже есть SQL запрос)
        result = db_auth.authenticate_user(login, password)

        if not result:
            logger.log_error(
                Exception(f"Аутентификация не удалась для user: {login}"),
                context="authenticate_user"
            )

        return jsonify({"success": result})

    except Exception as e:
        error_msg = str(e)
        logger.log_error(e, context="authenticate_user")
        print(f"Ошибка при аутентификации пользователя: {error_msg}")
        return jsonify({"success": False, "error": error_msg}), 500


@app.route('/api/user/create', methods=['POST'])
def create_user():
    """Создание нового пользователя"""
    try:
        data = safe_get_json()
        if data is None:
            return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
        if 'login' not in data or 'password' not in data or 'email' not in data:
            return jsonify({"success": False, "error": "Необходимы login, password и email"}), 400

        login = data['login']
        password = data['password']
        email = data['email']
        extra_fields = data.get('extra_fields', {})

        print(f"[DEBUG] Попытка создания пользователя: login={login}, email={email}")

        # Создаем пользователя (SQL запрос выполняется внутри метода)
        try:
            result = account_manager.create_account("user", login, password, email, **extra_fields)
            
            if result:
                print(f"[DEBUG] Пользователь {login} успешно создан")
                return jsonify({"success": True, "message": f"Пользователь {login} успешно создан"})
            else:
                error_msg = f"Не удалось создать пользователя {login}"
                logger.log_error(Exception(error_msg), context="create_user")
                print(f"[ERROR] {error_msg}")
                return jsonify({"success": False, "error": error_msg}), 400
        except ValueError as ve:
            # Обрабатываем ошибки валидации (например, UniqueViolation)
            error_msg = str(ve)
            logger.log_error(ve, context="create_user")
            print(f"[ERROR] {error_msg}")
            return jsonify({"success": False, "error": error_msg}), 400

    except Exception as e:
        error_msg = str(e)
        logger.log_error(e, context="create_user")
        print(f"[ERROR] Ошибка при создании пользователя: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": error_msg}), 500


@app.route('/api/user/remove', methods=['POST'])
def remove_user():
    """Удаление пользователя"""
    try:
        data = safe_get_json()
        if data is None:
            return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
        if 'login' not in data:
            return jsonify({"success": False, "error": "Необходим login"}), 400

        login = data['login']

        # Удаляем пользователя (SQL запрос выполняется внутри метода)
        result = account_manager.delete_account("user", login)

        return jsonify({"success": result})

    except Exception as e:
        logger.log_error(e, context="remove_user")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/admin/create', methods=['POST'])
def create_admin():
    """Создание нового администратора"""
    try:
        data = safe_get_json()
        if data is None:
            return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
        if 'login' not in data or 'password' not in data or 'email' not in data:
            return jsonify({"success": False, "error": "Необходимы login, password и email"}), 400

        login = data['login']
        password = data['password']
        email = data['email']
        extra_fields = data.get('extra_fields', {})

        print(f"[DEBUG] Попытка создания администратора: login={login}, email={email}")

        # Создаем администратора (SQL запрос выполняется внутри метода)
        try:
            result = account_manager.create_account("admin", login, password, email, **extra_fields)
            
            if result:
                print(f"[DEBUG] Администратор {login} успешно создан")
                return jsonify({"success": True, "message": f"Администратор {login} успешно создан"})
            else:
                error_msg = f"Не удалось создать администратора {login}"
                logger.log_error(Exception(error_msg), context="create_admin")
                print(f"[ERROR] {error_msg}")
                return jsonify({"success": False, "error": error_msg}), 400
        except ValueError as ve:
            # Обрабатываем ошибки валидации (например, UniqueViolation)
            error_msg = str(ve)
            logger.log_error(ve, context="create_admin")
            print(f"[ERROR] {error_msg}")
            return jsonify({"success": False, "error": error_msg}), 400

    except Exception as e:
        error_msg = str(e)
        logger.log_error(e, context="create_admin")
        print(f"[ERROR] Ошибка при создании администратора: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": error_msg}), 500


@app.route('/api/admin/remove', methods=['POST'])
def remove_admin():
    """Удаление администратора"""
    try:
        data = safe_get_json()
        if data is None:
            return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
        if 'login' not in data:
            return jsonify({"success": False, "error": "Необходим login"}), 400

        login = data['login']

        # Удаляем администратора (SQL запрос выполняется внутри метода)
        result = account_manager.delete_account("admin", login)

        return jsonify({"success": result})

    except Exception as e:
        logger.log_error(e, context="remove_admin")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/report/find_group_students', methods=['POST'])
def find_group_students():
    """Поиск студентов группы"""
    try:
        data = safe_get_json()
        if data is None:
            return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
        if 'group_number' not in data:
            return jsonify({"success": False, "error": "Необходим group_number"}), 400

        group_number = data['group_number']

        # Ищем студентов группы (SQL запрос выполняется внутри метода)
        result = report_manager.find_group_students(group_number)

        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.log_error(e, context="find_group_students")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/report/find_subject_grades', methods=['POST'])
def find_subject_grades():
    """Поиск оценок по предмету"""
    try:
        data = safe_get_json()
        if data is None:
            return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
        required_fields = ['subject_name', 'group_number', 'course', 'semester']
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "error": f"Необходимы поля: {', '.join(required_fields)}"}), 400

        subject_name = data['subject_name']
        group_number = data['group_number']
        course = data['course']
        semester = data['semester']

        # Ищем оценки по предмету (SQL запрос выполняется внутри метода)
        result = report_manager.find_subject_grades(subject_name, group_number, course, semester)

        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.log_error(e, context="find_subject_grades")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/data/save', methods=['POST'])
def save_data():
    """Сохранение данных студентов и их оценок (автоматически сохраняется при изменениях)"""
    try:
        data = safe_get_json()
        if data is None:
            return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
        required_fields = ['group_name', 'course', 'semester', 'subject_name', 'students_data']
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "error": f"Необходимы поля: {', '.join(required_fields)}"}), 400

        group_name = data['group_name']
        course = data['course']
        semester = data['semester']
        subject_name = data['subject_name']
        students_data = data['students_data']

        # Валидация данных студентов
        if not isinstance(students_data, list):
            return jsonify({"success": False, "error": "students_data должен быть списком"}), 400

        # Сохраняем данные (автоматически выполняется commit внутри метода)
        result = database_saver.save_data(group_name, course, semester, subject_name, students_data)

        if result:
            return jsonify({"success": True, "message": "Данные успешно сохранены"})
        else:
            return jsonify({"success": False, "error": "Не удалось сохранить данные"}), 500

    except Exception as e:
        logger.log_error(e, context="save_data")
        return jsonify({"success": False, "error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибок"""
    logger.log_error(error, context="404_not_found")
    return jsonify({"success": False, "error": "Endpoint не найден"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработка 500 ошибок"""
    logger.log_error(error, context="500_internal_error")
    return jsonify({"success": False, "error": "Внутренняя ошибка сервера"}), 500


def shutdown_handler():
    """Обработчик завершения работы сервера"""
    logger.close()


if __name__ == '__main__':
    import atexit
    atexit.register(shutdown_handler)

    print("=" * 80)
    print("Сервер базы данных запущен")
    print(f"Логи записываются в: {logger.log_file_path}")
    print("=" * 80)
    print("\nДоступные endpoints:")
    print("  GET  /api/health - проверка работоспособности")
    print("  POST /api/auth/admin - аутентификация администратора")
    print("  POST /api/auth/user - аутентификация пользователя")
    print("  POST /api/user/create - создание пользователя")
    print("  POST /api/user/remove - удаление пользователя")
    print("  POST /api/admin/create - создание администратора")
    print("  POST /api/admin/remove - удаление администратора")
    print("  POST /api/report/find_group_students - поиск студентов группы")
    print("  POST /api/report/find_subject_grades - поиск оценок по предмету")
    print("  POST /api/data/save - сохранение данных студентов и оценок")
    print("\n" + "=" * 80)

    # Запуск сервера из конфига
    app.run(
        host=SERVER_CONFIG['host'],
        port=SERVER_CONFIG['port'],
        debug=SERVER_CONFIG['debug']
    )

