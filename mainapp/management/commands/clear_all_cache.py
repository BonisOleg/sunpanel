"""
Команда для очищення всіх кешів Django
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
import os

class Command(BaseCommand):
    help = 'Очищення всіх кешів Django'

    def handle(self, *args, **options):
        self.stdout.write('🧹 Очищення всіх кешів...')
        
        # Очистити Django cache
        try:
            cache.clear()
            self.stdout.write('✅ Django cache очищено')
        except Exception as e:
            self.stdout.write(f'❌ Помилка очищення Django cache: {e}')
        
        # Очистити __pycache__ файли
        try:
            import subprocess
            result = subprocess.run(['find', '/opt/render/project/src', '-name', '__pycache__', '-type', 'd', '-exec', 'rm', '-rf', '{}', '+'], 
                                  capture_output=True, text=True)
            self.stdout.write('✅ __pycache__ очищено')
        except Exception as e:
            self.stdout.write(f'⚠️ Не вдалося очистити __pycache__: {e}')
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Всі кеші очищено! Перезапустіть Gunicorn.')
        ) 