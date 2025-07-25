"""
Команда для повного імпорту каталогу з Excel таблиць
Імпортує всі 42 товари тільки з українським контентом
"""
import pandas as pd
import requests
import re
import os
import time
import hashlib
from urllib.parse import urlparse
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.text import slugify
from mainapp.models import Product, Category, Brand, ProductImage
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Повний імпорт каталогу з Excel таблиць (42 товари)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Видалити всі існуючі товари перед імпортом'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Режим попереднього перегляду'
        )

    def handle(self, *args, **options):
        self.clear_existing = options['clear_existing']
        self.dry_run = options['dry_run']
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING("🔍 РЕЖИМ ПОПЕРЕДНЬОГО ПЕРЕГЛЯДУ"))
        
        self.stdout.write("🚀 ПОВНИЙ ІМПОРТ КАТАЛОГУ")
        self.stdout.write('='*60)
        
        # Ініціалізуємо статистику
        self.stats = {
            'products_created': 0,
            'categories_created': 0,
            'brands_created': 0,
            'images_downloaded': 0,
            'products_skipped': 0,
            'errors': 0
        }
        
        try:
            # Перевіряємо файли
            if not os.path.exists('export-products-10-07-25_11-38-56.xlsx'):
                raise CommandError('Файл export-products-10-07-25_11-38-56.xlsx не знайдений')
            
            if not os.path.exists('second.xlsx'):
                raise CommandError('Файл second.xlsx не знайдений')
            
            # Очищуємо існуючі товари якщо потрібно
            if self.clear_existing:
                self.clear_existing_products()
            
            # Створюємо основні категорії
            self.create_main_categories()
            
            # Імпортуємо товари
            self.import_products()
            
            # Показуємо фінальну статистику
            self.show_final_stats()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Критична помилка: {str(e)}"))
            raise

    def clear_existing_products(self):
        """Видаляє всі існуючі товари"""
        if self.dry_run:
            self.stdout.write("   [DRY RUN] Видалив би всі товари")
            return
            
        count = Product.objects.count()
        if count > 0:
            Product.objects.all().delete()
            self.stdout.write(f"🗑️ Видалено {count} існуючих товарів")

    def create_main_categories(self):
        """Створює 4 основні категорії"""
        categories_data = [
            {
                'name': 'Інвертори',
                'description': 'Гібридні та сонячні інвертори для систем резервного живлення'
            },
            {
                'name': 'Акумуляторні батареї', 
                'description': 'LiFePO4 та інші типи акумуляторів для систем накопичення енергії'
            },
            {
                'name': 'Сонячні панелі',
                'description': 'Монокристалічні та полікристалічні сонячні панелі'
            },
            {
                'name': 'Комплекти резервного живлення',
                'description': 'Готові рішення для автономного електропостачання'
            }
        ]
        
        for cat_data in categories_data:
            if self.dry_run:
                self.stdout.write(f"   [DRY RUN] Створив би категорію: {cat_data['name']}")
                continue
                
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            
            if created:
                self.stats['categories_created'] += 1
                self.stdout.write(f"✅ Створено категорію: {category.name}")

    def get_category_mapping(self):
        """Мапінг груп товарів на основні категорії"""
        return {
            'Инверторы Must': 'Інвертори',
            'Инверторы Deye': 'Інвертори', 
            'Аккумуляторы для ИБП MUST': 'Акумуляторні батареї',
            'Аккумуляторы для ИБП Deye': 'Акумуляторні батареї',
            'Аккумуляторы для ИБП lvtopsun': 'Акумуляторні батареї',
            'Солнечные панели Longi Solar': 'Сонячні панелі',
            'Солнечные панели Risen Energy': 'Сонячні панелі',
            'Автономні та гібридні комплекти резервного живлення': 'Комплекти резервного живлення'
        }

    def contains_russian(self, text):
        """Перевіряє чи містить текст російські символи"""
        if pd.isna(text):
            return False
        
        russian_chars = ['ы', 'э', 'ъ', 'ё']
        russian_words = [
            'мощность', 'производитель', 'гарантия', 'номинальная', 
            'допустимая', 'пиковая', 'рабочая', 'величина', 'срок', 'службы'
        ]
        
        text_lower = str(text).lower()
        
        # Перевіряємо російські літери
        for char in russian_chars:
            if char in text_lower:
                return True
        
        # Перевіряємо російські слова
        for word in russian_words:
            if word in text_lower:
                return True
                
        return False

    def clean_html_description(self, description):
        """Очищає опис від HTML тегів, але зберігає структуру"""
        if pd.isna(description):
            return ""
        
        # Замінюємо <br /> на нові рядки
        description = str(description).replace('<br />', '\n').replace('<br/>', '\n').replace('<br>', '\n')
        
        # Видаляємо HTML теги
        soup = BeautifulSoup(description, 'html.parser')
        clean_text = soup.get_text()
        
        # Очищуємо зайві пробіли та порожні рядки
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        
        return '\n'.join(lines)

    def create_or_get_brand(self, brand_name):
        """Створює або отримує бренд"""
        if pd.isna(brand_name):
            brand_name = "Невідомий"
        
        brand_name = str(brand_name).strip()
        
        if self.dry_run:
            return None
            
        brand, created = Brand.objects.get_or_create(
            name=brand_name,
            defaults={
                'description': f'Продукція бренду {brand_name}',
                'is_active': True
            }
        )
        
        if created:
            self.stats['brands_created'] += 1
            self.stdout.write(f"✅ Створено бренд: {brand.name}")
        
        return brand

    def download_image(self, url, product_name):
        """Завантажує зображення з URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url.strip(), headers=headers, timeout=30)
            response.raise_for_status()
            
            # Генеруємо унікальне ім'я файлу
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            safe_name = re.sub(r'[^\w\-_.]', '_', product_name)[:30]
            
            # Визначаємо розширення
            parsed_url = urlparse(url)
            path = parsed_url.path.lower()
            if path.endswith('.jpg') or path.endswith('.jpeg'):
                ext = '.jpg'
            elif path.endswith('.png'):
                ext = '.png'
            else:
                ext = '.jpg'  # За замовчуванням
            
            filename = f"{safe_name}_{url_hash}{ext}"
            
            self.stats['images_downloaded'] += 1
            return ContentFile(response.content, name=filename)
            
        except Exception as e:
            self.stdout.write(f"⚠️ Помилка завантаження {url}: {str(e)}")
            return None

    def get_characteristics(self, row):
        """Витягує характеристики товару (тільки українські)"""
        characteristics = {}
        
        for i in range(15):  # 0-14 характеристики
            name_col = f'Назва_Характеристики{"."+str(i) if i > 0 else ""}'
            value_col = f'Значення_Характеристики{"."+str(i) if i > 0 else ""}'
            unit_col = f'Одиниця_виміру_Характеристики{"."+str(i) if i > 0 else ""}'
            
            if name_col in row.index and value_col in row.index:
                char_name = row[name_col]
                char_value = row[value_col]
                char_unit = row.get(unit_col, '')
                
                if (pd.notna(char_name) and pd.notna(char_value) and 
                    not self.contains_russian(char_name) and 
                    not self.contains_russian(char_value)):
                    
                    value_str = str(char_value)
                    if pd.notna(char_unit) and not self.contains_russian(char_unit):
                        value_str += f" {char_unit}"
                    
                    characteristics[str(char_name)] = value_str
        
        return characteristics

    def import_products(self):
        """Імпортує всі товари з Excel файлу"""
        self.stdout.write("\n📦 Читання товарів з Excel...")
        
        df = pd.read_excel('export-products-10-07-25_11-38-56.xlsx')
        category_mapping = self.get_category_mapping()
        
        self.stdout.write(f"📋 Знайдено {len(df)} товарів у файлі")
        
        for index, row in df.iterrows():
            try:
                # Перевіряємо українську назву
                ukrainian_name = row.get('Назва_позиції_укр')
                if pd.isna(ukrainian_name) or self.contains_russian(ukrainian_name):
                    self.stdout.write(f"⏭️ Пропускаємо товар {index+1}: немає української назви")
                    self.stats['products_skipped'] += 1
                    continue
                
                # Перевіряємо групу товару
                product_group = row.get('Назва_групи')
                if pd.isna(product_group) or product_group not in category_mapping:
                    self.stdout.write(f"⏭️ Пропускаємо товар {index+1}: невідома група '{product_group}'")
                    self.stats['products_skipped'] += 1
                    continue
                
                # Отримуємо дані товару
                category_name = category_mapping[product_group]
                ukrainian_description = self.clean_html_description(row.get('Опис_укр'))
                price = row.get('Ціна', 0)
                brand_name = row.get('Виробник')
                
                # Перевіряємо що опис українською
                if self.contains_russian(ukrainian_description):
                    ukrainian_description = ""
                
                if self.dry_run:
                    self.stdout.write(f"   [DRY RUN] Створив би товар: {ukrainian_name}")
                    continue
                
                # Отримуємо категорію та бренд
                category = Category.objects.get(name=category_name)
                brand = self.create_or_get_brand(brand_name)
                
                # Отримуємо характеристики
                characteristics = self.get_characteristics(row)
                
                # Формуємо повний опис з характеристиками
                full_description = ukrainian_description
                if characteristics:
                    full_description += "\n\nХарактеристики:\n"
                    for char_name, char_value in characteristics.items():
                        full_description += f"• {char_name}: {char_value}\n"
                
                # Створюємо товар
                product = Product.objects.create(
                    name=ukrainian_name,
                    description=full_description,
                    price=float(price) if pd.notna(price) else 0,
                    category=category,
                    brand=brand,
                    model=f"{brand_name} Model" if brand_name else "Standard",
                    in_stock=True,
                    featured=False
                )
                
                # Завантажуємо зображення
                images_urls = row.get('Посилання_зображення')
                if pd.notna(images_urls):
                    image_urls = [url.strip() for url in str(images_urls).split(',')]
                    
                    for img_index, img_url in enumerate(image_urls):
                        if img_url:
                            image_file = self.download_image(img_url, ukrainian_name)
                            if image_file:
                                if img_index == 0:
                                    # Перше зображення як головне
                                    product.image = image_file
                                    product.save()
                                else:
                                    # Додаткові зображення в галерею
                                    ProductImage.objects.create(
                                        product=product,
                                        image=image_file,
                                        alt_text=f"{ukrainian_name} - зображення {img_index + 1}",
                                        order=img_index
                                    )
                
                self.stats['products_created'] += 1
                self.stdout.write(f"✅ Створено товар: {ukrainian_name}")
                
                # Невелика затримка між запитами
                time.sleep(0.5)
                
            except Exception as e:
                self.stats['errors'] += 1
                self.stdout.write(f"❌ Помилка при створенні товару {index+1}: {str(e)}")

    def show_final_stats(self):
        """Показує фінальну статистику"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('🎉 ІМПОРТ ЗАВЕРШЕНО')
        self.stdout.write(f"✅ Створено товарів: {self.stats['products_created']}")
        self.stdout.write(f"📂 Створено категорій: {self.stats['categories_created']}")
        self.stdout.write(f"🏷️ Створено брендів: {self.stats['brands_created']}")
        self.stdout.write(f"🖼️ Завантажено зображень: {self.stats['images_downloaded']}")
        self.stdout.write(f"⏭️ Пропущено товарів: {self.stats['products_skipped']}")
        self.stdout.write(f"❌ Помилки: {self.stats['errors']}")
        
        # Показуємо статистику по категоріях
        if not self.dry_run:
            self.stdout.write('\n📈 Статистика по категоріях:')
            for category in Category.objects.all():
                count = Product.objects.filter(category=category).count()
                self.stdout.write(f"   📂 {category.name}: {count} товарів")
        
        self.stdout.write('='*60) 