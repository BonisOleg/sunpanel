import pandas as pd
import requests
import re
import os
import time
from urllib.parse import urlparse, urljoin
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.db import transaction, models
from django.utils.text import slugify
from mainapp.models import Product, Category, Brand, ProductImage
from bs4 import BeautifulSoup
from django.db import models


class Command(BaseCommand):
    help = 'Універсальний імпорт товарів з повною українізацією та категоризацією як на сайті'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products-file',
            type=str,
            default='export-products-10-07-25_11-38-56.xlsx',
            help='Файл з товарами'
        )
        parser.add_argument(
            '--categories-file', 
            type=str,
            default='second.xlsx',
            help='Файл з категоріями'
        )
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
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Детальний вивід'
        )

    def handle(self, *args, **options):
        self.products_file = options['products_file']
        self.categories_file = options['categories_file'] 
        self.clear_existing = options['clear_existing']
        self.dry_run = options['dry_run']
        self.verbose = options['verbose']

        # Перевіряємо файли
        for file_path in [self.products_file, self.categories_file]:
            if not os.path.exists(file_path):
                raise CommandError(f'Файл {file_path} не існує')

        if self.dry_run:
            self.stdout.write(self.style.WARNING("🔍 РЕЖИМ ПОПЕРЕДНЬОГО ПЕРЕГЛЯДУ"))

        self.stdout.write("🚀 Початок універсального імпорту товарів")

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
            # Крок 1: Видаляємо існуючі товари якщо потрібно
            if self.clear_existing:
                self.clear_existing_products()

            # Крок 2: Читаємо та обробляємо категорії
            category_mapping = self.read_categories()

            # Крок 3: Імпортуємо товари
            self.import_products(category_mapping)

            # Крок 4: Показуємо результати
            self.show_final_stats()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Критична помилка: {str(e)}"))
            raise

    def clear_existing_products(self):
        """Видаляє всі існуючі товари"""
        count = Product.objects.count()
        if count == 0:
            self.stdout.write("ℹ️ Товарів для видалення немає")
            return

        if self.dry_run:
            self.stdout.write(f"🗑️ БУДЕ ВИДАЛЕНО: {count} товарів")
        else:
            with transaction.atomic():
                Product.objects.all().delete()
                self.stdout.write(f"🗑️ Видалено {count} товарів")

    def read_categories(self):
        """Читає та створює мапінг категорій - ТІЛЬКИ УКРАЇНСЬКІ НАЗВИ"""
        self.stdout.write("📂 Обробка категорій...")
        
        try:
            df = pd.read_excel(self.categories_file)
            category_mapping = {}
            
            # Базові категорії для правильного мапування на сайт
            base_categories = {
                'Інвертори': ['інвертор', 'гібридн'],
                'Сонячні панелі': ['панел', 'сонячн', 'монокристал', 'полікристал'],
                'Акумуляторні батареї': ['акумулятор', 'батарея', 'літієв', 'lifepo4', 'високовольтн'],
                'Комплекти резервного живлення': ['комплект', 'набір', 'резервн', 'живлення'],
                'Додаткові послуги': ['монтаж', 'послуг', 'сервіс']
            }
            
            for index, row in df.iterrows():
                ukr_name = str(row.get('Назва_групи_укр', '')).strip()
                rus_name = str(row.get('Назва_групи', '')).strip()
                
                # Тільки якщо є українська назва
                if ukr_name and pd.notna(row.get('Назва_групи_укр')) and ukr_name != 'nan':
                    # Очищаємо українську назву (БЕЗ перекладу)
                    clean_ukr_name = self.clean_ukrainian_text_only(ukr_name)
                    
                    # Перевіряємо що це чисто українська назва
                    if self.is_pure_ukrainian_text(clean_ukr_name):
                        # Мапимо на базові категорії сайту
                        mapped_category = self.map_to_base_category(clean_ukr_name, base_categories)
                        
                        # Зберігаємо мапінг від російської до української
                        if rus_name and pd.notna(row.get('Назва_групи')):
                            category_mapping[rus_name] = mapped_category
                        
                        if self.verbose:
                            self.stdout.write(f"  📝 {rus_name} → {mapped_category}")
                    else:
                        if self.verbose:
                            self.stdout.write(f"  ⏭️ Пропущено категорію з неукраїнськими символами: {clean_ukr_name}")

            self.stdout.write(f"✅ Створено {len(category_mapping)} мапінгів категорій")
            return category_mapping
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Помилка читання категорій: {str(e)}"))
            return {}

    def map_to_base_category(self, category_name, base_categories):
        """Мапить назву категорії на базові категорії сайту"""
        category_lower = category_name.lower()
        
        for base_cat, keywords in base_categories.items():
            for keyword in keywords:
                if keyword.lower() in category_lower:
                    return base_cat
        
        # Якщо не знайшли відповідність, повертаємо очищену назву
        return category_name

    def determine_category_by_product_name(self, product_name):
        """Визначає категорію товару за його назвою"""
        if not product_name:
            return ''
        
        name_lower = product_name.lower()
        
        # НАЙВИЩИЙ ПРІОРИТЕТ - КОМПЛЕКТИ (перевіряємо ПЕРШ ЗА ВСЕ!)
        if any(word in name_lower for word in ['комплект', 'набір']):
            return 'Комплекти резервного живлення'
        
        # Сонячні панелі
        if any(word in name_lower for word in ['панел', 'сонячн']):
            return 'Сонячні панелі'
            
        # Акумуляторні батареї
        if any(word in name_lower for word in ['акумулятор', 'батарея', 'літієв', 'lifepo4']):
            return 'Акумуляторні батареї'
        
        # Інвертори (включно з гібридними) - ОСТАННІЙ пріоритет    
        if any(word in name_lower for word in ['інвертор', 'гібридн']):
            return 'Інвертори'
            
        # Пропускаємо монтаж - не імпортуємо послуги
        if any(word in name_lower for word in ['монтаж', 'послуг', 'сервіс']):
            return ''  # Повертаємо порожню категорію = пропускаємо товар
        
        # Якщо нічого не підійшло
        return ''

    def import_products(self, category_mapping):
        """Головна функція імпорту товарів"""
        self.stdout.write("📦 Імпорт товарів...")
        
        try:
            # Читаємо файл товарів
            try:
                df = pd.read_excel(self.products_file, sheet_name='Export Products Sheet')
            except:
                try:
                    df = pd.read_excel(self.products_file, sheet_name=0)
                except:
                    df = pd.read_excel(self.products_file)

            self.stdout.write(f"📋 Знайдено {len(df)} товарів у файлі")
            
            if len(df) == 0:
                raise CommandError('Файл з товарами порожній')

            # Обробляємо товари пакетами для продуктивності
            batch_size = 50
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                self.process_product_batch(batch, category_mapping)
                
                if (i + batch_size) % 100 == 0:
                    self.stdout.write(f"⏳ Оброблено {min(i + batch_size, len(df))}/{len(df)} товарів...")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Помилка імпорту товарів: {str(e)}"))
            self.stats['errors'] += 1

    def process_product_batch(self, batch, category_mapping):
        """Обробляє пакет товарів"""
        for index, row in batch.iterrows():
            try:
                self.process_single_product(row, category_mapping)
            except Exception as e:
                self.stats['errors'] += 1
                if self.verbose:
                    self.stdout.write(f"❌ Помилка товару {index}: {str(e)}")

    def process_single_product(self, row, category_mapping):
        """Обробляє один товар з логічним перекладом російських назв"""
        # Отримуємо українську та російську назви
        name_ukr = str(row.get('Назва_позиції_укр', '')).strip() if pd.notna(row.get('Назва_позиції_укр')) else ''
        name_rus = str(row.get('Назва_позиції', '')).strip() if pd.notna(row.get('Назва_позиції')) else ''
        
        # Визначаємо фінальну назву
        if name_ukr and name_ukr != 'nan' and len(name_ukr) > 4:
            # Є українська назва - використовуємо її
            final_name = self.clean_and_translate_text(name_ukr)
        elif name_rus and name_rus != 'nan' and len(name_rus) > 4:
            # Немає української - ЧІТКО перекладаємо російську
            final_name = self.clean_and_translate_text(name_rus)
        else:
            # Немає жодної назви - пропускаємо
            if self.verbose:
                self.stdout.write(f"  ⏭️ Пропущено: немає жодної назви")
            self.stats['products_skipped'] += 1
            return
        
        # Перевіряємо що назва не порожня після очистки
        if not final_name or len(final_name) < 5:
            if self.verbose:
                self.stdout.write(f"  ⏭️ Пропущено: назва занадто коротка після очистки")
            self.stats['products_skipped'] += 1
            return

        # Отримуємо описи
        description_ukr = str(row.get('Опис_укр', '')).strip() if pd.notna(row.get('Опис_укр')) else ''
        description_rus = str(row.get('Опис', '')).strip() if pd.notna(row.get('Опис')) else ''
        
        # Визначаємо фінальний опис
        if description_ukr and description_ukr != 'nan' and len(description_ukr) > 10:
            # Є український опис
            clean_description = self.clean_description(description_ukr)
        elif description_rus and description_rus != 'nan' and len(description_rus) > 10:
            # Немає українського - перекладаємо російський
            clean_description = self.clean_description(description_rus)
        else:
            # Створюємо базовий опис
            clean_description = f"Професійний {final_name} від надійного виробника. Висока якість та гарантія."

        # Отримуємо інші дані
        price = self.parse_price(row.get('Ціна', 0))
        
        # Для категорії використовуємо мапінг + логіку за назвою товару
        category_name_rus = str(row.get('Назва_групи', '')).strip() if pd.notna(row.get('Назва_групи')) else ''
        category_name = category_mapping.get(category_name_rus, '')
        
        # ЗАВЖДИ перевіряємо категорію за назвою товару (пріоритет над мапінгом!)
        auto_category = self.determine_category_by_product_name(final_name)
        if auto_category and auto_category != category_name:
            if self.verbose:
                self.stdout.write(f"  🔄 Перевизначення категорії: '{final_name[:30]}...' → '{auto_category}' (було: '{category_name}')")
            category_name = auto_category
        
        # Якщо немає мапінгу - визначаємо категорію за назвою товару
        if not category_name:
            category_name = self.determine_category_by_product_name(final_name)
            if self.verbose and category_name:
                self.stdout.write(f"  🔍 Автовизначення категорії: '{final_name[:30]}...' → '{category_name}'")
        
        # Якщо все ще немає категорії - пропускаємо товар
        if not category_name:
            if self.verbose:
                self.stdout.write(f"  ⏭️ Пропущено: не вдалося визначити категорію для '{category_name_rus}' / '{final_name[:30]}...'")
            self.stats['products_skipped'] += 1
            return
        
        brand_name = str(row.get('Виробник', '')).strip() if pd.notna(row.get('Виробник')) else ''
        country = str(row.get('Країна_виробник', '')).strip() if pd.notna(row.get('Країна_виробник')) else ''
        model = str(row.get('Код_товару', '')).strip() if pd.notna(row.get('Код_товару')) else ''
        image_links = str(row.get('Посилання_зображення', '')).strip() if pd.notna(row.get('Посилання_зображення')) else ''

        if self.verbose:
            self.stdout.write(f"  ✅ Обробка: {final_name[:50]}...")

        if self.dry_run:
            self.stdout.write(f"БУДЕ СТВОРЕНО: {final_name}")
            self.stats['products_created'] += 1
            return

        # Створюємо товар
        product = self.create_product_with_relations(
            final_name, clean_description, price, category_name, 
            brand_name, model, country, image_links, category_mapping
        )
        
        if product:
            self.stats['products_created'] += 1
        else:
            self.stats['products_skipped'] += 1

    def create_product_with_relations(self, name, description, price, category_name, 
                                    brand_name, model, country, image_links, category_mapping):
        """Створює товар з усіма зв'язками"""
        try:
            # Створюємо/отримуємо категорію
            category = self.get_or_create_category(category_name, category_mapping)
            
            # Створюємо/отримуємо бренд
            brand = self.get_or_create_brand(brand_name, country)
            
            # Створюємо товар
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                category=category,
                brand=brand,
                model=model,
                country=country,
                in_stock=True,
                featured=False  # Можна додати логіку для визначення рекомендованих
            )
            
            # Додаємо зображення
            if image_links:
                try:
                    self.add_product_images(product, image_links)
                except Exception as e:
                    if self.verbose:
                        self.stdout.write(f"  ⚠️ Помилка зображень для {name}: {str(e)}")
            
            return product
            
        except Exception as e:
            if self.verbose:
                self.stdout.write(f"  ❌ Помилка створення {name}: {str(e)}")
            return None

    def get_or_create_category(self, category_name, category_mapping):
        """Створює або отримує категорію з мапінгом"""
        if not category_name:
            category_name = "Інше обладнання"
        
        # Перевіряємо мапінг
        mapped_name = category_mapping.get(category_name, category_name)
        clean_name = self.clean_and_translate_text(mapped_name)
        
        if not clean_name:
            clean_name = "Інше обладнання"
        
        category, created = Category.objects.get_or_create(
            name=clean_name,
            defaults={
                'description': f'Категорія {clean_name}',
                'is_active': True
            }
        )
        
        if created:
            self.stats['categories_created'] += 1
            if self.verbose:
                self.stdout.write(f"  📂 Створено категорію: {clean_name}")
        
        return category

    def get_or_create_brand(self, brand_name, country=""):
        """Створює або отримує бренд"""
        if not brand_name:
            brand_name = "Загальний"
        
        clean_name = self.clean_and_translate_text(brand_name)
        if not clean_name:
            clean_name = "Загальний"
        
        brand, created = Brand.objects.get_or_create(
            name=clean_name,
            defaults={
                'description': f'Бренд {clean_name}' + (f' з {country}' if country else ''),
                'is_active': True
            }
        )
        
        if created:
            self.stats['brands_created'] += 1
            if self.verbose:
                self.stdout.write(f"  🏷️ Створено бренд: {clean_name}")
        
        return brand

    def add_product_images(self, product, image_links):
        """Додає зображення до товару"""
        if not image_links:
            return
        
        # Розділяємо посилання
        links = re.split(r'[,;\n]+', image_links)
        
        for i, link in enumerate(links[:5]):  # Максимум 5 зображень
            link = link.strip()
            if not link or not link.startswith('http'):
                continue
                
            try:
                if self.download_and_save_image(product, link, i):
                    self.stats['images_downloaded'] += 1
                    if i == 0:  # Затримка лише після першого зображення
                        time.sleep(0.5)
                    
            except Exception as e:
                if self.verbose:
                    self.stdout.write(f"    ⚠️ Помилка зображення {link}: {str(e)}")

    def download_and_save_image(self, product, image_url, index):
        """Завантажує та зберігає зображення"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(image_url, timeout=15, headers=headers)
            response.raise_for_status()
            
            # Отримуємо назву файлу
            parsed_url = urlparse(image_url)
            original_filename = os.path.basename(parsed_url.path)
            
            if original_filename and '.' in original_filename:
                name_part, ext_part = original_filename.rsplit('.', 1)
                filename = f"product_{product.id}_{index}_{name_part[:20]}.{ext_part}"
            else:
                filename = f"product_{product.id}_{index}.jpg"
            
            content = ContentFile(response.content, name=filename)
            
            if index == 0:
                # Головне зображення
                product.image.save(filename, content, save=True)
                if self.verbose:
                    self.stdout.write(f"    🖼️ Головне зображення: {filename}")
            else:
                # Додаткові зображення
                ProductImage.objects.create(
                    product=product,
                    image=content,
                    alt_text=f"{product.name} - зображення {index+1}",
                    order=index
                )
                if self.verbose:
                    self.stdout.write(f"    🖼️ Додаткове зображення: {filename}")
            
            return True
            
        except Exception as e:
            if self.verbose:
                self.stdout.write(f"    ❌ Помилка завантаження {image_url}: {str(e)}")
            return False

    # === ФУНКЦІЇ ОЧИСТКИ ТА ПЕРЕКЛАДУ ===

    def clean_and_translate_text(self, text):
        """Основна функція очистки та перекладу"""
        if not text:
            return ""
        
        # Видаляємо HTML теги
        text = BeautifulSoup(str(text), 'html.parser').get_text()
        
        # Перекладаємо з російської
        text = self.translate_to_ukrainian(text)
        
        # Очищаємо від зайвих символів
        text = self.clean_text_content(text)
        
        return text.strip()

    def clean_description(self, text):
        """Спеціальна очистка для описів"""
        if not text:
            return ""
        
        # Основна очистка
        text = self.clean_and_translate_text(text)
        
        # Видаляємо російські речення
        sentences = re.split(r'[.!?]+', text)
        ukrainian_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Перевіряємо українськість речення
            if self.is_ukrainian_text(sentence):
                ukrainian_sentences.append(sentence)
        
        result = '. '.join(ukrainian_sentences)
        if result and not result.endswith('.'):
            result += '.'
            
        return result

    def translate_to_ukrainian(self, text):
        """Розширений перекладач російсько-українських термінів"""
        if not text:
            return ""
        
        # Логічний словник перекладів - російська ↔ українська
        translations = {
            # Основні терміни
            'Гибридный': 'Гібридний', 'гибридный': 'гібридний',
            'инвертор': 'інвертор', 'Инвертор': 'Інвертор',
            'Солнечная': 'Сонячна', 'солнечная': 'сонячна', 'Солнечные': 'Сонячні', 'солнечные': 'сонячні',
            'панель': 'панель', 'Панель': 'Панель', 'панели': 'панелі', 'Панели': 'Панелі',
            'Аккумуляторная': 'Акумуляторна', 'аккумуляторная': 'акумуляторна',
            'батарея': 'батарея', 'Батарея': 'Батарея',
            'аккумулятор': 'акумулятор', 'Аккумулятор': 'Акумулятор',
            'система': 'система', 'Система': 'Система',
            'комплект': 'комплект', 'Комплект': 'Комплект',
            'мощность': 'потужність', 'Мощность': 'Потужність',
            'эффективность': 'ефективність', 'Эффективность': 'Ефективність',
            'напряжение': 'напруга', 'Напряжение': 'Напруга',
            'емкость': 'ємність', 'Емкость': 'Ємність',
            'энергии': 'енергії', 'Энергии': 'Енергії', 'энергия': 'енергія', 'Энергия': 'Енергія',
            'резервного': 'резервного', 'Резервного': 'Резервного',
            'питания': 'живлення', 'Питания': 'Живлення', 'питание': 'живлення', 'Питание': 'Живлення',
            'производитель': 'виробник', 'Производитель': 'Виробник',
            'качество': 'якість', 'Качество': 'Якість',
            'надежность': 'надійність', 'Надежность': 'Надійність',
            'гарантия': 'гарантія', 'Гарантия': 'Гарантія',
            'установка': 'установка', 'Установка': 'Установка',
            'монтаж': 'монтаж', 'Монтаж': 'Монтаж',
            'хранения': 'зберігання', 'Хранения': 'Зберігання', 'хранение': 'зберігання', 'Хранение': 'Зберігання',
            'высоковольтная': 'високовольтна', 'Высоковольтная': 'Високовольтна',
            'модулей': 'модулів', 'Модулей': 'Модулів', 'модули': 'модулі', 'Модули': 'Модулі',
            
            # Технічні терміни
            'фазный': 'фазний', 'Фазный': 'Фазний',
            'контроллер': 'контролер', 'Контроллер': 'Контролер',
            'зарядное': 'зарядний', 'Зарядное': 'Зарядний',
            'устройство': 'пристрій', 'Устройство': 'Пристрій',
            'подключение': 'підключення', 'Подключение': 'Підключення',
            'максимальный': 'максимальний', 'максимальная': 'максимальна', 'Максимальный': 'Максимальний',
            'минимальный': 'мінімальний', 'минимальная': 'мінімальна', 'Минимальный': 'Мінімальний',
            'номинальный': 'номінальний', 'номинальная': 'номінальна', 'Номинальный': 'Номінальний',
            'рабочий': 'робочий', 'рабочая': 'робоча', 'Рабочий': 'Робочий',
            'температура': 'температура', 'Температура': 'Температура',
            'защита': 'захист', 'Защита': 'Захист',
            'размер': 'розмір', 'Размер': 'Розмір',
            'вес': 'вага', 'Вес': 'Вага',
            
            # Матеріали та типи
            'литиевый': 'літієвий', 'литиевая': 'літієва', 'Литиевый': 'Літієвий',
            'монокристалический': 'монокристалічний', 'Монокристалический': 'Монокристалічний',
            'поликристалический': 'полікристалічний', 'Поликристалический': 'Полікристалічний',
            
            # Збереження відповідних одиниць
            'кВт': 'кВт', 'квт': 'кВт', 'КВТ': 'кВт',
            'кВтч': 'кВт·год', 'квтч': 'кВт·год', 'КВТЧ': 'кВт·год',
            'Ватт': 'Вт', 'ватт': 'Вт', 'ВАТТ': 'Вт',
            'Вольт': 'В', 'вольт': 'В', 'ВОЛЬТ': 'В',
            'Ампер': 'А', 'ампер': 'А', 'АМПЕР': 'А'
        }
        
        result = str(text)
        
        # Застосовуємо переклади
        for rus, ukr in translations.items():
            result = result.replace(rus, ukr)
        
        # Заміняємо російські літери
        russian_letters = {
            'ы': 'и', 'Ы': 'И', 'э': 'е', 'Э': 'Е',
            'ё': 'е', 'Ё': 'Е', 'ъ': '', 'Ъ': ''
        }
        
        for rus, ukr in russian_letters.items():
            result = result.replace(rus, ukr)
        
        return result

    def clean_text_content(self, text):
        """Очищає текст від небажаних символів та форматує"""
        if not text:
            return ""
        
        # Заміняємо HTML entities
        text = text.replace('&ndash;', '–').replace('&mdash;', '—')
        text = text.replace('&nbsp;', ' ').replace('&deg;', '°')
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        
        # Видаляємо зайві пробіли та символи
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.,;:!?\-—–()°%№/АБВГҐДЕЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдежзиіїйклмнопрстуфхцчшщьюя]', '', text)
        
        return text.strip()

    def is_ukrainian_text(self, text):
        """Перевіряє чи текст українською мовою"""
        if not text:
            return False
        
        ukrainian_chars = len(re.findall(r'[абвгґдежзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ]', text))
        russian_chars = len(re.findall(r'[ыъэёЫЪЭЁ]', text))
        
        return ukrainian_chars >= 3 and russian_chars == 0

    def is_pure_ukrainian_text(self, text):
        """Перевірка на українську мову після перекладу"""
        if not text:
            return False
        
        # Перевіряємо наявність ЯВНИХ російських символів
        russian_chars = re.findall(r'[ыъэёЫЪЭЁ]', text)
        if russian_chars:
            return False
            
        # Перевіряємо наявність українських літер
        ukrainian_chars = len(re.findall(r'[абвгґдежзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ]', text))
        
        # Мінімум 2 українські літери і ЖОДНОЇ російської
        return ukrainian_chars >= 2

    def clean_ukrainian_text_only(self, text):
        """Очищає ТІЛЬКИ українській текст без перекладу"""
        if not text:
            return ""
        
        # Видаляємо HTML теги
        text = BeautifulSoup(str(text), 'html.parser').get_text()
        
        # Заміняємо HTML entities
        text = text.replace('&ndash;', '–').replace('&mdash;', '—')
        text = text.replace('&nbsp;', ' ').replace('&deg;', '°')
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        
        # Видаляємо зайві пробіли
        text = re.sub(r'\s+', ' ', text)
        
        # Видаляємо небажані символи, залишаючи тільки українські літери, цифри та базові знаки
        text = re.sub(r'[^\w\s\.,;:!?\-—–()°%№/АБВГҐДЕЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдежзиіїйклмнопрстуфхцчшщьюя0-9]', '', text)
        
        return text.strip()

    def clean_ukrainian_description_only(self, text):
        """Очищає український опис без перекладу"""
        if not text:
            return ""
        
        # Основна очистка
        text = self.clean_ukrainian_text_only(text)
        
        # Розділяємо на речення
        sentences = re.split(r'[.!?]+', text)
        ukrainian_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 5:
                continue
                
            # Перевіряємо СТРОГО на українськість
            if self.is_pure_ukrainian_text(sentence):
                ukrainian_sentences.append(sentence)
        
        result = '. '.join(ukrainian_sentences)
        if result and not result.endswith('.'):
            result += '.'
            
        return result

    def parse_price(self, price_value):
        """Парсить ціну з різних форматів"""
        if pd.isna(price_value):
            return 0.0
        
        if isinstance(price_value, (int, float)):
            return float(price_value)
        
        price_str = re.sub(r'[^\d.,]', '', str(price_value))
        price_str = price_str.replace(',', '.')
        
        try:
            return float(price_str)
        except:
            return 0.0

    def show_final_stats(self):
        """Показує підсумкову статистику"""
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n🔍 ПОПЕРЕДНІЙ ПЕРЕГЛЯД ЗАВЕРШЕНО\n"
                    f"Буде створено товарів: {self.stats['products_created']}\n"
                    f"Буде створено категорій: {self.stats['categories_created']}\n"
                    f"Буде створено брендів: {self.stats['brands_created']}\n"
                    f"Буде завантажено зображень: {self.stats['images_downloaded']}\n"
                    f"Пропущено товарів: {self.stats['products_skipped']}\n"
                    f"Помилки: {self.stats['errors']}\n"
                    f"\nДля реального імпорту запустіть без --dry-run"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 УНІВЕРСАЛЬНИЙ ІМПОРТ ЗАВЕРШЕНО\n"
                    f"✅ Створено товарів: {self.stats['products_created']}\n"
                    f"📂 Створено категорій: {self.stats['categories_created']}\n"
                    f"🏷️ Створено брендів: {self.stats['brands_created']}\n"
                    f"🖼️ Завантажено зображень: {self.stats['images_downloaded']}\n"
                    f"⏭️ Пропущено товарів: {self.stats['products_skipped']}\n"
                    f"❌ Помилки: {self.stats['errors']}\n"
                    f"\n📊 Підсумок у базі даних:\n"
                    f"   Всього товарів: {Product.objects.count()}\n"
                    f"   Всього категорій: {Category.objects.count()}\n"
                    f"   Всього брендів: {Brand.objects.count()}"
                )
            )
            
            # Показуємо статистику по категоріях
            self.show_category_stats()

    def show_category_stats(self):
        """Показує статистику товарів по категоріях"""
        self.stdout.write("\n📈 Статистика по категоріях:")
        categories = Category.objects.annotate(
            products_count=models.Count('product')
        ).order_by('-products_count')
        
        for category in categories:
            self.stdout.write(f"   📂 {category.name}: {category.products_count} товарів") 