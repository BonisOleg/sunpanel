import re
from django.core.management.base import BaseCommand
from mainapp.models import Product, Category, Brand, Portfolio, Review

class Command(BaseCommand):
    help = 'Перевіряє орфографічні помилки у описах товарів та інших моделях'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Автоматично виправити знайдені помилки',
        )

    def handle(self, *args, **options):
        fix_errors = options['fix']
        
        self.stdout.write("🔍 Перевірка орфографічних помилок...")
        
        # Словник частих орфографічних помилок
        spelling_errors = {
            # Неправильні закінчення
            'нй ': 'ний ',
            'нй.': 'ний.',
            'нй,': 'ний,',
            'сонячнй': 'сонячний',
            'гібриднй': 'гібридний',
            'високовольтнй': 'високовольтний',
            'акумуляторнй': 'акумуляторний',
            'літвй': 'літієвий',
            
            # Неправильні одиниці вимірювання
            'квт ': 'кВт ',
            'квт·год': 'кВт·год',
            ' в ': ' В ',
            ' в.': ' В.',
            ' в,': ' В,',
            'вт ': 'Вт ',
            ' а ': ' А ',
            ' а.': ' А.',
            ' а,': ' А,',
            'агод': 'А·год',
            'вт·год': 'Вт·год',
            
            # Технічні терміни
            'інветор': 'інвертор',
            'інвeртор': 'інвертор',
            'елeктростанція': 'електростанція',
            'елeктричний': 'електричний',
            'батaрея': 'батарея',
            'система': 'система',
            
            # Бренди та моделі
            'deye': 'Deye',
            'must': 'Must',
            'longi': 'Longi',
            'lifepo4': 'LiFePO4',
            'pv18': 'PV18',
            'sun-': 'SUN-',
            
            # Дублі символів та пробілів
            '  ': ' ',
            '..': '.',
            ',,': ',',
            '( ': '(',
            ' )': ')',
            ' ,': ',',
            ' .': '.',
            
            # Російські залишки
            'хранения': 'зберігання',
            'енергии': 'енергії',
            'система хранения': 'система зберігання',
            'высоковольтная': 'високовольтна',
            'аккумуляторная': 'акумуляторна',
            'солнечная': 'сонячна',
            'панель': 'панель',
            'модуль': 'модуль',
            'электростанция': 'електростанція',
            'питание': 'живлення',
            'мощность': 'потужність',
            'напряжение': 'напруга',
            'гибридный': 'гібридний',
            'резервного питания': 'резервного живлення',
            'комплект резервного': 'комплект резервного',
            

            
            # Неправильні написання імен та слів
            'КиївськА': 'Київська',
            'ПриватнА': 'Приватна', 
            'КомерційнА': 'Комерційна',
            'СонячнА': 'Сонячна',
            'АкумуляторнА': 'Акумуляторна',
            'ВисоковольтнА': 'Високовольтна',
            'ГібриднА': 'Гібридна',
            'СвітланА': 'Світлана',
            'АннА': 'Анна',
            'МаринА': 'Марина',
            'ОдеськА': 'Одеська',
            'ВінницькА': 'Вінницька',
            'ХерсонськА': 'Херсонська',
            'ЛьвівськА': 'Львівська',
            'ДніпропетровськА': 'Дніпропетровська',
            'ПолтавськА': 'Полтавська',
            'Івано-ФранківськА': 'Івано-Франківська',
            'модуліВ': 'модулів',
            'нА ': 'на ',
            'тА ': 'та ',
        }
        
        total_errors = 0
        fixed_errors = 0
        
        # Перевіряємо товари
        self.stdout.write("\n📦 Перевірка товарів...")
        products = Product.objects.all()
        
        for product in products:
            errors_found = []
            
            # Перевіряємо назву
            original_name = product.name
            fixed_name = self.fix_text(original_name, spelling_errors)
            if original_name != fixed_name:
                errors_found.append(f"Назва: {original_name} → {fixed_name}")
            
            # Перевіряємо опис
            original_desc = product.description
            fixed_desc = self.fix_text(original_desc, spelling_errors)
            if original_desc != fixed_desc:
                errors_found.append(f"Опис: змінено")
            
            # Перевіряємо додаткові поля
            for field in ['model', 'power', 'efficiency', 'warranty', 'country']:
                original_value = getattr(product, field, '')
                if original_value:
                    fixed_value = self.fix_text(original_value, spelling_errors)
                    if original_value != fixed_value:
                        errors_found.append(f"{field}: {original_value} → {fixed_value}")
            
            if errors_found:
                total_errors += len(errors_found)
                self.stdout.write(f"\n❌ Товар ID {product.id}: {product.name}")
                for error in errors_found:
                    self.stdout.write(f"   • {error}")
                
                if fix_errors:
                    product.name = fixed_name
                    product.description = fixed_desc
                    for field in ['model', 'power', 'efficiency', 'warranty', 'country']:
                        original_value = getattr(product, field, '')
                        if original_value:
                            setattr(product, field, self.fix_text(original_value, spelling_errors))
                    product.save()
                    fixed_errors += len(errors_found)
                    self.stdout.write(f"   ✅ Виправлено!")
        
        # Перевіряємо категорії
        self.stdout.write("\n📂 Перевірка категорій...")
        categories = Category.objects.all()
        
        for category in categories:
            errors_found = []
            
            original_name = category.name
            fixed_name = self.fix_text(original_name, spelling_errors)
            if original_name != fixed_name:
                errors_found.append(f"Назва: {original_name} → {fixed_name}")
            
            original_desc = category.description
            fixed_desc = self.fix_text(original_desc, spelling_errors)
            if original_desc != fixed_desc:
                errors_found.append(f"Опис: змінено")
            
            if errors_found:
                total_errors += len(errors_found)
                self.stdout.write(f"\n❌ Категорія ID {category.id}: {category.name}")
                for error in errors_found:
                    self.stdout.write(f"   • {error}")
                
                if fix_errors:
                    category.name = fixed_name
                    category.description = fixed_desc
                    category.save()
                    fixed_errors += len(errors_found)
                    self.stdout.write(f"   ✅ Виправлено!")
        
        # Перевіряємо бренди
        self.stdout.write("\n🏷️ Перевірка брендів...")
        brands = Brand.objects.all()
        
        for brand in brands:
            errors_found = []
            
            original_name = brand.name
            fixed_name = self.fix_text(original_name, spelling_errors)
            if original_name != fixed_name:
                errors_found.append(f"Назва: {original_name} → {fixed_name}")
            
            original_desc = brand.description
            fixed_desc = self.fix_text(original_desc, spelling_errors)
            if original_desc != fixed_desc:
                errors_found.append(f"Опис: змінено")
            
            if errors_found:
                total_errors += len(errors_found)
                self.stdout.write(f"\n❌ Бренд ID {brand.id}: {brand.name}")
                for error in errors_found:
                    self.stdout.write(f"   • {error}")
                
                if fix_errors:
                    brand.name = fixed_name
                    brand.description = fixed_desc
                    brand.save()
                    fixed_errors += len(errors_found)
                    self.stdout.write(f"   ✅ Виправлено!")
        
        # Перевіряємо проєкти портфоліо
        self.stdout.write("\n🏗️ Перевірка проєктів портфоліо...")
        portfolios = Portfolio.objects.all()
        
        for portfolio in portfolios:
            errors_found = []
            
            original_title = portfolio.title
            fixed_title = self.fix_text(original_title, spelling_errors)
            if original_title != fixed_title:
                errors_found.append(f"Назва: {original_title} → {fixed_title}")
            
            original_desc = portfolio.description
            fixed_desc = self.fix_text(original_desc, spelling_errors)
            if original_desc != fixed_desc:
                errors_found.append(f"Опис: змінено")
            
            for field in ['location', 'power_capacity', 'project_type', 'client_name']:
                original_value = getattr(portfolio, field, '')
                if original_value:
                    fixed_value = self.fix_text(original_value, spelling_errors)
                    if original_value != fixed_value:
                        errors_found.append(f"{field}: {original_value} → {fixed_value}")
            
            if errors_found:
                total_errors += len(errors_found)
                self.stdout.write(f"\n❌ Проєкт ID {portfolio.id}: {portfolio.title}")
                for error in errors_found:
                    self.stdout.write(f"   • {error}")
                
                if fix_errors:
                    portfolio.title = fixed_title
                    portfolio.description = fixed_desc
                    for field in ['location', 'power_capacity', 'project_type', 'client_name']:
                        original_value = getattr(portfolio, field, '')
                        if original_value:
                            setattr(portfolio, field, self.fix_text(original_value, spelling_errors))
                    portfolio.save()
                    fixed_errors += len(errors_found)
                    self.stdout.write(f"   ✅ Виправлено!")
        
        # Перевіряємо відгуки
        self.stdout.write("\n⭐ Перевірка відгуків...")
        reviews = Review.objects.all()
        
        for review in reviews:
            errors_found = []
            
            original_text = review.review_text
            fixed_text = self.fix_text(original_text, spelling_errors)
            if original_text != fixed_text:
                errors_found.append(f"Текст відгуку: змінено")
            
            for field in ['client_name', 'client_position', 'project_type', 'location']:
                original_value = getattr(review, field, '')
                if original_value:
                    fixed_value = self.fix_text(original_value, spelling_errors)
                    if original_value != fixed_value:
                        errors_found.append(f"{field}: {original_value} → {fixed_value}")
            
            if errors_found:
                total_errors += len(errors_found)
                self.stdout.write(f"\n❌ Відгук ID {review.id}: {review.client_name}")
                for error in errors_found:
                    self.stdout.write(f"   • {error}")
                
                if fix_errors:
                    review.review_text = fixed_text
                    for field in ['client_name', 'client_position', 'project_type', 'location']:
                        original_value = getattr(review, field, '')
                        if original_value:
                            setattr(review, field, self.fix_text(original_value, spelling_errors))
                    review.save()
                    fixed_errors += len(errors_found)
                    self.stdout.write(f"   ✅ Виправлено!")
        
        # Підсумки
        if fix_errors:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 ПЕРЕВІРКА ЗАВЕРШЕНА\n"
                    f"Знайдено помилок: {total_errors}\n"
                    f"Виправлено: {fixed_errors}"
                )
            )
        else:
            if total_errors > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"\n⚠️ ЗНАЙДЕНО ПОМИЛКИ\n"
                        f"Всього помилок: {total_errors}\n"
                        f"Для виправлення запустіть команду з параметром --fix"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✅ ПОМИЛОК НЕ ЗНАЙДЕНО\n"
                        f"Всі тексти виглядають коректно!"
                    )
                )

    def fix_text(self, text, errors_dict):
        """Виправляє текст відповідно до словника помилок"""
        if not text:
            return text
        
        result = str(text)
        
        # Застосовуємо виправлення
        for wrong, correct in errors_dict.items():
            result = result.replace(wrong, correct)
        
        # Очищаємо зайві пробіли
        result = re.sub(r'\s+', ' ', result).strip()
        
        # Перевіряємо на наявність підозрілих російських символів
        if re.search(r'[ёъыэ]', result):
            # Заміняємо російські символи на українські
            result = result.replace('ё', 'е')
            result = result.replace('ъ', '')
            result = result.replace('ы', 'и')
            result = result.replace('э', 'е')
        
        return result

    def check_suspicious_patterns(self, text):
        """Перевіряє на підозрілі паттерни у тексті"""
        if not text:
            return []
        
        suspicious = []
        
        # Перевіряємо на російські слова
        russian_patterns = [
            r'\bгибридн\w+',
            r'\bинвертор\w*',
            r'\bсолнечн\w+',
            r'\bаккумулятор\w+',
            r'\bхранени\w+',
            r'\bэнерги\w+',
            r'\bмощност\w+',
            r'\bнапряжени\w+',
        ]
        
        for pattern in russian_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                suspicious.extend(matches)
        
        # Перевіряємо на неправильні закінчення
        incorrect_endings = re.findall(r'\w+нй\b', text)
        if incorrect_endings:
            suspicious.extend(incorrect_endings)
        
        # Перевіряємо на дублі пробілів
        if '  ' in text:
            suspicious.append('подвійні пробіли')
        
        return suspicious 