import re
from django.core.management.base import BaseCommand
from django.db import transaction
from mainapp.models import Product

class Command(BaseCommand):
    help = 'Замінює російські слова на українські еквіваленти у назвах та описах товарів'

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
        
        # Словник заміни російських слів на українські
        russian_to_ukrainian = {
            'гибридный': 'гібридний',
            'гибридний': 'гібридний',
            'гибриднй': 'гібридний',
            'инвертор': 'інвертор',
            'инверторы': 'інвертори',
            'фазный': 'фазний',
            'фазные': 'фазні',
            'солнечная': 'сонячна',
            'солнечный': 'сонячний',
            'солнечные': 'сонячні',
            'панель': 'панель',
            'панели': 'панелі',
            'батарея': 'батарея',
            'батареи': 'батареї',
            'система': 'система',
            'системы': 'системи',
            'энергия': 'енергія',
            'энергии': 'енергії',
            'мощность': 'потужність',
            'мощности': 'потужності',
            'напряжение': 'напруга',
            'напряжения': 'напруги',
            'аккумулятор': 'акумулятор',
            'аккумуляторы': 'акумулятори',
            'аккумуляторная': 'акумуляторна',
            'аккумуляторный': 'акумуляторний',
            'аккумуляторные': 'акумуляторні',
            'литиевая': 'літієва',
            'литиевый': 'літієвий',
            'литиевые': 'літієві',
            'высоковольтная': 'високовольтна',
            'высоковольтный': 'високовольтний',
            'высоковольтные': 'високовольтні',
            'зарядка': 'зарядка',
            'зарядки': 'зарядки',
            'зарядное': 'зарядний',
            'устройство': 'пристрій',
            'устройства': 'пристрої',
            'оборудование': 'обладнання',
            'установка': 'установка',
            'установки': 'установки',
            'контроллер': 'контролер',
            'контроллеры': 'контролери',
            'преобразователь': 'перетворювач',
            'преобразователи': 'перетворювачі',
            'источник': 'джерело',
            'источники': 'джерела',
            'питание': 'живлення',
            'питания': 'живлення',
            'электричество': 'електрика',
            'электрический': 'електричний',
            'электрическая': 'електрична',
            'электрические': 'електричні',
            'производитель': 'виробник',
            'производители': 'виробники',
            'качество': 'якість',
            'качества': 'якості',
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
            'возможности': 'можливості'
        }
        
        for product in products:
            try:
                original_name = product.name
                original_description = product.description
                
                fixed_name = self.replace_russian_words(original_name, russian_to_ukrainian)
                fixed_description = self.replace_russian_words(original_description, russian_to_ukrainian)
                
                # Додаткове очищення неправильних символів
                fixed_name = self.fix_corrupted_text(fixed_name)
                fixed_description = self.fix_corrupted_text(fixed_description)
                
                needs_fixing = (
                    original_name != fixed_name or 
                    original_description != fixed_description
                )
                
                if needs_fixing:
                    if dry_run:
                        self.stdout.write(f"\n--- ТОВАР ID {product.id} ---")
                        if original_name != fixed_name:
                            self.stdout.write(f"Оригінальна назва: {original_name}")
                            self.stdout.write(f"Виправлена назва: {fixed_name}")
                        if original_description != fixed_description:
                            self.stdout.write(f"Опис оновлений (показано 100 символів)")
                    else:
                        with transaction.atomic():
                            product.name = fixed_name
                            product.description = fixed_description
                            product.save()
                            fixed_count += 1
                            self.stdout.write(f"Виправлено товар: {fixed_name}")
                
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
                    f"\nВИПРАВЛЕННЯ ЗАВЕРШЕНО\n"
                    f"Оброблено: {processed_count}\n"
                    f"Виправлено: {fixed_count}"
                )
            )

    def replace_russian_words(self, text, replacement_dict):
        """Замінює російські слова на українські еквіваленти"""
        if not text:
            return text
        
        text = str(text)
        
        # Замінюємо слова (регістронезалежно)
        for russian_word, ukrainian_word in replacement_dict.items():
            # Замінюємо цілі слова (з границями слів)
            pattern = r'\b' + re.escape(russian_word) + r'\b'
            text = re.sub(pattern, ukrainian_word, text, flags=re.IGNORECASE)
            
            # Також замінюємо з великої літери
            if russian_word[0].islower():
                russian_capitalized = russian_word.capitalize()
                ukrainian_capitalized = ukrainian_word.capitalize()
                pattern = r'\b' + re.escape(russian_capitalized) + r'\b'
                text = re.sub(pattern, ukrainian_capitalized, text)
        
        return text

    def fix_corrupted_text(self, text):
        """Виправляє пошкоджений текст після видалення російських символів"""
        if not text:
            return text
        
        text = str(text)
        
        # Список виправлень для пошкодженого тексту
        corrections = {
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
            'сонячнй': 'сонячний'
        }
        
        for corrupted, fixed in corrections.items():
            text = text.replace(corrupted, fixed)
        
        # Очищаємо зайві пробіли
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text 