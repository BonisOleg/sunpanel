from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
import os
import hashlib
from django.core.files.storage import default_storage

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва категорії")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-фрагмент")
    description = models.TextField(blank=True, verbose_name="Опис категорії")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата створення")
    
    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва бренду")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-фрагмент")
    logo = models.ImageField(upload_to='brands/', blank=True, verbose_name="Логотип")
    description = models.TextField(blank=True, verbose_name="Опис бренду")
    website = models.URLField(blank=True, verbose_name="Веб-сайт")
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата створення")
    
    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренди"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Brand.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва товару")
    description = models.TextField(verbose_name="Опис")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    image = models.ImageField(upload_to='products/', verbose_name="Зображення")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категорія")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Бренд")
    model = models.CharField(max_length=100, verbose_name="Модель")
    power = models.CharField(max_length=50, verbose_name="Потужність", blank=True)
    efficiency = models.CharField(max_length=50, verbose_name="Ефективність", blank=True)
    warranty = models.CharField(max_length=50, verbose_name="Гарантія", blank=True)
    country = models.CharField(max_length=100, verbose_name="Країна виробника", blank=True)
    in_stock = models.BooleanField(default=True, verbose_name="В наявності")
    featured = models.BooleanField(default=False, verbose_name="Рекомендований")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_image_url(self):
        """Отримує правильний URL зображення з кешбастингом"""
        if not self.image:
            return ''
        
        try:
            # Використовуємо стандартний Django URL який автоматично працює з налаштуваннями
            base_url = self.image.url
            
            # Додаємо версіонування для кешбастингу тільки у продакшні
            if hasattr(settings, 'DEBUG') and not settings.DEBUG:
                # У продакшні додаємо хеш для уникнення кешування
                file_hash = hashlib.md5(f"{self.image.name}{self.updated_at}".encode()).hexdigest()[:8]
                return f"{base_url}?v={file_hash}"
            else:
                # У розробці просто повертаємо стандартний URL
                return base_url
                
        except Exception:
            return ''
    
    @property
    def image_url(self):
        """Властивість для зручного доступу до URL зображення"""
        return self.get_image_url()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name="Товар")
    image = models.ImageField(upload_to='products/gallery/', verbose_name="Зображення")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Альтернативний текст")
    is_main = models.BooleanField(default=False, verbose_name="Головне зображення")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок відображення")
    
    class Meta:
        verbose_name = "Зображення товару"
        verbose_name_plural = "Зображення товарів"
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.product.name} - Зображення {self.order}"
    
    def get_image_url(self):
        """Отримує правильний URL зображення з кешбастингом"""
        if not self.image:
            return ''
        
        try:
            # Використовуємо стандартний Django URL який автоматично працює з налаштуваннями
            base_url = self.image.url
            
            # Додаємо версіонування для кешбастингу тільки у продакшні
            if hasattr(settings, 'DEBUG') and not settings.DEBUG:
                # У продакшні додаємо хеш для уникнення кешування
                file_hash = hashlib.md5(f"{self.image.name}{self.product.updated_at}".encode()).hexdigest()[:8]
                return f"{base_url}?v={file_hash}"
            else:
                # У розробці просто повертаємо стандартний URL
                return base_url
                
        except Exception:
            return ''
    
    @property
    def image_url(self):
        """Властивість для зручного доступу до URL зображення"""
        return self.get_image_url()


class Portfolio(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва проєкту")
    description = models.TextField(verbose_name="Опис проєкту")
    image = models.ImageField(upload_to='portfolio/', verbose_name="Головне зображення")
    location = models.CharField(max_length=200, verbose_name="Місце розташування", blank=True)
    power_capacity = models.CharField(max_length=50, verbose_name="Потужність станції", blank=True)
    completion_date = models.DateField(verbose_name="Дата завершення", blank=True, null=True)
    project_type = models.CharField(max_length=100, verbose_name="Тип проєкту", blank=True)
    client_name = models.CharField(max_length=200, verbose_name="Клієнт", blank=True)
    featured = models.BooleanField(default=False, verbose_name="Рекомендований")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата створення")
    
    class Meta:
        verbose_name = "Проєкт портфоліо"
        verbose_name_plural = "Проєкти портфоліо"
        ordering = ['-completion_date', '-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def all_images(self):
        """Повертає всі зображення для цього проекту"""
        import os
        from django.conf import settings
        
        # Визначаємо ключ проекту за назвою
        if "17.2" in self.title or "аналітика" in self.title.lower():
            project_key = "project1"
        elif "43" in self.title or "комерційна" in self.title.lower():
            project_key = "project2" 
        elif "10.6" in self.title:
            project_key = "project3"
        else:
            return []
        
        # Шлях до медіа папки
        media_portfolio = os.path.join(settings.BASE_DIR, 'media', 'portfolio')
        if not os.path.exists(media_portfolio):
            return []
        
        # Знаходимо всі зображення для цього проекту
        project_images = []
        for image_file in os.listdir(media_portfolio):
            if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Перевіряємо чи належить зображення цьому проекту
                if project_key == "project1" and (
                    'аналітика' in image_file or 'буд' in image_file or 
                    any(x in image_file for x in ['project1'])
                ):
                    project_images.append(f'portfolio/{image_file}')
                elif project_key == "project2" and any(x in image_file for x in ['4083', '65825', '8534', '87209', 'project2']):
                    project_images.append(f'portfolio/{image_file}')
                elif project_key == "project3" and any(x in image_file for x in ['1494', '15578', '69046', 'project3']):
                    project_images.append(f'portfolio/{image_file}')
        
        return sorted(project_images)


class Review(models.Model):
    client_name = models.CharField(max_length=200, verbose_name="Ім'я клієнта")
    client_position = models.CharField(max_length=200, verbose_name="Посада/компанія", blank=True)
    review_text = models.TextField(verbose_name="Текст відгуку")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Оцінка")
    project_type = models.CharField(max_length=100, verbose_name="Тип проєкту", blank=True)
    location = models.CharField(max_length=200, verbose_name="Місце проєкту", blank=True)
    is_published = models.BooleanField(default=True, verbose_name="Опубліковано")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата створення")
    
    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Відгук від {self.client_name} - {self.rating}★"
