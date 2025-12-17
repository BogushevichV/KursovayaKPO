@echo off
chcp 65001 >nul
echo ========================================
echo Установка зависимостей для сервера
echo Exam Report System
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.9 или выше с https://www.python.org/
    echo Убедитесь, что Python добавлен в PATH
    pause
    exit /b 1
)

echo [✓] Python найден
python --version
echo.

REM Проверка наличия pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] pip не найден!
    echo Установите pip или переустановите Python с опцией "Add Python to PATH"
    pause
    exit /b 1
)

echo [✓] pip найден
python -m pip --version
echo.

REM Обновление pip до последней версии
echo [1/3] Обновление pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Не удалось обновить pip, продолжаем...
) else (
    echo [✓] pip обновлен
)
echo.

REM Проверка наличия requirements.txt
if not exist "requirements.txt" (
    echo [ОШИБКА] Файл requirements.txt не найден!
    echo Убедитесь, что скрипт запущен из директории c файлом requirements.txt
    pause
    exit /b 1
)

echo [2/3] Установка зависимостей из requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось установить некоторые зависимости!
    echo.
    echo Возможные решения:
    echo 1. Убедитесь, что у вас установлен Microsoft Visual C++ Build Tools
    echo    (требуется для компиляции некоторых пакетов)
    echo 2. Попробуйте установить зависимости по отдельности:
    echo    python -m pip install Flask
    echo    python -m pip install Flask-CORS
    echo    python -m pip install psycopg2-binary
    echo    python -m pip install pytest
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Проверка установленных пакетов...
python -m pip list | findstr /i "Flask psycopg2 pytest"
echo.

echo ========================================
echo [✓] Установка завершена успешно!
echo ========================================
echo.
echo Установленные пакеты:
python -m pip list | findstr /i "Flask psycopg2 pytest"
echo.
echo Для запуска сервера используйте:
echo   python main.py
echo.
pause

