Установка и настройка
=====================

В этом разделе описывается процесс создания установочного пакета для приложения Exam Report System.
Для создания установщика используется **Inno Setup** - бесплатный инструмент для создания инсталляторов Windows.

Предварительные требования
--------------------------

Перед созданием установочного пакета убедитесь, что у вас установлено:

### Для разработки:
- Python 3.9 или выше
- PostgreSQL 13 или выше
- Git для контроля версий
- Inno Setup 6 или выше

### Для конечного пользователя:
- Windows 10 или выше (64-bit)
- 4 ГБ оперативной памяти
- 2 ГБ свободного места на диске
- Подключение к интернету (для работы с сервером)

Создание установочного пакета
-----------------------------

### 1. Подготовка зависимостей

Создайте файл `requirements.txt` со всеми зависимостями:

.. code-block:: text

   # requirements.txt
   PySide6==6.5.0
   requests==2.31.0
   openpyxl==3.1.2
   python-docx==1.1.0
   psycopg2-binary==2.9.9
   flask==2.3.3
   flask-cors==4.0.0

### 2. Структура установочного пакета

Подготовьте следующую структуру каталогов для установщика:

.. code-block:: text

   ExamReport_Installer/
   ├── Setup/
   │   ├── Client/          # Клиентская часть
   │   │   ├── main.exe     # Скомпилированный клиент
   │   │   ├── python39.dll # Python DLL
   │   │   └── ...         # Остальные зависимости
   │   ├── Server/          # Серверная часть (опционально)
   │   └── Database/        # Скрипты БД
   ├── Documentation/       # Документация
   ├── Examples/           # Примеры файлов
   └── setup.iss           # Скрипт Inno Setup

### 3. Создание скрипта Inno Setup

Создайте файл `setup.iss` со следующим содержимым:

.. code-block:: pascal
   :linenos:

   ; Exam Report System - Скрипт установки Inno Setup
   ; Внимание: Бесплатная версия Inno Setup подходит только для
   ; некоммерческого использования. Для коммерческого использования
   ; необходимо приобрести лицензию.

   [Setup]
   ; Основная информация
   AppName=Exam Report System
   AppVersion=1.0.0
   AppPublisher=BNTU University
   AppPublisherURL=https://github.com/BogushevichV/KursovayaKPO
   AppSupportURL=https://github.com/BogushevichV/KursovayaKPO/issues
   AppUpdatesURL=https://github.com/BogushevichV/KursovayaKPO/releases
   DefaultDirName={pf}\ExamReportSystem
   DefaultGroupName=Exam Report System
   Compression=lzma2
   SolidCompression=yes
   OutputDir=Output
   OutputBaseFilename=ExamReportSystem_Setup
   SetupIconFile=Setup\Client\icon.ico
   UninstallDisplayIcon={app}\icon.ico
   LicenseFile=LICENSE.txt
   InfoBeforeFile=README.txt
   ArchitecturesAllowed=x64
   ArchitecturesInstallIn64BitMode=x64

   [Languages]
   Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

   [Tasks]
   Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
   Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

   [Files]
   ; Клиентская часть
   Source: "Setup\Client\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
   ; Серверная часть (если включается в установку)
   ; Source: "Setup\Server\*"; DestDir: "{app}\Server"; Flags: ignoreversion recursesubdirs createallsubdirs
   ; Документация
   Source: "Documentation\*"; DestDir: "{app}\Documentation"; Flags: ignoreversion recursesubdirs createallsubdirs
   ; Примеры
   Source: "Examples\*"; DestDir: "{app}\Examples"; Flags: ignoreversion recursesubdirs createallsubdirs
   ; База данных
   Source: "Database\*"; DestDir: "{app}\Database"; Flags: ignoreversion recursesubdirs createallsubdirs

   [Icons]
   Name: "{group}\Exam Report System"; Filename: "{app}\main.exe"
   Name: "{group}\Документация"; Filename: "{app}\Documentation\index.html"
   Name: "{group}\Удалить Exam Report System"; Filename: "{uninstallexe}"
   Name: "{commondesktop}\Exam Report System"; Filename: "{app}\main.exe"; Tasks: desktopicon
   Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Exam Report System"; Filename: "{app}\main.exe"; Tasks: quicklaunchicon

   [Run]
   ; Запуск приложения после установки
   Filename: "{app}\main.exe"; Description: "{cm:LaunchProgram,Exam Report System}"; Flags: nowait postinstall skipifsilent
   ; Запуск скрипта настройки БД (опционально)
   ; Filename: "{app}\Database\init_database.bat"; Description: "Настроить базу данных"; Flags: runhidden

   [UninstallDelete]
   Type: filesandordirs; Name: "{app}\logs"
   Type: files; Name: "{app}\*.log"

   [Code]
   // Проверка наличия .NET Framework
   function InitializeSetup(): Boolean;
   begin
     if not IsDotNetInstalled(net452, '') then
     begin
       MsgBox('Для работы приложения требуется Microsoft .NET Framework 4.5.2 или выше.' + #13#10 +
              'Пожалуйста, установите его и запустите установку снова.', mbError, MB_OK);
       Result := False;
     end
     else
       Result := True;
   end;

   // Проверка наличия Python (опционально)
   function IsPythonInstalled(): Boolean;
   var
     PythonPath: string;
   begin
     Result := RegQueryStringValue(HKLM, 'Software\Python\PythonCore\3.9\InstallPath', '', PythonPath) or
               RegQueryStringValue(HKCU, 'Software\Python\PythonCore\3.9\InstallPath', '', PythonPath);
   end;

