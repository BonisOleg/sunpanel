"""
Команда для налаштування медіа файлів в production
Копіює всі медіа файли до staticfiles/media/ для обслуговування через WhiteNoise
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.staticfiles.management.commands.collectstatic import Command as CollectStaticCommand


class Command(BaseCommand):
    help = 'Налаштовує медіа файли для production (копіює до staticfiles)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Очистити існуючі медіа файли в staticfiles'
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Налаштування медіа файлів для production...')
        
        # Шляхи
        media_source = os.path.join(settings.BASE_DIR, 'media')  # Вихідна папка media
        staticfiles_root = settings.STATIC_ROOT
        static_media_dest = os.path.join(staticfiles_root, 'media')
        
        # Створюємо staticfiles якщо не існує
        os.makedirs(staticfiles_root, exist_ok=True)
        
        # Очищення якщо потрібно
        if options['clean'] and os.path.exists(static_media_dest):
            shutil.rmtree(static_media_dest)
            self.stdout.write('🗑️ Очищено існуючі медіа файли в staticfiles')

        # Створюємо папку медіа в staticfiles
        os.makedirs(static_media_dest, exist_ok=True)
        
        if not os.path.exists(media_source):
            self.stdout.write(
                self.style.WARNING('⚠️ Папка media не знайдена! Створюю порожню структуру...')
            )
            # Створюємо базову структуру
            os.makedirs(os.path.join(static_media_dest, 'products'), exist_ok=True)
            os.makedirs(os.path.join(static_media_dest, 'portfolio'), exist_ok=True)
            os.makedirs(os.path.join(static_media_dest, 'brands'), exist_ok=True)
            return

        # Копіюємо всі медіа файли
        copied_files = 0
        for root, dirs, files in os.walk(media_source):
            for file in files:
                # Копіюємо всі файли (не лише зображення)
                source_file = os.path.join(root, file)
                
                # Зберігаємо структуру папок
                rel_path = os.path.relpath(source_file, media_source)
                dest_file = os.path.join(static_media_dest, rel_path)
                
                # Створюємо папки якщо потрібно
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                
                # Копіюємо файл
                try:
                    shutil.copy2(source_file, dest_file)
                    copied_files += 1
                    
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        self.stdout.write(f'✅ 🖼️ {rel_path}')
                    else:
                        self.stdout.write(f'✅ 📄 {rel_path}')
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Помилка копіювання {rel_path}: {e}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'📁 Скопійовано {copied_files} медіа файлів до staticfiles/media/'
            )
        )
        
        # Запускаємо collectstatic для збирання всіх статичних файлів
        self.stdout.write('📦 Запускаю collectstatic...')
        try:
            collect_command = CollectStaticCommand()
            collect_command.handle(interactive=False, verbosity=0)
            self.stdout.write(self.style.SUCCESS('✅ Collectstatic завершено'))
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Помилка collectstatic: {e}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                '🎉 Медіа файли готові для production!\n'
                'Тепер всі медіа файли доступні через /static/media/ URL'
            )
        ) 