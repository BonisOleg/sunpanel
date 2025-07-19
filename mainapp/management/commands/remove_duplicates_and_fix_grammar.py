import re
from django.core.management.base import BaseCommand
from django.db import transaction
from mainapp.models import Product
from collections import defaultdict

class Command(BaseCommand):
    help = 'Видаляє дублікати товарів та виправляє граматичні помилки'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати результат без збереження в базу',
        )
        parser.add_argument(
            '--target-count',
            type=int,
            default=41,
            help='Цільова кількість товарів (за замовчуванням 41)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        target_count = options['target_count']
        
        products = Product.objects.all()
        total_products = products.count()
        
        self.stdout.write(f"Поточна кількість товарів: {total_products}")
        self.stdout.write(f"Цільова кількість товарів: {target_count}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("РЕЖИМ ПОПЕРЕДНЬОГО ПЕРЕГЛЯДУ - зміни не будуть збережені"))
        
        # Крок 1: Видаляємо точні дублікати
        self.stdout.write("\n🔍 Крок 1: Видалення точних дублікатів...")
        deleted_duplicates = self.remove_exact_duplicates(dry_run)
        
        # Крок 2: Виправляємо граматичні помилки
        self.stdout.write("\n✏️ Крок 2: Виправлення граматичних помилок...")
        fixed_grammar = self.fix_grammar_errors(dry_run)
        
        # Крок 3: Видаляємо зайві товари якщо потрібно
        remaining_products = Product.objects.count() if not dry_run else total_products - deleted_duplicates
        if remaining_products > target_count:
            self.stdout.write(f"\n🗑️ Крок 3: Видалення зайвих товарів (потрібно видалити {remaining_products - target_count})...")
            deleted_extra = self.remove_extra_products(target_count, dry_run)
        else:
            deleted_extra = 0
        
        # Підсумки
        final_count = remaining_products - deleted_extra if not dry_run else remaining_products - deleted_extra
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\nПОПЕРЕДНІЙ ПЕРЕГЛЯД ЗАВЕРШЕНО\n"
                    f"Поточна кількість: {total_products}\n"
                    f"Буде видалено дублікатів: {deleted_duplicates}\n"
                    f"Буде виправлено граматичних помилок: {fixed_grammar}\n"
                    f"Буде видалено зайвих: {deleted_extra}\n"
                    f"Фінальна кількість: {final_count}\n"
                    f"Для застосування змін запустіть без --dry-run"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nОЧИЩЕННЯ ЗАВЕРШЕНО\n"
                    f"Видалено дублікатів: {deleted_duplicates}\n"
                    f"Виправлено граматичних помилок: {fixed_grammar}\n"
                    f"Видалено зайвих: {deleted_extra}\n"
                    f"Фінальна кількість товарів: {Product.objects.count()}"
                )
            )

    def remove_exact_duplicates(self, dry_run):
        """Видаляє точні дублікати товарів"""
        # Групуємо товари за назвою (в нижньому регістрі)
        product_groups = defaultdict(list)
        
        for product in Product.objects.all():
            normalized_name = product.name.lower().strip()
            product_groups[normalized_name].append(product)
        
        deleted_count = 0
        
        for name, products in product_groups.items():
            if len(products) > 1:
                # Залишаємо перший товар, видаляємо решту
                products_to_delete = products[1:]
                
                for product in products_to_delete:
                    if dry_run:
                        self.stdout.write(f"ВИДАЛИТИ дублікат: {product.name} (ID: {product.id})")
                    else:
                        product.delete()
                        self.stdout.write(f"Видалено дублікат: {product.name}")
                    deleted_count += 1
        
        return deleted_count

    def fix_grammar_errors(self, dry_run):
        """Виправляє граматичні помилки в назвах та описах"""
        fixed_count = 0
        
        # Словник граматичних виправлень
        grammar_fixes = {
            # Виправлення основних помилок
            'солнечнх': 'сонячних',
            'електростанций': 'електростанцій',
            'електростанцій': 'електростанцій',
            'всоковольтная': 'високовольтна',
            'всоковольтнй': 'високовольтний',
            'хранения': 'зберігання',
            'енергии': 'енергії',
            'модулей': 'модулів',
            'модулів': 'модулів',
            'квтгод': 'кВт·год',
            'квт': 'кВт',
            'квт ': 'кВт ',
            'вт': 'Вт',
            ' вт ': ' Вт ',
            'агод': 'А·год',
            'мність': 'ємність',
            'зберігання': 'зберігання',
            
            # Виправлення російських помилок
            'всоковольтная система': 'високовольтна система',
            'хранения енергии': 'зберігання енергії',
            'резервного живлення': 'резервного живлення',
            'комплект резервного': 'комплект резервного',
            'монтаж солнечнх': 'монтаж сонячних',
            'електростанций': 'електростанцій',
            
            # Виправлення регістру та пунктуації
            'деye': 'Deye',
            'must': 'Must',
            'longi': 'Longi',
            'solar': 'Solar',
            'sun-': 'SUN-',
            'pv18': 'PV18',
            'pv19': 'PV19',
            'lifepo4': 'LiFePO4',
            'lvts': 'LVTS',
            'bos-': 'BOS-',
            
            # Технічні одиниці
            'квт·год': 'кВт·год',
            'а·год': 'А·год',
            ' в ': ' В ',
            ' а)': ' А)',
            '( ': '(',
            ' )': ')',
            '  ': ' ',
        }
        
        products = Product.objects.all()
        
        for product in products:
            original_name = product.name
            original_description = product.description
            
            # Виправляємо назву
            fixed_name = self.apply_grammar_fixes(original_name, grammar_fixes)
            
            # Виправляємо опис
            fixed_description = self.apply_grammar_fixes(original_description, grammar_fixes)
            
            # Перевіряємо чи потрібні зміни
            if original_name != fixed_name or original_description != fixed_description:
                if dry_run:
                    if original_name != fixed_name:
                        self.stdout.write(f"ВИПРАВИТИ назву: {original_name} → {fixed_name}")
                    if original_description != fixed_description:
                        self.stdout.write(f"ВИПРАВИТИ опис товару ID {product.id}")
                else:
                    with transaction.atomic():
                        product.name = fixed_name
                        product.description = fixed_description
                        product.save()
                        self.stdout.write(f"Виправлено: {fixed_name}")
                fixed_count += 1
        
        return fixed_count

    def apply_grammar_fixes(self, text, fixes_dict):
        """Застосовує граматичні виправлення до тексту"""
        if not text:
            return text
        
        result = str(text)
        
        # Застосовуємо виправлення
        for wrong, correct in fixes_dict.items():
            result = result.replace(wrong, correct)
        
        # Виправляємо капіталізацію першої літери
        if result and result[0].islower():
            result = result[0].upper() + result[1:]
        
        # Очищаємо зайві пробіли
        result = re.sub(r'\s+', ' ', result).strip()
        
        # Виправляємо пробіли навколо дужок
        result = re.sub(r'\s*\(\s*', ' (', result)
        result = re.sub(r'\s*\)\s*', ') ', result)
        result = result.strip()
        
        return result

    def remove_extra_products(self, target_count, dry_run):
        """Видаляє зайві товари щоб досягти цільової кількості"""
        current_products = Product.objects.all()
        current_count = current_products.count()
        
        if current_count <= target_count:
            return 0
        
        to_delete = current_count - target_count
        
        # Сортуємо товари за важливістю (менш важливі видаляємо першими)
        # Критерії: товари без опису, дубльовані моделі, менш популярні бренди
        products_by_priority = []
        
        for product in current_products:
            priority = 0
            
            # Нижчий пріоритет для товарів без опису
            if not product.description or len(product.description.strip()) < 10:
                priority -= 10
            
            # Нижчий пріоритет для деяких брендів з меншою кількістю товарів
            brand_count = Product.objects.filter(brand=product.brand).count()
            if brand_count == 1:  # Унікальний бренд з одним товаром
                priority -= 5
            
            # Нижчий пріоритет для дуже схожих назв
            similar_count = Product.objects.filter(
                name__icontains=product.name.split()[0]  # Перше слово назви
            ).count()
            if similar_count > 3:
                priority -= 3
            
            products_by_priority.append((priority, product))
        
        # Сортуємо за пріоритетом (найменш важливі першими)
        products_by_priority.sort(key=lambda x: x[0])
        
        deleted_count = 0
        for priority, product in products_by_priority[:to_delete]:
            if dry_run:
                self.stdout.write(f"ВИДАЛИТИ зайвий: {product.name} (пріоритет: {priority})")
            else:
                product_name = product.name
                product.delete()
                self.stdout.write(f"Видалено зайвий: {product_name}")
            deleted_count += 1
        
        return deleted_count 