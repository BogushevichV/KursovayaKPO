"""
Стили для приложения ведомостей
"""

BUTTON_STYLE = """
    QPushButton {
        min-width: 180px;
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
    QLineEdit, QSpinBox, QDateEdit, QComboBox {
        padding: 5px 10px;
        border: 1px solid #ced4da;
        border-radius: 4px;
        font-size: 14px;
        color: black;
        background: white;
    }
    QLabel {
        background: transparent;
        border: none;
        font-size: 14px;
    }
    QTableWidget {
        background-color: #4CAF50;
        border: 1px solid #45a049;
        border-radius: 10px;
        font-size: 20px;
        color: white;
    }
    QTableWidget::item {
        border: 1px solid black;
    }
    QHeaderView::section {
        background-color: #45a049;
        color: white;
        padding: 5px;
        border: none;
        font-size: 14px;
    }
"""



