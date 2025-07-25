"""
Команда для примусової повної очистки БД від старих товарів
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from mainapp.models import Product, ProductImage, Category, Brand

class Command(BaseCommand):
    help = 'ПРИМУСОВО очищає БД від всіх товарів та створює їх заново'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Підтвердження примусової очистки'
        )

    def handle(self, *args, **options):
        if not options['force']:
            self.stdout.write(
                self.style.ERROR(
                    '⚠️ УВАГА! Ця команда видалить ВСІ товари!\n'
                    'Для підтвердження запустіть з флагом --force'
                )
            )
            return
        
        self.stdout.write('🚨 ПРИМУСОВА ОЧИСТКА БД...')
        
        try:
            with transaction.atomic():
                # Показуємо поточний стан
                products_count = Product.objects.count()
                images_count = ProductImage.objects.count()
                max_product = Product.objects.order_by('-id').first()
                
                self.stdout.write(f'📊 ПОТОЧНИЙ СТАН БД:')
                self.stdout.write(f'  Товарів: {products_count}')
                self.stdout.write(f'  Зображень: {images_count}')
                self.stdout.write(f'  Макс ID: {max_product.id if max_product else "Немає"}')
                
                if products_count == 0:
                    self.stdout.write('✅ БД вже порожня!')
                    return
                
                # ПОВНЕ ВИДАЛЕННЯ
                self.stdout.write('🗑️ Видаляю ВСІ товари...')
                
                # Видаляємо зображення товарів
                deleted_images = ProductImage.objects.all().delete()
                self.stdout.write(f'  ✅ Видалено зображень: {deleted_images[0]}')
                
                # Видаляємо товари  
                deleted_products = Product.objects.all().delete()
                self.stdout.write(f'  ✅ Видалено товарів: {deleted_products[0]}')
                
                # Скидаємо AUTO_INCREMENT якщо можливо
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        try:
                            # PostgreSQL
                            cursor.execute(f"ALTER SEQUENCE {Product._meta.db_table}_id_seq RESTART WITH 1")
                            cursor.execute(f"ALTER SEQUENCE {ProductImage._meta.db_table}_id_seq RESTART WITH 1")
                            self.stdout.write('  ✅ PostgreSQL AUTO_INCREMENT скинуто')
                        except Exception:
                            try:
                                # MySQL/SQLite
                                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{Product._meta.db_table}'")
                                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{ProductImage._meta.db_table}'")
                                self.stdout.write('  ✅ SQLite AUTO_INCREMENT скинуто')
                            except Exception as e:
                                self.stdout.write(f'  ⚠️ Не вдалося скинути AUTO_INCREMENT: {e}')
                except Exception as e:
                    self.stdout.write(f'  ⚠️ Помилка скидання AUTO_INCREMENT: {e}')
                
                # Перевіряємо результат
                final_count = Product.objects.count()
                final_images = ProductImage.objects.count()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'🎉 ПРИМУСОВА ОЧИСТКА ЗАВЕРШЕНА!\n'
                        f'Товарів залишилося: {final_count}\n'
                        f'Зображень залишилося: {final_images}\n'
                        f'БД готова для нового імпорту!'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ ПОМИЛКА ОЧИСТКИ: {e}')
            )
            raise
        
        self.stdout.write('✅ Очистка завершена! Тепер запустіть імпорт товарів.') 