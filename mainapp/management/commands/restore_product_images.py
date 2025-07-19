import pandas as pd
import requests
import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import transaction
from mainapp.models import Product
from urllib.parse import urlparse

class Command(BaseCommand):
    help = 'Підключає фотографії товарів за посиланнями з Excel таблиці'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='export-products-10-07-25_11-38-56.xlsx',
            help='Шлях до Excel файлу з даними',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати результат без збереження',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        dry_run = options['dry_run']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Файл {file_path} не знайдено"))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING("РЕЖИМ ПОПЕРЕДНЬОГО ПЕРЕГЛЯДУ - фото не будуть завантажені"))
        
        self.stdout.write(f"📊 Читання Excel файлу: {file_path}")
        
        try:
            df = pd.read_excel(file_path)
            self.stdout.write(f"Прочитано {len(df)} рядків")
            
            # Перевіряємо необхідні колонки
            required_columns = ['Назва_позиції', 'Посилання_зображення']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.stdout.write(self.style.ERROR(f"Відсутні колонки: {missing_columns}"))
                return
            
            processed_count = 0
            updated_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    product_name = self.clean_name(str(row['Назва_позиції']))
                    image_urls = str(row['Посилання_зображення'])
                    
                    if pd.isna(image_urls) or image_urls.lower() in ['nan', '']:
                        continue
                    
                    # Шукаємо товар за назвою
                    matching_products = Product.objects.filter(name__icontains=product_name[:30])
                    
                    if not matching_products.exists():
                        # Пробуємо знайти за частиною назви
                        words = product_name.split()[:3]  # Перші 3 слова
                        for word in words:
                            if len(word) > 4:  # Тільки довгі слова
                                matching_products = Product.objects.filter(name__icontains=word)
                                if matching_products.exists():
                                    break
                    
                    if matching_products.exists():
                        product = matching_products.first()
                        
                        # Отримуємо перше посилання на зображення
                        first_image_url = image_urls.split(',')[0].strip()
                        
                        if first_image_url.startswith('http'):
                            if dry_run:
                                self.stdout.write(f"ПІДКЛЮЧИТИ: {product.name} → {first_image_url}")
                            else:
                                success = self.download_and_attach_image(product, first_image_url)
                                if success:
                                    updated_count += 1
                                    self.stdout.write(f"✅ Підключено фото: {product.name}")
                                else:
                                    error_count += 1
                                    self.stdout.write(f"❌ Помилка фото: {product.name}")
                    
                    processed_count += 1
                    
                except Exception as e:
                    error_count += 1
                    self.stdout.write(f"❌ Помилка в рядку {index + 1}: {str(e)}")
                    continue
            
            # Підсумки
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"\nПОПЕРЕДНІЙ ПЕРЕГЛЯД ЗАВЕРШЕНО\n"
                        f"Оброблено рядків: {processed_count}\n"
                        f"Буде підключено фото: {updated_count}\n"
                        f"Помилки: {error_count}\n"
                        f"Для завантаження фото запустіть без --dry-run"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nПІДКЛЮЧЕННЯ ФОТО ЗАВЕРШЕНО\n"
                        f"Оброблено рядків: {processed_count}\n"
                        f"Підключено фото: {updated_count}\n"
                        f"Помилки: {error_count}"
                    )
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Помилка читання файлу: {str(e)}"))

    def clean_name(self, name):
        """Очищає назву для пошуку"""
        # Простий переклад основних термінів для пошуку
        translations = {
            'Гибридный': 'Гібридний',
            'инвертор': 'інвертор',
            'Солнечная': 'Сонячна',
            'панель': 'панель',
            'Аккумуляторная': 'Акумуляторна',
            'батарея': 'батарея',
            'Комплект': 'Комплект',
        }
        
        result = str(name)
        for rus, ukr in translations.items():
            result = result.replace(rus, ukr)
        
        return result.strip()

    def download_and_attach_image(self, product, image_url):
        """Завантажує та прикріплює зображення до товару"""
        try:
            # Завантажуємо зображення
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Отримуємо ім'я файлу з URL
            parsed_url = urlparse(image_url)
            filename = os.path.basename(parsed_url.path)
            
            if not filename or '.' not in filename:
                filename = f"product_{product.id}.jpg"
            
            # Зберігаємо файл
            with transaction.atomic():
                product.image.save(
                    filename,
                    ContentFile(response.content),
                    save=True
                )
            
            return True
            
        except Exception as e:
            self.stdout.write(f"Помилка завантаження {image_url}: {str(e)}")
            return False 