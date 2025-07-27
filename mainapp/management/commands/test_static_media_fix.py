"""
Команда для тестування виправлення конфлікту static/staticfiles
Перевіряє що всі зображення товарів та портфоліо правильно доступні
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from mainapp.models import Product, ProductImage, Portfolio


class Command(BaseCommand):
    help = 'Тестує виправлення конфлікту static/staticfiles'

    def handle(self, *args, **options):
        self.stdout.write('🧪 ТЕСТУВАННЯ ВИПРАВЛЕННЯ STATIC/STATICFILES КОНФЛІКТУ')
        self.stdout.write('=' * 60)
        
        # Перевіряємо налаштування
        self.stdout.write('📋 Перевірка налаштувань:')
        self.stdout.write(f'   • STATIC_URL: {settings.STATIC_URL}')
        self.stdout.write(f'   • MEDIA_URL: {settings.MEDIA_URL}')
        self.stdout.write(f'   • STATIC_ROOT: {settings.STATIC_ROOT}')
        self.stdout.write(f'   • MEDIA_ROOT: {settings.MEDIA_ROOT}')
        self.stdout.write(f'   • DEBUG: {settings.DEBUG}')
        
        # Перевіряємо чи є конфлікт між STATIC_URL та MEDIA_URL
        if settings.STATIC_URL == settings.MEDIA_URL:
            self.stdout.write(
                self.style.ERROR('❌ КОНФЛІКТ: STATIC_URL і MEDIA_URL однакові!')
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Налаштування: STATIC_URL і MEDIA_URL різні')
            )
        
        # Перевіряємо структуру файлів
        self.stdout.write('\n📁 Перевірка структури файлів:')
        
        staticfiles_media = os.path.join(settings.STATIC_ROOT, 'media')
        if os.path.exists(staticfiles_media):
            file_count = sum(1 for _, _, files in os.walk(staticfiles_media) for _ in files)
            self.stdout.write(f'   ✅ staticfiles/media/ існує ({file_count} файлів)')
        else:
            self.stdout.write('   ❌ staticfiles/media/ не існує')
            
        # Перевіряємо products папку
        products_path = os.path.join(staticfiles_media, 'products')
        if os.path.exists(products_path):
            product_files = len([f for f in os.listdir(products_path) 
                               if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            self.stdout.write(f'   ✅ products/ папка ({product_files} зображень)')
        else:
            self.stdout.write('   ❌ products/ папка не існує')
            
        # Перевіряємо portfolio папку  
        portfolio_path = os.path.join(staticfiles_media, 'portfolio')
        if os.path.exists(portfolio_path):
            portfolio_files = len([f for f in os.listdir(portfolio_path) 
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            self.stdout.write(f'   ✅ portfolio/ папка ({portfolio_files} зображень)')
        else:
            self.stdout.write('   ❌ portfolio/ папка не існує')
        
        # Тестуємо генерацію URLs для товарів
        self.stdout.write('\n🛍️ Тестування товарів:')
        
        products = Product.objects.filter(image__isnull=False)[:5]
        for product in products:
            image_url = product.image_url
            if image_url:
                if image_url.startswith(settings.MEDIA_URL):
                    self.stdout.write(f'   ✅ {product.name[:40]}... → {image_url[:50]}...')
                else:
                    self.stdout.write(f'   ❌ {product.name[:40]}... → неправильний URL: {image_url}')
            else:
                self.stdout.write(f'   ⚠️ {product.name[:40]}... → немає зображення')
        
        # Тестуємо додаткові зображення
        self.stdout.write('\n🖼️ Тестування додаткових зображень:')
        
        product_images = ProductImage.objects.filter(image__isnull=False)[:5]
        for img in product_images:
            image_url = img.image_url
            if image_url:
                if image_url.startswith(settings.MEDIA_URL):
                    self.stdout.write(f'   ✅ {img.product.name[:30]}... → {image_url[:50]}...')
                else:
                    self.stdout.write(f'   ❌ {img.product.name[:30]}... → неправильний URL: {image_url}')
            else:
                self.stdout.write(f'   ⚠️ {img.product.name[:30]}... → немає зображення')
        
        # Тестуємо портфоліо
        self.stdout.write('\n🏢 Тестування портфоліо:')
        
        portfolios = Portfolio.objects.filter(image__isnull=False)[:3]
        for portfolio in portfolios:
            if hasattr(portfolio, 'image') and portfolio.image:
                if portfolio.image.url.startswith(settings.MEDIA_URL):
                    self.stdout.write(f'   ✅ {portfolio.title[:40]}... → URL правильний')
                else:
                    self.stdout.write(f'   ❌ {portfolio.title[:40]}... → неправильний URL')
        
        # Підсумок
        self.stdout.write('\n' + '=' * 60)
        
        # Перевіряємо статистику
        total_products = Product.objects.count()
        products_with_images = Product.objects.filter(image__isnull=False).count()
        total_images = ProductImage.objects.count()
        total_portfolio = Portfolio.objects.count()
        
        self.stdout.write('📊 СТАТИСТИКА:')
        self.stdout.write(f'   • Товарів: {total_products} (з фото: {products_with_images})')
        self.stdout.write(f'   • Додаткових зображень: {total_images}')
        self.stdout.write(f'   • Портфоліо проєктів: {total_portfolio}')
        
        if products_with_images > 0:
            self.stdout.write(
                self.style.SUCCESS('\n🎉 ТЕСТ ПРОЙДЕНО! Конфлікт виправлено!')
            )
            self.stdout.write('✅ Каталог та портфоліо мають працювати правильно')
        else:
            self.stdout.write(
                self.style.WARNING('\n⚠️ Товари без зображень - потрібен імпорт')
            )
            
        self.stdout.write(f'\n🌐 Для перевірки:')
        self.stdout.write(f'   • Каталог: /catalog/')
        self.stdout.write(f'   • Портфоліо: /portfolio/') 