### 4. Создание бат-файла для инициализации БД

Создайте файл `init_database.bat` для настройки PostgreSQL:

.. code-block:: batch
   :linenos:

   @echo off
   echo Настройка базы данных Exam Report System...
   echo.

   REM Проверка наличия PostgreSQL
   where psql >nul 2>nul
   if %ERRORLEVEL% neq 0 (
       echo Ошибка: PostgreSQL не найден!
       echo Установите PostgreSQL 13 или выше и добавьте его в PATH.
       pause
       exit /b 1
   )

   REM Запрос данных для подключения
   set /p PGHOST=Введите хост PostgreSQL [localhost]:
   if "%PGHOST%"=="" set PGHOST=localhost

   set /p PGPORT=Введите порт PostgreSQL [5432]:
   if "%PGPORT%"=="" set PGPORT=5432

   set /p PGUSER=Введите пользователя PostgreSQL [postgres]:
   if "%PGUSER%"=="" set PGUSER=postgres

   echo Введите пароль для пользователя %PGUSER%:
   set /p PGPASSWORD=

   REM Создание базы данных
   echo Создание базы данных ExaminationReport...
   psql -h %PGHOST% -p %PGPORT% -U %PGUSER% -c "CREATE DATABASE ExaminationReport;" postgres

   if %ERRORLEVEL% neq 0 (
       echo Ошибка при создании базы данных!
       pause
       exit /b 1
   )

   REM Выполнение скрипта схемы
   echo Загрузка схемы базы данных...
   psql -h %PGHOST% -p %PGPORT% -U %PGUSER% -d ExaminationReport -f "schema.sql"

   if %ERRORLEVEL% eq 0 (
       echo База данных успешно настроена!
   ) else (
       echo Ошибка при загрузке схемы!
   )

   pause

### 5. Создание ярлыков и меню "Пуск"

Inno Setup автоматически создаст:
- Ярлык в меню "Пуск" в папке "Exam Report System"
- Ярлык на рабочем столе (опционально)
- Ярлык в панели быстрого запуска (опционально)
- Запись в "Установка и удаление программ"

### 6. Сборка установщика

1. Откройте Inno Setup Compiler
2. Загрузите файл `setup.iss`
3. Нажмите "Compile" (F9)
4. Готовый установщик будет создан в папке `Output`

Файлы установщика:
- `ExamReportSystem_Setup.exe` - основной установщик
- `ExamReportSystem_Setup.exe.sig` - цифровая подпись (если настроена)

Распределенная установка
------------------------

### Вариант 1: Полная установка (все компоненты)

Установщик включает:
- Клиентское приложение (PySide6 GUI)
- Серверное приложение (Flask API) - опционально
- База данных (скрипты инициализации)
- Документация в формате HTML
- Примеры Excel файлов

### Вариант 2: Только клиент

Для работы в сети с уже развернутым сервером:
- Только клиентское приложение
- Файл конфигурации для подключения к серверу

Конфигурационный файл `config.ini`:

.. code-block:: ini

   [SERVER]
   host = 192.168.1.100
   port = 5000
   ssl = false

   [DATABASE]
   auto_connect = true

   [UI]
   language = ru
   theme = light

### Вариант 3: Серверная установка

Для системных администраторов:
- Серверное приложение как служба Windows
- Автоматическое резервное копирование БД
- Мониторинг и логирование

Запуск сервера как службы:

.. code-block:: batch

   sc create ExamReportServer binPath= "C:\Program Files\ExamReportSystem\Server\server.exe"
   sc description ExamReportServer "Сервер Exam Report System"
   sc start ExamReportServer

Настройка после установки
-------------------------

### 1. Первый запуск

При первом запуске приложение:
1. Проверит наличие файла конфигурации
2. Предложит настроить подключение к серверу
3. Создаст необходимые каталоги для логов и данных
4. Проверит соединение с базой данных

### 2. Настройка подключения к БД

Если БД не настроена, появится мастер настройки:

