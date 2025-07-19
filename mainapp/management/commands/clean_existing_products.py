import re
from django.core.management.base import BaseCommand
from django.db import transaction
from bs4 import BeautifulSoup
from mainapp.models import Product

class Command(BaseCommand):
    help = 'Очищає існуючі товари від HTML тегів та російських слів, залишає тільки українську мову'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати результат без збереження в базу',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Розмір пакету для обробки (за замовчуванням 100)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        products = Product.objects.all()
        total_products = products.count()
        
        self.stdout.write(f"Знайдено {total_products} товарів для обробки")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("РЕЖИМ ПОПЕРЕДНЬОГО ПЕРЕГЛЯДУ - зміни не будуть збережені"))
        
        processed_count = 0
        cleaned_count = 0
        deleted_count = 0
        
        # Обробляємо товари пакетами
        for start_idx in range(0, total_products, batch_size):
            end_idx = min(start_idx + batch_size, total_products)
            batch_products = products[start_idx:end_idx]
            
            self.stdout.write(f"Обробка товарів {start_idx + 1}-{end_idx} з {total_products}")
            
            for product in batch_products:
                try:
                    original_name = product.name
                    original_description = product.description
                    
                    cleaned_name = self.clean_name(original_name)
                    cleaned_description = self.clean_text(original_description)
                    
                    # Перевіряємо чи назва українська
                    if not self.is_ukrainian_text(cleaned_name):
                        if dry_run:
                            self.stdout.write(f"ВИДАЛИТИ: {original_name} (не українська назва)")
                        else:
                            product.delete()
                            deleted_count += 1
                            self.stdout.write(f"Видалено товар з неукраїнською назвою: {original_name}")
                        processed_count += 1
                        continue
                    
                    # Перевіряємо чи потрібне очищення
                    needs_cleaning = (
                        original_name != cleaned_name or 
                        original_description != cleaned_description
                    )
                    
                    if needs_cleaning:
                        if dry_run:
                            self.stdout.write(f"\n--- ТОВАР ID {product.id} ---")
                            self.stdout.write(f"Оригінальна назва: {original_name}")
                            self.stdout.write(f"Очищена назва: {cleaned_name}")
                            if original_description != cleaned_description:
                                self.stdout.write(f"Оригінальний опис: {original_description[:100]}...")
                                self.stdout.write(f"Очищений опис: {cleaned_description[:100]}...")
                        else:
                            with transaction.atomic():
                                product.name = cleaned_name
                                product.description = cleaned_description
                                product.save()
                                cleaned_count += 1
                                self.stdout.write(f"Очищено товар: {cleaned_name}")
                    
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
                    f"Потребують очищення: {cleaned_count}\n"
                    f"Будуть видалені: {deleted_count}\n"
                    f"Для застосування змін запустіть без --dry-run"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nОЧИЩЕННЯ ЗАВЕРШЕНО\n"
                    f"Оброблено: {processed_count}\n"
                    f"Очищено: {cleaned_count}\n"
                    f"Видалено: {deleted_count}"
                )
            )

    def is_ukrainian_text(self, text):
        """Перевіряє чи текст українською мовою"""
        if not text or len(text) < 3:
            return False
        
        # Підраховуємо українські символи
        ukrainian_chars = len(re.findall(r'[абвгґдежзиіїйклмнопрстуфхцчшщьюя]', text.lower()))
        total_chars = len(re.findall(r'[а-яёa-z]', text.lower()))
        
        # Якщо менше 3 українських символів - не українська
        if ukrainian_chars < 3:
            return False
        
        # Якщо є букви, то мінімум 60% повинні бути українськими
        if total_chars > 0:
            ukrainian_percentage = ukrainian_chars / total_chars
            return ukrainian_percentage >= 0.6
        
        return True

    def clean_text(self, text):
        """Очищає текст від HTML тегів та російських слів"""
        if not text:
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
            'решения', 'хранения', 'управления', 'солнечной', 'системе',
            'солнечные', 'панели', 'батарея', 'источник', 'питания', 'электричество',
            'напряжение', 'ток', 'мощность', 'энергия', 'система', 'устройство',
            'оборудование', 'установка', 'подключение', 'использование', 'работа'
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
        if not name:
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