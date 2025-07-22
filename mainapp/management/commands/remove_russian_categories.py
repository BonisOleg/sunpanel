from django.core.management.base import BaseCommand
from django.db import transaction
from mainapp.models import Category, Product

class Command(BaseCommand):
    help = 'Видаляє російські дублікати категорій та переносить товари в українські'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати результат без збереження в базу',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write("🔍 Пошук дублікатів категорій...")
        
        # Російські категорії, які потрібно видалити і їх українські аналоги
        russian_to_ukrainian = {
            'Аккумуляторы для ИБП Deye': 'Акумулятори для ДБЖ Deye',
            'Аккумуляторы для ИБП MUST': 'Акумулятори для ДБЖ MUST', 
            'Аккумуляторы для ИБП lvtopsun': 'Акумулятори для ДБЖ lvtopsun',
            'Инверторы Deye': 'Інвертори Deye',
            'Инверторы Must': 'Інвертори Must',
            'Солнечные панели Longi Solar': 'Сонячні панелі Longi Solar',
            'Солнечные панели Risen Energy': 'Сонячні панелі Risen Energy',
            'Дополниельные услуги': 'Додаткові послуги'
        }
        
        moved_products = 0
        deleted_categories = 0
        
        for russian_name, ukrainian_name in russian_to_ukrainian.items():
            try:
                russian_category = Category.objects.get(name=russian_name)
                ukrainian_category = Category.objects.get(name=ukrainian_name)
                
                self.stdout.write(f"\n🔄 Обробка: {russian_name} → {ukrainian_name}")
                
                # Переносимо товари з російської категорії в українську
                products_to_move = Product.objects.filter(category=russian_category)
                product_count = products_to_move.count()
                
                if product_count > 0:
                    self.stdout.write(f"   📦 Товарів для переносу: {product_count}")
                    
                    if not dry_run:
                        with transaction.atomic():
                            products_to_move.update(category=ukrainian_category)
                            moved_products += product_count
                            self.stdout.write(f"   ✅ Перенесено {product_count} товарів")
                    else:
                        self.stdout.write(f"   🔍 БУДЕ перенесено {product_count} товарів")
                        for product in products_to_move[:5]:  # Показуємо перші 5
                            self.stdout.write(f"      - {product.name}")
                        if product_count > 5:
                            self.stdout.write(f"      ... та ще {product_count - 5}")
                
                # Видаляємо російську категорію
                if not dry_run:
                    russian_category.delete()
                    deleted_categories += 1
                    self.stdout.write(f"   🗑️ Видалено російську категорію")
                else:
                    self.stdout.write(f"   🔍 БУДЕ видалена російська категорія")
                    
            except Category.DoesNotExist as e:
                if russian_name in str(e):
                    self.stdout.write(f"⚠️ Російська категорія '{russian_name}' не знайдена")
                elif ukrainian_name in str(e):
                    self.stdout.write(f"⚠️ Українська категорія '{ukrainian_name}' не знайдена")
                continue
            except Exception as e:
                self.stdout.write(f"❌ Помилка при обробці '{russian_name}': {str(e)}")
                continue
        
        # Підсумки
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n📋 ПОПЕРЕДНІЙ ПЕРЕГЛЯД\n"
                    f"Буде перенесено товарів: {moved_products}\n"
                    f"Буде видалено категорій: {deleted_categories}\n"
                    f"Для застосування змін запустіть без --dry-run"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 ОЧИЩЕННЯ ЗАВЕРШЕНО\n"
                    f"Перенесено товарів: {moved_products}\n"
                    f"Видалено російських категорій: {deleted_categories}"
                )
            )
            
        # Показуємо поточний список категорій
        self.stdout.write(f"\n📂 Поточні категорії:")
        for category in Category.objects.all().order_by('name'):
            product_count = Product.objects.filter(category=category).count()
            self.stdout.write(f"   {category.id}: {category.name} ({product_count} товарів)") 