"""
Конфигурация pytest для тестов регистрации
"""

import pytest
import requests
from typing import Generator
import time


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Базовый URL для API тестов"""
    return "http://localhost:3000/api"


@pytest.fixture(scope="session")
def ensure_server_running(api_base_url: str) -> Generator[None, None, None]:
    """Проверяет, что сервер запущен перед выполнением тестов"""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.get(f"{api_base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Сервер доступен на {api_base_url}")
                break
        except requests.exceptions.RequestException:
            pass
            
        retry_count += 1
        if retry_count < max_retries:
            print(f"⏳ Ожидание запуска сервера... попытка {retry_count}/{max_retries}")
            time.sleep(2)
    else:
        pytest.skip(f"❌ Сервер не доступен на {api_base_url} после {max_retries} попыток")
    
    yield
    
    print("🧹 Очистка после тестов завершена")


@pytest.fixture
def cleanup_test_users():
    """Очищает тестовых пользователей после выполнения тестов"""
    test_users = []
    
    def add_user(login: str):
        test_users.append(login)
    
    yield add_user
    
    # Очистка после теста
    for user_login in test_users:
        try:
            # Здесь должен быть код для удаления тестовых пользователей
            # requests.delete(f"{api_base_url}/users/{user_login}")
            pass
        except Exception as e:
            print(f"⚠️ Не удалось удалить тестового пользователя {user_login}: {e}")


def pytest_configure(config):
    """Конфигурация pytest"""
    config.addinivalue_line(
        "markers", "integration: помечает тесты как интеграционные"
    )
    config.addinivalue_line(
        "markers", "smoke: помечает тесты как smoke тесты"
    )


def pytest_collection_modifyitems(config, items):
    """Модификация собранных тестовых элементов"""
    for item in items:
        # Добавляем маркер integration ко всем тестам в test_registration
        if "test_registration" in item.nodeid:
            item.add_marker(pytest.mark.integration)