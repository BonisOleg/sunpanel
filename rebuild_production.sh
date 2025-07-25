#!/usr/bin/env bash
# СКРИПТ ДЛЯ ПОВНОГО ПЕРЕБІЛДУ PRODUCTION НА RENDER

set -o errexit  # Exit on error

echo "🚨 ПОЧАТОК ПОВНОГО ПЕРЕБІЛДУ PRODUCTION..."

# Перевіряємо чи ми на Render
if [[ "$RENDER" == "true" ]]; then
    echo "✅ Виконуємо на Render environment"
    BASE_DIR="/opt/render/project/src"
else
    echo "⚠️ Локальне тестування"
    BASE_DIR="."
fi

cd $BASE_DIR

echo "🗃️ ПОВНЕ ОЧИЩЕННЯ БАЗИ ДАНИХ..."
python manage.py flush --no-input --settings=config.settings_production

echo "🔧 СТВОРЕННЯ НОВИХ ТАБЛИЦЬ..."
python manage.py migrate --settings=config.settings_production

echo "🛡️ Перевірка на російський контент..."
python manage.py prevent_russian_import --settings=config.settings_production

echo "🧹 Повне очищення російського контенту..."
python manage.py clean_russian_content --settings=config.settings_production

echo "✏️ Перевірка та виправлення орфографії..."
python manage.py remove_russian_categories --settings=config.settings_production
python manage.py check_spelling_errors --fix --settings=config.settings_production

echo "📦 ІМПОРТ ТОВАРІВ..."
python manage.py universal_import_products --settings=config.settings_production

echo "🎨 ЗБІРКА СТАТИЧНИХ ФАЙЛІВ..."
python manage.py collectstatic --no-input --settings=config.settings_production

echo "📁 НАЛАШТУВАННЯ МЕДІА ФАЙЛІВ..."
python manage.py setup_media_for_production --settings=config.settings_production

echo "🔄 ОНОВЛЕННЯ МЕДІА URL..."
python manage.py update_media_urls --settings=config.settings_production

echo "🧹 ОЧИЩЕННЯ ВСІХ КЕШІВ..."
python manage.py clear_all_cache --settings=config.settings_production

# Перезапуск Gunicorn тільки на Render
if [[ "$RENDER" == "true" ]]; then
    echo "🔄 ПЕРЕЗАПУСК GUNICORN..."
    sudo supervisorctl restart gunicorn || echo "⚠️ Не вдалося перезапустити Gunicorn"
fi

echo "🎉 ПОВНИЙ ПЕРЕБІЛД ЗАВЕРШЕНО!"
echo "🌐 Сайт готовий: https://greensolartech.com.ua" 