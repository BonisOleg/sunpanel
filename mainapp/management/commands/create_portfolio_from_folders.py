import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from mainapp.models import Portfolio
from datetime import date
from docx import Document

class Command(BaseCommand):
    help = 'Створює проекти портфоліо з папок з читанням тексту з документів'

    def read_docx_text(self, file_path):
        """Читає текст з .docx файлу"""
        try:
            doc = Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text.strip())
            return ' '.join(text)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Помилка читання файлу {file_path}: {e}'))
            return ""

    def copy_images_from_folder(self, source_folder, project_name):
        """Копіює всі зображення з папки проекту"""
        portfolio_media_path = os.path.join(settings.MEDIA_ROOT, 'portfolio')
        os.makedirs(portfolio_media_path, exist_ok=True)
        
        copied_images = []
        source_path = os.path.join(settings.BASE_DIR, source_folder)
        
        if os.path.exists(source_path):
            for filename in os.listdir(source_path):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    source_image = os.path.join(source_path, filename)
                    # Створюємо унікальне ім'я файлу
                    new_filename = f"{project_name}_{filename}"
                    dest_image = os.path.join(portfolio_media_path, new_filename)
                    
                    try:
                        shutil.copy2(source_image, dest_image)
                        copied_images.append(f'portfolio/{new_filename}')
                        self.stdout.write(f'Скопійовано: {filename}')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Помилка копіювання {filename}: {e}'))
        
        return copied_images

    def handle(self, *args, **options):
        # Проект 1
        self.stdout.write(self.style.SUCCESS('\n=== Створення Проекту 1 ==='))
        
        # Читаємо опис з документу
        docx_path = os.path.join(settings.BASE_DIR, '1_проект ', 'Опис_.docx')
        description_1 = self.read_docx_text(docx_path)
        if not description_1:
            description_1 = 'Реалізація сонячної електростанції для комерційного об\'єкта. Проект включає повний цикл робіт: від проектування до введення в експлуатацію. Встановлено високоефективні панелі з системою моніторингу продуктивності.'
        
        # Копіюємо всі фото
        images_1 = self.copy_images_from_folder('1_проект ', 'project1')
        main_image_1 = images_1[0] if images_1 else None
        
        if main_image_1:
            project1, created = Portfolio.objects.get_or_create(
                title="Комерційна СЕС потужністю 150 кВт",
                defaults={
                    'description': description_1,
                    'image': main_image_1,
                    'location': 'Київська область',
                    'power_capacity': '150',
                    'completion_date': date(2024, 8, 15),
                    'project_type': 'Комерційна СЕС',
                    'client_name': 'ТОВ "Енергетичні рішення"',
                    'featured': True
                }
            )
            
            self.stdout.write(self.style.SUCCESS(f'Проект 1 створено: {project1.title}'))
            self.stdout.write(f'Головне фото: {main_image_1}')
            self.stdout.write(f'Всього фото: {len(images_1)}')
            self.stdout.write(f'Опис з документу (перші 100 символів): {description_1[:100]}...')

        # Проект 2  
        self.stdout.write(self.style.SUCCESS('\n=== Створення Проекту 2 ==='))
        
        # Читаємо опис з документу
        docx_path = os.path.join(settings.BASE_DIR, '2_проект', 'Опис .docx')
        description_2 = self.read_docx_text(docx_path)
        if not description_2:
            description_2 = 'Масштабний проект встановлення сонячної електростанції на промисловому об\'єкті. Система забезпечує значну частину енергопотреб підприємства та дозволяє суттєво знизити витрати на електроенергію.'
        
        # Копіюємо всі фото
        images_2 = self.copy_images_from_folder('2_проект', 'project2')
        main_image_2 = images_2[0] if images_2 else None
        
        if main_image_2:
            project2, created = Portfolio.objects.get_or_create(
                title="Промислова СЕС потужністю 250 кВт",
                defaults={
                    'description': description_2,
                    'image': main_image_2,
                    'location': 'Дніпропетровська область',
                    'power_capacity': '250',
                    'completion_date': date(2024, 7, 20),
                    'project_type': 'Промислова СЕС',
                    'client_name': 'ПрАТ "Металургійний комбінат"',
                    'featured': True
                }
            )
            
            self.stdout.write(self.style.SUCCESS(f'Проект 2 створено: {project2.title}'))
            self.stdout.write(f'Головне фото: {main_image_2}')
            self.stdout.write(f'Всього фото: {len(images_2)}')
            self.stdout.write(f'Опис з документу (перші 100 символів): {description_2[:100]}...')

        # Проект 3
        self.stdout.write(self.style.SUCCESS('\n=== Створення Проекту 3 ==='))
        
        # Читаємо опис з документу
        docx_path = os.path.join(settings.BASE_DIR, '3_проект', 'Опис .docx')
        description_3 = self.read_docx_text(docx_path)
        if not description_3:
            description_3 = 'Домашня сонячна електростанція для приватного будинку. Система повністю покриває енергетичні потреби сім\'ї та дозволяє продавати надлишки електроенергії до мережі за "зеленим" тарифом.'
        
        # Копіюємо всі фото
        images_3 = self.copy_images_from_folder('3_проект', 'project3')
        main_image_3 = images_3[0] if images_3 else None
        
        if main_image_3:
            project3, created = Portfolio.objects.get_or_create(
                title="Приватна СЕС потужністю 30 кВт",
                defaults={
                    'description': description_3,
                    'image': main_image_3,
                    'location': 'Львівська область',
                    'power_capacity': '30',
                    'completion_date': date(2024, 6, 10),
                    'project_type': 'Приватна СЕС',
                    'client_name': 'Приватний клієнт',
                    'featured': False
                }
            )
            
            self.stdout.write(self.style.SUCCESS(f'Проект 3 створено: {project3.title}'))
            self.stdout.write(f'Головне фото: {main_image_3}')
            self.stdout.write(f'Всього фото: {len(images_3)}')
            self.stdout.write(f'Опис з документу (перші 100 символів): {description_3[:100]}...')

        self.stdout.write(self.style.SUCCESS('\n✅ Всі проекти портфоліо успішно створені з усіма фото та текстом з документів!')) 