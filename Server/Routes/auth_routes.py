from flask import request, jsonify
from Server.Source.utils import safe_get_json


def register_auth_routes(app, db_auth, logger):
    """Регистрирует маршруты аутентификации"""

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Проверка работоспособности сервера"""
        return jsonify({"status": "ok", "message": "Сервер работает"})

    @app.route('/api/auth/admin', methods=['POST'])
    def authenticate_admin():
        """Аутентификация администратора"""
        try:
            data = safe_get_json(request, logger)
            if data is None:
                return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
            if 'login' not in data or 'password' not in data:
                return jsonify({"success": False, "error": "Необходимы login и password"}), 400

            login = data['login']
            password = data['password']

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
            data = safe_get_json(request, logger)
            if data is None:
                return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
            if 'login' not in data or 'password' not in data:
                return jsonify({"success": False, "error": "Необходимы login и password"}), 400

            login = data['login']
            password = data['password']

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