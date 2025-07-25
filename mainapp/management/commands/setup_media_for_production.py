"""
Команда для налаштування медіа файлів в production
Копіює всі медіа файли до staticfiles/media/ для обслуговування через WhiteNoise
Оптимізовано для правильної роботи з товарами на Render
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from mainapp.models import Product, ProductImage


class Command(BaseCommand):
    help = 'Налаштовує медіа файли для production (копіює до staticfiles)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Очистити існуючі медіа файли в staticfiles'
        )
        parser.add_argument(
            '--verify',
            action='store_true',
            help='Перевірити що всі зображення товарів доступні'
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Налаштування медіа файлів для production...')
        
        # Шляхи
        media_source = os.path.join(settings.BASE_DIR, 'media')  
        staticfiles_root = getattr(settings, 'STATIC_ROOT', os.path.join(settings.BASE_DIR, 'staticfiles'))
        static_media_dest = os.path.join(staticfiles_root, 'media')
        
        # Створюємо staticfiles якщо не існує
        os.makedirs(staticfiles_root, exist_ok=True)
        
        # Очищення якщо потрібно
        if options['clean'] and os.path.exists(static_media_dest):
            shutil.rmtree(static_media_dest)
            self.stdout.write('🗑️ Очищено існуючі медіа файли в staticfiles')

        # Створюємо структуру папок
        os.makedirs(static_media_dest, exist_ok=True)
        os.makedirs(os.path.join(static_media_dest, 'products'), exist_ok=True)
        os.makedirs(os.path.join(static_media_dest, 'products', 'gallery'), exist_ok=True)
        os.makedirs(os.path.join(static_media_dest, 'portfolio'), exist_ok=True)
        os.makedirs(os.path.join(static_media_dest, 'brands'), exist_ok=True)
        
        if not os.path.exists(media_source):
            self.stdout.write(
                self.style.WARNING('⚠️ Папка media не знайдена! Створюю порожню структуру...')
            )
            return

        # Копіюємо всі медіа файли зі збереженням структури
        copied_files = 0
        for root, dirs, files in os.walk(media_source):
            for file in files:
                source_file = os.path.join(root, file)
                
                # Зберігаємо відносний шлях від media папки
                rel_path = os.path.relpath(source_file, media_source)
                dest_file = os.path.join(static_media_dest, rel_path)
                
                # Створюємо папки якщо потрібно
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                
                # Копіюємо файл
                try:
                    shutil.copy2(source_file, dest_file)
                    copied_files += 1
                    
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        self.stdout.write(f'✅ 🖼️ {rel_path}')
                    else:
                        self.stdout.write(f'✅ 📄 {rel_path}')
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Помилка копіювання {rel_path}: {e}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'📁 Скопійовано {copied_files} медіа файлів до staticfiles/media/'
            )
        )
        
        # Перевіряємо що всі зображення товарів доступні
        if options['verify']:
            self.verify_product_images(static_media_dest)
        
        self.stdout.write(
            self.style.SUCCESS(
                '🎉 Медіа файли готові для production!\n'
                'Тепер всі медіа файли доступні через /static/media/ URL'
            )
        )

    def verify_product_images(self, static_media_dest):
        """Перевіряє що всі зображення товарів правильно скопійовані"""
        self.stdout.write('\n🔍 Перевірка доступності зображень товарів...')
        
        missing_count = 0
        available_count = 0
        
        # Перевіряємо головні зображення товарів
        for product in Product.objects.all():
            if product.image:
                # Очікуваний шлях в staticfiles
                expected_path = os.path.join(static_media_dest, str(product.image.name))
                
                if os.path.exists(expected_path):
                    available_count += 1
                    if available_count <= 3:  # Показуємо перші 3
                        self.stdout.write(f'   ✅ {product.name[:40]}... → {product.image.name}')
                else:
                    missing_count += 1
                    if missing_count <= 3:  # Показуємо перші 3 проблемні
                        self.stdout.write(f'   ❌ {product.name[:40]}... → {product.image.name}')
        
        # Перевіряємо додаткові зображення
        gallery_missing = 0
        gallery_available = 0
        
        for image in ProductImage.objects.all():
            if image.image:
                expected_path = os.path.join(static_media_dest, str(image.image.name))
                
                if os.path.exists(expected_path):
                    gallery_available += 1
                else:
                    gallery_missing += 1
        
        # Підсумок
        self.stdout.write(f'\n📊 Результати перевірки:')
        self.stdout.write(f'   🖼️ Головні зображення: {available_count} доступні, {missing_count} відсутні')
        self.stdout.write(f'   🖼️ Додаткові зображення: {gallery_available} доступні, {gallery_missing} відсутні')
        
        if missing_count > 0 or gallery_missing > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️ Всього відсутніх зображень: {missing_count + gallery_missing}\n'
                    'Запустіть команду universal_import_products для повторного завантаження'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Всі зображення товарів доступні!')
            ) 