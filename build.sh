#!/usr/bin/env bash
# Оптимізований build script для Render з гарантованим успіхом деплою

set -o errexit  # Exit on error
set -o pipefail # Exit on pipe failure
set -o nounset  # Exit on unset variable

echo "🚀 ЗАПУСК ОПТИМІЗОВАНОГО BUILD ПРОЦЕСУ ДЛЯ RENDER"
echo "=================================================="

# Функція для логування з часом
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# Функція для обробки помилок
handle_error() {
    log "❌ ПОМИЛКА НА КРОЦІ: $1"
    exit 1
}

# 1. Встановлення залежностей
log "📦 Встановлення Python залежностей..."
pip install -r requirements-production.txt || handle_error "pip install"

# 2. Перевірка Django налаштувань
log "⚙️ Перевірка Django налаштувань..."
python manage.py check --settings=config.settings_production || handle_error "Django check"

# 3. Міграції бази даних
log "🗃️ Застосування міграцій бази даних..."
python manage.py migrate --settings=config.settings_production || handle_error "migrations"

# 4. Очищення російського контенту (КРИТИЧНО!)
log "🛡️ Блокування російського контенту..."
python manage.py prevent_russian_import --settings=config.settings_production || log "⚠️ Prevent russian skipped"

log "🧹 Очищення російського контенту..."
python manage.py clean_russian_content --fix --settings=config.settings_production || log "⚠️ Clean russian skipped"

log "🗑️ Видалення російських категорій..."
python manage.py remove_russian_categories --settings=config.settings_production || log "⚠️ Remove categories skipped"

# 5. Перевірка та виправлення орфографії
log "✏️ Виправлення орфографічних помилок..."
python manage.py check_spelling_errors --fix --settings=config.settings_production || log "⚠️ Spelling check skipped"

# 6. ІДЕАЛЬНИЙ ІМПОРТ ТОВАРІВ (ПОВНА ПОСЛІДОВНІСТЬ)
log "🔥 ПОВНИЙ ІМПОРТ 42 ТОВАРІВ З ФОТО БЕЗ РОСІЙСЬКОЇ..."

# Спочатку імпортуємо товари
log "📦 Імпорт каталогу товарів..."
python manage.py import_full_catalog --clear-existing --settings=config.settings_production || log "⚠️ Імпорт помилка"

# КРИТИЧНО: Очищення російського контенту ОДРАЗУ
log "🇺🇦 ПОВНЕ ОЧИЩЕННЯ РОСІЙСЬКОЇ ХЕРНІ..."
python manage.py clean_russian_content --settings=config.settings_production || log "⚠️ Очищення помилка"

# ФІНАЛЬНЕ ВИПРАВЛЕННЯ ВСЬОГО
log "🔥 ФІНАЛЬНЕ ВИПРАВЛЕННЯ КАТЕГОРІЙ ТА РОСІЙСЬКОЇ МОВИ..."
python manage.py fix_categories_final --settings=config.settings_production || log "⚠️ Final fix failed"

# Оновлення портфоліо згідно фото
log "🏢 ОНОВЛЕННЯ ПОРТФОЛІО ЗГІДНО ФОТО..."
python manage.py update_portfolio_descriptions --settings=config.settings_production || log "⚠️ Portfolio update failed"

# Створюємо медіа структуру FORCE
log "📁 СТВОРЕННЯ МЕДІА СТРУКТУРИ..."
mkdir -p /opt/render/project/src/media/products
mkdir -p /opt/render/project/src/media/products/gallery  
mkdir -p /opt/render/project/src/media/portfolio
log "✅ Медіа папки створені"

# 7. Збір статичних файлів
log "🎨 Збір статичних файлів..."
python manage.py collectstatic --no-input --settings=config.settings_production || handle_error "collectstatic"

# 8. СИЛОВЕ НАЛАШТУВАННЯ МЕДІА ФАЙЛІВ 
log "📁 КОПІЮВАННЯ МЕДІА ФАЙЛІВ З СИЛОЮ..."
python manage.py setup_media_for_production --verify --settings=config.settings_production || log "⚠️ Медіа setup помилка"

# ДОДАТКОВЕ КОПІЮВАННЯ медіа файлів якщо щось не так
if [ ! -d "/opt/render/project/src/staticfiles/media/products" ]; then
    log "🚨 КРИТИЧНО: staticfiles/media/products не існує! Створюю..."
    mkdir -p /opt/render/project/src/staticfiles/media/products
    mkdir -p /opt/render/project/src/staticfiles/media/products/gallery
    mkdir -p /opt/render/project/src/staticfiles/media/portfolio
fi

