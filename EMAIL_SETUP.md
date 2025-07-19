# Налаштування Email для зворотного зв'язку

Щоб система зворотного зв'язку працювала, потрібно налаштувати відправку email через Gmail.

## Кроки налаштування:

### 1. Створіть Gmail акаунт для проекту
- Створіть новий Gmail акаунт (наприклад: greensolartech@gmail.com)
- Або використовуйте існуючий

### 2. Увімкніть двофакторну автентифікацію
- Перейдіть в Google Account: https://myaccount.google.com/
- Security → 2-Step Verification → Turn on

### 3. Створіть App Password
- Перейдіть в Google Account → Security
- 2-Step Verification → App passwords
- Виберіть "Mail" та "Other (custom name)"
- Введіть назву: "Django GreenSolarTech"
- Скопіюйте згенерований пароль (16 символів)

### 4. Оновіть settings.py
У файлі `config/settings.py` замініть:

```python
EMAIL_HOST_USER = 'greensolartech@gmail.com'  # Ваш Gmail
EMAIL_HOST_PASSWORD = 'your_app_password'  # App Password з кроку 3
DEFAULT_FROM_EMAIL = 'GreenSolarTech <greensolartech@gmail.com>'
CONTACT_EMAIL = 'greensolartech@gmail.com'  # Email для отримання заявок
```

### 5. Налаштування для production
Для production сервера рекомендується використовувати змінні середовища:

```python
import os
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f'Set the {var_name} environment variable'
        raise ImproperlyConfigured(error_msg)

# Email settings
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD')
CONTACT_EMAIL = get_env_variable('CONTACT_EMAIL')
```

### 6. Тестування
Після налаштування запустіть сервер та протестуйте:
- Кнопку "Зателефонувати мені"
- Форму зворотного зв'язку
- Корзину покупок

## Функціональність

### Кнопка зворотного зв'язку
- Фіксована позиція зліва внизу
- Адаптивна для мобільних пристроїв
- Анімований значок телефону

### Модальне вікно
- "Написати нам" - показує контактну інформацію
- "Залишити заявку" - форма для зворотного зв'язку

### Email повідомлення
- Заявки зворотного зв'язку приходять на вказаний email
- Замовлення з корзини також відправляються на email
- Включають всю необхідну інформацію та час створення

## Безпека
- Використовується CSRF токен для захисту
- Валідація даних на сервері
- App Password замість основного паролю Gmail 