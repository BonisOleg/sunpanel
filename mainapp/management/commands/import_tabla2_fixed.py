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
    help = 'Імпорт товарів з українського Excel файлу (виправлена версія)'

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
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Оновлювати існуючі товари'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        dry_run = options['dry_run']
        update_existing = options['update_existing']
        
        if not os.path.exists(file_path):
            raise CommandError(f'Файл {file_path} не існує. Будь ласка, експортуйте файл Numbers у формат Excel.')

        self.stdout.write(self.style.SUCCESS(f'{"[DRY RUN] " if dry_run else ""}Починаю імпорт з файлу: {file_path}'))

        try:
            # Читаємо Excel файл
            df = pd.read_excel(file_path)
            self.stdout.write(f'Прочитано {len(df)} рядків')
            
            # Визначаємо правильні колонки для української таблиці
            column_mapping = {
                'name': self.find_ukrainian_name_column(df),
                'price': self.find_column(df, ['ціна', 'price', 'вартість']),
                'description': self.find_column(df, ['опис_укр', 'опис', 'description']),
                'category': self.find_column(df, ['назва_групи', 'категорія', 'група']),
                'brand': self.find_column(df, ['виробник', 'бренд', 'brand']),
                'code': self.find_column(df, ['код_товару', 'код', 'code']),
                'country': self.find_column(df, ['країна_виробник', 'країна']),
                'image_url': self.find_column(df, ['посилання_зображення', 'зображення'])
            }
            
            self.stdout.write(f"\nВизначені колонки:")
            for key, col in column_mapping.items():
                self.stdout.write(f"  {key}: {col}")
            
            if not column_mapping['name']:
                raise CommandError('Не вдалося знайти колонку з назвою товару')
            
            if dry_run:
                self.stdout.write("\nПерші 5 товарів:")
                for i in range(min(5, len(df))):
                    row = df.iloc[i]
                    name = self.get_clean_value(row, column_mapping['name'])
                    price = self.parse_price(row.get(column_mapping['price'], 0))
                    if name and name.lower() not in ['nan', '']:
                        self.stdout.write(f"  {i+1}. {name} - ₴{price}")
                
                self.stdout.write(self.style.WARNING('\nЦе пробний запуск. Для реального імпорту запустіть без --dry-run'))
                return
            
            # Статистика
            created_count = 0
            updated_count = 0
            skipped_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Отримуємо дані
                    name = self.get_clean_value(row, column_mapping['name'])
                    
                    if not name or name.lower() in ['nan', '']:
                        skipped_count += 1
                        continue
                    
                    price = self.parse_price(row.get(column_mapping['price'], 0))
                    description = self.get_clean_value(row, column_mapping['description']) or f'Опис для {name}'
                    category = self.get_clean_value(row, column_mapping['category']) or 'Загальне'
                    brand = self.get_clean_value(row, column_mapping['brand']) or ''
                    country = self.get_clean_value(row, column_mapping['country']) or ''
                    
                    # Перевіряємо чи існує товар
                    existing = Product.objects.filter(name=name).first()
                    
                    if existing:
                        if update_existing:
                            existing.price = price
                            existing.description = description
                            existing.category = category
                            existing.brand = brand
                            existing.country = country
                            existing.save()
                            updated_count += 1
                            self.stdout.write(f'Оновлено товар: {name} (₴{price})')
                        else:
                            self.stdout.write(self.style.WARNING(f'Товар "{name}" вже існує, пропускаю'))
                            skipped_count += 1
                        continue
                    
                    # Створюємо новий товар
                    product = Product.objects.create(
                        name=name,
                        description=description,
                        price=price,
                        category=category,
                        brand=brand,
                        country=country,
                        in_stock=True,
                        featured=False
                    )
                    
                    # Обробляємо зображення якщо є
                    if column_mapping['image_url']:
                        image_url = self.get_clean_value(row, column_mapping['image_url'])
                        if image_url and image_url.startswith('http'):
                            self.download_and_set_image(product, image_url)
                    
                    created_count += 1
                    self.stdout.write(f'Створено товар: {name} (₴{price})')
                    
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'Помилка при обробці рядка {index}: {str(e)}'))
                    continue
            
            # Підсумок
            self.stdout.write(self.style.SUCCESS(f'\nІмпорт завершено!'))
            self.stdout.write(f'Створено товарів: {created_count}')
            self.stdout.write(f'Оновлено товарів: {updated_count}')
            self.stdout.write(f'Пропущено товарів: {skipped_count}')
            self.stdout.write(f'Помилок: {error_count}')

        except Exception as e:
            raise CommandError(f'Помилка при читанні файлу: {str(e)}')

    def find_ukrainian_name_column(self, df):
        """Знаходить правильну колонку з українською назвою"""
        priority_columns = [
            'Назва_позиції_укр',
            'назва_укр', 
            'назва_товару',
            'name_ukr',
            'product_name_ukr'
        ]
        
        for col in priority_columns:
            if col in df.columns:
                return col
        
        # Якщо не знайшли точну відповідність, шукаємо по частині назви
        for col in df.columns:
            col_lower = str(col).lower()
            if 'назва' in col_lower and 'укр' in col_lower:
                return col
            elif 'name' in col_lower and 'ukr' in col_lower:
                return col
        
        return None

    def find_column(self, df, possible_names):
        """Знаходить колонку за можливими назвами"""
        for col in df.columns:
            for name in possible_names:
                if name.lower() in str(col).lower():
                    return col
        return None

    def get_clean_value(self, row, column_name):
        """Отримує очищене значення з рядка"""
        if not column_name or column_name not in row.index:
            return ''
        
        value = row.get(column_name)
        if pd.isna(value):
            return ''
        
        return str(value).strip()

    def parse_price(self, price_value):
        """Парсить ціну з різних форматів"""
        if pd.isna(price_value):
            return 0
        
        if isinstance(price_value, (int, float)):
            return max(0, float(price_value))
        
        price_str = str(price_value).strip()
        price_str = price_str.replace('₴', '').replace('грн', '').replace(',', '').replace(' ', '')
        
        try:
            return max(0, float(price_str))
        except (ValueError, TypeError):
            return 0

    def download_and_set_image(self, product, image_url):
        """Завантажує та встановлює зображення для товару"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Генеруємо ім'я файлу
            filename = f'product_{product.id}_{int(time.time())}.jpg'
            
            # Зберігаємо зображення
            image_file = ContentFile(response.content)
            product.image.save(filename, image_file, save=True)
            
            self.stdout.write(f'  ✓ Завантажено зображення для {product.name}')
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠ Не вдалося завантажити зображення: {str(e)}')) 