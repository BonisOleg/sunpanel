import pandas as pd
import requests
import re
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.db import transaction
from bs4 import BeautifulSoup
from mainapp.models import Product, Category, Brand
import os
from urllib.parse import urlparse
import time

class Command(BaseCommand):
    help = 'Чистий імпорт товарів з українським контентом без HTML тегів та російських слів'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            required=True,
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
            raise CommandError(f'Файл {file_path} не існує')

        self.stdout.write(self.style.SUCCESS(f'{"[DRY RUN] " if dry_run else ""}Початок чистого імпорту з файлу: {file_path}'))

        try:
            # Читаємо Excel файл
            df = pd.read_excel(file_path)
            self.stdout.write(f'Прочитано {len(df)} рядків')
            
            # Визначаємо українські колонки
            column_mapping = self.find_ukrainian_columns(df)
            
            self.stdout.write(f"\nВизначені українські колонки:")
            for key, col in column_mapping.items():
                self.stdout.write(f"  {key}: {col}")
            
            if not column_mapping['name']:
                raise CommandError('Не вдалося знайти колонку з українською назвою товару')
            
            if dry_run:
                self.show_preview(df, column_mapping)
                return
            
            # Імпорт товарів
            self.import_products(df, column_mapping, update_existing)
            
        except Exception as e:
            raise CommandError(f'Помилка під час імпорту: {str(e)}')

    def find_ukrainian_columns(self, df):
        """Знаходить колонки з українським контентом"""
        columns = df.columns.tolist()
        
        # Пошук колонок
        name_columns = [col for col in columns if any(word in col.lower() for word in 
                       ['назва_укр', 'назва', 'name_ukr', 'товар_укр', 'продукт_укр'])]
        
        description_columns = [col for col in columns if any(word in col.lower() for word in 
                              ['опис_укр', 'опис', 'описание_укр', 'description_ukr'])]
        
        price_columns = [col for col in columns if any(word in col.lower() for word in 
                        ['ціна', 'price', 'вартість', 'стоимость'])]
        
        category_columns = [col for col in columns if any(word in col.lower() for word in 
                           ['категорія', 'група', 'category', 'назва_групи'])]
        
        brand_columns = [col for col in columns if any(word in col.lower() for word in 
                        ['виробник', 'бренд', 'brand', 'виготовлювач'])]
        
        code_columns = [col for col in columns if any(word in col.lower() for word in 
                       ['код', 'code', 'артикул', 'id'])]
        
        image_columns = [col for col in columns if any(word in col.lower() for word in 
                        ['зображення', 'фото', 'image', 'картинка'])]
        
        return {
            'name': name_columns[0] if name_columns else None,
            'description': description_columns[0] if description_columns else None,
            'price': price_columns[0] if price_columns else None,
            'category': category_columns[0] if category_columns else None,
            'brand': brand_columns[0] if brand_columns else None,
            'code': code_columns[0] if code_columns else None,
            'image_url': image_columns[0] if image_columns else None,
        }

    def clean_text(self, text):
        """Очищає текст від HTML тегів та російських слів"""
        if not text or pd.isna(text):
            return ""
        
        text = str(text).strip()
        
        # Видаляємо HTML теги
        soup = BeautifulSoup(text, 'html.parser')
        clean_text = soup.get_text()
        
        # Заміняємо HTML entities
        clean_text = clean_text.replace('&ndash;', '–')
        clean_text = clean_text.replace('&mdash;', '—')
        clean_text = clean_text.replace('&nbsp;', ' ')
        clean_text = clean_text.replace('&deg;', '°')
        clean_text = clean_text.replace('&amp;', '&')
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        clean_text = clean_text.replace('&quot;', '"')
        
        # Російські слова які треба видалити
        russian_words = [
            'гибридный', 'инвертор', 'технологией', 'современное', 'технологическое', 
            'решение', 'предназначенное', 'усовершенствования', 'обеспечивающее',
            'производительность', 'мощностью', 'работает', 'имеет', 'функцию',
            'отслеживания', 'точки', 'максимальной', 'мощности', 'обеспечивает',
            'оптимальный', 'сбор', 'энергии', 'солнечных', 'панелей', 'конструкция',
            'позволяет', 'использовать', 'низковольтные', 'аккумуляторы', 'изоляцию',
            'трансформатора', 'повышения', 'безопасности', 'эффективности', 
            'особенностей', 'способность', 'поддерживать', 'выход', 'номинальной',
            'любой', 'одной', 'фазе', 'ключевой', 'особенностью', 'является',
            'совместимость', 'имеющимися', 'системами', 'подключать', 'сети',
            'переменного', 'тока', 'делает', 'идеальным', 'выбором', 'модернизации',
            'старых', 'установок', 'меняя', 'новые', 'более', 'эффективные',
            'необходимости', 'полного', 'капитального', 'ремонта', 'кроме', 'того',
            'поддерживает', 'параллельное', 'подключение', 'единиц', 'работы',
            'автономной', 'масштабируемость', 'решающее', 'значение',
            'расширения', 'возможностей', 'больших', 'установках', 'постепенного',
            'увеличения', 'устройство', 'может', 'параллельно',
            'управлять', 'несколькими', 'батареями', 'предлагая', 'надежные', 
            'решения', 'хранения', 'управления', 'солнечной', 'системе'
        ]
        
        # Розбиваємо на речення
        sentences = re.split(r'[.!?]+', clean_text)
        ukrainian_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Перевіряємо чи містить речення російські слова
            sentence_lower = sentence.lower()
            has_russian_words = any(word in sentence_lower for word in russian_words)
            
            # Підраховуємо українські та російські символи
            ukrainian_chars = len(re.findall(r'[абвгґдежзиіїйклмнопрстуфхцчшщьюя]', sentence_lower))
            russian_specific_chars = len(re.findall(r'[ёъыэ]', sentence_lower))
            
            # Якщо речення містить російські слова або російські символи - пропускаємо
            if has_russian_words or russian_specific_chars > 0:
                continue
                
            # Якщо речення містить українські символи
            if ukrainian_chars > 3:  # Мінімум 3 українських символи
                # Залишаємо українські символи, латинські (для моделей), цифри та пунктуацію
                cleaned_sentence = re.sub(
                    r'[^абвгґдежзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯa-zA-Z0-9\s.,;:!?\-—–()°%№/]', 
                    '', 
                    sentence
                )
                
                # Очищаємо зайві пробіли
                cleaned_sentence = re.sub(r'\s+', ' ', cleaned_sentence).strip()
                
                if cleaned_sentence and len(cleaned_sentence) > 10:  # Мінімум 10 символів
                    ukrainian_sentences.append(cleaned_sentence)
        
        # Об'єднуємо речення
        result = '. '.join(ukrainian_sentences)
        if result and not result.endswith('.'):
            result += '.'
            
        # Очищаємо зайві пробіли та переноси рядків
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result

    def clean_name(self, name):
        """Очищає назву товару від HTML тегів та російських слів"""
        if not name or pd.isna(name):
            return ""
        
        name = str(name).strip()
        
        # Видаляємо HTML теги
        soup = BeautifulSoup(name, 'html.parser')
        clean_name = soup.get_text()
        
        # Заміняємо HTML entities
        clean_name = clean_name.replace('&ndash;', '–')
        clean_name = clean_name.replace('&mdash;', '—')
        clean_name = clean_name.replace('&nbsp;', ' ')
        clean_name = clean_name.replace('&deg;', '°')
        clean_name = clean_name.replace('&amp;', '&')
        
        # Видаляємо російські символи
        clean_name = re.sub(r'[ёъыэ]', '', clean_name)
        
        # Залишаємо тільки українські символи, латинські, цифри та базову пунктуацію
        clean_name = re.sub(
            r'[^абвгґдежзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯa-zA-Z0-9\s.,\-—–()°%№/]',
            '',
            clean_name
        )
        
        # Очищаємо зайві пробіли
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()
        
        return clean_name

    def parse_price(self, price_value):
        """Парсить ціну з різних форматів"""
        if not price_value or pd.isna(price_value):
            return 0
        
        # Конвертуємо в рядок та очищаємо від пробілів
        price_str = str(price_value).strip()
        
        # Видаляємо валюти та інші символи
        price_str = re.sub(r'[₴$€грн\s,]', '', price_str)
        
        try:
            return float(price_str)
        except ValueError:
            return 0

    def get_or_create_category(self, category_name):
        """Створює або знаходить категорію"""
        if not category_name:
            category_name = "Без категорії"
        
        category_name = self.clean_name(category_name)
        
        if not category_name:
            category_name = "Без категорії"
        
        # Спочатку пробуємо знайти за назвою
        try:
            category = Category.objects.get(name=category_name)
            return category
        except Category.DoesNotExist:
            # Якщо не знайшли, створюємо нову
            try:
                category = Category.objects.create(
                    name=category_name
                )
                return category
            except Exception:
                # Якщо все ж таки є конфлікт, повертаємо першу знайдену
                return Category.objects.filter(name__icontains=category_name.split()[0]).first() or Category.objects.first()

    def get_or_create_brand(self, brand_name):
        """Створює або знаходить виробника"""
        if not brand_name:
            brand_name = "Без бренду"
        
        brand_name = self.clean_name(brand_name)
        
        if not brand_name:
            brand_name = "Без бренду"
        
        # Спочатку пробуємо знайти за назвою
        try:
            brand = Brand.objects.get(name=brand_name)
            return brand
        except Brand.DoesNotExist:
            # Якщо не знайшли, створюємо новий
            try:
                brand = Brand.objects.create(
                    name=brand_name
                )
                return brand
            except Exception:
                # Якщо все ж таки є конфлікт, повертаємо перший знайдений
                return Brand.objects.filter(name__icontains=brand_name.split()[0]).first() or Brand.objects.first()

    def show_preview(self, df, column_mapping):
        """Показує попередній перегляд товарів"""
        self.stdout.write("\nПопередній перегляд перших 5 товарів:")
        
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            
            name = self.clean_name(row.get(column_mapping['name'], ''))
            description = self.clean_text(row.get(column_mapping['description'], ''))
            price = self.parse_price(row.get(column_mapping['price'], 0))
            
            if name:
                self.stdout.write(f"\n--- Товар {i+1} ---")
                self.stdout.write(f"Назва: {name}")
                self.stdout.write(f"Ціна: ₴{price}")
                if description:
                    self.stdout.write(f"Опис: {description[:100]}...")
        
        self.stdout.write(self.style.WARNING('\nЦе попередній перегляд. Для імпорту запустіть без --dry-run'))

    def import_products(self, df, column_mapping, update_existing):
        """Імпортує товари в базу даних"""
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        total_rows = len(df)
        
        for index, row in df.iterrows():
            try:
                # Очищаємо дані
                name = self.clean_name(row.get(column_mapping['name'], ''))
                description = self.clean_text(row.get(column_mapping['description'], ''))
                price = self.parse_price(row.get(column_mapping['price'], 0))
                
                # Пропускаємо товари без назви
                if not name or len(name) < 3:
                    skipped_count += 1
                    continue
                
                # Перевіряємо чи назва українська
                ukrainian_chars = len(re.findall(r'[абвгґдежзиіїйклмнопрстуфхцчшщьюя]', name.lower()))
                if ukrainian_chars < 3:  # Мінімум 3 українських символи
                    skipped_count += 1
                    continue
                
                # Створюємо або знаходимо категорію та бренд
                category = self.get_or_create_category(row.get(column_mapping['category'], ''))
                brand = self.get_or_create_brand(row.get(column_mapping['brand'], ''))
                
                # Код товару
                product_code = row.get(column_mapping['code'], '')
                
                with transaction.atomic():
                    # Перевіряємо чи існує товар за назвою
                    existing_product = Product.objects.filter(name=name).first()
                    
                    if existing_product:
                        if update_existing:
                            existing_product.name = name
                            existing_product.description = description
                            existing_product.price = price
                            existing_product.category = category
                            existing_product.brand = brand
                            existing_product.save()
                            updated_count += 1
                            self.stdout.write(f"Оновлено: {name}")
                        else:
                            skipped_count += 1
                    else:
                        # Створюємо новий товар
                        product = Product.objects.create(
                            name=name,
                            description=description,
                            price=price,
                            category=category,
                            brand=brand,
                            model=str(product_code) if product_code else '',
                            in_stock=True
                        )
                        created_count += 1
                        self.stdout.write(f"Створено: {name}")
                
                # Показуємо прогрес
                if (index + 1) % 50 == 0:
                    self.stdout.write(f"Оброблено {index + 1}/{total_rows} рядків...")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Помилка при обробці рядка {index + 1}: {str(e)}")
                )
                skipped_count += 1
                continue
        
        # Підсумки
        self.stdout.write(
            self.style.SUCCESS(
                f"\nІмпорт завершено!\n"
                f"Створено: {created_count}\n"
                f"Оновлено: {updated_count}\n"
                f"Пропущено: {skipped_count}\n"
                f"Всього оброблено: {created_count + updated_count + skipped_count}"
            )
        ) 