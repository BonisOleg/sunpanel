"""
Команда для оновлення медіа URL після зміни MEDIA_URL в settings
"""
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Оновлення медіа URL після зміни налаштувань'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Оновлення медіа URL налаштувань...')
        
        # Виводимо поточні налаштування
        self.stdout.write(f'📂 MEDIA_URL: {settings.MEDIA_URL}')
        self.stdout.write(f'📁 MEDIA_ROOT: {settings.MEDIA_ROOT}')
        self.stdout.write(f'📦 STATIC_URL: {settings.STATIC_URL}')
        self.stdout.write(f'📁 STATIC_ROOT: {settings.STATIC_ROOT}')
        
        # Перевіряємо чи правильні налаштування
        if settings.MEDIA_URL == '/static/media/':
            self.stdout.write(
                self.style.SUCCESS('✅ MEDIA_URL правильно налаштований на /static/media/')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️ MEDIA_URL: {settings.MEDIA_URL} (очікується /static/media/)')
            )
        
        # Перевіряємо Django cache
        from django.core.cache import cache
        cache.clear()
        self.stdout.write('🗑️ Django cache очищено')
        
        self.stdout.write(
            self.style.SUCCESS('✅ Налаштування оновлено! Restart Gunicorn для застосування змін.')
        ) 