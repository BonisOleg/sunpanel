"""
Команда для швидкого виправлення зображень на Render
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Швидко виправляє зображення товарів на Render'

    def handle(self, *args, **options):
        self.stdout.write("🔧 ШВИДКЕ ВИПРАВЛЕННЯ ЗОБРАЖЕНЬ НА RENDER")
        self.stdout.write('='*60)
        
        # 1. Налаштування медіа файлів
        self.stdout.write("📁 Налаштування медіа файлів...")
        call_command('setup_media_for_production', '--verify')
        
        # 2. Збір статичних файлів БЕЗ очищення
        self.stdout.write("🎨 Збір статичних файлів...")
        call_command('collectstatic', '--no-input')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 ЗОБРАЖЕННЯ ВИПРАВЛЕНО!'))
        self.stdout.write("✅ Тепер всі товари мають зображення")
        self.stdout.write("🌐 Перевір каталог: https://greensolartech-b0m2.onrender.com/catalog/") 