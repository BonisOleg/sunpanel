"""
Команда для експорту товарів в JSON формат
"""
import json
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from mainapp.models import Product, Category, Brand, ProductImage

class Command(BaseCommand):
    help = 'Експортує всі товари в JSON формат'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='feed',
            help='Папка для збереження JSON файлів'
        )
        parser.add_argument(
            '--include-images',
            action='store_true',
            help='Включити інформацію про зображення'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        include_images = options['include_images']
        
        # Створюємо папку якщо не існує
        os.makedirs(output_dir, exist_ok=True)
        
        # Отримуємо всі товари з оптимізацією
        products = Product.objects.select_related('category', 'brand').prefetch_related('images')
        
        # Підготовка даних
        products_data = []
        categories_data = []
        brands_data = []
        
        # Унікальні категорії та бренди
        categories = Category.objects.all()
        brands = Brand.objects.all()
        
        # Експорт категорій
        for category in categories:
            category_data = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'is_active': category.is_active,
                'created_at': category.created_at.isoformat() if category.created_at else None
            }
            categories_data.append(category_data)
        
        # Експорт брендів
        for brand in brands:
            brand_data = {
                'id': brand.id,
                'name': brand.name,
                'slug': brand.slug,
                'description': brand.description,
                'website': brand.website,
                'is_active': brand.is_active,
                'created_at': brand.created_at.isoformat() if brand.created_at else None
            }
            brands_data.append(brand_data)
        
        # Експорт товарів
        for product in products:
            # Основні дані товару
            product_data = {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'model': product.model,
                'power': product.power,
                'efficiency': product.efficiency,
                'warranty': product.warranty,
                'country': product.country,
                'in_stock': product.in_stock,
                'featured': product.featured,
                'created_at': product.created_at.isoformat() if product.created_at else None,
                'updated_at': product.updated_at.isoformat() if product.updated_at else None,
                'category': {
                    'id': product.category.id,
                    'name': product.category.name,
                    'slug': product.category.slug
                },
                'brand': {
                    'id': product.brand.id,
                    'name': product.brand.name,
                    'slug': product.brand.slug
                }
            }
            
            # Додаємо зображення якщо потрібно
            if include_images:
                images_data = []
                
                # Головне зображення
                if product.image:
                    images_data.append({
                        'type': 'main',
                        'url': f'https://greensolartech.com.ua{product.image_url}',
                        'alt': product.name
                    })
                
                # Додаткові зображення
                for img in product.images.all():
                    images_data.append({
                        'type': 'gallery',
                        'url': f'https://greensolartech.com.ua{img.image_url}',
                        'alt': img.alt_text or product.name,
                        'is_main': img.is_main,
                        'order': img.order
                    })
                
                product_data['images'] = images_data
            
            products_data.append(product_data)
        
        # Створюємо метадані
        meta_data = {
            'export_date': timezone.now().isoformat(),
            'total_products': len(products_data),
            'total_categories': len(categories_data),
            'total_brands': len(brands_data),
            'version': '1.0',
            'source': 'GreenSolarTech Catalog'
        }
        
        # Зберігаємо окремі файли
        files_created = []
        
        # 1. Повний каталог
        full_catalog = {
            'meta': meta_data,
            'categories': categories_data,
            'brands': brands_data,
            'products': products_data
        }
        
        full_catalog_path = os.path.join(output_dir, 'full_catalog.json')
        with open(full_catalog_path, 'w', encoding='utf-8') as f:
            json.dump(full_catalog, f, ensure_ascii=False, indent=2)
        files_created.append(full_catalog_path)
        
        # 2. Тільки товари
        products_only = {
            'meta': meta_data,
            'products': products_data
        }
        
        products_path = os.path.join(output_dir, 'products.json')
        with open(products_path, 'w', encoding='utf-8') as f:
            json.dump(products_only, f, ensure_ascii=False, indent=2)
        files_created.append(products_path)
        
        # 3. Категорії
        categories_only = {
            'meta': meta_data,
            'categories': categories_data
        }
        
        categories_path = os.path.join(output_dir, 'categories.json')
        with open(categories_path, 'w', encoding='utf-8') as f:
            json.dump(categories_only, f, ensure_ascii=False, indent=2)
        files_created.append(categories_path)
        
        # 4. Бренди
        brands_only = {
            'meta': meta_data,
            'brands': brands_data
        }
        
        brands_path = os.path.join(output_dir, 'brands.json')
        with open(brands_path, 'w', encoding='utf-8') as f:
            json.dump(brands_only, f, ensure_ascii=False, indent=2)
        files_created.append(brands_path)
        
        # 5. Товари по категоріях
        for category in categories:
            category_products = [p for p in products_data if p['category']['id'] == category.id]
            
            category_file = {
                'meta': {
                    **meta_data,
                    'category_name': category.name,
                    'category_slug': category.slug,
                    'products_count': len(category_products)
                },
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'description': category.description
                },
                'products': category_products
            }
            
            category_filename = f"category_{category.slug}.json"
            category_path = os.path.join(output_dir, category_filename)
            with open(category_path, 'w', encoding='utf-8') as f:
                json.dump(category_file, f, ensure_ascii=False, indent=2)
            files_created.append(category_path)
        
        # 6. Товари по брендах
        for brand in brands:
            brand_products = [p for p in products_data if p['brand']['id'] == brand.id]
            
            brand_file = {
                'meta': {
                    **meta_data,
                    'brand_name': brand.name,
                    'brand_slug': brand.slug,
                    'products_count': len(brand_products)
                },
                'brand': {
                    'id': brand.id,
                    'name': brand.name,
                    'slug': brand.slug,
                    'description': brand.description,
                    'website': brand.website
                },
                'products': brand_products
            }
            
            brand_filename = f"brand_{brand.slug}.json"
            brand_path = os.path.join(output_dir, brand_filename)
            with open(brand_path, 'w', encoding='utf-8') as f:
                json.dump(brand_file, f, ensure_ascii=False, indent=2)
            files_created.append(brand_path)
        
        # Показуємо результати
        self.stdout.write(self.style.SUCCESS(f'✅ Експорт завершено!'))
        self.stdout.write(f'📁 Папка: {output_dir}')
        self.stdout.write(f'📦 Товарів: {len(products_data)}')
        self.stdout.write(f'📂 Категорій: {len(categories_data)}')
        self.stdout.write(f'🏷️ Брендів: {len(brands_data)}')
        self.stdout.write(f'📄 Файлів створено: {len(files_created)}')
        
        if include_images:
            self.stdout.write('🖼️ Зображення включені')
        
        self.stdout.write('\n📋 Створені файли:')
        for file_path in files_created:
            file_size = os.path.getsize(file_path)
            self.stdout.write(f'  • {os.path.basename(file_path)} ({file_size:,} байт)') 