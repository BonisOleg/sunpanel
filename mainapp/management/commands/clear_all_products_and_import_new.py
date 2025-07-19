import pandas as pd
import requests
import re
import os
from urllib.parse import urlparse, urljoin
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.text import slugify
from mainapp.models import Product, Category, Brand, ProductImage
import time
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Видаляє всі товари та імпортує нові з second.xlsx та export-products-10-07-25_11-38-56.xlsx ЛИШЕ УКРАЇНСЬКОЮ'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories-file',
            type=str,
            default='second.xlsx',
            help='Файл з категоріями (second.xlsx)'
        )
        parser.add_argument(
            '--products-file',
            type=str,
            default='export-products-10-07-25_11-38-56.xlsx',
            help='Файл з товарами (export-products-10-07-25_11-38-56.xlsx)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Тільки показати що буде зроблено, без збереження'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Детальний вивід - показати всі товари та причини їх пропуску'
        )

    def handle(self, *args, **options):
        categories_file = options['categories_file']
        products_file = options['products_file']
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        # Перевіряємо наявність файлів
        if not os.path.exists(categories_file):
            raise CommandError(f'Файл {categories_file} не існує')
        if not os.path.exists(products_file):
            raise CommandError(f'Файл {products_file} не існує')

        if dry_run:
            self.stdout.write(self.style.WARNING("РЕЖИМ ПОПЕРЕДНЬОГО ПЕРЕГЛЯДУ - зміни не будуть збережені"))

        # Крок 1: Видаляємо всі існуючі товари
        self.stdout.write("\n🗑️ Крок 1: Видалення всіх існуючих товарів...")
        self.clear_all_products(dry_run)

        # Крок 2: Читаємо категорії
        self.stdout.write("\n📂 Крок 2: Читання категорій...")
        categories_mapping = self.read_categories(categories_file)

        # Крок 3: Читаємо товари та імпортуємо
        self.stdout.write("\n📦 Крок 3: Імпорт товарів...")
        imported_count = self.import_products(products_file, categories_mapping, dry_run, verbose)

        # Підсумки
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\nПОПЕРЕДНІЙ ПЕРЕГЛЯД ЗАВЕРШЕНО\n"
                    f"Буде видалено товарів: {Product.objects.count()}\n"
                    f"Буде імпортовано товарів: {imported_count}\n"
                    f"Для застосування змін запустіть без --dry-run"
                )
            )
        else:
            final_count = Product.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nІМПОРТ ЗАВЕРШЕНО\n"
                    f"Імпортовано товарів: {final_count}\n"
                    f"Категорій: {Category.objects.count()}\n"
                    f"Брендів: {Brand.objects.count()}"
                )
            )

    def clear_all_products(self, dry_run):
        """Видаляє всі існуючі товари"""
        current_count = Product.objects.count()
        
        if current_count == 0:
            self.stdout.write("Товарів для видалення немає")
            return

        if dry_run:
            self.stdout.write(f"БУДЕ ВИДАЛЕНО: {current_count} товарів")
        else:
            with transaction.atomic():
                Product.objects.all().delete()
                self.stdout.write(f"Видалено {current_count} товарів")

    def read_categories(self, file_path):
        """Читає категорії з файлу second.xlsx"""
        try:
            df = pd.read_excel(file_path)
            self.stdout.write(f'Знайдено {len(df)} категорій у файлі')
            
            categories_mapping = {}
            
            for index, row in df.iterrows():
                ukrainian_name = str(row.get('Назва_групи_укр', '')).strip()
                
                if ukrainian_name and pd.notna(row.get('Назва_групи_укр')):
                    # Очищаємо від HTML тегів та зайвих символів
                    ukrainian_name = self.clean_text(ukrainian_name)
                    
                    if ukrainian_name and len(ukrainian_name) > 3:
                        categories_mapping[ukrainian_name] = ukrainian_name
                        self.stdout.write(f'  Категорія: {ukrainian_name}')
            
            self.stdout.write(f'Всього українських категорій: {len(categories_mapping)}')
            return categories_mapping
            
        except Exception as e:
            raise CommandError(f'Помилка при читанні файлу категорій: {str(e)}')

    def import_products(self, file_path, categories_mapping, dry_run, verbose):
        """Імпортує товари з файлу export-products-10-07-25_11-38-56.xlsx"""
        try:
            # Читаємо файл - спробуємо різні назви листів
            try:
                df = pd.read_excel(file_path, sheet_name='Export Products Sheet')
            except:
                try:
                    df = pd.read_excel(file_path, sheet_name=0)  # Перший лист
                except:
                    df = pd.read_excel(file_path)

            self.stdout.write(f'Знайдено {len(df)} товарів у файлі')
            
            if len(df) == 0:
                raise CommandError('Файл з товарами порожній')

            created_count = 0
            skipped_count = 0
            skip_reasons = {
                'no_ukrainian_name': 0,
                'short_name': 0,
                'not_ukrainian': 0,
                'no_description': 0,
                'other': 0
            }
            
            for index, row in df.iterrows():
                try:
                    # Отримуємо українську назву та опис
                    name_ukr = str(row.get('Назва_позиції_укр', '')).strip() if pd.notna(row.get('Назва_позиції_укр')) else ''
                    description_ukr = str(row.get('Опис_укр', '')).strip() if pd.notna(row.get('Опис_укр')) else ''
                    
                    # Якщо немає української назви, спробуємо російську і переведемо
                    if not name_ukr:
                        name_rus = str(row.get('Назва_позиції', '')).strip() if pd.notna(row.get('Назва_позиції')) else ''
                        if name_rus:
                            name_ukr = self.translate_to_ukrainian(name_rus)
                            self.stdout.write(f"Переклад: '{name_rus}' -> '{name_ukr}'")
                    
                    # Якщо все ще немає назви
                    if not name_ukr:
                        skip_reasons['no_ukrainian_name'] += 1
                        if verbose:
                            self.stdout.write("❌ ПРОПУЩЕНО: немає назви для перекладу")
                        skipped_count += 1
                        continue
                    
                    # Детальна діагностика для verbose режиму
                    if verbose:
                        self.stdout.write(f"\n--- Товар {index + 1} ---")
                        self.stdout.write(f"Назва укр: '{name_ukr[:100]}'")
                        self.stdout.write(f"Опис укр: '{description_ukr[:100]}'")
                    
                    # Перевіряємо довжину назви
                    if len(name_ukr) < 5:
                        skip_reasons['short_name'] += 1
                        if verbose:
                            self.stdout.write("❌ ПРОПУЩЕНО: назва занадто коротка")
                        skipped_count += 1
                        continue
                    
                    # Очищаємо назву та опис
                    name_clean = self.clean_and_fix_text(name_ukr)
                    
                    # Якщо немає українського опису, спробуємо російський
                    if not description_ukr:
                        description_rus = str(row.get('Опис', '')).strip() if pd.notna(row.get('Опис')) else ''
                        if description_rus:
                            description_ukr = self.translate_to_ukrainian(description_rus)
                    
                    description_clean = self.clean_description(description_ukr) if description_ukr else "Опис товару буде доданий пізніше."
                    
                    # Тепер приймаємо всі товари з українськими назвами
                    if not name_clean or len(name_clean) < 5:
                        skip_reasons['not_ukrainian'] += 1
                        if verbose:
                            self.stdout.write(f"❌ ПРОПУЩЕНО: не вдалося очистити назву")
                        skipped_count += 1
                        continue
                    
                    # Отримуємо інші дані
                    price = self.parse_price(row.get('Ціна', 0))
                    category_name = str(row.get('Назва_групи', '')).strip() if pd.notna(row.get('Назва_групи')) else ''
                    brand_name = str(row.get('Виробник', '')).strip() if pd.notna(row.get('Виробник')) else ''
                    country = str(row.get('Країна_виробник', '')).strip() if pd.notna(row.get('Країна_виробник')) else ''
                    model = str(row.get('Код_товару', '')).strip() if pd.notna(row.get('Код_товару')) else ''
                    
                    # Отримуємо посилання на зображення
                    image_links = str(row.get('Посилання_зображення', '')).strip() if pd.notna(row.get('Посилання_зображення')) else ''
                    
                    if verbose:
                        self.stdout.write(f"✅ ПІДХОДИТЬ: '{name_clean[:50]}...'")
                        self.stdout.write(f"   Ціна: {price}, Категорія: {category_name}, Бренд: {brand_name}")
                    
                    if dry_run:
                        self.stdout.write(f"БУДЕ СТВОРЕНО: {name_clean[:50]}...")
                        created_count += 1
                    else:
                        # Створюємо товар
                        product = self.create_product(
                            name_clean, 
                            description_clean, 
                            price, 
                            category_name, 
                            brand_name, 
                            model,
                            country,
                            image_links
                        )
                        
                        if product:
                            created_count += 1
                            self.stdout.write(f"Створено: {product.name}")
                        else:
                            skip_reasons['other'] += 1
                            skipped_count += 1
                    
                    # Показуємо прогрес
                    if (index + 1) % 10 == 0:
                        self.stdout.write(f"Оброблено {index + 1}/{len(df)} товарів...")
                        
                except Exception as e:
                    skip_reasons['other'] += 1
                    self.stdout.write(self.style.ERROR(f"Помилка при обробці товару {index + 1}: {str(e)}"))
                    skipped_count += 1
                    continue

            self.stdout.write(f"\nРезультат імпорту:")
            self.stdout.write(f"  Створено: {created_count}")
            self.stdout.write(f"  Пропущено: {skipped_count}")
            self.stdout.write(f"\nПричини пропуску:")
            self.stdout.write(f"  Немає української назви: {skip_reasons['no_ukrainian_name']}")
            self.stdout.write(f"  Назва занадто коротка: {skip_reasons['short_name']}")
            self.stdout.write(f"  Не українська мова: {skip_reasons['not_ukrainian']}")
            self.stdout.write(f"  Інші помилки: {skip_reasons['other']}")
            
            return created_count
            
        except Exception as e:
            raise CommandError(f'Помилка при імпорті товарів: {str(e)}')

    def create_product(self, name, description, price, category_name, brand_name, model, country, image_links):
        """Створює товар з усіма зв'язками"""
        try:
            # Створюємо або отримуємо категорію
            category = self.get_or_create_category(category_name)
            
            # Створюємо або отримуємо бренд
            brand = self.get_or_create_brand(brand_name, country)
            
            # Створюємо товар БЕЗ транзакції для зображень
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                category=category,
                brand=brand,
                model=model,
                country=country,
                in_stock=True
            )
            
            # Додаємо зображення ПІСЛЯ створення товару (без atomic)
            if image_links:
                try:
                    self.add_product_images(product, image_links)
                except Exception as e:
                    self.stdout.write(f"  Помилка завантаження зображень для {name}: {str(e)}")
            
            return product
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Помилка створення товару '{name}': {str(e)}"))
            return None

    def get_or_create_category(self, name):
        """Створює або отримує категорію"""
        if not name:
            name = "Загальне"
        
        name = self.clean_text(name)
        
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={'description': f'Категорія {name}'}
        )
        
        if created:
            self.stdout.write(f"Створено категорію: {name}")
        
        return category

    def get_or_create_brand(self, name, country=""):
        """Створює або отримує бренд"""
        if not name:
            name = "Загальний"
        
        name = self.clean_text(name)
        
        brand, created = Brand.objects.get_or_create(
            name=name,
            defaults={'description': f'Бренд {name}' + (f' з {country}' if country else '')}
        )
        
        if created:
            self.stdout.write(f"Створено бренд: {name}")
        
        return brand

    def add_product_images(self, product, image_links):
        """Додає зображення до товару з посилань"""
        if not image_links:
            return
        
        # Розділяємо посилання (можуть бути розділені комою, крапкою з комою або новим рядком)
        links = re.split(r'[,;\n]+', image_links)
        
        image_added = False
        for i, link in enumerate(links):
            link = link.strip()
            if not link:
                continue
                
            try:
                # Завантажуємо зображення
                response = requests.get(link, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    # Отримуємо назву файлу з URL
                    parsed_url = urlparse(link)
                    original_filename = os.path.basename(parsed_url.path)
                    
                    # Створюємо унікальну назву файлу
                    if original_filename and '.' in original_filename:
                        name_part, ext_part = original_filename.rsplit('.', 1)
                        filename = f"product_{product.id}_{i}_{name_part}.{ext_part}"
                    else:
                        filename = f"product_{product.id}_{i}.jpg"
                    
                    # Створюємо файл з правильною назвою
                    content = ContentFile(response.content, name=filename)
                    
                    if i == 0 and not image_added:
                        # Перше зображення як головне
                        product.image.save(filename, content, save=True)
                        image_added = True
                        self.stdout.write(f"  Додано головне зображення: {filename}")
                    else:
                        # Додаткові зображення
                        ProductImage.objects.create(
                            product=product,
                            image=content,
                            alt_text=f"{product.name} - зображення {i+1}",
                            order=i
                        )
                        self.stdout.write(f"  Додано додаткове зображення: {filename}")
                    
                    time.sleep(0.3)  # Зменшена затримка між запитами
                    
                else:
                    self.stdout.write(f"  Помилка завантаження {link}: HTTP {response.status_code}")
                    
            except Exception as e:
                self.stdout.write(f"  Помилка завантаження зображення {link}: {str(e)}")
                continue

    def clean_text(self, text):
        """Очищає текст від HTML тегів та зайвих символів"""
        if not text:
            return ""
        
        # Видаляємо HTML теги
        text = BeautifulSoup(str(text), 'html.parser').get_text()
        
        # Видаляємо зайві пробіли
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def clean_description(self, text):
        """Очищає опис за логікою метарозмітки без самої розмітки"""
        if not text:
            return ""
        
        # Очищаємо від HTML
        text = self.clean_text(text)
        
        # Перекладаємо російські слова
        text = self.translate_to_ukrainian(text)
        
        # Застосовуємо орфографічні виправлення
        text = self.clean_and_fix_text(text)
        
        # Структуруємо опис за логікою метарозмітки
        # Розбиваємо на речення та абзаци
        sentences = []
        
        # Спочатку розбиваємо по абзацах
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Якщо це список характеристик (містить кілька двокрапок)
            if paragraph.count(':') >= 2:
                # Розбиваємо на окремі характеристики
                parts = re.split(r'[;,]\s*(?=[А-ЯІЇЄҐ])', paragraph)
                for part in parts:
                    part = part.strip()
                    if ':' in part:
                        key, value = part.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value:
                            sentences.append(f"{key}: {value}")
                    elif part:
                        sentences.append(part)
            
            # Якщо це характеристика (одна двокрапка)
            elif ':' in paragraph:
                parts = paragraph.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    sentences.append(f"{key}: {value}")
                else:
                    sentences.append(paragraph)
            
            # Звичайний текст
            else:
                # Розбиваємо на речення
                sent_parts = re.split(r'[.!?]+\s+', paragraph)
                for sent in sent_parts:
                    sent = sent.strip()
                    if sent and len(sent) > 3:
                        # Додаємо крапку в кінці, якщо немає
                        if not sent.endswith(('.', '!', '?', ':')):
                            sent += '.'
                        sentences.append(sent)
        
        # Об'єднуємо речення
        result = '. '.join(sentences)
        
        # Фінальні виправлення
        result = re.sub(r'\.+', '.', result)  # Видаляємо подвійні крапки
        result = re.sub(r'\s*\.\s*\.', '.', result)  # Виправляємо ". ."
        result = re.sub(r'\s+', ' ', result)  # Зайві пробіли
        
        # Обрізаємо зайві крапки в кінці
        result = result.rstrip('.').strip()
        
        return result

    def is_ukrainian_text_soft(self, text):
        """М'якша перевірка чи текст українською мовою"""
        if not text:
            return False
        
        # Перевіряємо наявність українських символів
        ukrainian_chars = len(re.findall(r'[абвгґдежзиіїйклмнопрстуфхцчшщьюя]', text.lower()))
        russian_specific = len(re.findall(r'[ыъэё]', text.lower()))
        
        # Якщо є специфічно російські символи - відкидаємо
        if russian_specific > 0:
            return False
        
        # Якщо є українські символи - приймаємо
        return ukrainian_chars >= 3

    def get_text_language_info(self, text):
        """Повертає інформацію про мову тексту для діагностики"""
        if not text:
            return "порожній текст"
        
        ukrainian_chars = len(re.findall(r'[абвгґдежзиіїйклмнопрстуфхцчшщьюя]', text.lower()))
        russian_specific = len(re.findall(r'[ыъэё]', text.lower()))
        latin_chars = len(re.findall(r'[a-z]', text.lower()))
        
        return f"укр:{ukrainian_chars}, рос:{russian_specific}, лат:{latin_chars}"

    def parse_price(self, price_value):
        """Парсить ціну з різних форматів"""
        if pd.isna(price_value):
            return 0.0
        
        if isinstance(price_value, (int, float)):
            return float(price_value)
        
        # Видаляємо все крім цифр та крапки
        price_str = re.sub(r'[^\d.,]', '', str(price_value))
        price_str = price_str.replace(',', '.')
        
        try:
            return float(price_str)
        except:
            return 0.0 

    def translate_to_ukrainian(self, text):
        """Перекладає російський текст українською"""
        if not text:
            return ""
        
        # Словник російсько-українських перекладів
        translations = {
            # Основні слова
            'Гибридный': 'Гібридний',
            'гибридный': 'гібридний', 
            'инвертор': 'інвертор',
            'Инвертор': 'Інвертор',
            'фазный': 'фазний',
            'кВт': 'кВт',
            'Солнечная': 'Сонячна',
            'солнечная': 'сонячна',
            'панель': 'панель',
            'на': 'на',
            'Вт': 'Вт',
            'Аккумуляторная': 'Акумуляторна',
            'аккумуляторная': 'акумуляторна',
            'батарея': 'батарея',
            'система': 'система',
            'зберігання': 'зберігання',
            'энергии': 'енергії',
            'модулів': 'модулів',
            'высоковольтная': 'високовольтна',
            'Высоковольтная': 'Високовольтна',
            'модулей': 'модулів',
            'модули': 'модулі',
            'подходит': 'підходить',
            'для': 'для',
            'дома': 'дому',
            'офиса': 'офісу',
            'комплект': 'комплект',
            'резервного': 'резервного',
            'питания': 'живлення',
            'хранения': 'зберігання',
            'мощность': 'потужність',
            'мощности': 'потужності',
            'напряжение': 'напруга',
            'емкость': 'ємність',
            'аккумулятор': 'акумулятор',
            'батареи': 'батареї',
            'литиевый': 'літієвий',
            'литиевая': 'літієва',
            'домашней': 'домашньої',
            'домашних': 'домашніх',
            'солнечной': 'сонячної',
            'солнечных': 'сонячних',
            'системы': 'системи',
            'электростанции': 'електростанції',
            'электростанций': 'електростанцій',
            'установки': 'установки',
            'установка': 'установка',
            'монтаж': 'монтаж',
            'Монтаж': 'Монтаж',
            'услуги': 'послуги',
            'Услуги': 'Послуги',
            'сервис': 'сервіс',
            'Сервис': 'Сервіс',
            'обслуживание': 'обслуговування',
            'Обслуживание': 'Обслуговування',
            'гарантия': 'гарантія',
            'Гарантия': 'Гарантія',
            'качество': 'якість',
            'Качество': 'Якість',
            'надежность': 'надійність',
            'Надежность': 'Надійність',
            'эффективность': 'ефективність',
            'Эффективность': 'Ефективність',
            'производительность': 'продуктивність',
            'Производительность': 'Продуктивність',
            'контроллер': 'контролер',
            'Контроллер': 'Контролер',
            'зарядное': 'зарядний',
            'зарядный': 'зарядний',
            'устройство': 'пристрій',
            'Устройство': 'Пристрій',
            'подключение': 'підключення',
            'Подключение': 'Підключення',
            'кабель': 'кабель',
            'Кабель': 'Кабель',
            'разъем': 'роз`єм',
            'Разъем': 'Роз`єм',
            'максимальный': 'максимальний',
            'максимальная': 'максимальна',
            'минимальный': 'мінімальний',
            'минимальная': 'мінімальна',
            'номинальный': 'номінальний',
            'номинальная': 'номінальна',
            'рабочий': 'робочий',
            'рабочая': 'робоча',
            'рабочее': 'робоче',
            'температура': 'температура',
            'Температура': 'Температура',
            'влажность': 'вологість',
            'Влажность': 'Вологість',
            'защита': 'захист',
            'Защита': 'Захист',
            'корпус': 'корпус',
            'Корпус': 'Корпус',
            'размер': 'розмір',
            'Размер': 'Розмір',
            'размеры': 'розміри',
            'Размеры': 'Розміри',
            'вес': 'вага',
            'Вес': 'Вага',
            'цвет': 'колір',
            'Цвет': 'Колір',
            'черный': 'чорний',
            'черная': 'чорна',
            'белый': 'білий',
            'белая': 'біла',
            'серый': 'сірий',
            'серая': 'сіра',
            'комплектация': 'комплектація',
            'Комплектация': 'Комплектація',
            'комплекте': 'комплекті',
            'включает': 'включає',
            'поставляется': 'постачається',
            'артикул': 'артикул',
            'Артикул': 'Артикул',
            'модель': 'модель',
            'Модель': 'Модель',
            'серия': 'серія',
            'Серия': 'Серія',
            'производитель': 'виробник',
            'Производитель': 'Виробник',
            'страна': 'країна',
            'Страна': 'Країна',
            'происхождения': 'походження',
            'изготовления': 'виготовлення',
            'технические': 'технічні',
            'Технические': 'Технічні',
            'характеристики': 'характеристики',
            'Характеристики': 'Характеристики',
            'параметры': 'параметри',
            'Параметры': 'Параметри',
            'спецификация': 'специфікація',
            'Спецификация': 'Специфікація',
            'описание': 'опис',
            'Описание': 'Опис',
            'применение': 'застосування',
            'Применение': 'Застосування',
            'использование': 'використання',
            'Использование': 'Використання',
            'эксплуатация': 'експлуатація',
            'Эксплуатация': 'Експлуатація',
            'инструкция': 'інструкція',
            'Инструкция': 'Інструкція',
            'руководство': 'керівництво',
            'Руководство': 'Керівництво',
            'документация': 'документація',
            'Документация': 'Документація',
            'сертификат': 'сертифікат',
            'Сертификат': 'Сертифікат',
            'сертификация': 'сертифікація',
            'Сертификация': 'Сертифікація',
            'соответствие': 'відповідність',
            'Соответствие': 'Відповідність',
            'стандарт': 'стандарт',
            'Стандарт': 'Стандарт',
            'стандарты': 'стандарти',
            'Стандарты': 'Стандарти',
            
            # Специфічні слова електроніки
            'SUN-6K-SG03LP1-EU': 'SUN-6K-SG03LP1-EU',
            'SUN-6K-SG04LP1-EU-SM2': 'SUN-6K-SG04LP1-EU-SM2',
            'SUN-8K-SG05LP1-EU-SM2': 'SUN-8K-SG05LP1-EU-SM2',
            'SUN-15K-SG05LP3-EU-SM2': 'SUN-15K-SG05LP3-EU-SM2',
        }
        
        result = str(text)
        
        # Застосовуємо переклади
        for rus, ukr in translations.items():
            result = result.replace(rus, ukr)
        
        # Виправляємо російські літери на українські
        russian_to_ukrainian = {
            'ы': 'и',
            'э': 'е', 
            'ё': 'е',
            'ъ': '',
            'Ы': 'И',
            'Э': 'Е',
            'Ё': 'Е',
            'Ъ': '',
        }
        
        for rus, ukr in russian_to_ukrainian.items():
            result = result.replace(rus, ukr)
        
        return result.strip()

    def clean_and_fix_text(self, text):
        """Очищає та виправляє текст від помилок"""
        if not text:
            return ""
        
        # Спочатку очищаємо HTML
        text = self.clean_text(text)
        
        # Перекладаємо російські слова
        text = self.translate_to_ukrainian(text)
        
        # Словник орфографічних виправлень
        corrections = {
            # Одиниці вимірювання
            'кВт рік': 'кВт·год',
            'кВт час': 'кВт·год', 
            'кВтгод': 'кВт·год',
            'квтгод': 'кВт·год',
            'kWh': 'кВт·год',
            'kWt': 'кВт',
            'Wt': 'Вт',
            'А год': 'А·год',
            'агод': 'А·год',
            'Агод': 'А·год',
            'Ah': 'А·год',
            'Ампер час': 'А·год',
            'ампер-час': 'А·год',
            'ампер час': 'А·год',
            
            # Характеристики модулів та струму
            'модулів 100А': 'модулів 100 А',
            'модулів 100A': 'модулів 100 А',
            'модулів 200А': 'модулів 200 А',
            'модулів 200A': 'модулів 200 А',
            '100А': '100 А',
            '200А': '200 А',
            '100A': '100 А',
            '200A': '200 А',
            
            # Напруга
            '220V и 110V': '220 В / 110 В',
            '220V': '220 В',
            '110V': '110 В',
            '48V': '48 В',
            '24V': '24 В',
            '12V': '12 В',
            'В 100А': 'В 100 А',
            'В 200А': 'В 200 А',
            '51,2B': '51,2 В',
            '614V': '614 В',
            '409.6V': '409,6 В',
            '307.2V': '307,2 В',
            '204.8V': '204,8 В',
            '25,6 В': '25,6 В',
            
            # Характеристики акумуляторів
            '614V 100Ah': '614 В 100 А·год',
            '409.6V 100Ah': '409,6 В 100 А·год',
            '307.2V 100Ah': '307,2 В 100 А·год',
            '204.8 V 100 Ah': '204,8 В 100 А·год',
            '51,2B 200A': '51,2 В 200 А',
            '48V 100A': '48 В 100 А',
            '48V 200A': '48 В 200 А',
            '24В , 100А': '24 В, 100 А',
            
            # Описи та терміни
            'Black Frame': 'з чорною рамкою',
            'Explorer': 'Explorer',
            'Hi-MO 6': 'Hi-MO 6',
            'LiFePO4': 'LiFePO4',
            'Lithium Battery-G2': 'Lithium Battery-G2',
            'резервного живлення': 'резервного живлення',
            'MPPT': 'MPPT',
            'PRO': 'PRO',
            'VPM II': 'VPM II',
            'EXP': 'EXP',
            'BOS-GM5.1': 'BOS-GM5.1',
            'RW-F10.6': 'RW-F10.6',
            'SE-G5.1Pro-B': 'SE-G5.1Pro-B',
            'LVTS-512200': 'LVTS-512200',
            'LVTS-512300': 'LVTS-512300',
            'LVTS-512228': 'LVTS-512228',
            'LVTS-48100': 'LVTS-48100',
            'LVTS-256100': 'LVTS-256100',
            'LP16-48100': 'LP16-48100',
            'LP16-48200': 'LP16-48200',
            'PV19-6048': 'PV19-6048',
            'PV18-3224': 'PV18-3224',
            'PV18-5248': 'PV18-5248',
            
            # Моделі сонячних панелей
            'LR8-66HGD-615M': 'LR8-66HGD-615M',
            'LR7-72HTH-610M': 'LR7-72HTH-610M',
            'LR5-72HTH-590M': 'LR5-72HTH-590M',
            'LR5-66HTH-530M': 'LR5-66HTH-530M',
            'LR5-54HTH-435M': 'LR5-54HTH-435M',
            'LR5-54HTB-420M': 'LR5-54HTB-420M',
            'RSM132-8-700BHDG': 'RSM132-8-700BHDG',
            
            # Моделі інверторів Deye
            'SUN-6K-SG03LP1-EU': 'SUN-6K-SG03LP1-EU',
            'SUN-6K-SG04LP1-EU-SM2': 'SUN-6K-SG04LP1-EU-SM2',
            'SUN-8K-SG01LP1-EU': 'SUN-8K-SG01LP1-EU',
            'SUN-8K-SG05LP1-EU-SM2': 'SUN-8K-SG05LP1-EU-SM2',
            'SUN-10K-SG02LP1-EU-AM3': 'SUN-10K-SG02LP1-EU-AM3',
            'SUN-12K-SG02LP1-EU-AM3': 'SUN-12K-SG02LP1-EU-AM3',
            'SUN-12K-SG04LP3-EU': 'SUN-12K-SG04LP3-EU',
            'SUN-15K-SG05LP3-EU-SM2': 'SUN-15K-SG05LP3-EU-SM2',
            'SUN-18K-SG05LP3-EU-SM2': 'SUN-18K-SG05LP3-EU-SM2',
            'SUN-20K-SG05LP3-EU-SM2': 'SUN-20K-SG05LP3-EU-SM2',
            'SUN-30K-SG01HP3-EU-BM3': 'SUN-30K-SG01HP3-EU-BM3',
            'SUN-50K-SG01HP3-EU-BM': 'SUN-50K-SG01HP3-EU-BM',
            'SUN-80K-SG02HP3-EU-EM6': 'SUN-80K-SG02HP3-EU-EM6',
            
            # Моделі акумуляторних систем
            'BOS-G60-61,44kW': 'BOS-G60-61,44kW',
            'BOS-G40-40,96kW': 'BOS-G40-40,96kW',
            'BOS-G30-30,72kW': 'BOS-G30-30,72kW',
            'BOS-G20-20,48kW': 'BOS-G20-20,48kW',
            
            # Орфографічні помилки
            'елекростанцій': 'електростанцій',
            'електросистем': 'електросистем',
            'сонцної': 'сонячної',
            'ефективіність': 'ефективність',
            'функціональніість': 'функціональність',
            'продуктівність': 'продуктивність',
            'максимільний': 'максимальний',
            'мінімільний': 'мінімальний',
            'номінільний': 'номінальний',
            'потужніість': 'потужність',
            'ємніість': 'ємність',
            'надійніість': 'надійність',
            'якіість': 'якість',
            
            # Кирилиця
            'и': 'і',  # російське и -> українське і (але тільки всередині слів)
            
            # Пробіли навколо знаків пунктуації
            ' ,': ',',
            ' .': '.',
            ' !': '!',
            ' ?': '?',
            ' :': ':',
            ' ;': ';',
            '( ': '(',
            ' )': ')',
            '[ ': '[',
            ' ]': ']',
            '{ ': '{',
            ' }': '}',
        }
        
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        
        # Спеціальне виправлення російського "и" всередині українських слів
        # Але залишаємо "и" в абревіатурах та англійських назвах
        words = text.split()
        fixed_words = []
        
        for word in words:
            # Пропускаємо англійські слова, абревіатури та моделі
            if (re.match(r'^[A-Z0-9\-_]+$', word) or 
                re.match(r'^[A-Z][a-z]+-\w+', word) or
                len(word) <= 3):
                fixed_words.append(word)
            else:
                # Замінюємо російське "и" на українське "і" тільки в українських словах
                if re.search(r'[абвгґдежзйклмнопрстуфхцчшщьюя]и[абвгґдежзйклмнопрстуфхцчшщьюя]', word.lower()):
                    word = re.sub(r'([абвгґдежзйклмнопрстуфхцчшщьюя])и([абвгґдежзйклмнопрстуфхцчшщьюя])', r'\1і\2', word)
                fixed_words.append(word)
        
        text = ' '.join(fixed_words)
        
        # Видаляємо зайві пробіли та очищаємо
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text 