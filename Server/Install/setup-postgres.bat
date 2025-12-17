@echo off
chcp 65001 >nul
echo ==========================================
echo   Docker PostgreSQL Setup
echo ==========================================
echo.

echo [1/4] Запуск контейнера PostgreSQL...
docker run --name exam_pg -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=Password1 -e POSTGRES_DB=ExaminationReport -p 5433:5432 -d postgres:18

if %errorlevel% neq 0 (
    echo [ОШИБКА] Не удалось запустить контейнер!
    pause
    exit /b 1
)

echo [2/4] Ожидание запуска PostgreSQL (10 секунд)...
timeout /t 10 /nobreak >nul

echo [3/4] Копирование backup.sql в контейнер...
REM Получаем путь к директории скрипта и формируем путь к backup.sql
set SCRIPT_DIR=%~dp0
set BACKUP_FILE=%SCRIPT_DIR%..\Source\backup.sql

REM Проверка существования файла
if not exist "%BACKUP_FILE%" (
    echo [ОШИБКА] Файл backup.sql не найден в папке Source!
    echo Ожидаемый путь: %BACKUP_FILE%
    pause
    exit /b 1
)

docker cp "%BACKUP_FILE%" exam_pg:/backup.sql

if %errorlevel% neq 0 (
    echo [ОШИБКА] Не удалось скопировать файл!
    pause
    exit /b 1
)

echo [4/4] Восстановление базы данных...
docker exec -i exam_pg pg_restore -U postgres -d ExaminationReport /backup.sql

echo.
echo ==========================================
echo   Готово!
echo   Контейнер: exam_pg
echo   Порт: 5433
echo ==========================================
echo.
pause