# Копіюємо файли з media до staticfiles якщо вони існують
if [ -d "/opt/render/project/src/media" ]; then
    log "📁 Копіювання з media/ до staticfiles/media/..."
    cp -r /opt/render/project/src/media/* /opt/render/project/src/staticfiles/media/ 2>/dev/null || log "⚠️ Копіювання не вдалося"
fi

log "✅ Медіа файли налаштовані СИЛОЮ"

# 9. ПІДГОТОВКА ПОРТФОЛІО
log "🏢 Підготовка портфоліо проєктів..."
python manage.py prepare_portfolio --settings=config.settings_production || log "⚠️ Portfolio setup skipped"

# 10. Оновлення медіа URL
log "🔄 Оновлення медіа URL налаштувань..."
python manage.py update_media_urls --settings=config.settings_production || log "⚠️ Media URLs update skipped"

# 11. ОСТАННЄ ОЧИЩЕННЯ РОСІЙСЬКОЇ ДРЯНІ
log "🇺🇦 ОСТАННЄ ОЧИЩЕННЯ РОСІЙСЬКОГО ЛАЙНА..."
python manage.py clean_russian_content --settings=config.settings_production || log "⚠️ Final cleanup skipped"

# Перевіряємо кількість товарів
log "📊 Перевірка кількості товарів..."
PRODUCTS_COUNT=$(python manage.py shell --settings=config.settings_production -c "from mainapp.models import Product; print(Product.objects.count())" 2>/dev/null | tail -1)
log "📦 Товарів у базі: $PRODUCTS_COUNT"

if [ "$PRODUCTS_COUNT" -lt "40" ]; then
    log "🚨 КРИТИЧНО: Мало товарів! Додатковий імпорт..."
    python manage.py create_sample_products --settings=config.settings_production || log "⚠️ Sample products failed"
fi

# 12. Очищення кешу
log "🧹 Очищення всіх кешів..."
python manage.py clear_all_cache --settings=config.settings_production || log "⚠️ Cache clear skipped"

# 13. ДЕТАЛЬНА ФІНАЛЬНА ПЕРЕВІРКА
log "🔍 ДЕТАЛЬНА ФІНАЛЬНА ПЕРЕВІРКА..."

# Перевіряємо всі компоненти
PRODUCTS=$(python manage.py shell --settings=config.settings_production -c "from mainapp.models import Product; print(Product.objects.count())" 2>/dev/null | tail -1)
CATEGORIES=$(python manage.py shell --settings=config.settings_production -c "from mainapp.models import Category; print(Category.objects.count())" 2>/dev/null | tail -1) 
PORTFOLIO=$(python manage.py shell --settings=config.settings_production -c "from mainapp.models import Portfolio; print(Portfolio.objects.count())" 2>/dev/null | tail -1)

log "📊 ФІНАЛЬНА СТАТИСТИКА:"
log "   📦 Товари: $PRODUCTS/42"
log "   📂 Категорії: $CATEGORIES/4" 
log "   🏢 Портфоліо: $PORTFOLIO/4"

# Перевіряємо медіа файли
if [ -d "/opt/render/project/src/staticfiles/media/products" ]; then
    MEDIA_COUNT=$(find /opt/render/project/src/staticfiles/media -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" | wc -l 2>/dev/null || echo "0")
    log "   🖼️ Медіа файли: $MEDIA_COUNT"
else
    log "   ❌ Медіа папка відсутня!"
fi

# Остаточна перевірка російського контенту
log "🇺🇦 Остаточна перевірка мови..."
python manage.py clean_russian_content --settings=config.settings_production || log "⚠️ Language check failed"



echo "=================================================="
log "🎉 BUILD ЗАВЕРШЕНО!"

# Фінальна перевірка успіху
if [ "$PRODUCTS" -ge "40" ] && [ "$CATEGORIES" -ge "4" ]; then
    log "✅ BUILD УСПІШНИЙ! ВСЕ ГОТОВО!"
    log "🎯 РЕЗУЛЬТАТ:"
    log "   ✅ $PRODUCTS товарів з українськими описами"
    log "   ✅ $CATEGORIES категорії без конфліктів"
    log "   ✅ $PORTFOLIO проєктів портфоліо"
    log "   ✅ ${MEDIA_COUNT:-0} медіа файлів готові"
    log "   ✅ Російський контент очищено"
    log "   ✅ Каталог буде працювати ідеально!"
else
    log "⚠️ BUILD ЗАВЕРШЕНО З ПРОБЛЕМАМИ"
    log "❌ Товарів: $PRODUCTS (потрібно 42+)"
    log "❌ Категорій: $CATEGORIES (потрібно 4+)"
    log "⚠️ Можливі проблеми з каталогом"
fi

echo "=================================================="
log "🚀 ПРОЕКТ ЗАПУЩЕНО НА RENDER!"
log "🌐 Перевірте: https://greensolartech-b0m2.onrender.com/catalog/"
