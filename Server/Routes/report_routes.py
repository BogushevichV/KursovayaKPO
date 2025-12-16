from flask import request, jsonify
from Server.Source.utils import safe_get_json


def register_report_routes(app, report_manager, logger):
    """Регистрирует маршруты для отчетов"""

    @app.route('/api/report/find_group_students', methods=['POST'])
    def find_group_students():
        """Поиск студентов группы"""
        try:
            data = safe_get_json(request, logger)
            if data is None:
                return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
            if 'group_number' not in data:
                return jsonify({"success": False, "error": "Необходим group_number"}), 400

            group_number = data['group_number']
            result = report_manager.find_group_students(group_number)

            return jsonify({"success": True, "data": result})

        except Exception as e:
            logger.log_error(e, context="find_group_students")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/report/find_subject_grades', methods=['POST'])
    def find_subject_grades():
        """Поиск оценок по предмету"""
        try:
            data = safe_get_json(request, logger)
            if data is None:
                return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
            required_fields = ['subject_name', 'group_number', 'course', 'semester']
            if not all(field in data for field in required_fields):
                return jsonify({"success": False, "error": f"Необходимы поля: {', '.join(required_fields)}"}), 400

            subject_name = data['subject_name']
            group_number = data['group_number']
            course = data['course']
            semester = data['semester']

            result = report_manager.find_subject_grades(subject_name, group_number, course, semester)

            return jsonify({"success": True, "data": result})

        except Exception as e:
            logger.log_error(e, context="find_subject_grades")
            return jsonify({"success": False, "error": str(e)}), 500