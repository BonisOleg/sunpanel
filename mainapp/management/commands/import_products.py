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
    help = 'Імпорт товарів з Excel файлу'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='export-products-10-07-25_11-38-56.xlsx',
            help='Шлях до Excel файлу'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        if not os.path.exists(file_path):
            raise CommandError(f'Файл {file_path} не існує')

        self.stdout.write(self.style.SUCCESS(f'Починаю імпорт з файлу: {file_path}'))

        try:
            # Читаємо обидві вкладки
            products_df = pd.read_excel(file_path, sheet_name='Export Products Sheet')
            groups_df = pd.read_excel(file_path, sheet_name='Export Groups Sheet')
            
            self.stdout.write(f'Знайдено {len(products_df)} товарів та {len(groups_df)} груп')
            
            # Пропускаємо товари з номерами 140234183 та 140232669
            excluded_codes = [140234183, 140232669]
            
            # Відслідковуємо унікальні категорії та виробників
            unique_categories = set()
            unique_brands = set()
            
            created_count = 0
            skipped_count = 0
            
            for index, row in products_df.iterrows():
                try:
                    product_code = row.get('Код_товару')
                    
                    # Пропускаємо виключені товари
                    if product_code in excluded_codes:
                        self.stdout.write(self.style.WARNING(f'Пропускаю товар з кодом: {product_code}'))
                        skipped_count += 1
                        continue
                    
                    # Отримуємо основні дані з перевіркою на NaN
                    name = str(row.get('Назва_позиції_укр', '')).strip() if pd.notna(row.get('Назва_позиції_укр')) else ''
                    description = str(row.get('Опис_укр', '')).strip() if pd.notna(row.get('Опис_укр')) else ''
                    price = row.get('Ціна', 0)
                    category = str(row.get('Назва_групи', '')).strip() if pd.notna(row.get('Назва_групи')) else ''
                    brand = str(row.get('Виробник', '')).strip() if pd.notna(row.get('Виробник')) else ''
                    country = str(row.get('Країна_виробник', '')).strip() if pd.notna(row.get('Країна_виробник')) else ''
                    image_links = row.get('Посилання_зображення', '')
                    
                    # Перевіряємо обов'язкові поля
                    if not name or not description:
                        self.stdout.write(self.style.WARNING(f'Пропускаю товар без назви або опису: {product_code}'))
                        skipped_count += 1
                        continue
                    
                    # Створюємо товар
                    product = Product(
                        name=name,
                        description=description,
                        price=price if pd.notna(price) else 0,
                        category=category,
                        brand=brand,
                        model='',  # В Excel немає окремого поля для моделі
                        country=country,
                        in_stock=True,
                        featured=False
                    )
                    
                    # Обробляємо зображення
                    if pd.notna(image_links) and str(image_links).strip():
                        image_url = self.get_first_image_url(image_links)
                        if image_url:
                            image_result = self.download_image(image_url, product_code)
                            if image_result:
                                filename, image_file = image_result
                                product.image.save(filename, image_file, save=False)
                    
                    product.save()
                    
                    # Додаємо до унікальних категорій та брендів
                    if category:
                        unique_categories.add(category)
                    if brand:
                        unique_brands.add(brand)
                    
                    created_count += 1
                    self.stdout.write(f'Створено товар: {name}')
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Помилка при створенні товару {product_code}: {str(e)}'))
                    skipped_count += 1
                    continue
            
            # Виводимо статистику
            self.stdout.write(self.style.SUCCESS(f'\nІмпорт завершено!'))
            self.stdout.write(f'Створено товарів: {created_count}')
            self.stdout.write(f'Пропущено товарів: {skipped_count}')
            self.stdout.write(f'Унікальних категорій: {len(unique_categories)}')
            self.stdout.write(f'Унікальних брендів: {len(unique_brands)}')
            
            self.stdout.write('\nКатегорії:')
            for category in sorted(unique_categories):
                self.stdout.write(f'  - {category}')
                
            self.stdout.write('\nБренди:')
            for brand in sorted(unique_brands):
                self.stdout.write(f'  - {brand}')

        except Exception as e:
            raise CommandError(f'Помилка при читанні файлу: {str(e)}')

    def get_first_image_url(self, image_links):
        """Отримуємо перше зображення з списку посилань"""
        if pd.isna(image_links) or not image_links.strip():
            return None
            
        # Розділяємо посилання по комі
        links = [link.strip() for link in str(image_links).split(',')]
        
        for link in links:
            if link and link.startswith('http'):
                return link
        
        return None

    def download_image(self, image_url, product_code):
        """Завантажуємо зображення з URL"""
        try:
            self.stdout.write(f'Завантажую зображення: {image_url}')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Отримуємо розширення файлу
            parsed_url = urlparse(image_url)
            file_extension = os.path.splitext(parsed_url.path)[1]
            if not file_extension:
                file_extension = '.jpg'
            
            # Створюємо ім'я файлу
            filename = f'product_{product_code}{file_extension}'
            
            # Створюємо ContentFile
            image_file = ContentFile(response.content)
            
            return (filename, image_file)
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Не вдалося завантажити зображення {image_url}: {str(e)}'))
            return None 