#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements-production.txt

echo "🗃️ Running database migrations..."
python manage.py migrate --settings=config.settings_production

echo "📁 Setting up media files for production..."
python manage.py setup_media_for_production --settings=config.settings_production

echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input --settings=config.settings_production

echo "✅ Build completed successfully!" 