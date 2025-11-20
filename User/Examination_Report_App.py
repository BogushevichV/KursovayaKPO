from PySide6.QtWidgets import (QMainWindow, QWidget, QMessageBox, QTableWidgetItem, QHBoxLayout, QVBoxLayout,
                               QComboBox, QLineEdit, QSpinBox, QDateEdit, QTableWidget, QHeaderView,
                               QPushButton, QFormLayout, QScrollArea)
from PySide6.QtCore import Qt, QRegularExpression, QDate
from PySide6.QtGui import QRegularExpressionValidator

from DataBase.Report_Manager import ReportManager
from Grade_Item_Delegate import GradeItemDelegate
from Excel_Importer import ExcelImporter


class GradeBookApp(QMainWindow):
    def __init__(self, parent=None, signals=None):
        super().__init__(parent)
        self.signals = signals
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
        # self.setStyleSheet("background-color: white;")
        self.grade_mode = "grade"
        self.db_manager = ReportManager(**{
            'dbname': "ExaminationReport",
            'user': "postgres",
            'password': "",
            'host': "127.0.0.1",
            'port': "5432"
        })
        #
        #
        #
        # 2 PODKLYUCHENIYA K BD
        #
        #
        #
        #
        #

        self.welcome_window = None  # Добавляем ссылку на окно приветствия

        self.faculty_codes = [
            "АТФ", "ФГДИЭ", "МСФ", "МТФ", "ФММП",
            "ЭФ", "ФИТР", "ФТУГ", "ИПФ", "ФЭС",
            "АФ", "СФ", "ПСФ", "ФТК", "ВТФ", "СТФ"
        ]

        self.init_ui()
        self.add_empty_row()

        self.faculty_full = [
            "Автотракторный",
            "горного дела и инженерной экологии",
            "Машиностроительный",
            "Механико-технологический",
            "маркетинга, менеджмента и предпринимательства",
            "Энергетический",
            "информационных технологий и робототехники",
            "технологий управления и гуманитаризации",
            "Инженерно-педагогический",
            "энергетического строительства",
            "Архитектурный",
            "Строительный",
            "Приборостроительный",
            "транспортных коммуникаций",
            "Военно-технический",
            "Спортивно-технический"
        ]

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
        self.group_input.setPlaceholderText(self.tr("Номер группы"))
        self.group_input.setFixedWidth(125)
        self.group_input.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9]*")))
        top_panel_layout.addWidget(self.group_input)

        self.course_input = QLineEdit()
        self.course_input.setPlaceholderText(self.tr("Курс"))
        self.course_input.setFixedWidth(70)
        self.course_input.setValidator(QRegularExpressionValidator(QRegularExpression("[1-6]")))
        top_panel_layout.addWidget(self.course_input)

        self.semester_combo = QComboBox()
        self.semester_combo.addItems([self.tr("1 семестр"), self.tr("2 семестр")])
        self.semester_combo.setFixedWidth(100)
        top_panel_layout.addWidget(self.semester_combo)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText(self.tr("Название предмета"))
        self.subject_input.setFixedWidth(230)
        top_panel_layout.addWidget(self.subject_input)

        # Кнопки верхней панели
        self.btn_import = QPushButton(self.tr("Импорт из Excel"))
        self.btn_import.setStyleSheet(button_style)
        self.btn_import.clicked.connect(self.import_from_excel)
        top_panel_layout.addWidget(self.btn_import)

        self.btn_save = QPushButton(self.tr("Сохранить"))
        self.btn_save.setStyleSheet(button_style)
        self.btn_save.clicked.connect(self.save_data)
        top_panel_layout.addWidget(self.btn_save)

        self.btn_find_group = QPushButton(self.tr("Найти группу"))
        self.btn_find_group.setStyleSheet(button_style)
        self.btn_find_group.clicked.connect(self.find_group)
        top_panel_layout.addWidget(self.btn_find_group)

        self.btn_find_subject = QPushButton(self.tr("Найти предмет"))
        self.btn_find_subject.setStyleSheet(button_style)
        self.btn_find_subject.clicked.connect(self.find_subject)
        top_panel_layout.addWidget(self.btn_find_subject)

        self.btn_clear = QPushButton(self.tr("Очистить"))
        self.btn_clear.setStyleSheet(button_style)
        self.btn_clear.clicked.connect(self.clear_table)
        top_panel_layout.addWidget(self.btn_clear)

        top_panel_layout.addStretch()
        left_layout.addLayout(top_panel_layout)

        # Строим таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([self.tr("Фамилия, инициалы"), self.tr("№ зачетной книжки"),
                                              self.tr("Оценка/Зачет")])
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

        self.form_layout = QFormLayout(scroll_content)

        # Элементы формы
        self.statement_number_input = QLineEdit()
        self.statement_number_input.setPlaceholderText(self.tr("Номер ведомости"))
        self.statement_number_input.setStyleSheet(form_style)
        self.form_layout.addRow(self.tr("Номер ведомости:"), self.statement_number_input)

        self.education_type_combo = QComboBox()
        self.education_type_combo.addItems([self.tr("Общее высшее образование")])
        self.form_layout.addRow(self.tr("Вид образования:"), self.education_type_combo)

        self.study_form_combo = QComboBox()
        self.study_form_combo.addItems([self.tr("дневная"), self.tr("заочная")])
        self.form_layout.addRow(self.tr("Форма обучения:"), self.study_form_combo)

        self.exam_type_combo = QComboBox()
        self.exam_type_combo.addItems([self.tr("экзамен"), self.tr("зачёт"), self.tr("дифференцированный зачёт")])
        self.exam_type_combo.setCurrentIndex(0)
        self.exam_type_combo.currentTextChanged.connect(self.update_grade_mode)
        self.form_layout.addRow(self.tr("Форма аттестации:"), self.exam_type_combo)

        self.year_combo = QComboBox()
        for year in range(2000, 2101):
            self.year_combo.addItem(f"{year}/{year + 1}")
        self.year_combo.setCurrentText("2024/2025")
        self.form_layout.addRow(self.tr("Учебный год:"), self.year_combo)

        self.faculty_combo = QComboBox()
        for code in self.faculty_codes:
            self.faculty_combo.addItem(self.tr(code), code)
        self.form_layout.addRow(self.tr("Факультет:"), self.faculty_combo)

        self.hours_input = QSpinBox()
        self.hours_input.setRange(0, 1000)
        self.hours_input.setValue(108)
        self.hours_input.setStyleSheet(form_style)
        self.form_layout.addRow(self.tr("Количество часов:"), self.hours_input)

        self.credits_input = QSpinBox()
        self.credits_input.setRange(0, 10)
        self.credits_input.setValue(3)
        self.credits_input.setStyleSheet(form_style)
        self.form_layout.addRow(self.tr("Зачетные единицы:"), self.credits_input)

        self.teacher_input = QLineEdit()
        self.teacher_input.setPlaceholderText(self.tr("Фамилия И.О."))
        self.teacher_input.setStyleSheet(form_style)
        self.form_layout.addRow(self.tr("Преподаватель:"), self.teacher_input)

        self.exam_date_edit = QDateEdit()
        self.exam_date_edit.setCalendarPopup(True)
        self.exam_date_edit.setDate(QDate.currentDate())
        self.exam_date_edit.setStyleSheet(form_style)
        self.form_layout.addRow(self.tr("Дата аттестации:"), self.exam_date_edit)

        self.exam_format_input = QLineEdit()
        self.exam_format_input.setPlaceholderText(self.tr("очный/дистанционный"))
        self.exam_format_input.setStyleSheet(form_style)
        self.form_layout.addRow(self.tr("Формат аттестации:"), self.exam_format_input)

        self.dean_input = QLineEdit()
        self.dean_input.setPlaceholderText(self.tr("Фамилия И.О."))
        self.dean_input.setStyleSheet(form_style)
        self.form_layout.addRow(self.tr("Декан:"), self.dean_input)

        # Кнопка "Составить ведомость"
        self.btn_create_report = QPushButton(self.tr("Составить ведомость"))
        self.btn_create_report.setStyleSheet(button_style)
        self.btn_create_report.clicked.connect(self.create_exam_report)
        right_layout.addWidget(self.btn_create_report)

        # Кнопка "Назад"
        self.back_button = QPushButton(self.tr("Назад"))
        self.back_button.setFixedSize(100, 30)
        self.back_button.setStyleSheet(button_style)
        self.back_button.clicked.connect(self.return_to_welcome)

        # Контейнер для кнопки Назад
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.addStretch()
        button_layout.addWidget(self.back_button)

        right_layout.addWidget(scroll_area)
        right_layout.addWidget(button_container)
        right_layout.setContentsMargins(0, 0, 0, 10)

        main_layout.addWidget(right_panel, stretch=1)

        # Настройка окна
        self.setWindowTitle(self.tr("Панель составления ведомости"))
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
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Не удалось вернуться на начальное окно"))

    def get_full_faculty_name(self, abbrev):
        """Возвращает русское полное имя факультета по аббревиатуре"""
        if abbrev in self.faculty_codes:
            index = self.faculty_codes.index(abbrev)
            return self.faculty_full[index]
        return abbrev

    # abbr = self.faculty_combo.currentData()
    # full_name = self.get_full_faculty_name(abbr)
    # Возможно в вызове понадобится что-то поменять на это

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
                    QMessageBox.warning(
                        self,
                        self.tr("Ошибка"),
                        self.tr("Заполните обязательное поле: %1").replace("%1", field.replace("_", " "))
                    )

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
            QMessageBox.critical(
                self,
                self.tr("Ошибка"),
                self.tr("Ошибка при создании отчёта: %1").replace("%1", str(e))
            )

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
        """Поиск группы в БД и загрузка данных"""
        group_number = self.group_input.text()
        if not group_number:
            QMessageBox.warning(self, "Ошибка", "Введите номер группы!")
            return

        students = self.db_manager.find_group_students(group_number)
        if students is None:
            QMessageBox.warning(self, "Ошибка", "Ошибка при загрузке данных")
            return

        self.clear_table()

        # Заполняем таблицу
        for row, (name, gradebook) in enumerate(students):
            self.table.insertRow(row)

            item_name = QTableWidgetItem(name)
            item_name.setFlags(item_name.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, item_name)

            item_gradebook = QTableWidgetItem(gradebook)
            item_gradebook.setFlags(item_gradebook.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, item_gradebook)

            self.setup_grade_cell(row)

        self.add_empty_row()
        QMessageBox.information(self, "Успех", f"Загружено {len(students)} студентов")

    def find_subject(self):
        """Поиск предмета в БД и загрузка данных"""
        group_number = self.group_input.text()
        subject_name = self.subject_input.text()
        course = self.course_input.text()
        semester = self.semester_combo.currentText().split()[0]  # Берем только номер семестра

        if not all([group_number, subject_name, course]):
            QMessageBox.warning(self, "Ошибка", "Заполните все необходимые поля!")
            return

        grades = self.db_manager.find_subject_grades(subject_name, group_number, course, semester)
        if grades is None:
            QMessageBox.warning(self, "Ошибка", "Ошибка при загрузке данных")
            return

        self.clear_table()

        # Заполняем таблицу
        for row, (name, gradebook, grade) in enumerate(grades):
            self.table.insertRow(row)

            item_name = QTableWidgetItem(name)
            item_name.setFlags(item_name.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, item_name)

            item_gradebook = QTableWidgetItem(gradebook)
            item_gradebook.setFlags(item_gradebook.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, item_gradebook)

            # Устанавливаем оценку в зависимости от режима
            if self.grade_mode == "grade":
                grade_item = QTableWidgetItem(grade)
                grade_item.setFlags(grade_item.flags() | Qt.ItemFlag.ItemIsEditable)
                grade_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 2, grade_item)
            else:
                combo = QComboBox()
                combo.addItems(["не зачтено", "зачтено"])
                combo.setCurrentText(grade)
                self.table.setCellWidget(row, 2, combo)

        self.add_empty_row()
        QMessageBox.information(self, "Успех", f"Загружено {len(grades)} записей")

    def clear_table(self):
        """Очищает таблицу, оставляя одну пустую строку"""
        self.table.setRowCount(0)
        self.add_empty_row()

    def update_grade_mode(self):

        index = self.exam_type_combo.currentIndex()

        if index == 0:  # экзамен
            self.grade_mode = "grade"

        elif index == 1:  # зачёт
            self.grade_mode = "pass_fail"

        elif index == 2:  # дифференц. зачёт
            self.grade_mode = "grade"

        for row in range(self.table.rowCount()):
            self.setup_grade_cell(row)

    def import_from_excel(self):
        data = ExcelImporter.import_from_excel(self)
        if data:
            self.clear_table()

            for row, student in enumerate(data):
                self.table.insertRow(row)

                item_name = QTableWidgetItem(student['name'])
                item_name.setFlags(item_name.flags() | Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 0, item_name)

                item_gradebook = QTableWidgetItem(str(student['gradebook']))
                item_gradebook.setFlags(item_gradebook.flags() | Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 1, item_gradebook)

                self.setup_grade_cell(row)

            # Добавляем пустую строку и проверяем количество
            self.add_empty_row()
            self._check_empty_rows()

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
        combo_box.addItems([self.tr("не зачтено"), self.tr("зачтено")])
        combo_box.setCurrentIndex(-1)
        self.table.setCellWidget(row, 2, combo_box)

    def on_header_clicked(self, logicalIndex):
        if logicalIndex == 2:
            msg = QMessageBox()
            msg.setWindowTitle(self.tr("Выбор типа оценки"))
            msg.setText(self.tr("Выберите тип оценки для колонки:"))

            self.btn_grade = msg.addButton(self.tr("Оценка (0-10)"), QMessageBox.ButtonRole.ActionRole)
            self.btn_pass = msg.addButton(self.tr("Зачет (зачтено/не зачтено)"), QMessageBox.ButtonRole.ActionRole)
            msg.addButton(self.tr("Отмена"), QMessageBox.ButtonRole.RejectRole)

            msg.exec()

            if msg.clickedButton() == self.btn_grade:
                self.switch_to_grades()
            elif msg.clickedButton() == self.btn_pass:
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

    def retranslateUi(self):
        # Верхняя панель
        self.group_input.setPlaceholderText(self.tr("Номер группы"))
        self.course_input.setPlaceholderText(self.tr("Курс"))
        self.subject_input.setPlaceholderText(self.tr("Название предмета"))

        # Кнопки верхней панели
        self.btn_import.setText(self.tr("Импорт из Excel"))
        self.btn_save.setText(self.tr("Сохранить"))
        self.btn_find_group.setText(self.tr("Найти группу"))
        self.btn_find_subject.setText(self.tr("Найти предмет"))
        self.btn_clear.setText(self.tr("Очистить"))

        # Семестры
        self.semester_combo.setItemText(0, self.tr("1 семестр"))
        self.semester_combo.setItemText(1, self.tr("2 семестр"))

        # Заголовки таблицы
        self.table.setHorizontalHeaderLabels([
            self.tr("Фамилия, инициалы"),
            self.tr("№ зачетной книжки"),
            self.tr("Оценка/Зачет")
        ])

        # КомбоБоксы правой панели
        self.statement_number_input.setPlaceholderText(self.tr("Номер ведомости"))
        self.education_type_combo.setItemText(0, self.tr("Общее высшее образование"))
        self.study_form_combo.setItemText(0, self.tr("дневная"))
        self.study_form_combo.setItemText(1, self.tr("заочная"))
        self.exam_type_combo.setItemText(0, self.tr("экзамен"))
        self.exam_type_combo.setItemText(1, self.tr("зачёт"))
        self.exam_type_combo.setItemText(2, self.tr("дифференцированный зачёт"))

        # Факультеты
        self.form_layout.labelForField(self.faculty_combo).setText(self.tr("Факультет:"))
        for i, code in enumerate(self.faculty_codes):
            self.faculty_combo.setItemText(i, self.tr(code))

        # Правое меню
        self.teacher_input.setPlaceholderText(self.tr("Фамилия И.О."))
        self.exam_format_input.setPlaceholderText(self.tr("очный/дистанционный"))
        self.dean_input.setPlaceholderText(self.tr("Фамилия И.О."))

        # Кнопки снизу
        self.btn_create_report.setText(self.tr("Составить ведомость"))
        self.back_button.setText(self.tr("Назад"))

        # Заголовок окна
        self.setWindowTitle(self.tr("Панель составления ведомости"))
