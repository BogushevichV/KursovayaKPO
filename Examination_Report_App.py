from PySide6.QtWidgets import (QMainWindow, QWidget, QMessageBox, QTableWidgetItem, QHBoxLayout, QVBoxLayout,
                               QComboBox, QLineEdit, QSpinBox, QDateEdit, QTableWidget, QHeaderView,
                               QPushButton, QFormLayout, QScrollArea)
from PySide6.QtCore import Qt, QRegularExpression, QDate
from PySide6.QtGui import QRegularExpressionValidator


class GradeBookApp(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dean_input = None
        self.exam_format_input = None
        self.exam_date_edit = None
        self.teacher_input = None
        self.credits_input = None
        self.hours_input = None
        self.faculty_combo = None
        self.year_combo = None
        self.exam_type_combo = None
        self.study_form_combo = None
        self.education_type_combo = None
        self.statement_number_input = None
        self.table = None
        self.subject_input = None
        self.semester_combo = None
        self.course_input = None
        self.group_input = None
        self.setFixedSize(1920, 1000)
        self.setStyleSheet("background-color: White;")
        self.grade_mode = "grade"
        #
        #
        #
        # 2 PODKLYUCHENIYA K BD
        #
        #
        #
        #
        #
        self.init_ui()
        self.add_empty_row()
        self.welcome_window = None  # Добавляем ссылку на окно приветствия

    def set_welcome_window(self, welcome_window):
        """Устанавливает ссылку на окно приветствия"""
        self.welcome_window = welcome_window

    def init_ui(self):
        # Стиль кнопок
        button_style = """
            QPushButton {
                min-width: 180px;
                min-height: 40px;
                font-size: 16px;
                border-radius: 5px;
                background-color: #4CAF50;  /* Зеленый */
                color: white;
                border: 2px solid #45a049;
            }
            QPushButton:hover {
                background-color: #388038;
            }
        """

        # Стиль формы
        form_style = """
            QLineEdit, QSpinBox, QDateEdit, QComboBox {
                padding: 5px 10px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
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
                border: 1px solid black;  /* Толщина и цвет границы */
            }
            QHeaderView::section {
                background-color: #45a049;
                color: white;
                padding: 5px;
                border: none;
                font-size: 14px;
            }
        """

        # Применение стилей
        self.setStyleSheet(form_style)

        # Главный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Левая часть с таблицей
        left_layout = QVBoxLayout()

        # Строим верхнюю панель
        top_panel_layout = QHBoxLayout()

        # Элементы верхней панели
        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("Номер группы")
        self.group_input.setFixedWidth(125)
        self.group_input.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]*")))
        top_panel_layout.addWidget(self.group_input)

        self.course_input = QLineEdit()
        self.course_input.setPlaceholderText("Курс")
        self.course_input.setFixedWidth(70)
        self.course_input.setValidator(QRegularExpressionValidator(QRegularExpression("[1-6]")))
        top_panel_layout.addWidget(self.course_input)

        self.semester_combo = QComboBox()
        self.semester_combo.addItems(["1 семестр", "2 семестр"])
        self.semester_combo.setFixedWidth(100)
        top_panel_layout.addWidget(self.semester_combo)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Название предмета")
        self.subject_input.setFixedWidth(230)
        top_panel_layout.addWidget(self.subject_input)

        # Кнопки верхней панели
        btn_import = QPushButton("Импорт из Excel")
        btn_import.setStyleSheet(button_style)
        btn_import.clicked.connect(self.import_from_excel)
        top_panel_layout.addWidget(btn_import)

        btn_save = QPushButton("Сохранить")
        btn_save.setStyleSheet(button_style)
        btn_save.clicked.connect(self.save_data)
        top_panel_layout.addWidget(btn_save)

        btn_find_group = QPushButton("Найти группу")
        btn_find_group.setStyleSheet(button_style)
        btn_find_group.clicked.connect(self.find_group)
        top_panel_layout.addWidget(btn_find_group)

        btn_find_subject = QPushButton("Найти предмет")
        btn_find_subject.setStyleSheet(button_style)
        btn_find_subject.clicked.connect(self.find_subject)
        top_panel_layout.addWidget(btn_find_subject)

        btn_clear = QPushButton("Очистить")
        btn_clear.setStyleSheet(button_style)
        btn_clear.clicked.connect(self.clear_table)
        top_panel_layout.addWidget(btn_clear)

        top_panel_layout.addStretch()
        left_layout.addLayout(top_panel_layout)

        # Строим таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Фамилия, инициалы", "№ зачетной книжки", "Оценка/Зачет"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setItemDelegateForColumn(2, GradeItemDelegate())
        left_layout.addWidget(self.table)

        main_layout.addLayout(left_layout, stretch=3)

        # Правая панель с формой
        right_panel = QWidget()
        right_panel.setFixedWidth(400)
        right_panel.setFixedHeight(620)
        right_layout = QVBoxLayout(right_panel)

        # Контейнер для формы с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)

        form_layout = QFormLayout(scroll_content)

        # Элементы формы
        self.statement_number_input = QLineEdit()
        self.statement_number_input.setPlaceholderText("Номер ведомости")
        self.statement_number_input.setStyleSheet(form_style)
        form_layout.addRow("Номер ведомости:", self.statement_number_input)

        self.education_type_combo = QComboBox()
        self.education_type_combo.addItems(["Общее высшее образование"])
        form_layout.addRow("Вид образования:", self.education_type_combo)

        self.study_form_combo = QComboBox()
        self.study_form_combo.addItems(["дневная", "заочная"])
        form_layout.addRow("Форма обучения:", self.study_form_combo)

        self.exam_type_combo = QComboBox()
        self.exam_type_combo.addItems(["экзамен", "зачёт", "дифференцированный зачёт"])
        self.exam_type_combo.setCurrentIndex(0)
        self.exam_type_combo.currentTextChanged.connect(self.update_grade_mode)
        form_layout.addRow("Форма аттестации:", self.exam_type_combo)

        self.year_combo = QComboBox()
        for year in range(2000, 2101):
            self.year_combo.addItem(f"{year}/{year + 1}")
        self.year_combo.setCurrentText("2024/2025")
        form_layout.addRow("Учебный год:", self.year_combo)

        self.faculty_combo = QComboBox()
        faculties = ["АТФ", "ФГДИЭ", "МСФ", "МТФ", "ФММП", "ЭФ", "ФИТР", "ФТУГ",
                     "ИПФ", "ФЭС", "АФ", "СФ", "ПСФ", "ФТК", "ВТФ", "СТФ"]
        self.faculty_combo.addItems(faculties)
        form_layout.addRow("Факультет:", self.faculty_combo)

        self.hours_input = QSpinBox()
        self.hours_input.setRange(0, 1000)
        self.hours_input.setValue(108)
        self.hours_input.setStyleSheet(form_style)
        form_layout.addRow("Количество часов:", self.hours_input)

        self.credits_input = QSpinBox()
        self.credits_input.setRange(0, 10)
        self.credits_input.setValue(3)
        self.credits_input.setStyleSheet(form_style)
        form_layout.addRow("Зачетные единицы:", self.credits_input)

        self.teacher_input = QLineEdit()
        self.teacher_input.setPlaceholderText("Фамилия И.О.")
        self.teacher_input.setStyleSheet(form_style)
        form_layout.addRow("Преподаватель:", self.teacher_input)

        self.exam_date_edit = QDateEdit()
        self.exam_date_edit.setCalendarPopup(True)
        self.exam_date_edit.setDate(QDate.currentDate())
        self.exam_date_edit.setStyleSheet(form_style)
        form_layout.addRow("Дата аттестации:", self.exam_date_edit)

        self.exam_format_input = QLineEdit()
        self.exam_format_input.setPlaceholderText("очный/дистанционный")
        self.exam_format_input.setStyleSheet(form_style)
        form_layout.addRow("Формат аттестации:", self.exam_format_input)

        self.dean_input = QLineEdit()
        self.dean_input.setPlaceholderText("Фамилия И.О.")
        self.dean_input.setStyleSheet(form_style)
        form_layout.addRow("Декан:", self.dean_input)

        # Кнопка "Составить ведомость"
        btn_create_report = QPushButton("Составить ведомость")
        btn_create_report.setStyleSheet(button_style)
        btn_create_report.clicked.connect(self.create_exam_report)
        right_layout.addWidget(btn_create_report)

        # Кнопка "Назад"
        back_button = QPushButton("Назад")
        back_button.setFixedSize(100, 30)
        back_button.setStyleSheet(button_style)
        back_button.clicked.connect(self.return_to_welcome)

        # Контейнер для кнопки Назад
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.addStretch()
        button_layout.addWidget(back_button)

        right_layout.addWidget(scroll_area)
        right_layout.addWidget(button_container)
        right_layout.setContentsMargins(0, 0, 0, 10)

        main_layout.addWidget(right_panel, stretch=1)

        # Настройка окна
        self.setWindowTitle("Панель составления ведомости")
        self.setGeometry(0, 0, 1920, 980)

        # Подключение сигналов
        self.table.itemChanged.connect(self.handle_item_changed)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)

    def return_to_welcome(self):
        """Возврат на окно приветствия"""
        if self.welcome_window:
            self.welcome_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось вернуться на начальное окно")

    @staticmethod
    def get_full_faculty_name(abbrev):
        """Возвращает полное название факультета по аббревиатуре (использует match-case)"""
        match abbrev:
            case "АТФ":
                return "Автотракторный"
            case "ФГДИЭ":
                return "горного дела и инженерной экологии"
            case "МСФ":
                return "Машиностроительный"
            case "МТФ":
                return "Механико-технологический"
            case "ФММП":
                return "маркетинга, менеджмента и предпринимательства"
            case "ЭФ":
                return "Энергетический"
            case "ФИТР":
                return "информационных технологий и робототехники"
            case "ФТУГ":
                return "технологий управления и гуманитаризации"
            case "ИПФ":
                return "Инженерно-педагогический"
            case "ФЭС":
                return "энергетического строительства"
            case "АФ":
                return "Архитектурный"
            case "СФ":
                return "Строительный"
            case "ПСФ":
                return "Приборостроительный"
            case "ФТК":
                return "транспортных коммуникаций"
            case "ВТФ":
                return "Военно-технический"
            case "СТФ":
                return "Спортивно-технический"
            case _:
                return abbrev

    def create_exam_report(self):
        """Создание ведомости с данными из формы и БД"""
        try:
            # Проверка обязательных полей
            required_fields = {
                'statement_number': self.statement_number_input.text(),
                'group': self.group_input.text(),
                'course': self.course_input.text(),
                'subject': self.subject_input.text(),
                'semester': self.semester_combo.currentText().split()[0]
            }

            for field, value in required_fields.items():
                if not value:
                    QMessageBox.warning(self, "Ошибка",
                                        f"Заполните обязательное поле: {field.replace('_', ' ')}")
                    return

            abbrev = self.faculty_combo.currentText()
            faculty = self.get_full_faculty_name(abbrev)

            # Собираем данные из формы
            form_data = {
                'statement_number': self.statement_number_input.text(),
                'education_type': self.education_type_combo.currentText(),
                'study_form': self.study_form_combo.currentText(),
                'exam_type': self.exam_type_combo.currentText(),
                'year': self.year_combo.currentText(),
                'semester': self.semester_combo.currentText().split()[0],
                'faculty': faculty,
                'course': self.course_input.text(),
                'group': self.group_input.text(),
                'subject': self.subject_input.text(),
                'hours': str(self.hours_input.value()),
                'credits': str(self.credits_input.value()),
                'teacher': self.teacher_input.text(),
                'exam_date': self.exam_date_edit.date().toString("dd.MM.yyyy"),
                'exam_format': self.exam_format_input.text(),
                'dean': self.dean_input.text()
            }

            # Параметры подключения к БД
            # ДОПИСАТЬ
            # ДОПИСАТЬ
            # ДОПИСАТЬ
            # ДОПИСАТЬ
            # ДОПИСАТЬ
            # ДОПИСАТЬ
            # ДОПИСАТЬ
            # ДОПИСАТЬ
            # ДОПИСАТЬ


        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании отчёта: {str(e)}")

    def handle_item_changed(self, item):
        """Обработчик изменения данных в таблице"""
        # Проверяем, изменили ли последнюю строку
        if item.row() == self.table.rowCount() - 1:
            if any(self.table.item(item.row(), col) is not None and
                   self.table.item(item.row(), col).text().strip() != ""
                   for col in range(self.table.columnCount())):
                self.add_empty_row()

        # Проверяем количество пустых строк в конце таблицы
        self._check_empty_rows()

    def _check_empty_rows(self):
        """Проверяет количество пустых строк в конце таблицы и удаляет лишние"""
        empty_rows_at_end = 0

        # Считаем количество полностью пустых строк в конце таблицы
        for row in reversed(range(self.table.rowCount())):
            if all(self.table.item(row, col) is None or
                   self.table.item(row, col).text().strip() == ""
                   for col in range(self.table.columnCount())):
                empty_rows_at_end += 1
            else:
                break

        # Если пустых строк больше одной, удаляем лишние
        if empty_rows_at_end > 1:
            rows_to_remove = empty_rows_at_end - 1
            self.table.setRowCount(self.table.rowCount() - rows_to_remove)

    def add_empty_row(self):
        """Добавляет пустую строку в таблицу"""
        current_rows = self.table.rowCount()
        self.table.setRowCount(current_rows + 1)

        # Добавляем пустые ячейки
        for col in range(self.table.columnCount()):
            item = QTableWidgetItem()
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            if col == 2 and self.grade_mode == "grade":
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(current_rows, col, item)

        # Проверяем количество пустых строк
        self._check_empty_rows()

    def find_group(self):
        pass

    def find_subject(self):
        pass

    def clear_table(self):
        """Очищает таблицу, оставляя одну пустую строку"""
        self.table.setRowCount(0)
        self.add_empty_row()

    def update_grade_mode(self, exam_type):
        """Обновляет режим оценки в зависимости от выбранного типа аттестации"""
        if exam_type == "экзамен":
            self.grade_mode = "grade"
        elif exam_type == "зачёт":
            self.grade_mode = "pass_fail"
        elif exam_type == "дифференцированный зачёт":
            self.grade_mode = "grade"

        for row in range(self.table.rowCount()):
            self.setup_grade_cell(row)

    def import_from_excel(self):
        pass

    def setup_grade_cell(self, row):
        if self.grade_mode == "grade":
            self.show_as_grade(row)
        else:
            self.show_as_pass_fail(row)

    def show_as_grade(self, row):
        if self.table.cellWidget(row, 2):
            self.table.removeCellWidget(row, 2)

        grade_item = QTableWidgetItem()
        grade_item.setFlags(grade_item.flags() | Qt.ItemFlag.ItemIsEditable)
        grade_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 2, grade_item)

    def show_as_pass_fail(self, row):
        if self.table.item(row, 2):
            self.table.takeItem(row, 2)

        combo_box = QComboBox()
        combo_box.addItems(["не зачтено", "зачтено"])
        combo_box.setCurrentIndex(-1)
        self.table.setCellWidget(row, 2, combo_box)

    def on_header_clicked(self, logicalIndex):
        if logicalIndex == 2:
            msg = QMessageBox()
            msg.setWindowTitle("Выбор типа оценки")
            msg.setText("Выберите тип оценки для колонки:")

            btn_grade = msg.addButton("Оценка (0-10)", QMessageBox.ButtonRole.ActionRole)
            btn_pass = msg.addButton("Зачет (зачтено/не зачтено)", QMessageBox.ButtonRole.ActionRole)
            msg.addButton("Отмена", QMessageBox.ButtonRole.RejectRole)

            msg.exec()

            if msg.clickedButton() == btn_grade:
                self.switch_to_grades()
            elif msg.clickedButton() == btn_pass:
                self.switch_to_pass_fail()

    def save_data(self):
        pass

    def _get_grade_value(self, row):
        """Получает значение оценки из ячейки"""
        if self.grade_mode == "grade":
            grade_item = self.table.item(row, 2)
            return grade_item.text() if grade_item else ""
        else:
            combo = self.table.cellWidget(row, 2)
            return combo.currentText() if combo else "не зачтено"

    def switch_to_grades(self):
        self.grade_mode = "grade"
        self.table.setItemDelegateForColumn(2, GradeItemDelegate(self.table))
        for row in range(self.table.rowCount()):
            self.show_as_grade(row)

    def switch_to_pass_fail(self):
        self.grade_mode = "pass_fail"
        self.table.setItemDelegateForColumn(2, None)
        for row in range(self.table.rowCount()):
            self.show_as_pass_fail(row)