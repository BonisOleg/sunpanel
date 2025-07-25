"""
Фінальна команда підготовки проекту до деплою на Render
Перевіряє та виправляє все що потрібно для ідеального деплою
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
from mainapp.models import Product, ProductImage, Category, Brand
from django.db import transaction

class Command(BaseCommand):
    help = 'Фінальна підготовка проекту до деплою на Render'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full-check',
            action='store_true',
            help='Повна перевірка всього проекту'
        )
        parser.add_argument(
            '--fix-images',
            action='store_true', 
            help='Виправити проблеми з зображеннями'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 ФІНАЛЬНА ПІДГОТОВКА ДО ДЕПЛОЮ НА RENDER'))
        self.stdout.write('='*60)
        
        full_check = options['full_check']
        fix_images = options['fix_images']
        
        issues_found = 0
        fixes_applied = 0
        
        # 1. Перевірка налаштувань
        self.stdout.write('\n1️⃣ Перевірка production налаштувань...')
        if self.check_production_settings():
            self.stdout.write(self.style.SUCCESS('   ✅ Production налаштування OK'))
        else:
            issues_found += 1
            self.stdout.write(self.style.ERROR('   ❌ Проблеми з production налаштуваннями'))
        
        # 2. Перевірка російського контенту
        self.stdout.write('\n2️⃣ Перевірка російського контенту...')
        russian_issues = self.check_russian_content()
        if russian_issues == 0:
            self.stdout.write(self.style.SUCCESS('   ✅ Російський контент відсутній'))
        else:
            issues_found += russian_issues
            self.stdout.write(self.style.WARNING(f'   ⚠️ Знайдено {russian_issues} елементів з російським контентом'))
            self.stdout.write('   🔧 Запустіть: python manage.py clean_russian_content --fix')
        
        # 3. Перевірка структури бази даних
        self.stdout.write('\n3️⃣ Перевірка структури бази даних...')
        db_issues = self.check_database_structure()
        if db_issues == 0:
            self.stdout.write(self.style.SUCCESS('   ✅ База даних структурована правильно'))
        else:
            issues_found += db_issues
        
        # 4. Перевірка медіа файлів (КРИТИЧНО!)
        self.stdout.write('\n4️⃣ Перевірка медіа файлів...')
        media_issues = self.check_media_files(fix_images)
        if media_issues == 0:
            self.stdout.write(self.style.SUCCESS('   ✅ Всі медіа файли на місці'))
        else:
            issues_found += media_issues
            if fix_images:
                self.stdout.write('   🔧 Виправляю проблеми з зображеннями...')
                self.fix_media_issues()
                fixes_applied += 1
        
        # 5. Перевірка static файлів
        self.stdout.write('\n5️⃣ Перевірка статичних файлів...')
        if self.check_static_files():
            self.stdout.write(self.style.SUCCESS('   ✅ Статичні файли готові'))
        else:
            issues_found += 1
        
        # 6. Перевірка URL структури
        self.stdout.write('\n6️⃣ Перевірка URL структури...')
        if self.check_urls():
            self.stdout.write(self.style.SUCCESS('   ✅ URL структура правильна'))
        else:
            issues_found += 1
        
        # 7. Підготовка до деплою
        if issues_found == 0:
            self.stdout.write('\n7️⃣ Підготовка медіа файлів для Render...')
            self.prepare_for_render()
            
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('🎉 ПРОЕКТ ГОТОВИЙ ДО ДЕПЛОЮ!'))
            self.stdout.write(self.style.SUCCESS('Можете запускати деплой на Render'))
            self.stdout.write('='*60)
        else:
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.ERROR(f'❌ Знайдено {issues_found} проблем'))
            self.stdout.write(self.style.WARNING('Виправте проблеми перед деплоєм:'))
            
            if russian_issues > 0:
                self.stdout.write('   • python manage.py clean_russian_content --fix')
            if media_issues > 0:
                self.stdout.write('   • python manage.py final_render_prepare --fix-images')
            
            self.stdout.write('='*60)

    def check_production_settings(self):
        """Перевіряє production налаштування"""
        required_settings = [
            'STATIC_ROOT',
            'MEDIA_ROOT', 
            'WHITENOISE_USE_FINDERS',
            'DATABASES'
        ]
        
        for setting in required_settings:
            if not hasattr(settings, setting):
                self.stdout.write(f'   ❌ Відсутнє налаштування: {setting}')
                return False
        
        # Перевіряємо MEDIA_URL
        if settings.MEDIA_URL != '/static/media/':
            self.stdout.write(f'   ❌ MEDIA_URL повинно бути /static/media/, а не {settings.MEDIA_URL}')
            return False
            
        return True

    def check_russian_content(self):
        """Перевіряє російський контент"""
        russian_patterns = [
            'ы', 'э', 'ъ', 'ё',  # російські літери
            'ции', 'тся',         # російські закінчення
            'мощность', 'производитель', 'гарантия'  # російські слова
        ]
        
        issues = 0
        
        # Перевіряємо товари
        for product in Product.objects.all():
            for pattern in russian_patterns:
                if (pattern in product.name.lower() or 
                    pattern in product.description.lower()):
                    issues += 1
                    break
        
        # Перевіряємо категорії
        for category in Category.objects.all():
            for pattern in russian_patterns:
                if pattern in category.name.lower():
                    issues += 1
                    break
        
        return issues

    def check_database_structure(self):
        """Перевіряє структуру бази даних"""
        issues = 0
        
        # Перевіряємо що є товари
        if Product.objects.count() == 0:
            self.stdout.write('   ⚠️ Немає товарів в базі')
            issues += 1
        
        # Перевіряємо що є категорії
        if Category.objects.count() == 0:
            self.stdout.write('   ⚠️ Немає категорій в базі')
            issues += 1
        
        # Перевіряємо що є бренди
        if Brand.objects.count() == 0:
            self.stdout.write('   ⚠️ Немає брендів в базі')
            issues += 1
        
        # Перевіряємо чи всі товари мають зображення
        products_without_images = Product.objects.filter(image='').count()
        if products_without_images > 0:
            self.stdout.write(f'   ⚠️ {products_without_images} товарів без зображень')
            issues += 1
        
        return issues

    def check_media_files(self, fix_mode=False):
        """Перевіряє медіа файли"""
        issues = 0
        
        # Перевіряємо папку media
        media_root = os.path.join(settings.BASE_DIR, 'media')
        if not os.path.exists(media_root):
            self.stdout.write('   ❌ Папка media не існує')
            issues += 1
            return issues
        
        # Перевіряємо папку products
        products_dir = os.path.join(media_root, 'products')
        if not os.path.exists(products_dir):
            self.stdout.write('   ❌ Папка media/products не існує')
            issues += 1
        
        # Перевіряємо чи всі товари мають зображення
        for product in Product.objects.all():
            if product.image:
                image_path = os.path.join(settings.BASE_DIR, 'media', str(product.image))
                if not os.path.exists(image_path):
                    self.stdout.write(f'   ❌ Відсутнє зображення: {product.image}')
                    issues += 1
        
        return issues

    def check_static_files(self):
        """Перевіряє статичні файли"""
        static_dirs = [
            os.path.join(settings.BASE_DIR, 'static', 'css'),
            os.path.join(settings.BASE_DIR, 'static', 'js'),
            os.path.join(settings.BASE_DIR, 'static', 'images'),
        ]
        
        for static_dir in static_dirs:
            if not os.path.exists(static_dir):
                self.stdout.write(f'   ❌ Відсутня папка: {static_dir}')
                return False
        
        return True

    def check_urls(self):
        """Перевіряє URL структуру"""
        try:
            from django.urls import reverse
            
            # Перевіряємо основні URL
            test_urls = [
                'mainapp:index',
                'mainapp:catalog', 
                'mainapp:portfolio',
                'mainapp:reviews'
            ]
            
            for url_name in test_urls:
                try:
                    reverse(url_name)
                except:
                    self.stdout.write(f'   ❌ Проблема з URL: {url_name}')
                    return False
            
            return True
        except Exception as e:
            self.stdout.write(f'   ❌ Помилка перевірки URLs: {e}')
            return False

    def fix_media_issues(self):
        """Виправляє проблеми з медіа файлами"""
        # Створюємо необхідні папки
        media_dirs = [
            os.path.join(settings.BASE_DIR, 'media'),
            os.path.join(settings.BASE_DIR, 'media', 'products'),
            os.path.join(settings.BASE_DIR, 'media', 'products', 'gallery'),
            os.path.join(settings.BASE_DIR, 'media', 'portfolio'),
            os.path.join(settings.BASE_DIR, 'media', 'brands'),
        ]
        
        for media_dir in media_dirs:
            os.makedirs(media_dir, exist_ok=True)
        
        self.stdout.write('   ✅ Створено необхідні медіа папки')

    def prepare_for_render(self):
        """Підготовка до деплою на Render"""
        # Запускаємо setup_media_for_production
        call_command('setup_media_for_production', '--verify')
        
        # Очищаємо кеш
        call_command('clear_all_cache')
        
        # Фінальна перевірка
        static_media = os.path.join(settings.BASE_DIR, 'staticfiles', 'media')
        if os.path.exists(static_media):
            files_count = len([f for f in os.listdir(static_media) if f.endswith(('.jpg', '.jpeg', '.png'))])
            self.stdout.write(f'   ✅ Підготовлено {files_count} медіа файлів для Render')
        
        self.stdout.write('   ✅ Проект готовий до деплою!') 