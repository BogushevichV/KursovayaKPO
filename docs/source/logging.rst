Журналирование
===========================

В проекте реализовано централизованное журналирование на стороне сервера.
Логи позволяют отслеживать:

1. **HTTP взаимодействия**: входящие запросы клиента и исходящие ответы сервера
2. **SQL операции**: выполняемые запросы к PostgreSQL и результаты выборок
3. **Ошибки**: ошибки парсинга входных данных, ошибки бизнес-логики и системные ошибки (404/500)



Где включается логирование
-------------------------

Логгер создаётся при запуске сервера в `Server/main.py`:

.. literalinclude:: ../../Server/main.py
   :language: python
   :linenos:
   :caption: main.py — создание DatabaseLogger и подключение middleware
   :lines: 84-106

При завершении работы сервера логгер корректно закрывается через `atexit`, чтобы в лог попало событие остановки.


Класс логгера и формат записей
-----------------------------

Основной класс — `DatabaseLogger` (`Server/SystemUtils/logger.py`).
Каждая запись в логе хранится в **структурированном JSON формате**:

.. literalinclude:: ../../Server/SystemUtils/logger.py
   :language: python
   :linenos:
   :caption: logger.py — структура записи и запись в файл
   :lines: 7-70

Ключевые поля записи:

- **timestamp** — время события (с миллисекундами)
- **action** — тип события (например, CLIENT_REQUEST, DB_QUERY, ERROR)
- **data** — данные события (payload)


Куда сохраняются логи
--------------------

При каждом запуске сервера создаётся **новый** файл лога в каталоге `Server/logs/`.
Имя файла содержит дату и время запуска, например:

.. code-block:: text

   db_server-2025-12-17_14-30-25.log

Путь и префикс файла настраиваются в `Server/Source/config.py` и могут быть переопределены переменными окружения:

.. literalinclude:: ../../Server/Source/config.py
   :language: python
   :linenos:
   :caption: config.py — параметры LOG_CONFIG
   :lines: 21-29

Поддерживаемые переменные окружения:

- **LOG_DIR** — директория, куда писать логи (по умолчанию `Server/logs`)
- **LOG_PREFIX** — префикс имени лог-файла (по умолчанию `db_server`)


Что именно журналируется
-----------------------

HTTP запросы и ответы (Flask middleware)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

В `Server/SystemUtils/middleware.py` настроены обработчики Flask:

- `@app.before_request` — логирует **каждый входящий запрос**
- `@app.after_request` — логирует **каждый исходящий ответ**
- `@app.errorhandler(404/500)` — логирует системные ошибки 404 и 500

.. literalinclude:: ../../Server/SystemUtils/middleware.py
   :language: python
   :linenos:
   :caption: middleware.py — логирование запросов, ответов и ошибок

Какие поля пишутся:

- **CLIENT_REQUEST**: method, endpoint, params, body
- **SERVER_RESPONSE**: status_code, response
- **ERROR**: error_type, error_message, context


SQL запросы и результаты (обёртка курсора)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Для журналирования SQL запросов используется обёртка курсора в `Server/DBUtils/db_wrapper.py`.
При подключении менеджеров к БД их `connection` заменяется на `LoggedConnection`, которая выдаёт `LoggedCursor`.

.. literalinclude:: ../../Server/DBUtils/db_wrapper.py
   :language: python
   :linenos:
   :caption: db_wrapper.py — LoggedCursor и patch_database_manager_for_logging

Какие события пишутся:

- **DB_QUERY**: query (строка SQL), params
- **DB_RESULT**: result, rowcount, result_type


Ошибки роутов и некорректный JSON
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Во всех маршрутах (`Server/Routes/*.py`) входной JSON читается через `safe_get_json()` из `Server/Source/utils.py`.
Если JSON не удалось распарсить — ошибка фиксируется в логе с контекстом `json_parsing_error`.

.. literalinclude:: ../../Server/Source/utils.py
   :language: python
   :linenos:
   :caption: utils.py — safe_get_json с логированием ошибок

Также в обработчиках маршрутов используются явные вызовы `logger.log_error(..., context="...")`
для фиксации ошибок бизнес-логики (например, `create_user`, `authenticate_admin`, `save_data` и т.д.).


Пример записи в лог-файле
-------------------------

Пример записи типа CLIENT_REQUEST (упрощённо):

.. code-block:: json

   {
     "timestamp": "2025-12-17 14:31:02.123",
     "action": "CLIENT_REQUEST",
     "data": {
       "method": "POST",
       "endpoint": "/api/auth/user",
       "params": {},
       "body": {"login": "user1", "password": "*****"}
     }
   }

.. note::

   Сейчас тело запроса (`body`) логируется как есть. Если требуется, можно добавить маскирование
   чувствительных полей (например, `password`) на уровне `middleware.py` или в `DatabaseLogger`.


