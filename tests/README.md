# Автотесты для формы регистрации

Этот набор pytest тестов предназначен для тестирования backend API эндпоинта регистрации пользователей.

## Структура тестов

### Основные тесты (test_registration.py)

1. **test_successful_registration** - Тест успешной регистрации
   - Проверяет регистрацию с валидными данными
   - Ожидает статус 201 и корректную структуру ответа
   - Проверяет, что пароль не возвращается в ответе

2. **test_duplicate_login_error** - Тест дублирующего логина
   - Проверяет отклонение регистрации с существующим логином
   - Ожидает статус 400/409 и соответствующее сообщение об ошибке

3. **test_weak_password_error** - Тест слабого пароля
   - Проверяет отклонение регистрации со слабым паролем
   - Ожидает статус 400 и описание требований к паролю

### Дополнительные тесты

- Проверка невалидного JSON
- Проверка отсутствующих обязательных полей  
- Проверка несовпадения паролей при подтверждении

## Установка и запуск

### 1. Установка зависимостей

```bash
pip install -r tests/requirements.txt
```

### 2. Запуск всех тестов

```bash
# Из корневой директории проекта
pytest tests/ -v

# Или с покрытием кода
pytest tests/ -v --cov=src
```

### 3. Запуск конкретных тестов

```bash
# Только основные 3 теста
pytest tests/test_registration.py::TestUserRegistration::test_successful_registration -v
pytest tests/test_registration.py::TestUserRegistration::test_duplicate_login_error -v
pytest tests/test_registration.py::TestUserRegistration::test_weak_password_error -v

# Все тесты класса
pytest tests/test_registration.py::TestUserRegistration -v
```

### 4. Запуск с HTML отчетом

```bash
pytest tests/ --html=reports/report.html --self-contained-html
```

## Настройка

### Конфигурация API

Перед запуском тестов убедитесь, что:

1. **Backend сервер запущен** на нужном порту
2. **BASE_URL в test_registration.py** указывает на правильный адрес API
3. **Эндпоинт регистрации** доступен по адресу `/api/register`

### Ожидаемая структура API ответов

#### Успешная регистрация (201)
```json
{
  "success": true,
  "message": "Пользователь успешно зарегистрирован",
  "user": {
    "id": "123",
    "login": "testuser123"
  }
}
```

#### Ошибка дублирующего логина (400/409)
```json
{
  "success": false,
  "error": "Пользователь с таким логином уже существует",
  "field": "login"
}
```

#### Ошибка слабого пароля (400)
```json
{
  "success": false,
  "error": "Пароль не соответствует требованиям безопасности",
  "field": "password",
  "requirements": [
    "минимум 8 символов",
    "заглавная буква", 
    "строчная буква",
    "цифра",
    "специальный символ"
  ]
}
```

## Примечания

- Тесты написаны для backend API, который еще не реализован
- Frontend форма уже создана и работает с клиентской валидацией
- Для полной интеграции нужно создать backend с соответствующими эндпоинтами
- Рекомендуется использовать Supabase или создать Express.js/FastAPI backend

## Интеграция с CI/CD

Добавьте в ваш CI pipeline:

```yaml
# Пример для GitHub Actions
- name: Run tests
  run: |
    pip install -r tests/requirements.txt
    pytest tests/ -v --junit-xml=test-results.xml
```