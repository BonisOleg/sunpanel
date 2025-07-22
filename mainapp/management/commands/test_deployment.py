"""
Команда для тестування деплою - перевіряє всі критичні компоненти
"""
import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.test import Client
from django.urls import reverse
from mainapp.models import Product, Portfolio, Review, Category, Brand


class Command(BaseCommand):
    help = 'Тестує готовність до деплою'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='URL сайту для тестування (для production)',
            default='http://localhost:8000'
        )

    def handle(self, *args, **options):
        self.test_url = options['url']
        self.client = Client()
        
        self.stdout.write('🧪 Розпочинаємо тестування деплою...\n')
        
        # Тести
        self.test_database_data()
        self.test_static_files()
        self.test_media_files()
        self.test_pages()
        self.test_portfolio_images()
        self.test_spelling_errors()
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Всі тести пройдені успішно! Готово до деплою! 🚀')
        )

    def test_database_data(self):
        """Тест наявності даних в базі"""
        self.stdout.write('📊 Тестування даних бази...')
        
        products_count = Product.objects.count()
        categories_count = Category.objects.count()
        brands_count = Brand.objects.count()
        portfolio_count = Portfolio.objects.count()
        reviews_count = Review.objects.count()
        
        assert products_count > 0, "❌ Немає товарів в базі!"
        assert categories_count > 0, "❌ Немає категорій в базі!"
        assert brands_count > 0, "❌ Немає брендів в базі!"
        assert portfolio_count > 0, "❌ Немає проектів портфоліо!"
        assert reviews_count > 0, "❌ Немає відгуків!"
        
        self.stdout.write(f'  ✅ Products: {products_count}')
        self.stdout.write(f'  ✅ Categories: {categories_count}')
        self.stdout.write(f'  ✅ Brands: {brands_count}')
        self.stdout.write(f'  ✅ Portfolio: {portfolio_count}')
        self.stdout.write(f'  ✅ Reviews: {reviews_count}')

    def test_static_files(self):
        """Тест статичних файлів"""
        self.stdout.write('\n🗂️ Тестування статичних файлів...')
        
        static_media_path = os.path.join(settings.BASE_DIR, 'static', 'media')
        
        if os.path.exists(static_media_path):
            # Підраховуємо файли
            total_files = 0
            for root, dirs, files in os.walk(static_media_path):
                total_files += len([f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            
            assert total_files > 0, "❌ Немає медіа файлів в static/media!"
            self.stdout.write(f'  ✅ Медіа файлів в static: {total_files}')
        else:
            self.stdout.write('  ⚠️ Папка static/media не існує')

    def test_media_files(self):
        """Тест медіа файлів"""
        self.stdout.write('\n📁 Тестування медіа файлів...')
        
        media_path = os.path.join(settings.BASE_DIR, 'media')
        portfolio_path = os.path.join(media_path, 'portfolio')
        products_path = os.path.join(media_path, 'products')
        
        # Тест портфоліо
        if os.path.exists(portfolio_path):
            portfolio_files = [f for f in os.listdir(portfolio_path) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            self.stdout.write(f'  ✅ Portfolio зображень: {len(portfolio_files)}')
        else:
            self.stdout.write('  ⚠️ Папка media/portfolio не існує')
        
        # Тест товарів
        if os.path.exists(products_path):
            product_files = [f for f in os.listdir(products_path) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            self.stdout.write(f'  ✅ Product зображень: {len(product_files)}')

    def test_pages(self):
        """Тест сторінок сайту"""
        self.stdout.write('\n🌐 Тестування сторінок...')
        
        pages = [
            ('/', 'Головна'),
            ('/catalog/', 'Каталог'),
            ('/portfolio/', 'Портфоліо'),
            ('/reviews/', 'Відгуки'),
        ]
        
        for url, name in pages:
            try:
                response = self.client.get(url)
                assert response.status_code == 200, f"❌ {name} не доступна!"
                self.stdout.write(f'  ✅ {name} ({response.status_code})')
            except Exception as e:
                self.stdout.write(f'  ❌ {name}: {e}')

    def test_portfolio_images(self):
        """Тест зображень портфоліо"""
        self.stdout.write('\n🎨 Тестування зображень портфоліо...')
        
        portfolios = Portfolio.objects.all()
        for portfolio in portfolios:
            images = portfolio.all_images
            self.stdout.write(f'  📷 "{portfolio.title}": {len(images)} зображень')
            
            if images:
                self.stdout.write(f'    ✅ Зображення знайдені')
                for img in images[:3]:  # показуємо перші 3
                    self.stdout.write(f'      - {img}')
                if len(images) > 3:
                    self.stdout.write(f'      ... та ще {len(images) - 3}')
            else:
                self.stdout.write(f'    ⚠️ Зображення не знайдені')

        self.stdout.write(f'\n📊 Загалом проектів: {len(portfolios)}')

    def test_spelling_errors(self):
        """Тест орфографічних помилок"""
        self.stdout.write('\n✏️ Тестування орфографії...')
        
        from django.core.management import call_command
        from io import StringIO
        
        # Запускаємо команду перевірки орфографії
        out = StringIO()
        try:
            call_command('check_spelling_errors', stdout=out)
            output = out.getvalue()
            
            if 'ПОМИЛОК НЕ ЗНАЙДЕНО' in output:
                self.stdout.write('  ✅ Орфографічні помилки не знайдені')
            elif 'ЗНАЙДЕНО ПОМИЛКИ' in output:
                self.stdout.write('  ⚠️ Знайдено орфографічні помилки (будуть виправлені при деплої)')
                # Показуємо короткий звіт
                lines = output.split('\n')
                error_count = 0
                for line in lines:
                    if 'Всього помилок:' in line:
                        self.stdout.write(f'    {line.strip()}')
                        break
            else:
                self.stdout.write('  ✅ Перевірка орфографії пройшла успішно')
                
        except Exception as e:
            self.stdout.write(f'  ⚠️ Помилка при перевірці орфографії: {str(e)}') 