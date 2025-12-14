"""
Стили для окна администратора
"""

BUTTON_STYLE = """
    QPushButton {
        min-width: 200px;
        min-height: 40px;
        font-size: 16px;
        border-radius: 5px;
        background-color: #4CAF50;
        color: white;
        border: 2px solid #45a049;
    }
    QPushButton:hover {
        background-color: #388038;
    }
"""

FORM_STYLE = """
    QWidget {
        background-color: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    QLineEdit {
        color: black;
        padding: 5px 10px;
        border: 1px solid #ced4da;
        border-radius: 4px;
        font-size: 14px;
    }
    QLabel {
        background: transparent;
        color: black;
        border: none;
        font-size: 14px;
    }
"""

LOGIN_FORM_STYLE = """
    QLineEdit#login_input, QLineEdit#password_input, QWidget#form_container {
        background-color: #f8f9fa;
        color: black;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    QLabel#login_label, QLabel#password_label {
        color: black;
        background-color: #f8f9fa;
    }
"""



