"""
Автотесты для API регистрации пользователей
Эти тесты предназначены для тестирования backend API эндпоинта регистрации
"""

import pytest
import requests
import json
from typing import Dict, Any


# Базовый URL API (замените на ваш реальный URL)
BASE_URL = "http://localhost:3000/api"  # Пример URL
REGISTRATION_ENDPOINT = f"{BASE_URL}/register"


class TestUserRegistration:
    """Тесты для функциональности регистрации пользователей"""
    
    @pytest.fixture
    def valid_user_data(self) -> Dict[str, str]:
        """Фикстура с валидными данными пользователя"""
        return {
            "login": "testuser123",
            "password": "StrongPass123!",
            "confirmPassword": "StrongPass123!"
        }
    
    @pytest.fixture
    def weak_password_data(self) -> Dict[str, str]:
        """Фикстура с данными пользователя со слабым паролем"""
        return {
            "login": "testuser456",
            "password": "weak",
            "confirmPassword": "weak"
        }
    
    @pytest.fixture
    def duplicate_login_data(self) -> Dict[str, str]:
        """Фикстура с данными пользователя с дублирующим логином"""
        return {
            "login": "admin",  # Уже существующий логин
            "password": "StrongPass123!",
            "confirmPassword": "StrongPass123!"
        }

    def test_successful_registration(self, valid_user_data: Dict[str, str]):
        """
        Тест 1: Успешная регистрация
        Проверяет, что пользователь может успешно зарегистрироваться с валидными данными
        """
        # Отправляем POST запрос на регистрацию
        response = requests.post(
            REGISTRATION_ENDPOINT,
            json=valid_user_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Проверяем статус код
        assert response.status_code == 201, f"Ожидался статус 201, получен {response.status_code}"
        
        # Проверяем структуру ответа
        response_data = response.json()
        assert "success" in response_data, "Ответ должен содержать поле 'success'"
        assert response_data["success"] is True, "Поле 'success' должно быть True"
        assert "message" in response_data, "Ответ должен содержать поле 'message'"
        assert "user" in response_data, "Ответ должен содержать данные о пользователе"
        
        # Проверяем данные пользователя в ответе
        user_data = response_data["user"]
        assert user_data["login"] == valid_user_data["login"], "Логин в ответе не совпадает"
        assert "id" in user_data, "Данные пользователя должны содержать ID"
        assert "password" not in user_data, "Пароль не должен возвращаться в ответе"
        
        # Проверяем сообщение об успехе
        assert "успешно" in response_data["message"].lower(), "Сообщение должно содержать информацию об успехе"
        
        print(f"✅ Тест успешной регистрации пройден для пользователя: {valid_user_data['login']}")

    def test_duplicate_login_error(self, duplicate_login_data: Dict[str, str]):
        """
        Тест 2: Ошибка при дублирующем логине
        Проверяет, что система отклоняет регистрацию с уже существующим логином
        """
        # Отправляем POST запрос с дублирующим логином
        response = requests.post(
            REGISTRATION_ENDPOINT,
            json=duplicate_login_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Проверяем статус код (должен быть 400 - Bad Request или 409 - Conflict)
        assert response.status_code in [400, 409], f"Ожидался статус 400 или 409, получен {response.status_code}"
        
        # Проверяем структуру ответа об ошибке
        response_data = response.json()
        assert "success" in response_data, "Ответ должен содержать поле 'success'"
        assert response_data["success"] is False, "Поле 'success' должно быть False"
        assert "error" in response_data, "Ответ должен содержать поле 'error'"
        
        # Проверяем сообщение об ошибке
        error_message = response_data["error"].lower()
        assert any(keyword in error_message for keyword in ["существует", "занят", "duplicate", "exists"]), \
            "Сообщение об ошибке должно указывать на дублирующий логин"
        
        # Проверяем, что поле с конкретной ошибкой указано
        if "field" in response_data:
            assert response_data["field"] == "login", "Поле ошибки должно указывать на логин"
            
        print(f"✅ Тест дублирующего логина пройден для логина: {duplicate_login_data['login']}")

    def test_weak_password_error(self, weak_password_data: Dict[str, str]):
        """
        Тест 3: Ошибка при слабом пароле
        Проверяет, что система отклоняет регистрацию со слабым паролем
        """
        # Отправляем POST запрос со слабым паролем
        response = requests.post(
            REGISTRATION_ENDPOINT,
            json=weak_password_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Проверяем статус код (должен быть 400 - Bad Request)
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
        
        # Проверяем структуру ответа об ошибке
        response_data = response.json()
        assert "success" in response_data, "Ответ должен содержать поле 'success'"
        assert response_data["success"] is False, "Поле 'success' должно быть False"
        assert "error" in response_data, "Ответ должен содержать поле 'error'"
        
        # Проверяем сообщение об ошибке пароля
        error_message = response_data["error"].lower()
        password_error_keywords = ["пароль", "password", "слаб", "weak", "символ", "character", "требован", "require"]
        assert any(keyword in error_message for keyword in password_error_keywords), \
            "Сообщение об ошибке должно указывать на проблемы с паролем"
        
        # Проверяем, что поле с конкретной ошибкой указано
        if "field" in response_data:
            assert response_data["field"] == "password", "Поле ошибки должно указывать на пароль"
            
        # Дополнительная проверка детальных требований к паролю
        if "requirements" in response_data:
            requirements = response_data["requirements"]
            expected_requirements = ["минимум 8 символов", "заглавная буква", "строчная буква", "цифра", "специальный символ"]
            assert isinstance(requirements, list), "Требования должны быть в виде списка"
            
        print(f"✅ Тест слабого пароля пройден для пароля: {weak_password_data['password']}")

    def test_invalid_json_format(self):
        """
        Дополнительный тест: Проверка обработки невалидного JSON
        """
        response = requests.post(
            REGISTRATION_ENDPOINT,
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, "Невалидный JSON должен возвращать статус 400"
        
    def test_missing_required_fields(self):
        """
        Дополнительный тест: Проверка обработки отсутствующих обязательных полей
        """
        incomplete_data = {"login": "testuser"}  # Отсутствует пароль
        
        response = requests.post(
            REGISTRATION_ENDPOINT,
            json=incomplete_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, "Отсутствие обязательных полей должно возвращать статус 400"
        response_data = response.json()
        assert response_data["success"] is False, "Success должно быть False при отсутствии полей"

    def test_password_confirmation_mismatch(self):
        """
        Дополнительный тест: Проверка несовпадения паролей
        """
        mismatch_data = {
            "login": "testuser789",
            "password": "StrongPass123!",
            "confirmPassword": "DifferentPass456!"
        }
        
        response = requests.post(
            REGISTRATION_ENDPOINT,
            json=mismatch_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, "Несовпадение паролей должно возвращать статус 400"
        response_data = response.json()
        assert "пароли не совпадают" in response_data["error"].lower() or \
               "passwords do not match" in response_data["error"].lower(), \
               "Ошибка должна указывать на несовпадение паролей"


if __name__ == "__main__":
    # Запуск тестов из командной строки
    pytest.main([__file__, "-v", "--tb=short"])