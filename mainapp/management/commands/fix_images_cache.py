from django.core.management.base import BaseCommand
from django.conf import settings
from mainapp.models import Product, ProductImage
import os
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Виправляє проблеми з кешуванням зображень товарів після деплою'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Примусово оновити updated_at для всіх товарів щоб скинути кеш',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Починаю виправлення зображень...'))
        
        # 1. Перевіряємо медіа налаштування
        self.stdout.write(f"📁 MEDIA_URL: {settings.MEDIA_URL}")
        self.stdout.write(f"📁 MEDIA_ROOT: {settings.MEDIA_ROOT}")
        self.stdout.write(f"🐛 DEBUG: {settings.DEBUG}")
        
        # 2. Підраховуємо товари та зображення
        products_count = Product.objects.count()
        images_count = ProductImage.objects.count()
        
        self.stdout.write(f"📦 Знайдено товарів: {products_count}")
        self.stdout.write(f"🖼️ Знайдено зображень: {images_count}")
        
        # 3. Перевіряємо існування файлів зображень
        missing_files = []
        
        for product in Product.objects.all():
            if product.image:
                if not default_storage.exists(product.image.name):
                    missing_files.append(f"Product {product.id}: {product.image.name}")
        
        for image in ProductImage.objects.all():
            if image.image:
                if not default_storage.exists(image.image.name):
                    missing_files.append(f"ProductImage {image.id}: {image.image.name}")
        
        if missing_files:
            self.stdout.write(self.style.WARNING("⚠️ Відсутні файли зображень:"))
            for missing in missing_files[:10]:  # Показуємо перші 10
                self.stdout.write(f"   {missing}")
            if len(missing_files) > 10:
                self.stdout.write(f"   ... та ще {len(missing_files) - 10} файлів")
        else:
            self.stdout.write(self.style.SUCCESS("✅ Всі файли зображень існують"))
        
        # 4. Якщо запитано force-update, оновлюємо всі товари
        if options['force_update']:
            self.stdout.write("🔄 Примусово оновлюю updated_at для всіх товарів...")
            
            updated_count = 0
            for product in Product.objects.all():
                product.save()  # Це автоматично оновить updated_at
                updated_count += 1
                
                if updated_count % 50 == 0:
                    self.stdout.write(f"   Оновлено {updated_count} товарів...")
            
            self.stdout.write(self.style.SUCCESS(f"✅ Оновлено {updated_count} товарів"))
        
        # 5. Тестуємо URL генерацію
        self.stdout.write("\n🧪 Тестую генерацію URL зображень:")
        
        test_product = Product.objects.filter(image__isnull=False).first()
        if test_product:
            url = test_product.get_image_url()
            self.stdout.write(f"   Тестовий товар: {test_product.name}")
            self.stdout.write(f"   Згенерований URL: {url}")
            
            # Перевіряємо чи URL містить версіонування у продакшні
            if not settings.DEBUG and '?v=' not in url:
                self.stdout.write(self.style.WARNING("   ⚠️ URL не містить версіонування!"))
            elif settings.DEBUG and '?v=' in url:
                self.stdout.write(self.style.WARNING("   ⚠️ URL містить версіонування у DEBUG режимі!"))
            else:
                self.stdout.write(self.style.SUCCESS("   ✅ URL згенеровано правильно"))
        
        # 6. Рекомендації
        self.stdout.write("\n💡 Рекомендації:")
        self.stdout.write("   1. Очистіть кеш браузера (Ctrl+F5)")
        self.stdout.write("   2. Перезапустіть сервер")
        if missing_files:
            self.stdout.write("   3. Завантажте відсутні зображення")
        
        self.stdout.write(self.style.SUCCESS("\n🎉 Виправлення завершено!")) 