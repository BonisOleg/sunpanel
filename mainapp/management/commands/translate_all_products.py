import re
from django.core.management.base import BaseCommand
from django.db import transaction
from bs4 import BeautifulSoup
from mainapp.models import Product

class Command(BaseCommand):
    help = 'Переводить усі товари на українську мову без видалення, очищає від HTML тегів'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати результат без збереження в базу',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        products = Product.objects.all()
        total_products = products.count()
        
        self.stdout.write(f"Знайдено {total_products} товарів для обробки")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("РЕЖИМ ПОПЕРЕДНЬОГО ПЕРЕГЛЯДУ - зміни не будуть збережені"))
        
        processed_count = 0
        fixed_count = 0
        
        for product in products:
            try:
                original_name = product.name
                original_description = product.description
                
                # Переводимо та очищаємо назву
                translated_name = self.translate_to_ukrainian(original_name)
                cleaned_name = self.clean_html_and_fix_text(translated_name)
                
                # Переводимо та очищаємо опис
                translated_description = self.translate_to_ukrainian(original_description)
                cleaned_description = self.clean_html_and_fix_text(translated_description)
                
                # Перевіряємо чи потрібне виправлення
                needs_fixing = (
                    original_name != cleaned_name or 
                    original_description != cleaned_description
                )
                
                if needs_fixing:
                    if dry_run:
                        self.stdout.write(f"\n--- ТОВАР ID {product.id} ---")
                        if original_name != cleaned_name:
                            self.stdout.write(f"Оригінальна назва: {original_name}")
                            self.stdout.write(f"Перекладена назва: {cleaned_name}")
                        if original_description != cleaned_description:
                            self.stdout.write(f"Опис перекладено та очищено")
                    else:
                        with transaction.atomic():
                            product.name = cleaned_name
                            product.description = cleaned_description
                            product.save()
                            fixed_count += 1
                            self.stdout.write(f"Виправлено: {cleaned_name}")
                
                processed_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Помилка при обробці товару ID {product.id}: {str(e)}")
                )
                processed_count += 1
                continue
        
        # Підсумки
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\nПОПЕРЕДНІЙ ПЕРЕГЛЯД ЗАВЕРШЕНО\n"
                    f"Оброблено: {processed_count}\n"
                    f"Потребують виправлення: {fixed_count}\n"
                    f"Для застосування змін запустіть без --dry-run"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nПЕРЕКЛАД ЗАВЕРШЕНО\n"
                    f"Оброблено: {processed_count}\n"
                    f"Виправлено: {fixed_count}"
                )
            )

    def translate_to_ukrainian(self, text):
        """Переводить російські та інші слова на українську мову"""
        if not text:
            return ""
        
        text = str(text)
        
        # Повний словник перекладу російських слів на українські
        translation_dict = {
            # Основні терміни
            'солнечная': 'сонячна',
            'солнечный': 'сонячний', 
            'солнечные': 'сонячні',
            'солнечных': 'сонячних',
            'панель': 'панель',
            'панели': 'панелі',
            'панелей': 'панелей',
            'гибридный': 'гібридний',
            'гибридная': 'гібридна',
            'гибридные': 'гібридні',
            'инвертор': 'інвертор',
            'инверторы': 'інвертори',
            'фазный': 'фазний',
            'фазная': 'фазна',
            'фазные': 'фазні',
            
            # Акумулятори та батареї
            'аккумуляторная': 'акумуляторна',
            'аккумуляторный': 'акумуляторний',
            'аккумуляторные': 'акумуляторні',
            'аккумулятор': 'акумулятор',
            'аккумуляторы': 'акумулятори',
            'батарея': 'батарея',
            'батареи': 'батареї',
            'батарей': 'батарей',
            'литиевая': 'літієва',
            'литиевый': 'літієвий',
            'литиевые': 'літієві',
            'литий': 'літій',
            
            # Системи та обладнання
            'система': 'система',
            'системы': 'системи',
            'высоковольтная': 'високовольтна',
            'высоковольтный': 'високовольтний',
            'высоковольтные': 'високовольтні',
            'зарядка': 'зарядка',
            'зарядное': 'зарядний',
            'зарядный': 'зарядний',
            'устройство': 'пристрій',
            'устройства': 'пристрої',
            'оборудование': 'обладнання',
            'установка': 'установка',
            'установки': 'установки',
            'монтаж': 'монтаж',
            
            # Технічні характеристики
            'мощность': 'потужність',
            'мощности': 'потужності',
            'энергия': 'енергія',
            'энергии': 'енергії',
            'напряжение': 'напруга',
            'напряжения': 'напруги',
            'электричество': 'електрика',
            'электрический': 'електричний',
            'электрическая': 'електрична',
            'электрические': 'електричні',
            'электростанция': 'електростанція',
            'электростанций': 'електростанцій',
            
            # Інші терміни
            'комплект': 'комплект',
            'резервного': 'резервного',
            'резервное': 'резервне',
            'живления': 'живлення',
            'питание': 'живлення',
            'питания': 'живлення',
            'контроллер': 'контролер',
            'контроллеры': 'контролери',
            'преобразователь': 'перетворювач',
            'преобразователи': 'перетворювачі',
            'источник': 'джерело',
            'источники': 'джерела',
            'производитель': 'виробник',
            'производители': 'виробники',
            'качество': 'якість',
            'надежность': 'надійність',
            'надежный': 'надійний',
            'надежная': 'надійна',
            'надежные': 'надійні',
            'эффективность': 'ефективність',
            'эффективный': 'ефективний',
            'эффективная': 'ефективна',
            'эффективные': 'ефективні',
            'современный': 'сучасний',
            'современная': 'сучасна',
            'современные': 'сучасні',
            'технология': 'технологія',
            'технологии': 'технології',
            'решение': 'рішення',
            'решения': 'рішення',
            'функция': 'функція',
            'функции': 'функції',
            'возможность': 'можливість',
            'возможности': 'можливості',
            'зберігання': 'зберігання',
            'хранения': 'зберігання',
            'storage': 'зберігання',
            
            # Виправлення пошкоджених слів після видалення російських символів
            'гибриднй': 'гібридний',
            'гибридий': 'гібридний',
            'фазнй': 'фазний',
            'аккумулторна': 'акумуляторна',
            'аккумулторнй': 'акумуляторний',
            'солнечнй': 'сонячний',
            'солнечна': 'сонячна',
            'инверторй': 'інвертор',
            'високовольтнй': 'високовольтний',
            'літвй': 'літієвий',
            'літва': 'літієва',
            'електричнй': 'електричний',
            'сучаснй': 'сучасний',
            'надійнй': 'надійний',
            'ефективнй': 'ефективний',
        }
        
        # Замінюємо слова з урахуванням регістру
        for russian_word, ukrainian_word in translation_dict.items():
            # Замінюємо в нижньому регістрі
            pattern = r'\b' + re.escape(russian_word) + r'\b'
            text = re.sub(pattern, ukrainian_word, text, flags=re.IGNORECASE)
            
            # Замінюємо з великої літери
            if russian_word[0].islower():
                russian_capitalized = russian_word.capitalize()
                ukrainian_capitalized = ukrainian_word.capitalize()
                pattern = r'\b' + re.escape(russian_capitalized) + r'\b'
                text = re.sub(pattern, ukrainian_capitalized, text)
        
        return text

    def clean_html_and_fix_text(self, text):
        """Очищає HTML теги та виправляє текст"""
        if not text:
            return ""
        
        text = str(text).strip()
        
        # Видаляємо HTML теги
        soup = BeautifulSoup(text, 'html.parser')
        clean_text = soup.get_text()
        
        # Заміняємо HTML entities
        html_entities = {
            '&ndash;': '–',
            '&mdash;': '—',
            '&nbsp;': ' ',
            '&deg;': '°',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&hellip;': '...',
            '&laquo;': '«',
            '&raquo;': '»',
        }
        
        for entity, replacement in html_entities.items():
            clean_text = clean_text.replace(entity, replacement)
        
        # Видаляємо російські символи
        clean_text = re.sub(r'[ёъыэ]', '', clean_text)
        
        # Виправляємо пошкоджений текст після видалення російських символів
        text_fixes = {
            'нй': 'ний',
            'нй ': 'ний ',
            'йй': 'ський',
            'тй': 'тний',
            'лй': 'льний',
            'рй': 'рний',
            'дй': 'дний',
            'пй': 'пний',
            'мй': 'мний',
            'вй': 'вний',
            'зй': 'зний',
            'кй': 'кний',
            'фазнй': 'фазний',
            'волтнй': 'вольтний',
            'літвй': 'літієвий',
            'сонячнй': 'сонячний',
            'гібридй': 'гібридний',
            'акумулторна': 'акумуляторна',
            'акумулторний': 'акумуляторний',
            'електричка': 'електрична',
            'електричкий': 'електричний',
        }
        
        for corrupted, fixed in text_fixes.items():
            clean_text = clean_text.replace(corrupted, fixed)
        
        # Очищаємо зайві пробіли та переноси рядків
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Видаляємо спеціальні символи крім дозволених
        allowed_chars = r'[^абвгґдежзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯa-zA-Z0-9\s.,;:!?\-—–()°%№/+*=]'
        clean_text = re.sub(allowed_chars, '', clean_text)
        
        # Остаточне очищення пробілів
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text 