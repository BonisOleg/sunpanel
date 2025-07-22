# 🚀 ІНСТРУКЦІЯ ДЕПЛОЮ НА RENDER - ЛОКАЛЬНІ МЕДІА ФАЙЛИ

## ✅ ГОТОВИЙ ПРОЕКТ

Проект **повністю підготовлено** до деплою на Render **БЕЗ сторонніх сервісів**.
Всі зображення працюють як локальні статичні файли.

### 📊 Поточний стан:
- ✅ **42 товари** з зображеннями
- ✅ **3 проекти портфоліо** з фотогалереями  
- ✅ **8 відгуків** клієнтів
- ✅ **191 медіа файл** скопійовано до статичних
- ✅ **Production налаштування** без Cloudinary
- ✅ **Автоматичні скрипти** для деплою
- ✅ **Автоматична перевірка орфографії** при деплої
- ✅ **Видалення російських дублікатів** при деплої

---

## 🎯 КРОК 1: ПІДГОТОВКА РЕПОЗИТОРІЮ

```bash
# Остаточна підготовка (новий зручний спосіб)
python manage.py prepare_for_deploy

# Або покроково:
python manage.py remove_russian_categories
python manage.py check_spelling_errors --fix
python manage.py copy_media_to_static --clean
python manage.py prepare_portfolio
python manage.py test_deployment

# Git push
git add .
git commit -m "🚀 Готово до деплою: орфографія + медіа файли"
git push origin main
```

---

## 🔧 КРОК 2: СТВОРЕННЯ WEB SERVICE НА RENDER

### 1. Зайдіть на [render.com](https://render.com)
### 2. Створіть новий Web Service:
```
New + → Web Service → Connect GitHub → sunpanel
```

### 3. Налаштування Web Service:
```
Name: greensolartech
Environment: Python 3
Build Command: ./build.sh
Start Command: gunicorn config.wsgi:application  
Branch: main
```

---

## 🗄️ КРОК 3: СТВОРЕННЯ POSTGRESQL БД

### 1. Створіть PostgreSQL:
```
New + → PostgreSQL → Free Plan
Name: greensolartech-db
```

### 2. Підключіть до Web Service:
```
Web Service → Environment → Add from Database → greensolartech-db
```

---

## ⚙️ КРОК 4: ENVIRONMENT VARIABLES

Додайте в Web Service → Environment:

```
DJANGO_SETTINGS_MODULE = config.settings_production
SECRET_KEY = [автогенерується Render]
DEBUG = False
ALLOWED_HOSTS = greensolartech.onrender.com,.onrender.com
EMAIL_HOST_USER = GreenSolarTech.pe@gmail.com
EMAIL_HOST_PASSWORD = [ваш Gmail App Password]
SECURE_SSL_REDIRECT = False
DJANGO_LOG_LEVEL = INFO
ADMIN_EMAIL = admin@greensolartech.com
ADMIN_PASSWORD = admin123456
```

---

## 🚀 КРОК 5: ДЕПЛОЙ

1. **Deploy** → Render автоматично:
   - Встановить залежності
   - Скопіює медіа файли до статичних
   - Запустить міграції  
   - Створить суперкористувача
   - Підготує портфоліо
   - Запустить сайт

2. **Очікуваний результат:**
```
🚀 Starting build process...
📦 Installing dependencies...
📁 Copying media files to static...
🗂️ Collecting static files...
💾 Running database migrations...
👤 Creating superuser...
🎨 Preparing portfolio...
⭐ Adding sample reviews...
✅ Build completed successfully!
```

---

## 🧪 КРОК 6: ТЕСТУВАННЯ

### Автоматичне тестування:
```bash
# На Render Shell:
python manage.py test_deployment --url https://yourdomain.onrender.com
```

### Ручна перевірка:
1. **Головна сторінка** - завантажується
2. **Каталог товарів** - 42 товари з фото
3. **Портфоліо** - 3 проекти з фотогалереями
4. **Відгуки** - 8 відгуків клієнтів
5. **Адмін панель** - `/admin/` (admin / admin123456)

---

## 📁 СТРУКТУРА СТАТИЧНИХ ФАЙЛІВ

