import re
from django.core.management.base import BaseCommand
from django.db import transaction
from bs4 import BeautifulSoup
from mainapp.models import Product


class Command(BaseCommand):
    help = 'Очищує описи товарів від HTML тегів та залишає тільки українську мову'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати результат без збереження в базу',
        )

    def handle(self, *args, **options):
        products = Product.objects.all()
        
        for product in products:
            self.stdout.write(f"\n--- Обробка товару ID {product.id}: {product.name} ---")
            
            original_description = product.description
            cleaned_description = self.clean_description(original_description)
            
            if options['dry_run']:
                self.stdout.write(f"Оригінал: {original_description[:100]}...")
                self.stdout.write(f"Очищений: {cleaned_description[:100]}...")
            else:
                with transaction.atomic():
                    product.description = cleaned_description
                    product.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"Оновлено опис для товару: {product.name}")
                    )

        if not options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f"\nОброблено {products.count()} товарів")
            )

    def clean_description(self, text):
        """Очищає текст від HTML тегів та залишає тільки українську мову"""
        if not text:
            return text

        # Видаляємо HTML теги
        soup = BeautifulSoup(text, 'html.parser')
        clean_text = soup.get_text()

        # Заміняємо HTML entities
        clean_text = clean_text.replace('&ndash;', '–')
        clean_text = clean_text.replace('&mdash;', '—')
        clean_text = clean_text.replace('&nbsp;', ' ')
        clean_text = clean_text.replace('&deg;', '°')

        # Російські слова які точно треба видалити
        russian_words = [
            'гибридный', 'инвертор', 'технологией', 'современное', 'технологическое', 
            'решение', 'предназначенное', 'усовершенствования', 'обеспечивающее',
            'производительность', 'мощностью', 'работает', 'имеет', 'функцию',
            'отслеживания', 'точки', 'максимальной', 'мощности', 'обеспечивает',
            'оптимальный', 'сбор', 'энергии', 'солнечных', 'панелей', 'конструкция',
            'позволяет', 'использовать', 'низковольтные', 'аккумуляторы', 'изоляцию',
            'трансформатора', 'повышения', 'безопасности', 'эффективности', 
            'особенностей', 'способность', 'поддерживать', 'выход', 'до', 'номинальной',
            'любой', 'одной', 'фазе', 'ключевой', 'особенностью', 'является',
            'совместимость', 'имеющимися', 'системами', 'подключать', 'сети',
            'переменного', 'тока', 'делает', 'идеальным', 'выбором', 'модернизации',
            'старых', 'установок', 'меняя', 'новые', 'более', 'эффективные',
            'необходимости', 'полного', 'капитального', 'ремонта', 'кроме', 'того',
            'поддерживает', 'параллельное', 'подключение', 'единиц', 'как', 'работы',
            'так', 'автономной', 'такая', 'масштабируемость', 'решающее', 'значение',
            'расширения', 'возможностей', 'больших', 'установках', 'постепенного',
            'увеличения', 'при', 'кроме', 'того', 'устройство', 'может', 'параллельно',
            'управлять', 'несколькими', 'батареями', 'предлагая', 'надежные', 
            'решения', 'хранения', 'управления'
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
            if ukrainian_chars > 5:  # Мінімум 5 українських символів
                # Залишаємо українські символи, латинські (для моделей), цифри та пунктуацію
                cleaned_sentence = re.sub(
                    r'[^абвгґдежзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯa-zA-Z0-9\s.,;:!?\-—–()°%№]', 
                    '', 
                    sentence
                )
                
                # Очищаємо зайві пробіли
                cleaned_sentence = re.sub(r'\s+', ' ', cleaned_sentence).strip()
                
                if cleaned_sentence and len(cleaned_sentence) > 15:  # Мінімум 15 символів
                    ukrainian_sentences.append(cleaned_sentence)

        # Об'єднуємо речення
        result = '. '.join(ukrainian_sentences)
        if result and not result.endswith('.'):
            result += '.'
            
        # Очищаємо зайві пробіли та переноси рядків
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result 