from flask import request, jsonify
from Server.Source.utils import safe_get_json


def register_data_routes(app, database_saver, report_manager, logger):
    """Регистрирует маршруты для работы с данными"""

    @app.route('/api/data/save', methods=['POST'])
    def save_data():
        """Сохранение данных студентов и их оценок"""
        try:
            data = safe_get_json(request, logger)
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

            if not isinstance(students_data, list):
                return jsonify({"success": False, "error": "students_data должен быть списком"}), 400

            result = database_saver.save_data(group_name, course, semester, subject_name, students_data)

            if result:
                return jsonify({"success": True, "message": "Данные успешно сохранены"})
            else:
                return jsonify({"success": False, "error": "Не удалось сохранить данные"}), 500

        except Exception as e:
            logger.log_error(e, context="save_data")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/data/delete_subject', methods=['POST'])
    def delete_subject():
        """Удаление предмета и всех связанных данных"""
        try:
            data = safe_get_json(request, logger)
            if data is None:
                return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
            if 'subject_name' not in data:
                return jsonify({"success": False, "error": "Необходимо поле subject_name"}), 400

            subject_name = data['subject_name']
            result = database_saver.delete_subject(subject_name)

            if result:
                return jsonify({"success": True, "message": f"Предмет '{subject_name}' успешно удален"})
            else:
                return jsonify({"success": False, "error": f"Предмет '{subject_name}' не найден"}), 404

        except Exception as e:
            logger.log_error(e, context="delete_subject")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/data/delete_group', methods=['POST'])
    def delete_group():
        """Удаление группы и всех связанных данных"""
        try:
            data = safe_get_json(request, logger)
            if data is None:
                return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
            if 'group_name' not in data:
                return jsonify({"success": False, "error": "Необходимо поле group_name"}), 400

            group_name = data['group_name']
            result = database_saver.delete_group(group_name)

            if result:
                return jsonify({"success": True, "message": f"Группа '{group_name}' успешно удалена"})
            else:
                return jsonify({"success": False, "error": f"Группа '{group_name}' не найдена"}), 404

        except Exception as e:
            logger.log_error(e, context="delete_group")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/data/delete_exam', methods=['POST'])
    def delete_exam():
        """Удаление экзамена и всех связанных оценок"""
        try:
            data = safe_get_json(request, logger)
            if data is None:
                return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
            if 'exam_id' not in data:
                return jsonify({"success": False, "error": "Необходимо поле exam_id"}), 400

            exam_id = data['exam_id']
            try:
                exam_id = int(exam_id)
            except (ValueError, TypeError):
                return jsonify({"success": False, "error": "exam_id должен быть числом"}), 400

            result = database_saver.delete_exam(exam_id)

            if result:
                return jsonify({"success": True, "message": f"Экзамен с ID {exam_id} успешно удален"})
            else:
                return jsonify({"success": False, "error": f"Экзамен с ID {exam_id} не найден"}), 404

        except Exception as e:
            logger.log_error(e, context="delete_exam")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/data/delete_student', methods=['POST'])
    def delete_student():
        """Удаление студента и всех его оценок"""
        try:
            data = safe_get_json(request, logger)
            if data is None:
                return jsonify({"success": False, "error": "Ошибка парсинга JSON"}), 400
            if 'student_id' not in data:
                return jsonify({"success": False, "error": "Необходимо поле student_id"}), 400

            student_id = data['student_id']
            try:
                student_id = int(student_id)
            except (ValueError, TypeError):
                return jsonify({"success": False, "error": "student_id должен быть числом"}), 400

            result = database_saver.delete_student(student_id)

            if result:
                return jsonify({"success": True, "message": f"Студент с ID {student_id} успешно удален"})
            else:
                return jsonify({"success": False, "error": f"Студент с ID {student_id} не найден"}), 404

        except Exception as e:
            logger.log_error(e, context="delete_student")
            return jsonify({"success": False, "error": str(e)}), 500

    # GET маршруты для получения всех данных
    @app.route('/api/data/get_all_subjects', methods=['GET'])
    def get_all_subjects():
        """Получение всех предметов"""
        result = report_manager.get_all_subjects()
        return jsonify({"success": True, "data": result})

    @app.route('/api/data/get_all_groups', methods=['GET'])
    def get_all_groups():
        """Получение всех групп"""
        result = report_manager.get_all_groups()
        return jsonify({"success": True, "data": result})

    @app.route('/api/data/get_all_exams', methods=['GET'])
    def get_all_exams():
        """Получение всех экзаменов"""
        result = report_manager.get_all_exams()
        return jsonify({"success": True, "data": result})

    @app.route('/api/data/get_all_students', methods=['GET'])
    def get_all_students():
        """Получение всех студентов"""
        result = report_manager.get_all_students()
        return jsonify({"success": True, "data": result})

    @app.route('/api/data/get_all_users', methods=['GET'])
    def get_all_users():
        """Получение всех пользователей"""
        result = report_manager.get_all_users()
        return jsonify({"success": True, "data": result})

    @app.route('/api/data/get_all_admins', methods=['GET'])
    def get_all_admins():
        """Получение всех администраторов"""
        result = report_manager.get_all_admins()
        return jsonify({"success": True, "data": result})