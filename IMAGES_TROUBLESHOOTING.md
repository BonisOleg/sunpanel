# 🖼️ СИСТЕМА ЗОБРАЖЕНЬ ТОВАРІВ - ПОВНИЙ ГАЙД

## 📋 ОГЛЯД СИСТЕМИ

Проект використовує **WhiteNoise** для обслуговування медіа файлів як статичних в продакшн середовищі.

### 🏗️ Архітектура

**Локальна розробка:**
- Зображення зберігаються в `media/products/`
- URL: `/media/products/image.jpg`
- Обслуговуються Django development server

**Production (Render):**
- Зображення копіюються до `staticfiles/media/products/`
- URL: `/static/media/products/image.jpg`
- Обслуговуються WhiteNoise

---

## 🔧 НАЛАШТУВАННЯ

### settings.py (локальна)
```python
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### settings_production.py
```python
MEDIA_URL = '/static/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'staticfiles', 'media')
```

---

## 📦 ПРОЦЕС ДЕПЛОЮ

### 1. Автоматичний процес (build.sh)
```bash
# 1. Імпорт товарів (зображення зберігаються в media/)
python manage.py universal_import_products

# 2. Копіювання медіа файлів до staticfiles
python manage.py setup_media_for_production --verify

# 3. Збір статичних файлів (включно з медіа)
python manage.py collectstatic --no-input

# 4. Тестування зображень
python manage.py test_production_images
```

### 2. Структура файлів після деплою
```
staticfiles/
├── css/
├── js/
└── media/           # ← Медіа файли як статичні
    ├── products/    # ← Головні зображення товарів
    │   ├── product_735_0_6738947748_gibridnyj.jpg
    │   └── gallery/ # ← Додаткові зображення
    ├── portfolio/   # ← Зображення портфоліо
    └── brands/      # ← Логотипи брендів
```

---

## 🎯 SMART URL ГЕНЕРАЦІЯ

### models.py - Product.get_image_url()
```python
def get_image_url(self):
    if hasattr(settings, 'MEDIA_URL') and settings.MEDIA_URL == '/static/media/':
        # ПРОДАКШН: WhiteNoise статичні файли
        image_path = str(self.image.name)
        if image_path.startswith('products/'):
            static_url = f"{settings.MEDIA_URL}{image_path}"
        else:
            static_url = f"{settings.MEDIA_URL}products/{image_path}"
        
        # Кешбастинг
        file_hash = hashlib.md5(f"{self.image.name}{self.updated_at}".encode()).hexdigest()[:8]
        return f"{static_url}?v={file_hash}"
    else:
        # ЛОКАЛЬНА РОЗРОБКА
        return self.image.url
```

### Шаблони
```html
<!-- Правильно ✅ -->
<img src="{{ product.image_url }}" alt="{{ product.name }}">

<!-- Неправильно ❌ -->
<img src="{{ product.image.url }}" alt="{{ product.name }}">
```

---

## 🚨 ДІАГНОСТИКА ПРОБЛЕМ

### 1. Перевірка налаштувань
```bash
python manage.py update_media_urls --settings=config.settings_production
```

**Очікуваний вивід:**
```
📂 MEDIA_URL: /static/media/
📁 MEDIA_ROOT: /path/to/staticfiles/media
✅ MEDIA_URL правильно налаштований
```

### 2. Тестування зображень
```bash
python manage.py test_production_images --limit=10 --settings=config.settings_production
```

**Успішний результат:**
```
✅ Гібридний інвертор Deye 80 кВт...
   URL: /static/media/products/product_735_0_6738947748_gibridnyj.jpg?v=a1b2c3d4
   📁 Файл існує: /path/to/staticfiles/media/products/...
🎉 Всі зображення працюють правильно!
```

### 3. Перевірка копіювання файлів
```bash
python manage.py setup_media_for_production --verify --settings=config.settings_production
```

### 4. Ручна перевірка файлів
```bash
# Перевіряємо що файли скопійовані
ls -la staticfiles/media/products/ | head -10

