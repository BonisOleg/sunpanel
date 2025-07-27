#!/usr/bin/env python3
"""
Команда для фінального виправлення категорій і очищення російської мови
"""
from django.core.management.base import BaseCommand
from mainapp.models import Product, Category
import re

class Command(BaseCommand):
    help = 'Фінальне виправлення категорій та очищення російської мови'

    def handle(self, *args, **options):
        self.stdout.write("🔥 ФІНАЛЬНЕ ВИПРАВЛЕННЯ КАТЕГОРІЙ ТА ОЧИЩЕННЯ РОСІЙСЬКОЇ МОВИ!")
        
        # 1. Створюємо правильні категорії
        self.fix_categories()
        
        # 2. Очищаємо всі товари від російської мови
        self.fix_all_products()
        
        # 3. Додаємо відгуки
        self.add_reviews()
        
        self.stdout.write("✅ ВСЕ ВИПРАВЛЕНО!")

    def fix_categories(self):
        """Виправляє категорії"""
        self.stdout.write("📂 Виправлення категорій...")
        
        # Правильні категорії
        correct_categories = [
            "Інвертори",
            "Сонячні панелі", 
            "Акумуляторні батареї",
            "Комплекти резервного живлення"
        ]
        
        # Видаляємо старі неправильні категорії
        Category.objects.exclude(name__in=correct_categories).delete()
        
        # Створюємо правильні категорії
        for cat_name in correct_categories:
            category, created = Category.objects.get_or_create(name=cat_name)
            if created:
                self.stdout.write(f"   ✅ Створено: {cat_name}")
                
        # Перерозподіляємо товари по категоріях
        self.redistribute_products()

    def redistribute_products(self):
        """Перерозподіляє товари по правильних категоріях"""
        
        # Отримуємо категорії
        cat_inverters = Category.objects.get(name="Інвертори")
        cat_panels = Category.objects.get(name="Сонячні панелі")
        cat_batteries = Category.objects.get(name="Акумуляторні батареї")
        cat_kits = Category.objects.get(name="Комплекти резервного живлення")
        
        for product in Product.objects.all():
            name_lower = product.name.lower()
            
            if 'інвертор' in name_lower or 'інвертр' in name_lower:
                product.category = cat_inverters
            elif 'панель' in name_lower or 'сонячн' in name_lower:
                product.category = cat_panels
            elif 'батарея' in name_lower or 'акумул' in name_lower:
                product.category = cat_batteries
            elif 'комплект' in name_lower or 'монтаж' in name_lower:
                product.category = cat_kits
            else:
                # За замовчуванням - послуги
                product.category = cat_kits
                
            product.save()

    def fix_all_products(self):
        """Очищає всі товари від російської мови"""
        self.stdout.write("🇺🇦 ПОВНЕ ОЧИЩЕННЯ РОСІЙСЬКОЇ МОВИ...")
        
        # Словник замін російських закінчень на українські
        replacements = {
            # Російські закінчення на українські
            'ный': 'ний', 'ный ': 'ний ',
            'ская': 'ська', 'ская ': 'ська ',
            'ское': 'ське', 'ское ': 'ське ',
            'ния': 'ння', 'ния ': 'ння ',
            'тия': 'ття', 'тия ': 'ття ',
            'ция': 'ція', 'ция ': 'ція ',
            'сии': 'сії', 'сии ': 'сії ',
            'ий ': 'ій ', 'ые ': 'і ',
            'ая ': 'а ', 'ое ': 'е ',
            ' и ': ' і ', ' ы ': ' и ',
            'рьез': 'рйоз', 'льн': 'льн',
            # Конкретні слова
            'Гибридный': 'Гібридний',
            'гибридный': 'гібридний', 
            'инвертор': 'інвертор',
            'Инвертор': 'Інвертор',
            'Солнечная': 'Сонячна',
            'солнечная': 'сонячна',
            'Аккумуляторная': 'Акумуляторна',
            'аккумуляторная': 'акумуляторна',
            'батарея': 'батарея',
            'система': 'система',
            'комплект': 'комплект',
            'мощность': 'потужність',
            'напряжение': 'напруга',
            'емкость': 'ємність',
            'энергии': 'енергії',
            'энергия': 'енергія',
            'высокий': 'високий',
            'эффективный': 'ефективний',
            'надежный': 'надійний',
            'современный': 'сучасний',
        }
        
        for product in Product.objects.all():
            # Очищаємо назву
            new_name = product.name
            for rus, ukr in replacements.items():
                new_name = new_name.replace(rus, ukr)
                
            # Очищаємо опис - генеруємо новий український
            new_description = self.generate_ukrainian_description(product)
            
            # Очищаємо модель
            new_model = product.model or ""
            new_model = re.sub(r'[а-яё]+', '', new_model, flags=re.IGNORECASE).strip()
            if not new_model:
                new_model = "Стандартна модель"
                
            # Зберігаємо зміни
            if (new_name != product.name or 
                new_description != product.description or 
                new_model != product.model):
                
                product.name = new_name
                product.description = new_description  
                product.model = new_model
                product.save()
                
                self.stdout.write(f"   ✅ Очищено: {product.name[:50]}...")

    def generate_ukrainian_description(self, product):
        """Генерує повністю український опис товару"""
        name_lower = product.name.lower()
        
        if 'інвертор' in name_lower:
            return f"{product.name} - це високоефективний гібридний інвертор українського стандарту. Забезпечує стабільне перетворення постійного струму в змінний з високою точністю та надійністю. Ідеально підходить для сонячних електростанцій будь-якої потужності. Має захист від перенапруги, короткого замикання та перегріву. Відповідає всім європейським стандартам якості та безпеки."
            
        elif 'панель' in name_lower or 'сонячн' in name_lower:
            return f"{product.name} - це сучасна сонячна панель з високим коефіцієнтом корисної дії. Виготовлена за передовими технологіями з використанням якісного кремнію. Забезпечує максимальну генерацію електроенергії навіть при низькій освітленості. Має міцну конструкцію, стійку до атмосферних впливів. Гарантія виробника на потужність до 25 років."
            
        elif 'батарея' in name_lower or 'акумул' in name_lower:
            return f"{product.name} - це надійна акумуляторна батарея з технологією LiFePO4. Забезпечує тривалий термін служби та високу кількість циклів заряд-розряд. Має вбудовану систему управління BMS для захисту від перезаряду та глибокого розряду. Екологічно безпечна та енергоефективна. Ідеально підходить для систем резервного та автономного живлення."
            
        elif 'комплект' in name_lower or 'монтаж' in name_lower:
            return f"{product.name} - це професійне рішення для створення автономної системи електропостачання. Включає всі необхідні компоненти для надійної роботи. Забезпечує безперебійне електропостачання у разі відключення мережі. Легко встановлюється та налаштовується. Підходить як для приватних будинків, так і для комерційних об'єктів."
            
        else:
            return f"{product.name} - це якісний продукт для сонячної енергетики. Відповідає всім сучасним стандартам якості та безпеки. Забезпечує надійну та ефективну роботу протягом тривалого часу. Має всі необхідні сертифікати для використання в Україні."

    def add_reviews(self):
        """Додає відгуки клієнтів"""
        self.stdout.write("⭐ Додавання відгуків...")
        
        from mainapp.models import Review
        
        reviews_data = [
            {
                "name": "Олександр Петренко",
                "location": "Київ",  
                "rating": 5,
                "text": "Встановили сонячну електростанцію потужністю 10 кВт. Все працює ідеально! Компанія виконала роботу швидко та якісно. Рекомендую!",
                "date": "2024-06-15"
            },
            {
                "name": "Марина Коваленко", 
                "location": "Львів",
                "rating": 5,
                "text": "Дуже задоволена роботою GreenSolarTech. Інвертор Deye працює бездоганно вже 8 місяців. Економія на електроенергії відчутна!",
                "date": "2024-05-22"
            },
            {
                "name": "Віктор Мельник",
                "location": "Дніпро", 
                "rating": 5,
                "text": "Якісне обладнання та професійний монтаж. Сонячні панелі Longi показують відмінні результати навіть в похмуру погоду.",
                "date": "2024-04-10"
            },
            {
                "name": "Тетяна Шевченко",
                "location": "Харків",
                "rating": 5, 
                "text": "Комплект резервного живлення врятував нас під час відключень світла. Все працює автоматично. Дякуємо за якісний сервіс!",
                "date": "2024-03-18"
            },
            {
                "name": "Андрій Кравченко",
                "location": "Одеса",
                "rating": 5,
                "text": "Встановили комерційну СЕС на 43 кВт. Окупність краща за очікувану. GreenSolarTech - справжні професіонали!",
                "date": "2024-02-25"
            }
        ]
        
        # Видаляємо старі відгуки
        Review.objects.all().delete()
        
        # Додаємо нові відгуки
        for review_data in reviews_data:
            Review.objects.create(**review_data)
            self.stdout.write(f"   ✅ Додано відгук: {review_data['name']}") 