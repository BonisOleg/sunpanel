#!/usr/bin/env bash
# Build script for Render.com deployment - LOCAL MEDIA FILES

set -o errexit  # exit on error

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements-production.txt

# Copy media files to static
echo "📁 Copying media files to static..."
python manage.py copy_media_to_static --clean

# Collect static files (including media)
echo "🗂️ Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "💾 Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
import os
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        'admin', 
        os.environ.get('ADMIN_EMAIL', 'admin@greensolartech.com'),
        os.environ.get('ADMIN_PASSWORD', 'admin123456')
    )
    print('✅ Superuser created')
else:
    print('✅ Superuser already exists')
"

# Prepare portfolio with images
echo "🎨 Preparing portfolio..."
python manage.py prepare_portfolio

# Add sample reviews if none exist
echo "⭐ Adding sample reviews..."
python manage.py shell -c "
from mainapp.models import Review
if Review.objects.count() == 0:
    exec(open('mainapp/management/commands/add_sample_reviews.py').read())
    print('✅ Sample reviews added')
else:
    print('✅ Reviews already exist')
"

echo "✅ Build completed successfully!"
echo "📊 Final status:"
python manage.py shell -c "
from mainapp.models import Product, Portfolio, Review, Category, Brand
print(f'  Products: {Product.objects.count()}')
print(f'  Categories: {Category.objects.count()}')
print(f'  Brands: {Brand.objects.count()}')
print(f'  Portfolio: {Portfolio.objects.count()}')
print(f'  Reviews: {Review.objects.count()}')
" 