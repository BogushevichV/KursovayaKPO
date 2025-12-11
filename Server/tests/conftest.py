"""
Конфигурация для pytest
"""
import pytest
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """Настройка тестового окружения"""
    # Проверяем подключение к БД перед запуском тестов
    try:
        from Server.config import DB_CONFIG
        import psycopg2
        
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        print("✓ Подключение к БД успешно")
    except Exception as e:
        pytest.skip(f"Не удалось подключиться к БД: {e}")


def pytest_configure(config):
    """Конфигурация pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )

