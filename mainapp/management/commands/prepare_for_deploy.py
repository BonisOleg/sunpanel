from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Підготовка проєкту до деплою: орфографія, медіа, тести'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-spelling',
            action='store_true',
            help='Пропустити перевірку орфографії',
        )
        parser.add_argument(
            '--skip-media',
            action='store_true', 
            help='Пропустити підготовку медіа файлів',
        )
        parser.add_argument(
            '--skip-tests',
            action='store_true',
            help='Пропустити тестування',
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Підготовка до деплою...\n")
        
        # Крок 1: Повне очищення російського контенту
        if not options['skip_spelling']:
            self.stdout.write("🧹 Повне очищення російського контенту...")
            try:
                call_command('clean_russian_content')
                self.stdout.write(self.style.SUCCESS("   ✅ Російський контент очищений"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Помилка при очищенні: {str(e)}"))
                return
        
        # Крок 2: Видалення російських дублікатів
        if not options['skip_spelling']:
            self.stdout.write("🗑️ Видалення російських дублікатів категорій...")
            try:
                call_command('remove_russian_categories')
                self.stdout.write(self.style.SUCCESS("   ✅ Російські дублікати видалені"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"   ⚠️ Дублікати не знайдені або вже видалені: {str(e)}"))
        
        # Крок 3: Перевірка та виправлення орфографії
        if not options['skip_spelling']:
            self.stdout.write("\n✏️ Перевірка та виправлення орфографії...")
            try:
                call_command('check_spelling_errors', '--fix')
                self.stdout.write(self.style.SUCCESS("   ✅ Орфографічні помилки виправлені"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Помилка при перевірці орфографії: {str(e)}"))
                return
        
        # Крок 4: Підготовка медіа файлів
        if not options['skip_media']:
            self.stdout.write("\n📁 Підготовка медіа файлів...")
            try:
                call_command('copy_media_to_static', '--clean')
                self.stdout.write(self.style.SUCCESS("   ✅ Медіа файли скопійовані"))
                
                call_command('prepare_portfolio')
                self.stdout.write(self.style.SUCCESS("   ✅ Портфоліо підготовлене"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Помилка при підготовці медіа: {str(e)}"))
        
        # Крок 5: Тестування
        if not options['skip_tests']:
            self.stdout.write("\n🧪 Запуск тестів...")
            try:
                call_command('test_deployment')
                self.stdout.write(self.style.SUCCESS("   ✅ Всі тести пройдені"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Помилка при тестуванні: {str(e)}"))
                return
        
        # Крок 6: Перевірка готовності
        self.stdout.write("\n📊 Фінальна перевірка...")
        
        from mainapp.models import Product, Category, Portfolio, Review
        
        products_count = Product.objects.count()
        categories_count = Category.objects.count()
        portfolios_count = Portfolio.objects.count()
        reviews_count = Review.objects.count()
        
        self.stdout.write(f"   📦 Товарів: {products_count}")
        self.stdout.write(f"   📂 Категорій: {categories_count}")
        self.stdout.write(f"   🏗️ Проєктів портфоліо: {portfolios_count}")
        self.stdout.write(f"   ⭐ Відгуків: {reviews_count}")
        
        # Перевірка медіа файлів
        media_path = os.path.join(settings.BASE_DIR, 'media')
        static_media_path = os.path.join(settings.BASE_DIR, 'static', 'media')
        
        if os.path.exists(media_path):
            media_files = sum([len(files) for r, d, files in os.walk(media_path)])
            self.stdout.write(f"   📸 Медіа файлів: {media_files}")
        
        if os.path.exists(static_media_path):
            static_files = sum([len(files) for r, d, files in os.walk(static_media_path)])
            self.stdout.write(f"   📁 Статичних медіа: {static_files}")
        
        # Перевірка російських залишків
        russian_categories = Category.objects.filter(
            name__icontains='Аккумуляторы'
        ) | Category.objects.filter(
            name__icontains='Инверторы'
        ) | Category.objects.filter(
            name__icontains='Солнечные'
        )
        
        if russian_categories.exists():
            self.stdout.write(self.style.WARNING(f"   ⚠️ Знайдено {russian_categories.count()} російських категорій"))
            for cat in russian_categories:
                self.stdout.write(f"      - {cat.name}")
        else:
            self.stdout.write(self.style.SUCCESS("   ✅ Російських категорій не знайдено"))
        
        # Інструкції по деплою
        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 ПРОЄКТ ГОТОВИЙ ДО ДЕПЛОЮ!\n\n"
                f"📋 Наступні кроки:\n"
                f"   1. git add .\n"
                f"   2. git commit -m '🚀 Підготовка до деплою: орфографія + медіа'\n"
                f"   3. git push origin main\n\n"
                f"💡 При деплої на Render автоматично виконається:\n"
                f"   - Повне очищення російського контенту\n"
                f"   - Видалення російських дублікатів\n"
                f"   - Виправлення орфографічних помилок\n"
                f"   - Налаштування медіа файлів\n"
                f"   - Збір статичних файлів\n\n"
                f"🔗 Файл build.sh оновлено для автоматичного очищення російської мови"
            )
        ) 