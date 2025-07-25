"""
Команда для видалення старих файлів продуктів з високими номерами
"""
import os
import re
import glob
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Видаляє всі старі файли продуктів з номерами понад 100'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-id',
            type=int,
            default=100,
            help='Мінімальний ID для видалення (за замовчуванням 100)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати які файли будуть видалені без фактичного видалення'
        )

    def handle(self, *args, **options):
        self.stdout.write('🧹 Очищення старих файлів продуктів...')
        
        min_id = options['min_id']
        dry_run = options['dry_run']
        
        # Папки для очистки
        media_paths = [
            os.path.join(settings.BASE_DIR, 'media', 'products'),
            os.path.join(settings.BASE_DIR, 'staticfiles', 'media', 'products'),
            os.path.join(settings.BASE_DIR, 'static', 'media', 'products') if hasattr(settings, 'STATIC_ROOT') else None
        ]
        
        # Додаємо gallery папки
        gallery_paths = [
            os.path.join(settings.BASE_DIR, 'media', 'products', 'gallery'),
            os.path.join(settings.BASE_DIR, 'staticfiles', 'media', 'products', 'gallery'),
            os.path.join(settings.BASE_DIR, 'static', 'media', 'products', 'gallery') if hasattr(settings, 'STATIC_ROOT') else None
        ]
        
        all_paths = [p for p in media_paths + gallery_paths if p and os.path.exists(p)]
        
        total_deleted = 0
        total_size = 0
        
        for media_path in all_paths:
            self.stdout.write(f'🔍 Перевіряю: {media_path}')
            
            # Патерн для знаходження файлів з високими номерами
            pattern = os.path.join(media_path, 'product_*.jpg')
            files = glob.glob(pattern)
            
            for file_path in files:
                filename = os.path.basename(file_path)
                
                # Витягуємо номер продукту з назви файлу
                match = re.match(r'product_(\d+)_', filename)
                if match:
                    product_id = int(match.group(1))
                    
                    if product_id >= min_id:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        
                        if dry_run:
                            self.stdout.write(f'  🗑️ [DRY-RUN] {filename} (ID: {product_id}, {file_size} bytes)')
                        else:
                            try:
                                os.remove(file_path)
                                self.stdout.write(f'  ✅ Видалено: {filename} (ID: {product_id}, {file_size} bytes)')
                                total_deleted += 1
                            except Exception as e:
                                self.stdout.write(f'  ❌ Помилка видалення {filename}: {e}')
        
        if dry_run:
            self.stdout.write(
                f'📊 [DRY-RUN] Буде видалено файлів: {len([f for f in files if re.match(r"product_(\d+)_", os.path.basename(f)) and int(re.match(r"product_(\d+)_", os.path.basename(f)).group(1)) >= min_id])}'
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 ОЧИСТКА ЗАВЕРШЕНА!\n'
                    f'Видалено файлів: {total_deleted}\n'
                    f'Звільнено місця: {total_size / (1024*1024):.2f} MB'
                )
            )
        
        self.stdout.write('✅ Старі файли очищено!') 