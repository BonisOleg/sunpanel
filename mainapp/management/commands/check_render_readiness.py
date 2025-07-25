"""
Команда для повної перевірки готовності проекту до деплою на Render
Перевіряє всі критичні компоненти та надає рекомендації
"""
import os
import glob
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from mainapp.models import Product, ProductImage, Category, Brand
from django.core.exceptions import ImproperlyConfigured

class Command(BaseCommand):
    help = 'Перевіряє готовність проекту до деплою на Render'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Детальна перевірка з повним звітом'
        )
        parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='Автоматично виправити знайдені проблеми'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 ПЕРЕВІРКА ГОТОВНОСТІ ДО RENDER DEPLOY'))
        self.stdout.write('='*70)
        
        detailed = options['detailed']
        fix_issues = options['fix_issues']
        
        # Ініціалізуємо результати
        checks = {
            'settings': False,
            'database': False,
            'media_files': False,
            'static_files': False,
            'models': False,
            'templates': False,
            'dependencies': False,
            'content': False
        }
        
        issues = []
        
        # 1. Перевірка production налаштувань
        self.stdout.write('\n1️⃣ Перевірка production налаштувань...')
        checks['settings'], setting_issues = self.check_production_settings(detailed)
        issues.extend(setting_issues)
        
        # 2. Перевірка бази даних
        self.stdout.write('\n2️⃣ Перевірка бази даних...')
        checks['database'], db_issues = self.check_database(detailed)
        issues.extend(db_issues)
        
        # 3. Перевірка медіа файлів
        self.stdout.write('\n3️⃣ Перевірка медіа файлів...')
        checks['media_files'], media_issues = self.check_media_files(detailed, fix_issues)
        issues.extend(media_issues)
        
        # 4. Перевірка статичних файлів
        self.stdout.write('\n4️⃣ Перевірка статичних файлів...')
        checks['static_files'], static_issues = self.check_static_files(detailed)
        issues.extend(static_issues)
        
        # 5. Перевірка моделей
        self.stdout.write('\n5️⃣ Перевірка моделей та даних...')
        checks['models'], model_issues = self.check_models(detailed)
        issues.extend(model_issues)
        
        # 6. Перевірка шаблонів
        self.stdout.write('\n6️⃣ Перевірка шаблонів...')
        checks['templates'], template_issues = self.check_templates(detailed)
        issues.extend(template_issues)
        
        # 7. Перевірка залежностей
        self.stdout.write('\n7️⃣ Перевірка залежностей...')
        checks['dependencies'], dep_issues = self.check_dependencies(detailed)
        issues.extend(dep_issues)
        
        # 8. Перевірка контенту
        self.stdout.write('\n8️⃣ Перевірка контенту...')
        checks['content'], content_issues = self.check_content(detailed)
        issues.extend(content_issues)
        
        # Фінальний звіт
        self.show_final_report(checks, issues, fix_issues)

    def check_production_settings(self, detailed):
        """Перевіряє production налаштування"""
        issues = []
        
        # Критичні налаштування
        required_settings = {
            'DEBUG': False,
            'STATIC_ROOT': True,
            'MEDIA_ROOT': True,
            'MEDIA_URL': '/static/media/',
            'DATABASES': True,
            'ALLOWED_HOSTS': True
        }
        
        for setting, expected in required_settings.items():
            if not hasattr(settings, setting):
                issues.append(f'Відсутнє налаштування: {setting}')
            elif expected is not True and getattr(settings, setting) != expected:
                issues.append(f'Неправильне значення {setting}: {getattr(settings, setting)}')
        
        # Перевіряємо WhiteNoise
        if 'whitenoise.middleware.WhiteNoiseMiddleware' not in settings.MIDDLEWARE:
            issues.append('WhiteNoise middleware не підключений')
        
        if detailed:
            self.stdout.write(f'   📊 Перевірено {len(required_settings)} налаштувань')
        
        if not issues:
            self.stdout.write(self.style.SUCCESS('   ✅ Production налаштування коректні'))
            return True, []
        else:
            for issue in issues:
                self.stdout.write(f'   ❌ {issue}')
            return False, issues

    def check_database(self, detailed):
        """Перевіряє базу даних"""
        issues = []
        
        try:
            # Перевіряємо підключення
            connection.ensure_connection()
            
            # Перевіряємо таблиці
            tables = connection.introspection.table_names()
            required_tables = ['mainapp_product', 'mainapp_category', 'mainapp_brand']
            
            for table in required_tables:
                if table not in tables:
                    issues.append(f'Відсутня таблиця: {table}')
            
            # Перевіряємо дані
            if Product.objects.count() == 0:
                issues.append('Немає товарів у базі даних')
            
            if Category.objects.count() == 0:
                issues.append('Немає категорій у базі даних')
            
            if detailed:
                self.stdout.write(f'   📊 Товарів: {Product.objects.count()}')
                self.stdout.write(f'   📊 Категорій: {Category.objects.count()}')
                self.stdout.write(f'   📊 Брендів: {Brand.objects.count()}')
            
        except Exception as e:
            issues.append(f'Помилка підключення до БД: {str(e)}')
        
        if not issues:
            self.stdout.write(self.style.SUCCESS('   ✅ База даних працює коректно'))
            return True, []
        else:
            for issue in issues:
                self.stdout.write(f'   ❌ {issue}')
            return False, issues

    def check_media_files(self, detailed, fix_issues):
        """Перевіряє медіа файли"""
        issues = []
        
        # Перевіряємо папки
        media_root = os.path.join(settings.BASE_DIR, 'media')
        staticfiles_media = os.path.join(settings.BASE_DIR, 'staticfiles', 'media')
        
        if not os.path.exists(media_root):
            issues.append('Папка media не існує')
            if fix_issues:
                os.makedirs(media_root, exist_ok=True)
                self.stdout.write('   🔧 Створено папку media')
        
        # Підрахунок файлів
        media_files = 0
        if os.path.exists(media_root):
            media_files = len(glob.glob(os.path.join(media_root, '**', '*.jpg'), recursive=True))
            media_files += len(glob.glob(os.path.join(media_root, '**', '*.jpeg'), recursive=True))
            media_files += len(glob.glob(os.path.join(media_root, '**', '*.png'), recursive=True))
        
        staticfiles_media_files = 0
        if os.path.exists(staticfiles_media):
            staticfiles_media_files = len(glob.glob(os.path.join(staticfiles_media, '**', '*.jpg'), recursive=True))
            staticfiles_media_files += len(glob.glob(os.path.join(staticfiles_media, '**', '*.jpeg'), recursive=True))
            staticfiles_media_files += len(glob.glob(os.path.join(staticfiles_media, '**', '*.png'), recursive=True))
        
        # Перевіряємо товари без зображень
        products_without_images = Product.objects.filter(image='').count()
        if products_without_images > 0:
            issues.append(f'{products_without_images} товарів без зображень')
        
        if detailed:
            self.stdout.write(f'   📊 Медіа файлів у media/: {media_files}')
            self.stdout.write(f'   📊 Медіа файлів у staticfiles/media/: {staticfiles_media_files}')
            self.stdout.write(f'   📊 Товарів без зображень: {products_without_images}')
        
        if staticfiles_media_files == 0 and media_files > 0:
            issues.append('Медіа файли не підготовлені для production (запустіть setup_media_for_production)')
        
        if not issues:
            self.stdout.write(self.style.SUCCESS('   ✅ Медіа файли готові'))
            return True, []
        else:
            for issue in issues:
                self.stdout.write(f'   ❌ {issue}')
            return False, issues

    def check_static_files(self, detailed):
        """Перевіряє статичні файли"""
        issues = []
        
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if not static_root:
            issues.append('STATIC_ROOT не налаштований')
            return False, issues
        
        if not os.path.exists(static_root):
            issues.append('Папка staticfiles не існує (запустіть collectstatic)')
        else:
            static_files = len(glob.glob(os.path.join(static_root, '**', '*'), recursive=True))
            if detailed:
                self.stdout.write(f'   📊 Статичних файлів: {static_files}')
        
        # Перевіряємо CSS/JS файли
        required_static = ['css/base.css', 'js/base.js']
        static_dir = os.path.join(settings.BASE_DIR, 'static')
        
        for file_path in required_static:
            full_path = os.path.join(static_dir, file_path)
            if not os.path.exists(full_path):
                issues.append(f'Відсутній статичний файл: {file_path}')
        
        if not issues:
            self.stdout.write(self.style.SUCCESS('   ✅ Статичні файли готові'))
            return True, []
        else:
            for issue in issues:
                self.stdout.write(f'   ❌ {issue}')
            return False, issues

    def check_models(self, detailed):
        """Перевіряє моделі"""
        issues = []
        
        # Перевіряємо методи image_url
        products_with_images = Product.objects.exclude(image='').count()
        if products_with_images > 0:
            # Тестуємо перший товар
            test_product = Product.objects.exclude(image='').first()
            try:
                test_url = test_product.image_url
                if not test_url:
                    issues.append('Метод image_url повертає порожній результат')
            except Exception as e:
                issues.append(f'Помилка в методі image_url: {str(e)}')
        
        if detailed:
            self.stdout.write(f'   📊 Товарів з зображеннями: {products_with_images}')
        
        if not issues:
            self.stdout.write(self.style.SUCCESS('   ✅ Моделі працюють коректно'))
            return True, []
        else:
            for issue in issues:
                self.stdout.write(f'   ❌ {issue}')
            return False, issues

    def check_templates(self, detailed):
        """Перевіряє шаблони"""
        issues = []
        
        template_dir = os.path.join(settings.BASE_DIR, 'mainapp', 'templates', 'mainapp')
        required_templates = ['base.html', 'index.html', 'catalog.html', 'product_detail.html']
        
        for template in required_templates:
            template_path = os.path.join(template_dir, template)
            if not os.path.exists(template_path):
                issues.append(f'Відсутній шаблон: {template}')
        
        if detailed:
            self.stdout.write(f'   📊 Перевірено {len(required_templates)} шаблонів')
        
        if not issues:
            self.stdout.write(self.style.SUCCESS('   ✅ Шаблони на місці'))
            return True, []
        else:
            for issue in issues:
                self.stdout.write(f'   ❌ {issue}')
            return False, issues

    def check_dependencies(self, detailed):
        """Перевіряє залежності"""
        issues = []
        
        requirements_file = os.path.join(settings.BASE_DIR, 'requirements-production.txt')
        if not os.path.exists(requirements_file):
            issues.append('Файл requirements-production.txt не знайдений')
        
        # Перевіряємо критичні пакети
        try:
            import django
            import psycopg2
            import whitenoise
            import gunicorn
        except ImportError as e:
            issues.append(f'Відсутній критичний пакет: {str(e)}')
        
        if detailed:
            self.stdout.write(f'   📊 Django версія: {django.get_version()}')
        
        if not issues:
            self.stdout.write(self.style.SUCCESS('   ✅ Залежності встановлені'))
            return True, []
        else:
            for issue in issues:
                self.stdout.write(f'   ❌ {issue}')
            return False, issues

    def check_content(self, detailed):
        """Перевіряє контент на російську мову"""
        issues = []
        
        russian_patterns = ['ы', 'э', 'ъ', 'ё']
        
        # Перевіряємо товари
        for pattern in russian_patterns:
            russian_products = Product.objects.filter(name__icontains=pattern).count()
            if russian_products > 0:
                issues.append(f'Знайдено {russian_products} товарів з російськими символами')
                break
        
        if detailed and not issues:
            self.stdout.write('   📊 Російський контент не знайдений')
        
        if not issues:
            self.stdout.write(self.style.SUCCESS('   ✅ Контент українізований'))
            return True, []
        else:
            for issue in issues:
                self.stdout.write(f'   ❌ {issue}')
            return False, issues

    def show_final_report(self, checks, issues, fix_issues):
        """Показує фінальний звіт"""
        self.stdout.write('\n' + '='*70)
        
        passed_checks = sum(checks.values())
        total_checks = len(checks)
        
        if passed_checks == total_checks:
            self.stdout.write(self.style.SUCCESS('🎉 ПРОЕКТ ГОТОВИЙ ДО ДЕПЛОЮ НА RENDER!'))
            self.stdout.write(self.style.SUCCESS(f'✅ Пройдено всі {total_checks} перевірок'))
            self.stdout.write('\n🚀 Можете запускати деплой:')
            self.stdout.write('   git push origin main')
        else:
            self.stdout.write(self.style.ERROR(f'❌ ЗНАЙДЕНО {len(issues)} ПРОБЛЕМ'))
            self.stdout.write(f'📊 Пройдено {passed_checks}/{total_checks} перевірок')
            
            self.stdout.write('\n🔧 Рекомендації для виправлення:')
            if not checks['settings']:
                self.stdout.write('   • Перевірте config/settings_production.py')
            if not checks['media_files']:
                self.stdout.write('   • python manage.py setup_media_for_production')
            if not checks['content']:
                self.stdout.write('   • python manage.py clean_russian_content --fix')
            if not checks['database']:
                self.stdout.write('   • python manage.py migrate && python manage.py universal_import_products')
        
        self.stdout.write('='*70) 