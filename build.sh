#!/usr/bin/env bash
# Build script for Render deployment with optimized media handling

set -o errexit  # Exit on error

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements-production.txt

echo "🗃️ Running database migrations..."
python manage.py migrate --settings=config.settings_production

echo "🛡️ Перевірка на російський контент..."
python manage.py prevent_russian_import --settings=config.settings_production

echo "🧹 Повне очищення російського контенту..."
python manage.py clean_russian_content --settings=config.settings_production

echo "✏️ Перевірка та виправлення орфографії..."
python manage.py remove_russian_categories --settings=config.settings_production
python manage.py check_spelling_errors --fix --settings=config.settings_production

echo "📦 Імпорт товарів (якщо потрібно)..."
python manage.py universal_import_products --settings=config.settings_production

echo "📁 Setting up media files for production..."
python manage.py setup_media_for_production --verify --settings=config.settings_production

echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input --settings=config.settings_production

echo "🔄 Updating media URL settings..."
python manage.py update_media_urls --settings=config.settings_production

echo "🗑️ Cleaning up old database products..."
python manage.py cleanup_old_database_products --min-id=50 --settings=config.settings_production

echo "🔄 Resetting product IDs..."
python manage.py reset_product_ids --settings=config.settings_production

echo "🗑️ Cleaning up old product files..."
python manage.py cleanup_old_products --min-id=50 --settings=config.settings_production

echo "🧹 Clearing all caches..."
python manage.py clear_all_cache --settings=config.settings_production

echo "✅ Build completed successfully! All media files ready for WhiteNoise."
