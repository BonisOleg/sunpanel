"""
Команда для створення зразкових товарів якщо Excel імпорт не працює
"""
from django.core.management.base import BaseCommand
from mainapp.models import Product, Category, Brand

class Command(BaseCommand):
    help = 'Створює зразкові товари для тестування'

    def handle(self, *args, **options):
        # Створюємо категорії
        inverter_cat, _ = Category.objects.get_or_create(
            name='Інвертори',
            defaults={'description': 'Гібридні та сонячні інвертори'}
        )
        
        battery_cat, _ = Category.objects.get_or_create(
            name='Акумуляторні батареї',
            defaults={'description': 'LiFePO4 акумулятори'}
        )
        
        panel_cat, _ = Category.objects.get_or_create(
            name='Сонячні панелі', 
            defaults={'description': 'Монокристалічні панелі'}
        )
        
        # Створюємо бренди
        must_brand, _ = Brand.objects.get_or_create(
            name='Must',
            defaults={'description': 'Must Energy Systems'}
        )
        
        deye_brand, _ = Brand.objects.get_or_create(
            name='Deye',
            defaults={'description': 'Deye Inverter Technology'}
        )
        
        longi_brand, _ = Brand.objects.get_or_create(
            name='LONGi Solar',
            defaults={'description': 'LONGi Solar Technology'}
        )
        
        # Створюємо товари
        products_data = [
            {
                'name': 'Гібридний інвертор MUST PV19-6048 EXP 6кВт',
                'description': 'Багатофункціональний інвертор 6кВт з вбудованим MPPT контролером.\n\nХарактеристики:\n• Номінальна потужність: 6000 Вт\n• Максимальна PV напруга: 500В\n• WiFi модуль в комплекті\n• Паралельна робота до 3 блоків',
                'price': 14900,
                'category': inverter_cat,
                'brand': must_brand,
                'model': 'PV19-6048 EXP',
                'in_stock': True,
                'featured': True
            },
            {
                'name': 'Акумуляторна батарея MUST LiFePO4 LP16-48100 5кВт',
                'description': 'Літієво-залізно-фосфатна батарея 48В 100А з BMS системою.\n\nХарактеристики:\n• Ємність: 5.12 кВт⋅год\n• Напруга: 48В\n• Струм: 100А\n• До 6000 циклів\n• Гарантія: 24 місяці',
                'price': 29399,
                'category': battery_cat,
                'brand': must_brand,
                'model': 'LP16-48100',
                'in_stock': True,
                'featured': True
            },
            {
                'name': 'Гібридний інвертор Deye 8кВт SUN-8K-SG01LP1-EU',
                'description': 'Однофазний гібридний інвертор 8кВт від Deye.\n\nХарактеристики:\n• Потужність: 8000 Вт\n• Фази: 1\n• Високовольтна батарея\n• Parallel функція\n• Wi-Fi моніторинг',
                'price': 18500,
                'category': inverter_cat,
                'brand': deye_brand,
                'model': 'SUN-8K-SG01LP1-EU',
                'in_stock': True,
                'featured': False
            },
            {
                'name': 'Сонячна панель Longi Solar LR8-66HGD-615M',
                'description': 'Монокристалічна сонячна панель 615Вт з високою ефективністю.\n\nХарактеристики:\n• Потужність: 615 Вт\n• Ефективність: 22.3%\n• Тип: монокристал\n• Розміри: 2384×1303×35мм\n• Гарантія: 25 років',
                'price': 8900,
                'category': panel_cat,
                'brand': longi_brand,
                'model': 'LR8-66HGD-615M',
                'in_stock': True,
                'featured': True
            },
            {
                'name': 'Акумуляторна батарея Deye SE-G5.1Pro-B',
                'description': 'Високовольтна LiFePO4 батарея від Deye.\n\nХарактеристики:\n• Ємність: 5.12 кВт⋅год\n• Напруга: 51.2В\n• Модульна система\n• BMS захист\n• Розширення до 40.96 кВт⋅год',
                'price': 35000,
                'category': battery_cat,
                'brand': deye_brand,
                'model': 'SE-G5.1Pro-B',
                'in_stock': True,
                'featured': False
            }
        ]
        
        created_count = 0
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"✅ Створено: {product.name}")
            else:
                self.stdout.write(f"⏭️ Вже існує: {product.name}")
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Створено {created_count} нових товарів!')
        ) 