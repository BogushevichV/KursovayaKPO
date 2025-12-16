from flask import request, jsonify
from Server.Source.utils import safe_get_json


def register_admin_routes(app, account_manager, logger):
    """Регистрирует маршруты для администраторов"""

    @app.route('/api/admin/create', methods=['POST'])
    def create_admin():
        """Создание нового администратора"""
        try:
            data = safe_get_json(request, logger)
            if data is None:
                return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
            if 'login' not in data or 'password' not in data or 'email' not in data:
                return jsonify({"success": False, "error": "Необходимы login, password и email"}), 400

            login = data['login']
            password = data['password']
            email = data['email']
            extra_fields = data.get('extra_fields', {})

            print(f"[DEBUG] Попытка создания администратора: login={login}, email={email}")

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
            data = safe_get_json(request, logger)
            if data is None:
                return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
            if 'login' not in data:
                return jsonify({"success": False, "error": "Необходим login"}), 400

            login = data['login']
            result = account_manager.delete_account("admin", login)

            return jsonify({"success": result})

        except Exception as e:
            logger.log_error(e, context="remove_admin")
            return jsonify({"success": False, "error": str(e)}), 500