# Перевіряємо розмір
du -sh staticfiles/media/
```

---

## 🔥 ТИПОВІ ПРОБЛЕМИ ТА РІШЕННЯ

### ❌ Проблема: Зображення не відображаються на Render

**Симптоми:**
- Локально все працює
- На Render товари без зображень або broken images

**Рішення:**
1. Перевірте що файли скопійовані:
```bash
python manage.py setup_media_for_production --verify --clean
```

2. Перевірте URL генерацію:
```bash
python manage.py test_production_images --limit=5
```

3. Примусово пересоберіть:
```bash
python manage.py collectstatic --clear --no-input
```

### ❌ Проблема: URL генеруються неправильно

**Симптоми:**
- URL містить `/media/` замість `/static/media/`
- Або навпаки в локальній розробці

**Рішення:**
Перевірте що модель правильно визначає середовище:
```python
# В models.py перевірте
if hasattr(settings, 'MEDIA_URL') and settings.MEDIA_URL == '/static/media/':
    # Продакшн логіка
else:
    # Локальна логіка
```

### ❌ Проблема: Файли є, але HTTP 404

**Симптоми:**
- Файли існують в staticfiles/media/
- Але при запиті HTTP 404

**Рішення:**
1. Перевірте налаштування WhiteNoise:
```python
# settings_production.py
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
WHITENOISE_USE_FINDERS = True
```

2. Переконайтесь що collectstatic виконано:
```bash
python manage.py collectstatic --no-input
```

### ❌ Проблема: Старі зображення кешуються

**Симптоми:**
- Оновили товар, але показується старе зображення

**Рішення:**
Кешбастинг автоматично додається до URL через хеш файлу.
Якщо не працює:
```bash
python manage.py clear_all_cache
```

---

## 🛠️ КОМАНДИ ДЛЯ ОБСЛУГОВУВАННЯ

### Повний перебілд зображень
```bash
# 1. Очистити старі файли
python manage.py setup_media_for_production --clean

# 2. Заново імпортувати товари
python manage.py universal_import_products --clear-existing

# 3. Скопіювати файли
python manage.py setup_media_for_production --verify

# 4. Пересобрати статичні файли
python manage.py collectstatic --clear --no-input
```

### Швидкий фікс
```bash
# Для швидкого виправлення на Render
python manage.py setup_media_for_production --verify
python manage.py collectstatic --no-input
python manage.py clear_all_cache
```

### Тестування після змін
```bash
# Локально
python manage.py test_production_images --limit=5

# Продакшн
python manage.py test_production_images --limit=5 --settings=config.settings_production
```

---

## 📊 МОНІТОРИНГ

### Перевірка через Django Shell
```python
from mainapp.models import Product
from django.conf import settings

# Тестуємо перший товар
product = Product.objects.first()
print(f"Image URL: {product.image_url}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")

# Перевіряємо файл
import os
if settings.MEDIA_URL == '/static/media/':
    path = os.path.join(settings.STATIC_ROOT, 'media', str(product.image.name))
else:
    path = os.path.join(settings.MEDIA_ROOT, str(product.image.name))
    
print(f"File exists: {os.path.exists(path)}")
print(f"File path: {path}")
```

### Перевірка в браузері
1. Відкрийте каталог товарів
2. Переглянте код сторінки (Ctrl+U)
3. Знайдіть `<img src="` - всі URL мають бути `/static/media/products/...`
4. Скопіюйте URL зображення та відкрийте в новій вкладці

---

## ✅ ЧЕКЛИСТ ПІСЛЯ ДЕПЛОЮ

- [ ] `python manage.py update_media_urls` показує правильні налаштування
- [ ] `python manage.py test_production_images` - всі зображення працюють
- [ ] Каталог товарів відображає зображення
- [ ] Деталі товару показують головне та додаткові зображення
- [ ] URL зображень містять `/static/media/` та параметр `?v=`
- [ ] Портфоліо проектів відображає зображення

---

## 🎯 ПІДСУМОК

Нова система зображень:
1. **Автоматично визначає** локальна/продакшн
2. **Правильно генерує URL** для кожного середовища
3. **Копіює файли** до staticfiles для WhiteNoise
4. **Додає кешбастинг** для оновлень
5. **Має діагностичні команди** для швидкого налагодження

При проблемах використовуйте команди тестування та цей гайд! 🚀 