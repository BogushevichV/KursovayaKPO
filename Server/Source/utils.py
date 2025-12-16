def safe_get_json(request, logger):
    try:
        return request.get_json()
    except Exception as e:
        logger.log_error(e, context="json_parsing_error")
        return None


def print_endpoints():
    """Выводит список всех доступных endpoints"""
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
    print("  POST /api/data/delete_subject - удаление предмета")
    print("  POST /api/data/delete_group - удаление группы")
    print("  POST /api/data/delete_exam - удаление экзамена")
    print("  POST /api/data/delete_student - удаление студента")
    print("  GET /api/data/get_all_subjects - получение всех предметов")
    print("  GET /api/data/get_all_groups - получение всех групп")
    print("  GET /api/data/get_all_exams - получение всех экзаменов")
    print("  GET /api/data/get_all_students - получение всех студентов")
    print("  GET /api/data/get_all_users - получение всех пользователей")
    print("  GET /api/data/get_all_admins - получение всех администраторов")