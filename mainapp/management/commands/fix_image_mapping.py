from django.core.management.base import BaseCommand
from django.conf import settings
from mainapp.models import Product, ProductImage
import os
import shutil
import glob
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Виправляє невідповідність між ID товарів у БД та файлами зображень'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати що буде зроблено без фактичного виконання',
        )
        parser.add_argument(
            '--fix-method',
            choices=['copy', 'rename', 'update-db'],
            default='copy',
            help='Метод виправлення: copy (копіювати файли), rename (перейменувати), update-db (оновити БД)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Починаю виправлення невідповідності зображень...'))
        
        dry_run = options['dry_run']
        fix_method = options['fix_method']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🧪 РЕЖИМ ТЕСТУВАННЯ - зміни не будуть збережені'))
        
        # Знаходимо всі існуючі файли зображень
        media_root = settings.MEDIA_ROOT
        products_dir = os.path.join(media_root, 'products')
        
        existing_files = []
        if os.path.exists(products_dir):
            for filename in os.listdir(products_dir):
                if filename.startswith('product_') and filename.endswith('.jpg'):
                    existing_files.append(filename)
        
        self.stdout.write(f"📁 Знайдено {len(existing_files)} файлів зображень")
        
        # Аналізуємо товари з проблемними зображеннями
        problematic_products = []
        
        for product in Product.objects.all():
            if product.image:
                image_path = product.image.name
                full_path = os.path.join(media_root, image_path)
                
                if not os.path.exists(full_path):
                    problematic_products.append({
                        'product': product,
                        'missing_file': image_path,
                        'expected_pattern': f"product_{product.id}_"
                    })
        
        self.stdout.write(f"⚠️ Знайдено {len(problematic_products)} товарів з відсутніми зображеннями")
        
        if fix_method == 'copy':
            self.fix_by_copying(problematic_products, existing_files, media_root, dry_run)
        elif fix_method == 'update-db':
            self.fix_by_updating_db(problematic_products, existing_files, dry_run)
        else:
            self.stdout.write(self.style.ERROR('Метод "rename" поки не реалізований'))

    def fix_by_copying(self, problematic_products, existing_files, media_root, dry_run):
        """Копіює існуючі файли з новими іменами для проблемних товарів"""
        self.stdout.write("📋 Метод: Копіювання файлів з новими іменами")
        
        # Створюємо мапінг по назвах товарів
        name_mapping = {}
        for product_data in problematic_products:
            product = product_data['product']
            # Витягуємо ключові слова з назви товару
            name_words = product.name.lower().split()
            key_words = [word for word in name_words if len(word) > 3][:3]  # Беремо перші 3 значущі слова
            name_mapping[product.id] = key_words
        
        fixed_count = 0
        
        for product_data in problematic_products:
            product = product_data['product']
            target_filename = f"product_{product.id}_0_{int(product.created_at.timestamp())}_{product.name[:20].replace(' ', '_').lower()}.jpg"
            target_path = os.path.join(media_root, 'products', target_filename)
            
            # Шукаємо найкращий match серед існуючих файлів
            best_match = None
            best_score = 0
            
            key_words = name_mapping[product.id]
            
            for existing_file in existing_files:
                score = 0
                file_lower = existing_file.lower()
                
                # Перевіряємо збіги по ключових словах
                for word in key_words:
                    if word in file_lower:
                        score += 1
                
                # Додаткові очки за тип товару
                if 'invertor' in file_lower or 'гібрид' in product.name.lower():
                    if 'invertor' in file_lower or 'gibrid' in file_lower:
                        score += 2
                elif 'panel' in file_lower or 'панел' in product.name.lower():
                    if 'panel' in file_lower or 'solnech' in file_lower:
                        score += 2
                elif 'батар' in product.name.lower() or 'battery' in product.name.lower():
                    if 'batare' in file_lower or 'battery' in file_lower:
                        score += 2
                elif 'комплект' in product.name.lower():
                    if 'komplekt' in file_lower:
                        score += 2
                
                if score > best_score:
                    best_score = score
                    best_match = existing_file
            
            if best_match and best_score > 0:
                source_path = os.path.join(media_root, 'products', best_match)
                
                self.stdout.write(f"   📦 {product.name[:50]}...")
                self.stdout.write(f"      🔍 Знайдено match: {best_match} (score: {best_score})")
                self.stdout.write(f"      📂 Буде скопійовано як: {target_filename}")
                
                if not dry_run:
                    try:
                        # Копіюємо файл
                        shutil.copy2(source_path, target_path)
                        
                        # Оновлюємо посилання у БД
                        product.image.name = f'products/{target_filename}'
                        product.save()
                        
                        fixed_count += 1
                        self.stdout.write(f"      ✅ Файл скопійовано та БД оновлено")
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"      ❌ Помилка: {str(e)}"))
            else:
                self.stdout.write(f"   ⚠️ Не знайдено підходящого файлу для: {product.name[:50]}...")
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f"✅ Виправлено {fixed_count} товарів"))
        else:
            self.stdout.write(f"🧪 Було б виправлено {len([p for p in problematic_products if self.find_best_match(p, existing_files)])} товарів")

    def fix_by_updating_db(self, problematic_products, existing_files, dry_run):
        """Оновлює БД щоб посилатись на існуючі файли"""
        self.stdout.write("📋 Метод: Оновлення БД для використання існуючих файлів")
        
        # Простий алгоритм: призначаємо файли по порядку
        fixed_count = 0
        
        for i, product_data in enumerate(problematic_products):
            if i < len(existing_files):
                product = product_data['product']
                new_file = existing_files[i]
                
                self.stdout.write(f"   📦 {product.name[:50]}...")
                self.stdout.write(f"      🔄 Буде використовувати: {new_file}")
                
                if not dry_run:
                    product.image.name = f'products/{new_file}'
                    product.save()
                    fixed_count += 1
                    self.stdout.write(f"      ✅ БД оновлено")
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f"✅ Оновлено {fixed_count} товарів"))

    def find_best_match(self, product_data, existing_files):
        """Допоміжна функція для знаходження найкращого співпадіння"""
        product = product_data['product']
        name_words = product.name.lower().split()
        key_words = [word for word in name_words if len(word) > 3][:3]
        
        best_score = 0
        for existing_file in existing_files:
            score = 0
            file_lower = existing_file.lower()
            
            for word in key_words:
                if word in file_lower:
                    score += 1
                    
            if score > best_score:
                best_score = score
                
        return best_score > 0 