.. code-block:: text

   Мастер настройки базы данных
   ----------------------------
   1. Тип подключения: PostgreSQL
   2. Хост: localhost
   3. Порт: 5432
   4. Имя БД: ExaminationReport
   5. Пользователь: postgres
   6. Пароль: *******

### 3. Настройка администратора

После настройки БД необходимо создать первого администратора:

1. Запустите приложение
2. Нажмите "Войти как администратор"
3. Используйте стандартные учетные данные:
   - Логин: `admin`
   - Пароль: `admin123`
4. Смените пароль в панели администратора

Обновление приложения
---------------------

### Автоматическое обновление

Приложение проверяет обновления при запуске:

.. code-block:: python

   # client_update.py
   import requests
   import json

   def check_for_updates(current_version):
       try:
           response = requests.get("https://api.github.com/repos/BogushevichV/KursovayaKPO/releases/latest")
           latest = response.json()
           if latest['tag_name'] > current_version:
               return latest['assets'][0]['browser_download_url']
       except:
           return None

### Ручное обновление

1. Скачайте новую версию установщика
2. Запустите установку поверх существующей
3. Установщик сохранит настройки и данные

Удаление приложения
-------------------

### Через панель управления:

1. Откройте "Панель управления" → "Программы и компоненты"
2. Найдите "Exam Report System"
3. Нажмите "Удалить"

### Через скрипт:

.. code-block:: batch

   @echo off
   echo Удаление Exam Report System...
   "C:\Program Files\ExamReportSystem\unins000.exe" /SILENT
   echo Приложение удалено.
   pause

Файлы, которые остаются после удаления (при необходимости):
- Каталог `%APPDATA%\ExamReportSystem\` с настройками пользователя
- Лог-файлы в `%TEMP%\ExamReportSystem\`

Создание портативной версии
---------------------------

Для создания версии без установки:

1. Скомпилируйте приложение в один исполняемый файл:

.. code-block:: bash

   pyinstaller --onefile --windowed --icon=icon.ico --name=ExamReportPortable main.py

2. Создайте портативный пакет:

.. code-block:: text

   ExamReportPortable/
   ├── ExamReportPortable.exe
   ├── config.ini
   ├── logs/
   └── data/

3. Настройки хранятся в той же папке, что и исполняемый файл.

Устранение проблем при установке
--------------------------------

### Проблема 1: Ошибка "Не удается найти Python.dll"

**Решение:**
1. Установите распространяемый пакет Visual C++
2. Убедитесь, что Python 3.9+ установлен и добавлен в PATH
3. Переустановите приложение

### Проблема 2: Не удается подключиться к PostgreSQL

**Решение:**
1. Проверьте, запущен ли сервер PostgreSQL
2. Убедитесь, что порт 5432 открыт в брандмауэре
3. Проверьте правильность учетных данных

### Проблема 3: Ошибка при создании базы данных

**Решение:**
1. Запустите `init_database.bat` от имени администратора
2. Убедитесь, что у пользователя PostgreSQL есть права на создание БД
3. Проверьте, что база данных с таким именем не существует

### Проблема 4: Антивирус блокирует установку

**Решение:**
1. Добавьте установщик в исключения антивируса
2. Отключите антивирус на время установки
3. Убедитесь, что скачали установщик из доверенного источника

Лицензионные соглашения
-----------------------

### Использование Inno Setup

**Внимание:** Бесплатная версия Inno Setup подходит только для некоммерческого использования.
Для коммерческого использования Exam Report System необходимо:

1. Приобрести лицензию на Inno Setup
2. Удалить все упоминания Inno Setup из конечного продукта
3. Использовать собственный брендинг в установщике

### Лицензирование приложения

Exam Report System распространяется под лицензией MIT:

- Можно свободно использовать, изменять и распространять
- Обязательно указание авторства
- Нет гарантий и ответственности за ущерб

Полный текст лицензии в файле `LICENSE.txt`.

Дополнительные ресурсы
----------------------

### Полезные ссылки:

- **Документация Inno Setup:** https://jrsoftware.org/ishelp/
- **Примеры скриптов:** https://github.com/orgs/innosetup/discussions
- **Форум поддержки:** https://groups.google.com/g/innosetup
- **Исходный код проекта:** https://github.com/BogushevichV/KursovayaKPO

### Инструменты для тестирования установщика:

1. **VMware / VirtualBox** - тестирование на чистой системе
2. **Sandboxie** - изолированное окружение
3. **Process Monitor** - мониторинг файловой системы и реестра

### Рекомендации по дистрибуции:

1. Подпишите установщик цифровой подписью
2. Проверьте на нескольких версиях Windows
3. Протестируйте установку с разными правами пользователя
4. Убедитесь в корректном удалении приложения

Этот файл содержит полное руководство по созданию и использованию установщика Exam Report System с помощью Inno Setup, с особым вниманием к лицензионным ограничениям бесплатной версии.