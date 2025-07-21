"""
Команда для копіювання медіа файлів до статичних файлів
Це дозволяє зображенням працювати на Render без сторонніх сервісів
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Копіює медіа файли до статичних для production'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Очистити існуючі статичні медіа файли'
        )

    def handle(self, *args, **options):
        # Шляхи
        media_source = os.path.join(settings.BASE_DIR, 'media')
        static_media_dest = os.path.join(settings.BASE_DIR, 'static', 'media')
        
        # Очищення якщо потрібно
        if options['clean'] and os.path.exists(static_media_dest):
            shutil.rmtree(static_media_dest)
            self.stdout.write('🗑️ Очищено існуючі статичні медіа файли')

        # Створюємо папку якщо не існує
        os.makedirs(static_media_dest, exist_ok=True)
        
        if not os.path.exists(media_source):
            self.stdout.write(
                self.style.WARNING('⚠️ Папка media не знайдена!')
            )
            return

        # Копіюємо всі медіа файли
        copied_files = 0
        for root, dirs, files in os.walk(media_source):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    source_file = os.path.join(root, file)
                    
                    # Зберігаємо структуру папок
                    rel_path = os.path.relpath(source_file, media_source)
                    dest_file = os.path.join(static_media_dest, rel_path)
                    
                    # Створюємо папки якщо потрібно
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    
                    # Копіюємо файл
                    shutil.copy2(source_file, dest_file)
                    copied_files += 1
                    
                    self.stdout.write(f'✅ {rel_path}')

        self.stdout.write(
            self.style.SUCCESS(
                f'📁 Скопійовано {copied_files} медіа файлів до static/media/'
            )
        )
        
        # Створюємо .htaccess для кращого кешування
        htaccess_content = """
# Кешування зображень
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 month"
    ExpiresByType image/jpeg "access plus 1 month"
    ExpiresByType image/gif "access plus 1 month"
    ExpiresByType image/png "access plus 1 month"
    ExpiresByType image/webp "access plus 1 month"
</IfModule>

# Заголовки для кешування
<IfModule mod_headers.c>
    <FilesMatch "\.(jpg|jpeg|png|gif|webp)$">
        Header set Cache-Control "max-age=2592000, public"
    </FilesMatch>
</IfModule>
        """
        
        htaccess_path = os.path.join(static_media_dest, '.htaccess')
        with open(htaccess_path, 'w') as f:
            f.write(htaccess_content)
            
        self.stdout.write('📝 Створено .htaccess для кешування') 