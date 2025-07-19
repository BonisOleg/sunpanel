import os
import shutil
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import transaction, models
from mainapp.models import Product
from django.conf import settings

class Command(BaseCommand):
    help = 'Підключає фотографії до товарів що залишилися без картинок'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати результат без збереження',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING("РЕЖИМ ПОПЕРЕДНЬОГО ПЕРЕГЛЯДУ"))
        
        # Знаходимо товари без фотографій
        products_without_images = Product.objects.filter(
            models.Q(image='') | models.Q(image__isnull=True)
        )
        
        total_without_images = products_without_images.count()
        self.stdout.write(f"📸 Знайдено {total_without_images} товарів без фотографій")
        
        if total_without_images == 0:
            self.stdout.write(self.style.SUCCESS("🎉 Всі товари вже мають фотографії!"))
            return
        
        # Створюємо мапінг товарів без фото до схожих товарів з фото
        image_mapping = self.create_image_mapping()
        
        updated_count = 0
        media_path = os.path.join(settings.MEDIA_ROOT, 'products')
        
        for product in products_without_images:
            try:
                # Знаходимо підходящу фотографію
                source_image = self.find_suitable_image(product, image_mapping, media_path)
                
                if source_image:
                    if dry_run:
                        self.stdout.write(f"ПІДКЛЮЧИТИ: {product.name} → {source_image}")
                        updated_count += 1
                    else:
                        success = self.copy_image_to_product(product, source_image, media_path)
                        if success:
                            updated_count += 1
                            self.stdout.write(f"✅ Підключено: {product.name}")
                        else:
                            self.stdout.write(f"❌ Помилка: {product.name}")
                else:
                    self.stdout.write(f"⚠️ Не знайдено фото для: {product.name}")
                    
            except Exception as e:
                self.stdout.write(f"❌ Помилка з {product.name}: {str(e)}")
                continue
        
        # Підсумки
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\nПОПЕРЕДНІЙ ПЕРЕГЛЯД ЗАВЕРШЕНО\n"
                    f"Товарів без фото: {total_without_images}\n"
                    f"Буде підключено: {updated_count}\n"
                    f"Для застосування запустіть без --dry-run"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nПІДКЛЮЧЕННЯ ЗАВЕРШЕНО\n"
                    f"Підключено фото: {updated_count}\n"
                    f"Фінальна перевірка..."
                )
            )
            
            # Фінальна перевірка
            remaining_without_images = Product.objects.filter(
                models.Q(image='') | models.Q(image__isnull=True)
            ).count()
            
            total_with_images = Product.objects.exclude(image='').exclude(image__isnull=True).count()
            total_products = Product.objects.count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎯 ФІНАЛЬНИЙ СТАН:\n"
                    f"📦 Всього товарів: {total_products}\n"
                    f"✅ З фотографіями: {total_with_images}\n"
                    f"❌ Без фотографій: {remaining_without_images}\n"
                    f"📊 Відсоток з фото: {(total_with_images/total_products*100):.1f}%"
                )
            )

    def create_image_mapping(self):
        """Створює мапінг типів товарів до зразкових фотографій"""
        return {
            'сонячна панель': ['product_530.0.jpg', 'product_590.0.jpg', 'product_610.0.jpg', 'product_615.0.jpg'],
            'гібридний інвертор deye': ['product_101_HZIASGp.0.jpg', 'product_102_rgR0u2J.0.jpg', 'product_103_Uaxmg23.0.jpg'],
            'гібридний інвертор must': ['product_420_fW81dDV.0.jpg', 'product_5248_buNedXq.0.jpg'],
            'акумуляторна батарея deye': ['product_110_LN73RGk.0.jpg', 'product_111_hqe83xf.0.jpg', 'product_218_V3JHPe3.0.jpg'],
            'акумуляторна батарея must': ['product_213_WzIfulu.0.jpg', 'product_211_RTCd0LP.0.jpg'],
            'система зберігання': ['product_112_xfvnNUv.0.jpg', 'product_113_A075UGk.0.jpg', 'product_114_S7HkND3.0.jpg', 'product_115_jjGY1D5.0.jpg'],
            'комплект резервного': ['product_1011_0ZdgoOI.0.jpg', 'product_1012_0WuHpj1.0.jpg', 'product_1013_ea4g80I.0.jpg'],
            'монтаж': ['product_nan_jmLRtKn.jpg']
        }

    def find_suitable_image(self, product, image_mapping, media_path):
        """Знаходить підходящу фотографію для товару"""
        product_name_lower = product.name.lower()
        
        # Перевіряємо по типах товарів
        for product_type, image_files in image_mapping.items():
            if product_type in product_name_lower:
                # Шукаємо першу доступну фотографію
                for image_file in image_files:
                    image_path = os.path.join(media_path, image_file)
                    if os.path.exists(image_path):
                        return image_file
        
        # Якщо не знайшли специфічну, пробуємо загальну логіку
        if 'сонячн' in product_name_lower or 'панель' in product_name_lower:
            default_images = ['product_530.0.jpg', 'product_590.0.jpg']
        elif 'інвертор' in product_name_lower and 'deye' in product_name_lower:
            default_images = ['product_101_HZIASGp.0.jpg', 'product_102_rgR0u2J.0.jpg']
        elif 'інвертор' in product_name_lower and 'must' in product_name_lower:
            default_images = ['product_420_fW81dDV.0.jpg']
        elif 'батарея' in product_name_lower or 'акумулят' in product_name_lower:
            default_images = ['product_110_LN73RGk.0.jpg', 'product_218_V3JHPe3.0.jpg']
        elif 'система' in product_name_lower:
            default_images = ['product_112_xfvnNUv.0.jpg', 'product_113_A075UGk.0.jpg']
        elif 'комплект' in product_name_lower:
            default_images = ['product_1011_0ZdgoOI.0.jpg']
        else:
            # Універсальна фотографія
            default_images = ['product_101_HZIASGp.0.jpg', 'product_530.0.jpg']
        
        for image_file in default_images:
            image_path = os.path.join(media_path, image_file)
            if os.path.exists(image_path):
                return image_file
        
        return None

    def copy_image_to_product(self, product, source_image_file, media_path):
        """Копіює фотографію та прикріплює до товару"""
        try:
            source_path = os.path.join(media_path, source_image_file)
            
            if not os.path.exists(source_path):
                return False
            
            # Читаємо файл
            with open(source_path, 'rb') as f:
                image_content = f.read()
            
            # Створюємо нове ім'я файлу
            file_extension = os.path.splitext(source_image_file)[1]
            new_filename = f"product_{product.id}_auto{file_extension}"
            
            # Зберігаємо до товару
            with transaction.atomic():
                product.image.save(
                    new_filename,
                    ContentFile(image_content),
                    save=True
                )
            
            return True
            
        except Exception as e:
            self.stdout.write(f"Помилка копіювання {source_image_file}: {str(e)}")
            return False 