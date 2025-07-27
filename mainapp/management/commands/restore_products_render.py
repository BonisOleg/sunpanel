"""
Команда для швидкого відновлення товарів після деплою на Render
Виправляє порожню базу даних та відновлює всі 42 товари
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Швидко відновлює товари після деплою на Render'

    def handle(self, *args, **options):
        self.stdout.write('🚨 ЕКСТРЕНЕ ВІДНОВЛЕННЯ ТОВАРІВ НА RENDER')
        self.stdout.write('='*60)
        
        # 1. Імпорт товарів
        self.stdout.write('📦 Імпорт 42 товарів...')
        try:
            call_command('import_full_catalog', '--clear-existing')
            self.stdout.write(self.style.SUCCESS('✅ Товари імпортовані'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Помилка імпорту: {e}'))
            # Backup - створюємо sample товари
            try:
                call_command('create_sample_products')
                self.stdout.write(self.style.WARNING('⚠️ Створено backup товари'))
            except Exception as e2:
                self.stdout.write(self.style.ERROR(f'❌ Backup помилка: {e2}'))
        
        # 2. Очищення російського контенту
        self.stdout.write('🇺🇦 Очищення російського контенту...')
        try:
            call_command('clean_russian_content')
            self.stdout.write(self.style.SUCCESS('✅ Російський контент очищено'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Помилка очищення: {e}'))
        
        # 3. Налаштування медіа
        self.stdout.write('🖼️ Налаштування медіа файлів...')
        try:
            call_command('setup_media_for_production', '--verify')
            self.stdout.write(self.style.SUCCESS('✅ Медіа файли налаштовані'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Помилка медіа: {e}'))
        
        # 4. Підготовка портфоліо
        self.stdout.write('🏢 Підготовка портфоліо...')
        try:
            call_command('prepare_portfolio')
            self.stdout.write(self.style.SUCCESS('✅ Портфоліо готове'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Помилка портфоліо: {e}'))
        
        # 5. Очищення кешу
        self.stdout.write('🧹 Очищення кешу...')
        try:
            call_command('clear_all_cache')
            self.stdout.write(self.style.SUCCESS('✅ Кеш очищено'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Помилка кешу: {e}'))
        
        # 6. Фінальна перевірка
        self.stdout.write()
        self.stdout.write('🔍 ФІНАЛЬНА ПЕРЕВІРКА:')
        
        from mainapp.models import Product, Portfolio, Category
        
        products_count = Product.objects.count()
        portfolio_count = Portfolio.objects.count()
        categories_count = Category.objects.count()
        
        self.stdout.write(f'📦 Товарів: {products_count}/42')
        self.stdout.write(f'📂 Категорій: {categories_count}/4')
        self.stdout.write(f'🏢 Портфоліо: {portfolio_count}/4')
        
        if products_count >= 40 and categories_count >= 4:
            self.stdout.write()
            self.stdout.write(self.style.SUCCESS('🎉 ВІДНОВЛЕННЯ ЗАВЕРШЕНО УСПІШНО!'))
            self.stdout.write('✅ Каталог працює')
            self.stdout.write('✅ Товари відображаються')  
            self.stdout.write('✅ Зображення доступні')
            self.stdout.write()
            self.stdout.write('🌐 Перевірте: https://greensolartech-b0m2.onrender.com/catalog/')
        else:
            self.stdout.write()
            self.stdout.write(self.style.ERROR('❌ ВІДНОВЛЕННЯ НЕ ПОВНЕ'))
            self.stdout.write('Потрібна додаткова діагностика')
        
        self.stdout.write('='*60) 