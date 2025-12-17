@echo off
chcp 65001 >nul
echo ==========================================
echo   Запуск сервера и тестов
echo   Exam Report System
echo ==========================================
echo.

REM Получаем путь к директории скрипта
set SCRIPT_DIR=%~dp0
set SERVER_DIR=%SCRIPT_DIR%..
cd /d "%SERVER_DIR%"

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.9 или выше
    pause
    exit /b 1
)

REM Проверка наличия pytest
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] pytest не установлен!
    echo Запустите install_dependencies.bat для установки зависимостей
    pause
    exit /b 1
)

echo [1/5] Проверка готовности окружения...
echo [✓] Python найден
python --version
echo [✓] pytest найден
python -m pytest --version
echo.

REM Проверка, не запущен ли уже сервер
echo [2/5] Проверка доступности сервера...
powershell -Command "$response = try { Invoke-WebRequest -Uri 'http://127.0.0.1:5000/api/health' -TimeoutSec 2 -UseBasicParsing } catch { $null }; if ($response) { exit 1 } else { exit 0 }" >nul 2>&1
if %errorlevel% equ 1 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Сервер уже запущен на порту 5000
    echo Продолжаем с запуском тестов...
    set SERVER_STARTED=0
    goto :run_tests
)

echo [3/5] Запуск сервера в фоновом режиме...
start "Exam Report Server" /min cmd /c "python main.py"
if errorlevel 1 (
    echo [ОШИБКА] Не удалось запустить сервер!
    pause
    exit /b 1
)

echo [✓] Сервер запущен в отдельном окне
set SERVER_STARTED=1

REM Ожидание запуска сервера
echo [4/5] Ожидание запуска сервера (до 30 секунд)...
set /a COUNTER=0
set /a MAX_WAIT=30

:wait_loop
timeout /t 2 /nobreak >nul
powershell -Command "$response = try { Invoke-WebRequest -Uri 'http://127.0.0.1:5000/api/health' -TimeoutSec 1 -UseBasicParsing } catch { $null }; if ($response -and $response.StatusCode -eq 200) { exit 0 } else { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] Сервер готов!
    goto :run_tests
)

set /a COUNTER+=2
if %COUNTER% geq %MAX_WAIT% (
    echo [ОШИБКА] Сервер не ответил за %MAX_WAIT% секунд!
    echo Проверьте логи сервера в отдельном окне
    pause
    exit /b 1
)

echo Ожидание... (%COUNTER%/%MAX_WAIT% сек)
goto :wait_loop

:run_tests
echo.
echo ==========================================
echo [5/5] Запуск тестов...
echo ==========================================
echo.

REM Запуск тестов
python -m pytest tests/ -v --tb=short
set TEST_RESULT=%errorlevel%

echo.
echo ==========================================
if %TEST_RESULT% equ 0 (
    echo [✓] Все тесты пройдены успешно!
) else (
    echo [✗] Некоторые тесты не прошли
)
echo ==========================================
echo.

REM Остановка сервера, если мы его запустили
if %SERVER_STARTED% equ 1 (
    echo Остановка сервера...
    REM Ищем процесс Python, который запускает main.py
    for /f "tokens=2" %%a in ('tasklist /FI "WINDOWTITLE eq Exam Report Server*" /FO LIST ^| findstr /I "PID"') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    
    REM Альтернативный способ - найти процесс по порту (требует netstat)
    REM Используем более надежный способ - поиск по имени окна
    taskkill /FI "WINDOWTITLE eq Exam Report Server*" /F >nul 2>&1
    
    REM Дополнительная проверка через порт (если доступен netstat)
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    
    timeout /t 2 /nobreak >nul
    echo [✓] Сервер остановлен
)

echo.
echo Завершение работы...
pause
exit /b %TEST_RESULT%

