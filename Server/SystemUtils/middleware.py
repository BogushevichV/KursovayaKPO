from flask import request


def setup_middleware(app, logger):

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
        try:
            response_data = response.get_json()
        except:
            response_data = response.get_data(as_text=True)

        logger.log_server_response(
            status_code=response.status_code,
            response_data=response_data
        )
        return response

    @app.errorhandler(404)
    def not_found(error):
        """Обработка 404 ошибок"""
        from flask import jsonify
        logger.log_error(error, context="404_not_found")
        return jsonify({"success": False, "error": "Endpoint не найден"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Обработка 500 ошибок"""
        from flask import jsonify
        logger.log_error(error, context="500_internal_error")
        return jsonify({"success": False, "error": "Внутренняя ошибка сервера"}), 500