import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from mainapp.models import Product
import os

class Command(BaseCommand):
    help = 'Імпорт категорій з файлу second.xlsx та оновлення товарів'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='second.xlsx',
            help='Шлях до Excel файлу з категоріями'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Тільки показати що буде оновлено, без збереження'
        )
        parser.add_argument(
            '--update-products',
            action='store_true',
            help='Оновити категорії існуючих товарів'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        dry_run = options['dry_run']
        update_products = options['update_products']
        
        if not os.path.exists(file_path):
            raise CommandError(f'Файл {file_path} не існує')

        self.stdout.write(self.style.SUCCESS(f'{"[DRY RUN] " if dry_run else ""}Читаю категорії з файлу: {file_path}'))

        try:
            # Читаємо файл з категоріями
            df = pd.read_excel(file_path)
            self.stdout.write(f'Знайдено {len(df)} категорій')
            
            # Створюємо мапінг російських назв на українські
            category_mapping = {}
            ukrainian_categories = []
            
            for index, row in df.iterrows():
                russian_name = str(row.get('Назва_групи', '')).strip()
                ukrainian_name = str(row.get('Назва_групи_укр', '')).strip()
                
                if russian_name and ukrainian_name and pd.notna(row.get('Назва_групи')) and pd.notna(row.get('Назва_групи_укр')):
                    # Додаємо мапінг якщо назви відрізняються
                    if russian_name != ukrainian_name:
                        category_mapping[russian_name] = ukrainian_name
                        self.stdout.write(f'Мапінг: "{russian_name}" -> "{ukrainian_name}"')
                    
                    ukrainian_categories.append(ukrainian_name)
            
            self.stdout.write(f'\nСтворено {len(category_mapping)} мапінгів для перекладу')
            self.stdout.write(f'Всього українських категорій: {len(ukrainian_categories)}')
            
            # Виводимо всі українські категорії
            self.stdout.write('\nУкраїнські категорії:')
            for cat in sorted(ukrainian_categories):
                self.stdout.write(f'  - {cat}')
            
            if update_products:
                self.update_product_categories(category_mapping, dry_run)
            
            if dry_run:
                self.stdout.write(self.style.WARNING('\nЦе пробний запуск. Для реального оновлення запустіть без --dry-run'))

        except Exception as e:
            raise CommandError(f'Помилка при читанні файлу: {str(e)}')

    def update_product_categories(self, category_mapping, dry_run=False):
        """Оновлює категорії товарів згідно з мапінгом"""
        self.stdout.write(self.style.SUCCESS('\n=== Оновлення категорій товарів ==='))
        
        # Отримуємо всі товари з російськими категоріями
        products_to_update = []
        
        for russian_cat, ukrainian_cat in category_mapping.items():
            products = Product.objects.filter(category=russian_cat)
            if products.exists():
                self.stdout.write(f'\nЗнайдено {products.count()} товарів з категорією "{russian_cat}"')
                for product in products:
                    products_to_update.append((product, ukrainian_cat))
        
        if not products_to_update:
            self.stdout.write(self.style.WARNING('Не знайдено товарів для оновлення'))
            return
        
        self.stdout.write(f'\nВсього товарів для оновлення: {len(products_to_update)}')
        
        if dry_run:
            self.stdout.write('\nТовари що будуть оновлені:')
            for product, new_category in products_to_update[:10]:  # Показуємо перші 10
                self.stdout.write(f'  "{product.name}" ({product.category} -> {new_category})')
            if len(products_to_update) > 10:
                self.stdout.write(f'  ... та ще {len(products_to_update) - 10} товарів')
        else:
            # Оновлюємо товари
            updated_count = 0
            with transaction.atomic():
                for product, new_category in products_to_update:
                    old_category = product.category
                    product.category = new_category
                    product.save()
                    updated_count += 1
                    self.stdout.write(f'Оновлено: "{product.name}" ({old_category} -> {new_category})')
            
            self.stdout.write(self.style.SUCCESS(f'\nОновлено {updated_count} товарів'))
            
        # Показуємо поточну статистику категорій
        self.show_category_statistics()

    def show_category_statistics(self):
        """Показує статистику по категоріях"""
        self.stdout.write(self.style.SUCCESS('\n=== Статистика категорій ==='))
        
        from django.db.models import Count
        categories = Product.objects.values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        self.stdout.write('Категорії (кількість товарів):')
        for cat_data in categories:
            category = cat_data['category']
            count = cat_data['count']
            self.stdout.write(f'  {category}: {count} товарів') 