"""
Команда для тестування зображень товарів в production середовищі
Перевіряє що всі URL генеруються правильно та файли доступні
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from mainapp.models import Product, ProductImage
import os
import requests


class Command(BaseCommand):
    help = 'Тестує доступність зображень товарів в production'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-urls',
            action='store_true',
            help='Перевірити HTTP доступність URL зображень'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Максимальна кількість товарів для перевірки'
        )

    def handle(self, *args, **options):
        self.stdout.write('🔍 Тестування зображень товарів...')
        
        # Показуємо поточні налаштування
        self.stdout.write(f'📂 MEDIA_URL: {settings.MEDIA_URL}')
        self.stdout.write(f'📁 MEDIA_ROOT: {settings.MEDIA_ROOT}')
        self.stdout.write(f'🔧 DEBUG: {settings.DEBUG}')
        
        # Тестуємо генерацію URL
        limit = options['limit']
        products = Product.objects.filter(image__isnull=False)[:limit]
        
        self.stdout.write(f'\n🖼️ Перевірка {len(products)} товарів...')
        
        success_count = 0
        error_count = 0
        
        for product in products:
            try:
                # Генеруємо URL через модель
                image_url = product.image_url
                
                if image_url:
                    self.stdout.write(f'   ✅ {product.name[:40]}...')
                    self.stdout.write(f'      URL: {image_url}')
                    
                    # Перевіряємо файл локально
                    if settings.MEDIA_URL == '/static/media/':
                        # Продакшн: перевіряємо в staticfiles
                        file_path = image_url.replace('/static/media/', '')
                        local_path = os.path.join(settings.STATIC_ROOT, 'media', file_path)
                    else:
                        # Локальна розробка: перевіряємо в media
                        file_path = image_url.replace('/media/', '')
                        local_path = os.path.join(settings.MEDIA_ROOT, file_path)
                    
                    if os.path.exists(local_path):
                        self.stdout.write(f'      📁 Файл існує: {local_path}')
                        success_count += 1
                    else:
                        self.stdout.write(f'      ❌ Файл НЕ існує: {local_path}')
                        error_count += 1
                        
                    # HTTP перевірка якщо запитано
                    if options['check_urls']:
                        self.check_http_url(image_url)
                        
                else:
                    self.stdout.write(f'   ❌ {product.name[:40]}... - порожній URL')
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(f'   💥 {product.name[:40]}... - помилка: {e}')
                error_count += 1
        
        # Тестуємо додаткові зображення
        self.test_product_images(limit)
        
        # Підсумок
        self.stdout.write(f'\n📊 Результати тестування:')
        self.stdout.write(f'   ✅ Успішно: {success_count}')
        self.stdout.write(f'   ❌ Помилки: {error_count}')
        
        if error_count == 0:
            self.stdout.write(
                self.style.SUCCESS('🎉 Всі зображення працюють правильно!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Знайдено {error_count} проблем з зображеннями')
            )

    def test_product_images(self, limit):
        """Тестує додаткові зображення товарів"""
        self.stdout.write(f'\n🖼️ Перевірка додаткових зображень...')
        
        images = ProductImage.objects.select_related('product')[:limit]
        
        for image in images:
            try:
                image_url = image.image_url
                if image_url:
                    self.stdout.write(f'   ✅ {image.product.name[:30]}... (додаткове)')
                    self.stdout.write(f'      URL: {image_url}')
                else:
                    self.stdout.write(f'   ❌ {image.product.name[:30]}... - порожній URL додаткового зображення')
            except Exception as e:
                self.stdout.write(f'   💥 Помилка додаткового зображення: {e}')

    def check_http_url(self, url):
        """Перевіряє HTTP доступність URL"""
        try:
            # Додаємо базовий домен якщо URL відносний
            if url.startswith('/'):
                test_url = f'http://localhost:8000{url}'  # Для локального тестування
            else:
                test_url = url
                
            response = requests.head(test_url, timeout=5)
            if response.status_code == 200:
                self.stdout.write(f'      🌐 HTTP OK: {response.status_code}')
            else:
                self.stdout.write(f'      🌐 HTTP ERROR: {response.status_code}')
        except Exception as e:
            self.stdout.write(f'      🌐 HTTP помилка: {e}') 