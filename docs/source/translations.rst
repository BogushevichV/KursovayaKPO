Многоязычная поддержка
======================

Обзор
-----

Система Exam Report поддерживает три языка:
1. **Русский (ru)** - основной язык
2. **Английский (en)** - международный
3. **Китайский (zh)** - для иностранных студентов

Структура файлов переводов
--------------------------

.. code-block:: text

    translations/
    ├── en.ts     # Английский (исходные строки + переводы)
    ├── en.qm     # Скомпилированный английский (бинарный)
    ├── ru.ts     # Русский перевод
    ├── ru.qm     # Скомпилированный русский
    ├── zh.ts     # Китайский перевод
    └── zh.qm     # Скомпилированный китайский

Формат файлов .ts
-----------------

Файлы .ts (Translation Source) используют XML формат Qt Linguist:

.. literalinclude:: ../../translations/en.ts
   :language: xml
   :linenos:
   :lines: 1-30
   :caption: Пример перевода (en.ts)

Пример перевода интерфейса:

.. code-block:: xml

   <message>
       <location filename="../Admin/Admin_Window.py" line="36"/>
       <source>Панель администратора</source>
       <translation>Admin panel</translation>
   </message>

   <message>
       <location filename="../User/User_Window.py" line="42"/>
       <source>Вход пользователя</source>
       <translation>User login</translation>
   </message>

Загрузка переводов в приложении
-------------------------------

Основная логика загрузки переводов в `Main.py`:

.. literalinclude:: ../../Main.py
   :language: python
   :linenos:
   :lines: 54-70
   :caption: Загрузка переводов в Main.py
   :emphasize-lines: 1-10

Метод загрузки языка:

.. code-block:: python
   :linenos:

   def load_language(self, lang_code):
       self.translator = QTranslator()
       if self.translator.load(f"translations/{lang_code}.qm"):
           QCoreApplication.installTranslator(self.translator)
           self.current_lang = lang_code
           self.settings.setValue("language", lang_code)
           self.signals.language_changed.emit(lang_code)
       else:
           print(f"⚠ Не удалось загрузить translations/{lang_code}.qm")

Смена языка в WelcomeWindow
---------------------------

Класс `Welcome_Window.py` реализует переключение языков:

.. literalinclude:: ../../Welcome_Window.py
   :language: python
   :linenos:
   :lines: 27-45
   :caption: WelcomeWindow - инициализация выбора языка

Выпадающий список языков:

.. code-block:: python
   :linenos:

   # === Выпадающий список выбора языка ===
   self.language_box = QComboBox()
   self.language_box.addItem("Русский", "ru")
   self.language_box.addItem("English", "en")
   self.language_box.addItem("中文 (Chinese)", "zh")

Сигнал смены языка:

.. code-block:: python
   :linenos:

   def _emit_language_change(self):
       lang_code = self.language_box.currentData()
       self.language_changed.emit(lang_code)

Добавление нового языка
-----------------------

1. **Создайте файл перевода** в Qt Linguist
2. **Добавьте язык** в выпадающий список:

   .. code-block:: python

      self.language_box.addItem("Español", "es")

3. **Создайте файлы перевода:**
   - `translations/es.ts` - исходный файл
   - `translations/es.qm` - скомпилированный файл

4. **Обновите метод загрузки** (автоматически поддерживается)

Работа с Qt Linguist
--------------------

Для редактирования переводов:

1. **Установите Qt Linguist** (входит в состав Qt)
2. **Откройте .ts файл:** `File → Open`
3. **Добавьте переводы:** Для каждой строки введите перевод
4. **Сохраните:** `File → Save`
5. **Скомпилируйте в .qm:** `File → Release`

Строки для перевода в коде
--------------------------

В коде используйте функцию `self.tr()`:

.. code-block:: python

   # Пример из Welcome_Window.py
   self.welcome_label = QLabel(self.tr("Добро пожаловать!"))
   self.user_button = QPushButton(self.tr("Войти как пользователь"))
   self.admin_button = QPushButton(self.tr("Войти как администратор"))

Для динамических строк с параметрами:

.. code-block:: python

   # Пример из Admin_Window.py
   message = self.tr("Администратор {login} успешно добавлен!").format(login=login)
   QMessageBox.information(self, self.tr("Успех"), message)

Факультеты и специальности
--------------------------

В файлах переводов также содержатся названия факультетов:

.. code-block:: xml

   <message>
       <location filename="../User/Examination_Report_App.py" line="49"/>
       <source>АТФ</source>
       <translation>ATF</translation>
   </message>
   <message>
       <location filename="../User/Examination_Report_App.py" line="50"/>
       <source>ФГДИЭ</source>
       <translation>FMEE</translation>
   </message>

Всего поддерживается 16 факультетов на трех языках.

Отладка переводов
-----------------

Для проверки работы переводов:

1. **Включите вывод отладки:**

   .. code-block:: python

      import os
      os.environ['QT_LOGGING_RULES'] = 'qt.l10n.debug=true'

2. **Проверьте загрузку файлов:**
   - Убедитесь, что файлы .qm существуют
   - Проверьте пути к файлам переводов
   - Убедитесь в правильности кодов языков

3. **Тестирование:**
   - Запустите приложение
   - Смените язык в выпадающем списке
   - Проверьте, что все строки переведены