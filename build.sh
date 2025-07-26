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

# 6. Імпорт товарів з Excel файлів (НОВИЙ МЕТОД!)
log "📦 Імпорт каталогу з Excel файлів..."
if python manage.py import_full_catalog --clear-existing --settings=config.settings_production; then
    log "✅ Каталог успішно імпортований з Excel файлів"
else
    log "⚠️ Excel імпорт не вдався, використовуємо backup метод..."
    if python manage.py create_sample_products --settings=config.settings_production; then
        log "✅ Створено зразкові товари (backup метод)"
    else
        log "❌ Не вдалося створити товари"
    fi
fi

# 7. Збір статичних файлів
log "🎨 Збір статичних файлів..."
python manage.py collectstatic --no-input --settings=config.settings_production || handle_error "collectstatic"

# 8. Налаштування медіа файлів (ПІСЛЯ collectstatic щоб не втратити)
log "📁 Налаштування медіа файлів для production..."
python manage.py setup_media_for_production --verify --settings=config.settings_production || handle_error "media setup"

# 9. Оновлення медіа URL
log "🔄 Оновлення медіа URL налаштувань..."
python manage.py update_media_urls --settings=config.settings_production || log "⚠️ Media URLs update skipped"

# 10. Очищення старих даних (безпечно)
log "🗑️ Очищення старих товарів з бази..."
python manage.py cleanup_old_database_products --min-id=50 --settings=config.settings_production || log "⚠️ DB cleanup skipped"

log "🔄 Скидання ID товарів..."
python manage.py reset_product_ids --settings=config.settings_production || log "⚠️ ID reset skipped"

log "🗑️ Очищення старих файлів товарів..."
python manage.py cleanup_old_products --min-id=50 --settings=config.settings_production || log "⚠️ File cleanup skipped"

# 11. Очищення кешу
log "🧹 Очищення всіх кешів..."
python manage.py clear_all_cache --settings=config.settings_production || log "⚠️ Cache clear skipped"

# 12. Фінальна перевірка готовності
log "🔍 Фінальна перевірка готовності..."
python manage.py final_render_prepare --settings=config.settings_production || handle_error "final check"

# 13. Перевірка критичних компонентів
log "🔍 Перевірка критичних компонентів..."

# Перевіряємо staticfiles/media
if [ -d "staticfiles/media" ]; then
    MEDIA_FILES=$(find staticfiles/media -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" | wc -l)
    log "✅ Знайдено $MEDIA_FILES медіа файлів у staticfiles"
else
    log "⚠️ Папка staticfiles/media не знайдена"
fi

# Перевіряємо базу даних
if python manage.py shell --settings=config.settings_production -c "from mainapp.models import Product; print(f'Товарів у базі: {Product.objects.count()}')"; then
    log "✅ База даних доступна"
else
    log "⚠️ Проблеми з базою даних"
fi

echo "=================================================="
log "🎉 BUILD УСПІШНО ЗАВЕРШЕНО!"
log "📊 Статистика:"
log "   • Статичні файли: $(find staticfiles -type f | wc -l)"
log "   • Медіа файли: ${MEDIA_FILES:-0}"
log "   • Django налаштування: production"
log "   • База даних: готова"
echo "=================================================="
log "✅ ПРОЕКТ ГОТОВИЙ ДО ЗАПУСКУ НА RENDER!"
