import pytest
from PySide6.QtCore import Qt
from Welcome_Window import WelcomeWindow  # Импортируйте ваш файл

@pytest.fixture
def window(qtbot):
    w = WelcomeWindow()
    qtbot.addWidget(w)
    w.show()
    return w

def test_widgets_exist(window):
    assert window.welcome_label is not None
    assert window.user_button is not None
    assert window.admin_button is not None
    assert window.language_box is not None
    assert window.image_label is not None

def test_default_texts(window):
    assert window.welcome_label.text() == "Добро пожаловать!"
    assert window.user_button.text() == "Войти как пользователь"
    assert window.admin_button.text() == "Войти как администратор"

def test_user_login_signal(qtbot, window):
    with qtbot.waitSignal(window.user_login_requested, timeout=500):
        qtbot.mouseClick(window.user_button, Qt.LeftButton)

def test_admin_login_signal(qtbot, window):
    with qtbot.waitSignal(window.admin_login_requested, timeout=500):
        qtbot.mouseClick(window.admin_button, Qt.LeftButton)

def test_language_change_signal(qtbot, window):
    with qtbot.waitSignal(window.language_changed, timeout=500):
        window.language_box.setCurrentIndex(1)  # переключаем язык

def test_retranslate_ui(window):
    # имитируем смену языка
    window.retranslateUi()
    assert window.welcome_label.text() in ["Добро пожаловать!", "Welcome", "欢迎"]

def test_image_loaded(window):
    pix = window.image_label.pixmap()
    assert pix is not None
    assert pix.width() > 0
    assert pix.height() > 0

