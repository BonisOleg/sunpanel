"""
Команда для видалення товарів з високими ID з бази даних
"""
from django.core.management.base import BaseCommand
from mainapp.models import Product, ProductImage

class Command(BaseCommand):
    help = 'Видаляє товари з високими ID з бази даних'

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
            help='Показати які товари будуть видалені без фактичного видалення'
        )

    def handle(self, *args, **options):
        self.stdout.write('🗑️ Очищення товарів з високими ID...')
        
        min_id = options['min_id']
        dry_run = options['dry_run']
        
        # Знаходимо товари з високими ID
        old_products = Product.objects.filter(id__gte=min_id)
        old_images = ProductImage.objects.filter(product__id__gte=min_id)
        
        products_count = old_products.count()
        images_count = old_images.count()
        
        if dry_run:
            self.stdout.write(f'📊 [DRY-RUN] Товарів для видалення: {products_count}')
            self.stdout.write(f'📊 [DRY-RUN] Зображень для видалення: {images_count}')
            
            if products_count > 0:
                self.stdout.write('🗑️ [DRY-RUN] Товари що будуть видалені:')
                for product in old_products[:10]:  # Показуємо перші 10
                    self.stdout.write(f'  - ID {product.id}: {product.name}')
                if products_count > 10:
                    self.stdout.write(f'  ... та ще {products_count - 10} товарів')
        else:
            if products_count > 0:
                self.stdout.write(f'🗑️ Видаляю {products_count} товарів та {images_count} зображень...')
                
                # Видаляємо зображення товарів (CASCADE видалить автоматично, але явно для логування)
                deleted_images = old_images.delete()
                self.stdout.write(f'✅ Видалено зображень: {deleted_images[0]}')
                
                # Видаляємо товари
                deleted_products = old_products.delete()
                self.stdout.write(f'✅ Видалено товарів: {deleted_products[0]}')
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'🎉 ОЧИСТКА БД ЗАВЕРШЕНА!\n'
                        f'Видалено товарів: {deleted_products[0]}\n'
                        f'Видалено зображень: {deleted_images[0]}'
                    )
                )
            else:
                self.stdout.write('✅ Немає товарів з високими ID для видалення')
        
        # Показуємо поточний стан БД
        current_products = Product.objects.all()
        max_id = current_products.order_by('-id').first()
        
        self.stdout.write(f'📊 Поточний стан БД:')
        self.stdout.write(f'  Всього товарів: {current_products.count()}')
        self.stdout.write(f'  Максимальний ID: {max_id.id if max_id else "Немає товарів"}')
        
        if max_id and max_id.id < min_id:
            self.stdout.write('✅ Всі товари мають правильні ID!')
        elif max_id and max_id.id >= min_id:
            self.stdout.write(f'⚠️ Ще є товари з високими ID (максимальний: {max_id.id})')
        
        self.stdout.write('✅ Очистка БД завершена!') 