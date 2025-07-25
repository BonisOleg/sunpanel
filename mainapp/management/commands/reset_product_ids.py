"""
Команда для скидання AUTO_INCREMENT в таблицях продуктів
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Max
from mainapp.models import Product, ProductImage

class Command(BaseCommand):
    help = 'Скидає AUTO_INCREMENT для таблиць продуктів'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Скидання AUTO_INCREMENT...')
        
        with connection.cursor() as cursor:
            # Отримуємо назви таблиць
            product_table = Product._meta.db_table
            product_image_table = ProductImage._meta.db_table
            
            # Знаходимо максимальні ID
            max_product_id = Product.objects.aggregate(max_id=Max('id'))['max_id'] or 0
            max_image_id = ProductImage.objects.aggregate(max_id=Max('id'))['max_id'] or 0
            
            self.stdout.write(f'📊 Поточні максимальні ID:')
            self.stdout.write(f'  Products: {max_product_id}')
            self.stdout.write(f'  ProductImages: {max_image_id}')
            
            # Скидаємо AUTO_INCREMENT до наступного значення після максимального
            next_product_id = max_product_id + 1
            next_image_id = max_image_id + 1
            
            try:
                # PostgreSQL
                cursor.execute(f"SELECT setval(pg_get_serial_sequence('{product_table}', 'id'), {next_product_id}, false)")
                cursor.execute(f"SELECT setval(pg_get_serial_sequence('{product_image_table}', 'id'), {next_image_id}, false)")
                self.stdout.write('✅ PostgreSQL AUTO_INCREMENT скинуто')
            except Exception as e:
                try:
                    # MySQL/SQLite fallback
                    cursor.execute(f"ALTER TABLE {product_table} AUTO_INCREMENT = {next_product_id}")
                    cursor.execute(f"ALTER TABLE {product_image_table} AUTO_INCREMENT = {next_image_id}")
                    self.stdout.write('✅ MySQL AUTO_INCREMENT скинуто')
                except Exception as e2:
                    self.stdout.write(f'⚠️ Не вдалося скинути AUTO_INCREMENT: {e2}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 AUTO_INCREMENT СКИНУТО!\n'
                    f'Наступний Product ID: {next_product_id}\n'
                    f'Наступний ProductImage ID: {next_image_id}'
                )
            )
        
        self.stdout.write('✅ Скидання завершено!') 