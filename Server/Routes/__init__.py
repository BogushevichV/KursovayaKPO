from flask import Flask
from .auth_routes import register_auth_routes
from .user_routes import register_user_routes
from .admin_routes import register_admin_routes
from .report_routes import register_report_routes
from .data_routes import register_data_routes


def register_all_routes(app: Flask, db_auth, account_manager, report_manager, database_saver, logger):
    # Регистрируем группы маршрутов
    register_auth_routes(app, db_auth, logger)
    register_user_routes(app, account_manager, logger)
    register_admin_routes(app, account_manager, logger)
    register_report_routes(app, report_manager, logger)
    register_data_routes(app, database_saver, report_manager, logger)