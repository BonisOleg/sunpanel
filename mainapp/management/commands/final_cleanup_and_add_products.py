import re
from django.core.management.base import BaseCommand
from django.db import transaction
from mainapp.models import Product, Category, Brand

class Command(BaseCommand):
    help = 'Фінальне очищення граматичних помилок та додавання товарів до 41'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати результат без збереження в базу',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        current_count = Product.objects.count()
        target_count = 41
        
        self.stdout.write(f"Поточна кількість товарів: {current_count}")
        self.stdout.write(f"Цільова кількість товарів: {target_count}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("РЕЖИМ ПОПЕРЕДНЬОГО ПЕРЕГЛЯДУ - зміни не будуть збережені"))
        
        # Крок 1: Фінальне виправлення граматичних помилок
        self.stdout.write("\n✏️ Крок 1: Фінальне виправлення граматичних помилок...")
        fixed_count = self.final_grammar_fixes(dry_run)
        
        # Крок 2: Додавання недостаючих товарів
        if current_count < target_count:
            needed = target_count - current_count
            self.stdout.write(f"\n➕ Крок 2: Додавання {needed} недостаючих товарів...")
            added_count = self.add_missing_products(needed, dry_run)
        else:
            added_count = 0
        
        # Підсумки
        final_count = current_count + added_count if not dry_run else current_count + added_count
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\nПОПЕРЕДНІЙ ПЕРЕГЛЯД ЗАВЕРШЕНО\n"
                    f"Поточна кількість: {current_count}\n"
                    f"Буде виправлено помилок: {fixed_count}\n"
                    f"Буде додано товарів: {added_count}\n"
                    f"Фінальна кількість: {final_count}\n"
                    f"Для застосування змін запустіть без --dry-run"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nФІНАЛЬНЕ ОЧИЩЕННЯ ЗАВЕРШЕНО\n"
                    f"Виправлено помилок: {fixed_count}\n"
                    f"Додано товарів: {added_count}\n"
                    f"Фінальна кількість товарів: {Product.objects.count()}"
                )
            )

    def final_grammar_fixes(self, dry_run):
        """Фінальне виправлення граматичних помилок"""
        fixed_count = 0
        
        # Додаткові граматичні виправлення
        final_fixes = {
            'лектростанций': 'електростанцій',
            'Всоковольтная': 'Високовольтна',
            'всоковольтная': 'високовольтна',
            'система зберігання енергії': 'система зберігання енергії',
            'модулів 100А': 'модулів 100 А',
            'модулів 100A': 'модулів 100 А',
            'кВт год': 'кВт·год',
            'А год': 'А·год',
            'квтгод': 'кВт·год',
            'агод': 'А·год',
            'рік': 'год',
            'років': 'годин',
            'Акумуляторная': 'Акумуляторна',
            'акумуляторная': 'акумуляторна',
            'kWt': 'кВт',
            'kWh': 'кВт·год',
            'Wt': 'Вт',
        }
        
        products = Product.objects.all()
        
        for product in products:
            original_name = product.name
            original_description = product.description
            
            # Виправляємо назву
            fixed_name = self.apply_final_fixes(original_name, final_fixes)
            
            # Виправляємо опис
            fixed_description = self.apply_final_fixes(original_description, final_fixes)
            
            # Перевіряємо чи потрібні зміни
            if original_name != fixed_name or original_description != fixed_description:
                if dry_run:
                    if original_name != fixed_name:
                        self.stdout.write(f"ВИПРАВИТИ: {original_name} → {fixed_name}")
                else:
                    with transaction.atomic():
                        product.name = fixed_name
                        product.description = fixed_description
                        product.save()
                        self.stdout.write(f"Виправлено: {fixed_name}")
                fixed_count += 1
        
        return fixed_count

    def apply_final_fixes(self, text, fixes_dict):
        """Застосовує фінальні граматичні виправлення"""
        if not text:
            return text
        
        result = str(text)
        
        # Застосовуємо виправлення
        for wrong, correct in fixes_dict.items():
            result = result.replace(wrong, correct)
        
        # Очищаємо зайві пробіли
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result

    def add_missing_products(self, needed_count, dry_run):
        """Додає недостаючі товари"""
        added_count = 0
        
        # Отримуємо або створюємо категорії та бренди
        default_category, _ = Category.objects.get_or_create(
            name="Сонячні панелі",
            defaults={'description': 'Сонячні панелі для енергетичних систем'}
        )
        
        longi_brand, _ = Brand.objects.get_or_create(
            name="LONGi Solar",
            defaults={'description': 'Провідний виробник сонячних панелей'}
        )
        
        # Список додаткових товарів
        additional_products = [
            {
                'name': 'Сонячна панель LONGi Solar LR4-60HPH-370M монокристалічна 370 Вт',
                'description': 'Монокристалічна сонячна панель потужністю 370 Вт з високою ефективністю та надійністю. Ідеально підходить для житлових та комерційних сонячних систем.',
                'price': 8500.00,
                'category': default_category,
                'brand': longi_brand,
                'model': 'LR4-60HPH-370M'
            },
            {
                'name': 'Сонячна панель LONGi Solar LR5-54HTH-430M Black Frame монокристалічна 430 Вт',
                'description': 'Монокристалічна сонячна панель з чорною рамкою потужністю 430 Вт. Елегантний дизайн та висока продуктивність для сучасних енергетичних рішень.',
                'price': 10200.00,
                'category': default_category,
                'brand': longi_brand,
                'model': 'LR5-54HTH-430M'
            },
            {
                'name': 'Сонячна панель LONGi Solar LR5-66HTH-525M монокристалічна 525 Вт',
                'description': 'Потужна монокристалічна сонячна панель 525 Вт для великих енергетичних проектів. Забезпечує максимальну віддачу енергії з мінімальною площею.',
                'price': 12300.00,
                'category': default_category,
                'brand': longi_brand,
                'model': 'LR5-66HTH-525M'
            },
            {
                'name': 'Сонячна панель LONGi Solar LR7-72HTH-600M біфаціальна 600 Вт',
                'description': 'Біфаціальна сонячна панель потужністю 600 Вт з можливістю генерації енергії з обох сторін. Інноваційна технологія для максимальної ефективності.',
                'price': 14800.00,
                'category': default_category,
                'brand': longi_brand,
                'model': 'LR7-72HTH-600M'
            },
        ]
        
        for i, product_data in enumerate(additional_products[:needed_count]):
            if dry_run:
                self.stdout.write(f"ДОДАТИ: {product_data['name']} - ₴{product_data['price']}")
            else:
                with transaction.atomic():
                    product = Product.objects.create(
                        name=product_data['name'],
                        description=product_data['description'],
                        price=product_data['price'],
                        category=product_data['category'],
                        brand=product_data['brand'],
                        model=product_data['model'],
                        in_stock=True
                    )
                    self.stdout.write(f"Додано: {product.name}")
            added_count += 1
        
        return added_count 