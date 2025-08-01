from django.core.management.base import BaseCommand
from django.conf import settings
from mainapp.models import Product
import csv
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Експорт товарів для Google Merchant Center'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='google_merchant_products.csv',
            help='Назва вихідного файлу'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        
        # Створюємо папку exports якщо її немає
        exports_dir = os.path.join(settings.BASE_DIR, 'exports')
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
        
        output_path = os.path.join(exports_dir, output_file)
        
        # Отримуємо всі товари в наявності
        products = Product.objects.filter(in_stock=True).select_related('category', 'brand')
        
        # Заголовки для Google Merchant Center
        fieldnames = [
            'id',
            'title',
            'description', 
            'link',
            'image_link',
            'additional_image_link',
            'availability',
            'price',
            'sale_price',
            'brand',
            'gtin',
            'mpn',
            'condition',
            'product_type',
            'google_product_category',
            'custom_label_0',
            'custom_label_1',
            'custom_label_2',
            'custom_label_3',
            'custom_label_4'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in products:
                # Отримуємо основне зображення
                main_image = product.image_url if product.image else ''
                
                # Отримуємо додаткові зображення
                additional_images = []
                for image in product.images.all()[:9]:  # Google дозволяє максимум 10 зображень
                    if image.image_url and image.image_url != main_image:
                        additional_images.append(image.image_url)
                
                # Формуємо рядок для додаткових зображень
                additional_image_link = ','.join(additional_images) if additional_images else ''
                
                # Визначаємо категорію Google
                google_category = self.get_google_category(product.category.name)
                
                # Формуємо дані товару
                row = {
                    'id': str(product.id),
                    'title': product.name,
                    'description': product.description[:5000],  # Обмеження Google
                    'link': f'https://greensolartech.com.ua/product/{product.id}/',
                    'image_link': main_image,
                    'additional_image_link': additional_image_link,
                    'availability': 'in stock' if product.in_stock else 'out of stock',
                    'price': f'{product.price} UAH',
                    'sale_price': '',  # Якщо є знижка
                    'brand': product.brand.name if product.brand else 'GreenSolarTech',
                    'gtin': '',  # GTIN код якщо є
                    'mpn': product.model if product.model else '',
                    'condition': 'new',
                    'product_type': product.category.name,
                    'google_product_category': google_category,
                    'custom_label_0': product.power if product.power else '',
                    'custom_label_1': product.efficiency if product.efficiency else '',
                    'custom_label_2': product.warranty if product.warranty else '',
                    'custom_label_3': product.country if product.country else '',
                    'custom_label_4': 'featured' if product.featured else ''
                }
                
                writer.writerow(row)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Успішно експортовано {products.count()} товарів у файл {output_path}'
            )
        )
        
        # Виводимо статистику
        self.stdout.write(f'Загальна кількість товарів: {products.count()}')
        self.stdout.write(f'Товари з зображеннями: {products.filter(image__isnull=False).count()}')
        self.stdout.write(f'Рекомендовані товари: {products.filter(featured=True).count()}')
        
        # Перевіряємо якість даних
        self.check_data_quality(products)
    
    def get_google_category(self, category_name):
        """Визначає Google Product Category на основі назви категорії"""
        category_mapping = {
            'Сонячні панелі': '3239',  # Solar Panels
            'Інвертори': '3239',       # Solar Inverters  
            'Акумуляторні батареї': '3239',  # Solar Batteries
            'Комплекти резервного живлення': '3239',  # Solar Kits
        }
        
        for key, value in category_mapping.items():
            if key.lower() in category_name.lower():
                return value
        
        return '3239'  # За замовчуванням - Solar Energy
    
    def check_data_quality(self, products):
        """Перевіряє якість даних для Google Merchant Center"""
        self.stdout.write('\n=== ПЕРЕВІРКА ЯКОСТІ ДАНИХ ===')
        
        # Товари без зображень
        products_without_images = products.filter(image__isnull=True)
        if products_without_images.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  {products_without_images.count()} товарів без зображень:'
                )
            )
            for product in products_without_images[:5]:  # Показуємо перші 5
                self.stdout.write(f'   - {product.name} (ID: {product.id})')
        
        # Товари без опису
        products_without_description = products.filter(description='')
        if products_without_description.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  {products_without_description.count()} товарів без опису:'
                )
            )
            for product in products_without_description[:5]:
                self.stdout.write(f'   - {product.name} (ID: {product.id})')
        
        # Товари без бренду
        products_without_brand = products.filter(brand__isnull=True)
        if products_without_brand.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  {products_without_brand.count()} товарів без бренду:'
                )
            )
            for product in products_without_brand[:5]:
                self.stdout.write(f'   - {product.name} (ID: {product.id})')
        
        # Рекомендації
        self.stdout.write('\n=== РЕКОМЕНДАЦІЇ ===')
        self.stdout.write('✅ Для кращого відображення в Google Shopping:')
        self.stdout.write('   - Додайте зображення для всіх товарів (мінімум 250x250px)')
        self.stdout.write('   - Напишіть детальні описи для кожного товару')
        self.stdout.write('   - Вкажіть бренд для всіх товарів')
        self.stdout.write('   - Додайте GTIN коди якщо є')
        self.stdout.write('   - Перевірте правильність цін та наявності') 