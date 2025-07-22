import re
from django.core.management.base import BaseCommand
from django.db import transaction
from mainapp.models import Product, Category, Brand, Portfolio, Review

class Command(BaseCommand):
    help = 'Запобігає імпорту російського контенту - перевіряє та блокує'

    def add_arguments(self, parser):
        parser.add_argument(
            '--strict',
            action='store_true',
            help='Строга перевірка - блокує навіть підозрілий контент',
        )

    def handle(self, *args, **options):
        strict_mode = options['strict']
        
        self.stdout.write("🛡️ Перевірка на наявність російського контенту...")
        
        if strict_mode:
            self.stdout.write("⚠️ СТРОГИЙ РЕЖИМ - будь-який підозрілий контент буде позначений")
        
        total_russian = 0
        total_cleaned = 0
        
        # Перевіряємо товари
        self.stdout.write("\n📦 Перевірка товарів...")
        russian_products = self.check_products(strict_mode)
        total_russian += len(russian_products)
        
        # Перевіряємо категорії
        self.stdout.write("\n📂 Перевірка категорій...")
        russian_categories = self.check_categories(strict_mode)
        total_russian += len(russian_categories)
        
        # Перевіряємо бренди  
        self.stdout.write("\n🏷️ Перевірка брендів...")
        russian_brands = self.check_brands(strict_mode)
        total_russian += len(russian_brands)
        
        # Перевіряємо портфоліо
        self.stdout.write("\n🏗️ Перевірка портфоліо...")
        russian_portfolio = self.check_portfolio(strict_mode)
        total_russian += len(russian_portfolio)
        
        # Перевіряємо відгуки
        self.stdout.write("\n⭐ Перевірка відгуків...")
        russian_reviews = self.check_reviews(strict_mode)
        total_russian += len(russian_reviews)
        
        # Підсумки
        if total_russian > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️ ЗНАЙДЕНО РОСІЙСЬКИЙ КОНТЕНТ\n"
                    f"Товарів: {len(russian_products)}\n"
                    f"Категорій: {len(russian_categories)}\n"
                    f"Брендів: {len(russian_brands)}\n"
                    f"Портфоліо: {len(russian_portfolio)}\n"
                    f"Відгуків: {len(russian_reviews)}\n\n"
                    f"💡 Для очищення запустіть:\n"
                    f"python manage.py clean_russian_content"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ РОСІЙСЬКИЙ КОНТЕНТ НЕ ЗНАЙДЕНИЙ\n"
                    f"Всі тексти коректні! 🇺🇦"
                )
            )

    def is_definitely_russian(self, text):
        """Строга перевірка - тільки очевидно російський контент"""
        if not text:
            return False
        
        text = text.lower()
        
        # Російські символи (100% російська мова)
        if re.search(r'[ёъыэ]', text):
            return True
        
        # Специфічно російські слова (не використовуються в українській)
        definitely_russian = [
            'является', 'имеет', 'может', 'должен', 'будет', 'была', 'были', 'есть',
            'чтобы', 'потому', 'поэтому', 'если', 'когда', 'где', 'куда', 'откуда',
            'зачем', 'почему', 'сколько', 'который', 'какой', 'чей', 'такой', 
            'этот', 'тот', 'мой', 'твой', 'наш', 'ваш', 'свой', 'весь', 'каждый',
            'любой', 'другой', 'новый', 'старый', 'большой', 'маленький', 'хороший',
            'плохой', 'лучший', 'худший', 'первый', 'последний', 'следующий',
            'предыдущий', 'высокий', 'низкий', 'длинный', 'короткий', 'широкий',
            'узкий', 'толстый', 'тонкий', 'обеспечивает', 'позволяет', 'используется',
            'применяется', 'предназначен', 'разработан', 'создан', 'изготовлен',
            'производится', 'выпускается', 'гибридный', 'инвертор', 'солнечная',
            'батарея', 'энергия', 'мощность', 'напряжение', 'емкость', 'зарядка',
            'разрядка', 'контроллер', 'преобразователь', 'устройство', 'оборудование',
            'установка', 'подключение', 'эффективность', 'производительность',
            'надежность', 'качество', 'гарантия', 'сертификат', 'стандарт'
        ]
        
        for word in definitely_russian:
            if re.search(r'\b' + re.escape(word) + r'\b', text):
                return True
        
        # Російські граматичні конструкції
        russian_constructions = [
            r'\bчто\s+является\b',
            r'\bкоторый\s+имеет\b',
            r'\bто\s+что\b',
            r'\bдля\s+того\s+чтобы\b',
            r'\bв\s+связи\s+с\b',
            r'\bпо\s+сравнению\s+с\b',
        ]
        
        for pattern in russian_constructions:
            if re.search(pattern, text):
                return True
        
        return False

    def is_possibly_russian(self, text):
        """Менш строга перевірка - підозрілий контент"""
        if not text:
            return False
        
        if self.is_definitely_russian(text):
            return True
        
        text = text.lower()
        
        # Підозрілі слова (можуть бути російськими або українськими)
        suspicious_words = [
            'это', 'что', 'как', 'или', 'его', 'ее', 'их', 'от', 'до', 'при',
            'без', 'под', 'над', 'про', 'через', 'после', 'перед', 'вместо',
            'кроме', 'среди', 'между', 'внутри', 'снаружи', 'около', 'возле',
            'вокруг', 'против', 'благодаря', 'согласно', 'вследствие', 'несмотря'
        ]
        
        suspicious_count = 0
        for word in suspicious_words:
            if re.search(r'\b' + re.escape(word) + r'\b', text):
                suspicious_count += 1
        
        # Якщо більше 3 підозрілих слів - можливо російська
        return suspicious_count > 3

    def check_products(self, strict_mode):
        """Перевірка товарів"""
        products = Product.objects.all()
        russian_products = []
        
        for product in products:
            text = f"{product.name} {product.description}"
            
            if strict_mode:
                is_russian = self.is_possibly_russian(text)
            else:
                is_russian = self.is_definitely_russian(text)
            
            if is_russian:
                russian_products.append(product)
                self.stdout.write(f"   ❌ ID {product.id}: {product.name[:50]}...")
        
        if not russian_products:
            self.stdout.write("   ✅ Російський контент не знайдений")
        
        return russian_products

    def check_categories(self, strict_mode):
        """Перевірка категорій"""
        categories = Category.objects.all()
        russian_categories = []
        
        for category in categories:
            text = f"{category.name} {category.description}"
            
            if strict_mode:
                is_russian = self.is_possibly_russian(text)
            else:
                is_russian = self.is_definitely_russian(text)
            
            if is_russian:
                russian_categories.append(category)
                self.stdout.write(f"   ❌ Категорія: {category.name}")
        
        if not russian_categories:
            self.stdout.write("   ✅ Російський контент не знайдений")
        
        return russian_categories

    def check_brands(self, strict_mode):
        """Перевірка брендів"""
        brands = Brand.objects.all()
        russian_brands = []
        
        for brand in brands:
            text = f"{brand.name} {brand.description}"
            
            if strict_mode:
                is_russian = self.is_possibly_russian(text)
            else:
                is_russian = self.is_definitely_russian(text)
            
            if is_russian:
                russian_brands.append(brand)
                self.stdout.write(f"   ❌ Бренд: {brand.name}")
        
        if not russian_brands:
            self.stdout.write("   ✅ Російський контент не знайдений")
        
        return russian_brands

    def check_portfolio(self, strict_mode):
        """Перевірка портфоліо"""
        portfolios = Portfolio.objects.all()
        russian_portfolio = []
        
        for portfolio in portfolios:
            text = f"{portfolio.title} {portfolio.description}"
            
            if strict_mode:
                is_russian = self.is_possibly_russian(text)
            else:
                is_russian = self.is_definitely_russian(text)
            
            if is_russian:
                russian_portfolio.append(portfolio)
                self.stdout.write(f"   ❌ Проєкт: {portfolio.title}")
        
        if not russian_portfolio:
            self.stdout.write("   ✅ Російський контент не знайдений")
        
        return russian_portfolio

    def check_reviews(self, strict_mode):
        """Перевірка відгуків"""
        reviews = Review.objects.all()
        russian_reviews = []
        
        for review in reviews:
            if strict_mode:
                is_russian = self.is_possibly_russian(review.review_text)
            else:
                is_russian = self.is_definitely_russian(review.review_text)
            
            if is_russian:
                russian_reviews.append(review)
                self.stdout.write(f"   ❌ Відгук від: {review.client_name}")
        
        if not russian_reviews:
            self.stdout.write("   ✅ Російський контент не знайдений")
        
        return russian_reviews 