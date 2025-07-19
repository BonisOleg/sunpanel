import pandas as pd
import requests
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.utils.text import slugify
from mainapp.models import Product
import os
from urllib.parse import urlparse
import time

class Command(BaseCommand):
    help = 'Імпорт товарів з файлу tabla2.xlsx'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='tabla2.xlsx',
            help='Шлях до Excel файлу'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Тільки показати що буде імпортовано, без збереження'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        dry_run = options['dry_run']
        
        if not os.path.exists(file_path):
            raise CommandError(f'Файл {file_path} не існує. Будь ласка, експортуйте файл Numbers у формат Excel.')

        self.stdout.write(self.style.SUCCESS(f'{"[DRY RUN] " if dry_run else ""}Починаю імпорт з файлу: {file_path}'))

        try:
            # Спочатку спробуємо прочитати без вказівки аркуша
            try:
                df = pd.read_excel(file_path)
                self.stdout.write(f'Прочитано основний аркуш з {len(df)} рядками')
            except Exception as e:
                # Якщо не вдалося, спробуємо прочитати перший аркуш
                df = pd.read_excel(file_path, sheet_name=0)
                self.stdout.write(f'Прочитано перший аркуш з {len(df)} рядками')
            
            # Виводимо структуру файлу для аналізу
            self.stdout.write("Колонки в файлі:")
            for i, col in enumerate(df.columns):
                self.stdout.write(f"  {i}: {col}")
            
            self.stdout.write("\nПерші 3 рядки:")
            self.stdout.write(str(df.head(3)))
            
            if dry_run:
                self.stdout.write(self.style.WARNING('Це пробний запуск. Для реального імпорту запустіть без --dry-run'))
                return
            
            # Відслідковуємо статистику
            created_count = 0
            skipped_count = 0
            error_count = 0
            
            # Пробуємо визначити колонки автоматично
            name_col = self.find_column(df, ['назва', 'name', 'товар', 'продукт'])
            price_col = self.find_column(df, ['ціна', 'price', 'вартість', 'cost'])
            description_col = self.find_column(df, ['опис', 'description', 'desc'])
            category_col = self.find_column(df, ['категорія', 'category', 'група', 'group'])
            brand_col = self.find_column(df, ['бренд', 'brand', 'виробник', 'manufacturer'])
            
            self.stdout.write(f"\nВизначені колонки:")
            self.stdout.write(f"  Назва: {name_col}")
            self.stdout.write(f"  Ціна: {price_col}")
            self.stdout.write(f"  Опис: {description_col}")
            self.stdout.write(f"  Категорія: {category_col}")
            self.stdout.write(f"  Бренд: {brand_col}")
            
            if not name_col:
                raise CommandError('Не вдалося знайти колонку з назвою товару')
            
            for index, row in df.iterrows():
                try:
                    # Отримуємо базові дані
                    name = str(row.get(name_col, '')).strip() if pd.notna(row.get(name_col)) else ''
                    
                    if not name or name.lower() in ['nan', '']:
                        skipped_count += 1
                        continue
                    
                    price = self.parse_price(row.get(price_col, 0))
                    description = str(row.get(description_col, '')).strip() if pd.notna(row.get(description_col)) else ''
                    category = str(row.get(category_col, '')).strip() if pd.notna(row.get(category_col)) else 'Загальне'
                    brand = str(row.get(brand_col, '')).strip() if pd.notna(row.get(brand_col)) else ''
                    
                    # Перевіряємо чи товар вже існує
                    if Product.objects.filter(name=name).exists():
                        self.stdout.write(self.style.WARNING(f'Товар "{name}" вже існує, пропускаю'))
                        skipped_count += 1
                        continue
                    
                    # Створюємо товар
                    product = Product.objects.create(
                        name=name,
                        description=description or f'Опис для {name}',
                        price=price,
                        category=category,
                        brand=brand,
                        in_stock=True,
                        featured=False
                    )
                    
                    created_count += 1
                    self.stdout.write(f'Створено товар: {name} (₴{price})')
                    
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'Помилка при обробці рядка {index}: {str(e)}'))
                    continue
            
            # Виводимо статистику
            self.stdout.write(self.style.SUCCESS(f'\nІмпорт завершено!'))
            self.stdout.write(f'Створено товарів: {created_count}')
            self.stdout.write(f'Пропущено товарів: {skipped_count}')
            self.stdout.write(f'Помилок: {error_count}')

        except Exception as e:
            raise CommandError(f'Помилка при читанні файлу: {str(e)}')

    def find_column(self, df, possible_names):
        """Знаходить колонку за можливими назвами"""
        for col in df.columns:
            for name in possible_names:
                if name.lower() in str(col).lower():
                    return col
        return None

    def parse_price(self, price_value):
        """Парсить ціну з різних форматів"""
        if pd.isna(price_value):
            return 0
        
        # Якщо це вже число
        if isinstance(price_value, (int, float)):
            return max(0, float(price_value))
        
        # Якщо це рядок, очищуємо від символів
        price_str = str(price_value).strip()
        price_str = price_str.replace('₴', '').replace('грн', '').replace(',', '').replace(' ', '')
        
        try:
            return max(0, float(price_str))
        except (ValueError, TypeError):
            return 0 