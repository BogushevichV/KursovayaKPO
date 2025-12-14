"""
Стили для окна приветствия
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

ADMIN_BUTTON_STYLE = BUTTON_STYLE + """
    background-color: #ff6666; 
    border: 2px solid #e65c5c;
"""

COMBO_STYLE = """
    QComboBox {
        min-width: 150px;
        min-height: 36px;
        font-size: 16px;
        border-radius: 5px;
        background-color: #4CAF50;
        color: white;
        border: 2px solid #45a049;
        padding-left: 10px;
    }
    QComboBox:hover {
        background-color: #388038;
    }
    QComboBox::drop-down {
        width: 25px;
        border: none;
        background-color: transparent;
    }
    QComboBox QAbstractItemView {
        background-color: white;
        color: black;
        border-radius: 5px;
        selection-background-color: #4CAF50;
        selection-color: white;
    }
"""



