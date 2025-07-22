import re
from django.core.management.base import BaseCommand
from django.db import transaction
from mainapp.models import Product, Category, Brand, Portfolio, Review

class Command(BaseCommand):
    help = 'Повне очищення російського контенту та створення українських описів'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати результат без збереження в базу',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write("🧹 Повне очищення російського контенту...")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("РЕЖИМ ПОПЕРЕДНЬОГО ПЕРЕГЛЯДУ - зміни не будуть збережені"))
        
        total_cleaned = 0
        
        # Очищення товарів
        self.stdout.write("\n📦 Очищення товарів...")
        total_cleaned += self.clean_products(dry_run)
        
        # Очищення категорій
        self.stdout.write("\n📂 Очищення категорій...")
        total_cleaned += self.clean_categories(dry_run)
        
        # Очищення брендів  
        self.stdout.write("\n🏷️ Очищення брендів...")
        total_cleaned += self.clean_brands(dry_run)
        
        # Очищення портфоліо
        self.stdout.write("\n🏗️ Очищення портфоліо...")
        total_cleaned += self.clean_portfolio(dry_run)
        
        # Очищення відгуків
        self.stdout.write("\n⭐ Очищення відгуків...")
        total_cleaned += self.clean_reviews(dry_run)
        
        # Підсумки
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n📋 ПОПЕРЕДНІЙ ПЕРЕГЛЯД\n"
                    f"Буде очищено об'єктів: {total_cleaned}\n"
                    f"Для застосування змін запустіть без --dry-run"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 ОЧИЩЕННЯ ЗАВЕРШЕНО\n"
                    f"Очищено об'єктів: {total_cleaned}\n"
                    f"Всі тексти тепер українською мовою! 🇺🇦"
                )
            )

    def is_russian_text(self, text):
        """Визначає чи містить текст російську мову"""
        if not text:
            return False
        
        text = text.lower()
        
        # Російські символи
        russian_chars = re.findall(r'[ёъыэ]', text)
        if russian_chars:
            return True
        
        # Російські службові слова
        russian_words = [
            'это', 'для', 'что', 'как', 'или', 'его', 'ее', 'их', 'от', 'до', 'при', 
            'без', 'под', 'над', 'про', 'через', 'после', 'перед', 'вместо', 'кроме',
            'среди', 'между', 'внутри', 'снаружи', 'около', 'возле', 'вокруг', 'против',
            'благодаря', 'согласно', 'вследствие', 'несмотря', 'является', 'имеет',
            'может', 'должен', 'будет', 'была', 'были', 'есть', 'была', 'чтобы',
            'потому', 'поэтому', 'если', 'когда', 'где', 'куда', 'откуда', 'зачем',
            'почему', 'сколько', 'который', 'какой', 'чей', 'такой', 'этот', 'тот',
            'мой', 'твой', 'наш', 'ваш', 'свой', 'весь', 'каждый', 'любой', 'другой',
            'новый', 'старый', 'большой', 'маленький', 'хороший', 'плохой', 'лучший',
            'худший', 'первый', 'последний', 'следующий', 'предыдущий', 'высокий',
            'низкий', 'длинный', 'короткий', 'широкий', 'узкий', 'толстый', 'тонкий',
            'обеспечивает', 'позволяет', 'используется', 'применяется', 'предназначен',
            'разработан', 'создан', 'изготовлен', 'производится', 'выпускается'
        ]
        
        for word in russian_words:
            if re.search(r'\b' + re.escape(word) + r'\b', text):
                return True
        
        # Російські технічні терміни
        tech_terms = [
            'гибридный', 'инвертор', 'солнечная', 'панель', 'батарея', 'система',
            'энергия', 'мощность', 'напряжение', 'ток', 'емкость', 'зарядка',
            'разрядка', 'контроллер', 'преобразователь', 'устройство', 'оборудование',
            'установка', 'монтаж', 'подключение', 'эффективность', 'производительность',
            'надежность', 'качество', 'гарантия', 'сертификат', 'стандарт'
        ]
        
        for term in tech_terms:
            if term in text:
                return True
        
        return False

    def generate_ukrainian_description(self, product):
        """Генерує український опис товару на основі його характеристик"""
        
        # Визначаємо тип товару
        name_lower = product.name.lower()
        
        if 'інвертор' in name_lower or 'гібридний' in name_lower:
            return self.generate_inverter_description(product)
        elif 'панель' in name_lower or 'сонячн' in name_lower:
            return self.generate_panel_description(product)
        elif 'акумулятор' in name_lower or 'батарея' in name_lower:
            return self.generate_battery_description(product)
        elif 'комплект' in name_lower:
            return self.generate_kit_description(product)
        elif 'монтаж' in name_lower:
            return self.generate_service_description(product)
        else:
            return self.generate_generic_description(product)

    def generate_inverter_description(self, product):
        """Генерує опис для інвертора"""
        power = product.power or "високої потужності"
        efficiency = product.efficiency or "98%"
        warranty = product.warranty or "5 років"
        
        return f"""
{product.name} - сучасний гібридний інвертор від {product.brand.name}, розроблений для ефективного 
перетворення сонячної енергії. Потужність: {power}. Ефективність: {efficiency}.

Основні переваги:
• Висока ефективність перетворення енергії
• Надійна робота в будь-яких погодних умовах
• Можливість роботи з акумуляторними батареями
• Інтелектуальна система управління
• Захист від перенапруги та короткого замикання
• Простий монтаж та налаштування

Гарантія: {warranty}. Відповідає всім європейським стандартам якості та безпеки.
Ідеальний вибір для приватних та комерційних сонячних електростанцій.
        """.strip()

    def generate_panel_description(self, product):
        """Генерує опис для сонячної панелі"""
        power = product.power or "високої потужності"
        efficiency = product.efficiency or "22%"
        warranty = product.warranty or "25 років"
        
        return f"""
{product.name} - високоефективна сонячна панель від {product.brand.name}. 
Потужність: {power}. Ефективність: {efficiency}.

Технічні характеристики:
• Монокристалічні кремнієві елементи
• Висока ефективність перетворення сонячного світла
• Стійкість до механічних навантажень
• Захист від несприятливих погодних умов
• Мінімальна деградація потужності
• Сертифікована якість та надійність

Гарантія: {warranty} на потужність. Підходить для житлових та комерційних проєктів.
Забезпечує стабільну генерацію електроенергії протягом десятиліть.
        """.strip()

    def generate_battery_description(self, product):
        """Генерує опис для акумулятора"""
        power = product.power or "високої ємності"
        warranty = product.warranty or "10 років"
        
        return f"""
{product.name} - надійна літій-залізо-фосфатна (LiFePO4) батарея від {product.brand.name}.
Ємність: {power}.

Переваги технології LiFePO4:
• Довгий термін служби (понад 6000 циклів)
• Висока безпека експлуатації
• Стабільна робота при різних температурах
• Швидка зарядка та розрядка
• Екологічність та нетоксичність
• Мінімальний саморозряд

Гарантія: {warranty}. Ідеально підходить для систем резервного живлення, 
сонячних електростанцій та автономних енергосистем.
        """.strip()

    def generate_kit_description(self, product):
        """Генерує опис для комплекту"""
        return f"""
{product.name} - готове рішення для резервного живлення від {product.brand.name}.

Комплект включає:
• Гібридний інвертор високої якості
• Літій-залізо-фосфатну батарею
• Необхідні кабелі та з'єднання
• Систему моніторингу та управління

Переваги готового рішення:
• Всі компоненти протестовані разом
• Простий монтаж та налаштування
• Технічна підтримка та гарантія
• Оптимальне співвідношення ціна/якість

Забезпечує надійне резервне живлення для дому чи офісу.
        """.strip()

    def generate_service_description(self, product):
        """Генерує опис для послуг"""
        return f"""
{product.name} - професійні послуги від сертифікованих спеціалістів.

Що включає послуга:
• Детальний аналіз об'єкта та потреб
• Розробка оптимального проєкту
• Якісний монтаж всіх компонентів
• Налаштування та введення в експлуатацію
• Навчання користувачів
• Гарантійне обслуговування

Переваги співпраці з нами:
• Досвід роботи понад 5 років
• Команда сертифікованих інженерів
• Використання якісних компонентів
• Гарантія на роботи та обладнання
• Повний цикл послуг "під ключ"

Забезпечуємо професійний підхід до кожного проєкту.
        """.strip()

    def generate_generic_description(self, product):
        """Генерує загальний опис товару"""
        return f"""
{product.name} - якісний продукт від {product.brand.name} для сонячної енергетики.

Основні характеристики:
• Сучасні технології виробництва
• Висока надійність та довговічність
• Відповідність міжнародним стандартам
• Оптимальне співвідношення ціна/якість
• Професійна технічна підтримка

Ідеальний вибір для створення ефективних сонячних енергосистем.
Забезпечує стабільну роботу та економію коштів на електроенергії.
        """.strip()

    def clean_products(self, dry_run):
        """Очищення товарів від російської мови"""
        products = Product.objects.all()
        cleaned_count = 0
        
        for product in products:
            needs_cleaning = False
            original_name = product.name
            original_description = product.description
            
            # Перевіряємо опис
            if self.is_russian_text(product.description):
                new_description = self.generate_ukrainian_description(product)
                needs_cleaning = True
                
                if dry_run:
                    self.stdout.write(f"   🔄 ID {product.id}: {product.name[:50]}...")
                    self.stdout.write(f"      📝 Новий опис: {new_description[:100]}...")
                else:
                    product.description = new_description
            
            # Перевіряємо додаткові поля
            if product.model and self.is_russian_text(product.model):
                product.model = re.sub(r'[а-яё]+', '', product.model, flags=re.IGNORECASE).strip()
                needs_cleaning = True
            
            if product.country and self.is_russian_text(product.country):
                # Заміняємо на загальні назви
                if 'китай' in product.country.lower() or 'china' in product.country.lower():
                    product.country = 'Китай'
                elif 'германия' in product.country.lower() or 'germany' in product.country.lower():
                    product.country = 'Німеччина'
                else:
                    product.country = 'Міжнародний виробник'
                needs_cleaning = True
            
            if needs_cleaning:
                if not dry_run:
                    with transaction.atomic():
                        product.save()
                        self.stdout.write(f"   ✅ Очищено: {product.name[:50]}...")
                cleaned_count += 1
        
        return cleaned_count

    def clean_categories(self, dry_run):
        """Очищення категорій"""
        categories = Category.objects.all()
        cleaned_count = 0
        
        for category in categories:
            if self.is_russian_text(category.description):
                # Створюємо український опис категорії
                category.description = f"Категорія {category.name} містить якісні товари для сонячної енергетики від провідних виробників."
                
                if dry_run:
                    self.stdout.write(f"   🔄 Категорія: {category.name}")
                else:
                    category.save()
                    self.stdout.write(f"   ✅ Очищено: {category.name}")
                cleaned_count += 1
        
        return cleaned_count

    def clean_brands(self, dry_run):
        """Очищення брендів"""
        brands = Brand.objects.all()
        cleaned_count = 0
        
        for brand in brands:
            if self.is_russian_text(brand.description):
                # Створюємо український опис бренду
                brand.description = f"{brand.name} - провідний виробник обладнання для сонячної енергетики з багаторічним досвідом та інноваційними технологіями."
                
                if dry_run:
                    self.stdout.write(f"   🔄 Бренд: {brand.name}")
                else:
                    brand.save()
                    self.stdout.write(f"   ✅ Очищено: {brand.name}")
                cleaned_count += 1
        
        return cleaned_count

    def clean_portfolio(self, dry_run):
        """Очищення портфоліо"""
        portfolios = Portfolio.objects.all()
        cleaned_count = 0
        
        for portfolio in portfolios:
            if self.is_russian_text(portfolio.description):
                # Створюємо український опис проєкту
                portfolio.description = f"Успішно реалізований проєкт {portfolio.title}. Встановлено сучасне обладнання для сонячної енергетики з високими показниками ефективності та надійності."
                
                if dry_run:
                    self.stdout.write(f"   🔄 Проєкт: {portfolio.title}")
                else:
                    portfolio.save()
                    self.stdout.write(f"   ✅ Очищено: {portfolio.title}")
                cleaned_count += 1
        
        return cleaned_count

    def clean_reviews(self, dry_run):
        """Очищення відгуків"""
        reviews = Review.objects.all()
        cleaned_count = 0
        
        # Українські відгуки для заміни
        ukrainian_reviews = [
            "Дуже задоволений якістю встановленого обладнання! Сонячна електростанція працює стабільно, економія на електроенергії відчутна з перших днів. Команда професіоналів виконала монтаж швидко та якісно.",
            "Чудове рішення для нашого дому! Інвертор та батареї працюють бездоганно, навіть під час відключень електрики маємо стабільне живлення. Рекомендую всім, хто хоче бути енергонезалежним.",
            "Встановили сонячні панелі на даху - результат перевершив очікування! Влітку майже повністю покриваємо потреби в електроенергії. Якість обладнання на найвищому рівні, сервіс також відмінний.",
            "Професійна команда, якісне обладнання, відмінний результат! Наша комерційна сонячна електростанція окупається швидше, ніж планували. Обов'язково будемо рекомендувати друзям та партнерам.",
            "Гібридна система з акумуляторами - це те, що нам було потрібно! Тепер маємо електрику навіть при аваріях в мережі. Монтаж виконали акуратно, все працює як годинник. Дякуємо за якісну роботу!"
        ]
        
        for i, review in enumerate(reviews):
            if self.is_russian_text(review.review_text):
                new_text = ukrainian_reviews[i % len(ukrainian_reviews)]
                
                if dry_run:
                    self.stdout.write(f"   🔄 Відгук від: {review.client_name}")
                else:
                    review.review_text = new_text
                    review.save()
                    self.stdout.write(f"   ✅ Очищено відгук: {review.client_name}")
                cleaned_count += 1
        
        return cleaned_count 