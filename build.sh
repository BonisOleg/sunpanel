#!/usr/bin/env bash
# Build script for Render deployment

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

echo "📁 Setting up media files for production..."
python manage.py setup_media_for_production --settings=config.settings_production

echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input --settings=config.settings_production

echo "🔄 Updating media URL settings..."
python manage.py update_media_urls --settings=config.settings_production

echo "✅ Build completed successfully!" Dummy change to trigger Render rebuild
