"""
Команда для очищення безладу з медіа файлами
Залишає тільки необхідні зображення для існуючих товарів
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from mainapp.models import Product, ProductImage

class Command(BaseCommand):
    help = 'Очищає безлад з медіа файлами - залишає тільки необхідні'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Режим попереднього перегляду без видалення'
        )
        parser.add_argument(
            '--aggressive',
            action='store_true',
            help='Агресивне очищення - видаляє ВСЕ і створює заново'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        aggressive = options['aggressive']
        
        self.stdout.write('🔥 ОЧИЩЕННЯ МЕДІА БЕЗЛАДУ')
        self.stdout.write('='*50)
        
        media_root = os.path.join(settings.BASE_DIR, 'media')
        products_dir = os.path.join(media_root, 'products')
        gallery_dir = os.path.join(products_dir, 'gallery')
        
        if not os.path.exists(products_dir):
            self.stdout.write('❌ Папка products не знайдена')
            return
        
        # Підрахунок поточного стану
        current_main = len([f for f in os.listdir(products_dir) if f.endswith('.jpg')])
        current_gallery = len([f for f in os.listdir(gallery_dir) if f.endswith('.jpg')]) if os.path.exists(gallery_dir) else 0
        
        self.stdout.write(f'📊 Поточний стан:')
        self.stdout.write(f'   • Товарів в базі: {Product.objects.count()}')
        self.stdout.write(f'   • Головних зображень: {current_main}')
        self.stdout.write(f'   • Зображень галереї: {current_gallery}')
        self.stdout.write(f'   • ЗАГАЛОМ: {current_main + current_gallery}')
        
        if aggressive:
            self.aggressive_cleanup(products_dir, dry_run)
        else:
            self.smart_cleanup(products_dir, gallery_dir, dry_run)
        
        # Підрахунок після очищення
        if not dry_run:
            new_main = len([f for f in os.listdir(products_dir) if f.endswith('.jpg')])
            new_gallery = len([f for f in os.listdir(gallery_dir) if f.endswith('.jpg')]) if os.path.exists(gallery_dir) else 0
            
            self.stdout.write(f'\n✅ Результат:')
            self.stdout.write(f'   • Головних зображень: {new_main}')
            self.stdout.write(f'   • Зображень галереї: {new_gallery}')
            self.stdout.write(f'   • ЗАГАЛОМ: {new_main + new_gallery}')
            self.stdout.write(f'   • ВИДАЛЕНО: {(current_main + current_gallery) - (new_main + new_gallery)}')

    def aggressive_cleanup(self, products_dir, dry_run):
        """Агресивне очищення - видаляє ВСЕ і створює заново"""
        self.stdout.write('\n🔥 АГРЕСИВНЕ ОЧИЩЕННЯ - ВИДАЛЯЄМО ВСЕ!')
        
        if dry_run:
            self.stdout.write('   [DRY RUN] Видалив би всі файли в products/')
            return
        
        # Видаляємо всю папку products
        if os.path.exists(products_dir):
            shutil.rmtree(products_dir)
            self.stdout.write('   ✅ Видалено всю папку products/')
        
        # Створюємо заново
        os.makedirs(products_dir, exist_ok=True)
        os.makedirs(os.path.join(products_dir, 'gallery'), exist_ok=True)
        
        self.stdout.write('   ✅ Створено чисті папки')
        self.stdout.write('\n⚠️ ТЕПЕР ЗАПУСТІТЬ: python manage.py universal_import_products')

    def smart_cleanup(self, products_dir, gallery_dir, dry_run):
        """Розумне очищення - залишає тільки потрібні файли"""
        self.stdout.write('\n🧹 РОЗУМНЕ ОЧИЩЕННЯ')
        
        # Отримуємо список необхідних файлів з бази
        needed_files = set()
        
        for product in Product.objects.all():
            if product.image:
                # Витягуємо тільки ім'я файлу
                image_name = os.path.basename(str(product.image))
                needed_files.add(image_name)
        
        # Додаємо файли з ProductImage
        for img in ProductImage.objects.all():
            if img.image:
                image_name = os.path.basename(str(img.image))
                needed_files.add(image_name)
        
        self.stdout.write(f'   📝 Необхідних файлів: {len(needed_files)}')
        
        deleted_count = 0
        
        # Очищуємо головні зображення
        for filename in os.listdir(products_dir):
            if filename.endswith('.jpg') and filename not in needed_files:
                file_path = os.path.join(products_dir, filename)
                if dry_run:
                    self.stdout.write(f'   [DRY RUN] Видалив би: {filename}')
                else:
                    os.remove(file_path)
                deleted_count += 1
        
        # Очищуємо галерею - залишаємо максимум 3 фото на товар
        if os.path.exists(gallery_dir):
            gallery_files = {}
            
            # Групуємо файли галереї по товарах
            for filename in os.listdir(gallery_dir):
                if filename.endswith('.jpg'):
                    # Витягуємо ID товару з назви файлу
                    parts = filename.split('_')
                    if len(parts) >= 2:
                        product_id = parts[1]
                        if product_id not in gallery_files:
                            gallery_files[product_id] = []
                        gallery_files[product_id].append(filename)
            
            # Залишаємо максимум 3 фото на товар
            for product_id, files in gallery_files.items():
                files.sort()  # Сортуємо для передбачуваності
                
                if len(files) > 3:
                    files_to_delete = files[3:]  # Видаляємо все після 3-го
                    
                    for filename in files_to_delete:
                        file_path = os.path.join(gallery_dir, filename)
                        if dry_run:
                            self.stdout.write(f'   [DRY RUN] Видалив би галерею: {filename}')
                        else:
                            os.remove(file_path)
                        deleted_count += 1
        
        if not dry_run:
            self.stdout.write(f'   ✅ Видалено {deleted_count} зайвих файлів')
        else:
            self.stdout.write(f'   📊 Було б видалено {deleted_count} файлів') 