Render автоматично створить:
```
staticfiles/
├── css/ (стилі)
├── js/ (скрипти)  
├── images/ (загальні зображення)
├── videos/ (відео файли)
└── media/ (ВСІMEDІА ФАЙЛИ)
    ├── products/ (зображення товарів)
    │   ├── product_*.jpg
    │   └── gallery/
    └── portfolio/ (зображення портфоліо)
        ├── аналітика*.jpg
        ├── буд*.jpg
        ├── 4083.jpg, 8534.jpg...
        └── 1494.jpg, 15578.jpg...
```

---

## 🔍 ДІАГНОСТИКА ПРОБЛЕМ

### Логи:
```
Render Dashboard → Web Service → Logs
```

### Типові проблеми та рішення:

**❌ Зображення не завантажуються:**
```bash
# Перевірте чи скопіювалися медіа файли:
python manage.py shell -c "import os; print(os.listdir('static/media'))"
```

**❌ 500 Internal Server Error:**
```bash
# Перевірте Environment Variables та логи
```

**❌ Портфоліо без зображень:**
```bash
# Повторно підготуйте портфоліо:
python manage.py prepare_portfolio
```

---

## 🎉 ФІНАЛЬНИЙ РЕЗУЛЬТАТ

**Ваш сайт буде на 100% ідентичний локальній версії:**

- 🛒 **42 товари** з повними фотогалереями
- 🎨 **3 проекти портфоліо** з усіма зображеннями
- ⭐ **8 відгуків** клієнтів
- 📱 **Мобільна навігація** з сенсорним скролом
- 📞 **Оновлені контакти** (073-723-06-75)
- 🔒 **HTTPS** та **PostgreSQL**
- ⚡ **Швидка робота** через статичні файли

### 🔗 Готові URL:
- 🌐 **Сайт**: https://greensolartech.onrender.com
- 🔧 **Адмін**: https://greensolartech.onrender.com/admin/

---

## ✏️ АВТОМАТИЧНА ПЕРЕВІРКА ОРФОГРАФІЇ

### 🔧 Що відбувається автоматично при деплої:

1. **🛡️ Перевірка на російський контент** - запобігання імпорту
2. **🧹 Повне очищення російського контенту** з усіх текстів
3. **🗑️ Видалення російських дублікатів** категорій
4. **✏️ Виправлення орфографічних помилок** у всіх текстах:
   - Назви та описи товарів
   - Назви та описи категорій
   - Проєкти портфоліо
   - Відгуки клієнтів

### 📝 Типи помилок які виправляються:
- Технічні одиниці: `квт` → `кВт`, `вт` → `Вт`
- Назви брендів: `must` → `Must`, `deye` → `Deye`
- Російські залишки в текстах
- Неправильні закінчення прикметників
- Подвійні пробіли та пунктуація

### 🛠️ Команди для ручної перевірки:
```bash
# Перевірка на російський контент
python manage.py prevent_russian_import

# Строга перевірка (з підозрілим контентом)
python manage.py prevent_russian_import --strict

# Повне очищення російського контенту
python manage.py clean_russian_content

# Перевірка без виправлення
python manage.py check_spelling_errors

# Перевірка з автовиправленням
python manage.py check_spelling_errors --fix

# Видалення російських дублікатів
python manage.py remove_russian_categories

# Повна підготовка до деплою
python manage.py prepare_for_deploy
```

---

## 💪 ПЕРЕВАГИ ЦЬОГО ПІДХОДУ

1. **🚫 Без сторонніх сервісів** - все локально
2. **💰 Безкоштовно** - тільки Render Free Plan
3. **⚡ Швидко** - статичні файли через WhiteNoise
4. **🔄 Надійно** - автоматичне відновлення файлів
5. **🛠️ Просто** - один push для деплою
6. **✏️ Автоматична орфографія** - тексти завжди коректні

---

## 🎯 ПІДСУМОК

**ВСЕ ГОТОВО!** Просто деплойте та користуйтеся! 🚀

Система автоматично:
- ✅ Завантажить всі зображення
- ✅ Налаштує базу даних
- ✅ Створить адміністратора  
- ✅ Запустить сайт з усім функціоналом

**Час деплою: ~10 хвилин**  
**Складність: Мінімальна** (все автоматизовано) 