"""
Команда для підготовки портфоліо з усіма зображеннями
Оновлює всі проекти портфоліо та додає всі доступні зображення
"""
import os
import glob
from django.core.management.base import BaseCommand
from django.conf import settings
from mainapp.models import Portfolio
from datetime import date


class Command(BaseCommand):
    help = 'Підготовка портфоліо з усіма зображеннями'

    def handle(self, *args, **options):
        # Шлях до медіа файлів
        media_portfolio = os.path.join(settings.BASE_DIR, 'media', 'portfolio')
        
        if not os.path.exists(media_portfolio):
            self.stdout.write(
                self.style.WARNING('⚠️ Папка media/portfolio не знайдена!')
            )
            return

        # Знаходимо всі зображення
        portfolio_images = {}
        for image_file in os.listdir(media_portfolio):
            if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Групуємо за номером проекту
                if 'project1' in image_file or 'проект 1' in image_file or 'аналітика' in image_file or 'буд' in image_file:
                    project_key = 'project1'
                elif 'project2' in image_file or 'проект 2' in image_file or any(x in image_file for x in ['4083', '65825', '8534', '87209']):
                    project_key = 'project2'
                elif 'project3' in image_file or 'проект 3' in image_file or any(x in image_file for x in ['1494', '15578', '69046']):
                    project_key = 'project3'
                else:
                    continue
                    
                if project_key not in portfolio_images:
                    portfolio_images[project_key] = []
                portfolio_images[project_key].append(image_file)

        # Оновлюємо або створюємо проекти
        projects_data = {
            'project1': {
                'title': 'Приватна СЕС потужністю 17.2 кВт',
                'description': '''Цей проект демонструє ефективне використання сонячної енергії для приватного домогосподарства. 
                
Встановлена потужність: 17.2 кВт
Тип панелей: монокристалічні Longi Solar
Інвертор: Deye 15 кВт гібридний
Система накопичення: LiFePO4 акумулятори 20 кВт·год

Проект забезпечує повну енергонезалежність будинку та дозволяє продавати надлишки електроенергії за зеленим тарифом.''',
                'location': 'Київська область',
                'power_capacity': '17.2',
                'project_type': 'Приватна сонячна електростанція',
                'client_name': 'Приватний клієнт',
                'completion_date': date(2024, 8, 15)
            },
            'project2': {
                'title': 'Комерційна СЕС потужністю 43 кВт',
                'description': '''Комерційна сонячна електростанція для забезпечення електроенергією виробничого підприємства.

Встановлена потужність: 43 кВт
Тип панелей: монокристалічні високої ефективності
Інвертор: Deye 50 кВт трифазний
Система моніторингу: повний контроль генерації

Станція забезпечує 70% енергопотреб підприємства та значно знижує витрати на електроенергію.''',
                'location': 'м. Київ',
                'power_capacity': '43',
                'project_type': 'Комерційна сонячна електростанція',
                'client_name': 'ТОВ "Енергоефективність"',
                'completion_date': date(2024, 6, 20)
            },
            'project3': {
                'title': 'Приватна СЕС потужністю 10.6 кВт',
                'description': '''Компактна та ефективна сонячна електростанція для заміського будинку.

Встановлена потужність: 10.6 кВт  
Тип панелей: монокристалічні з чорною рамкою
Інвертор: Must PV18-5248 гібридний
Система накопичення: LVTS акумулятори 10 кВт·год

Оптимальне рішення для забезпечення електроенергією будинку та зарядки електромобіля.''',
                'location': 'Київська область',
                'power_capacity': '10.6',
                'project_type': 'Приватна сонячна електростанція',
                'client_name': 'Сім\'я Іваненко',
                'completion_date': date(2024, 9, 10)
            }
        }

        # Оновлюємо проекти
        for project_key, project_data in projects_data.items():
            # Знаходимо або створюємо проект
            portfolio, created = Portfolio.objects.get_or_create(
                title=project_data['title'],
                defaults=project_data
            )
            
            if not created:
                # Оновлюємо існуючий проект
                for field, value in project_data.items():
                    setattr(portfolio, field, value)
            
            # Встановлюємо головне зображення
            if project_key in portfolio_images and portfolio_images[project_key]:
                main_image = portfolio_images[project_key][0]
                portfolio.image = f'portfolio/{main_image}'
            
            portfolio.save()
            
            status = "створено" if created else "оновлено"
            self.stdout.write(f'✅ Проект "{portfolio.title}" {status}')
            
            # Показуємо доступні зображення
            if project_key in portfolio_images:
                self.stdout.write(f'   📷 Зображень: {len(portfolio_images[project_key])}')
                for img in portfolio_images[project_key]:
                    self.stdout.write(f'      - {img}')
            else:
                self.stdout.write('   ⚠️ Зображення не знайдені')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎨 Підготовка портфоліо завершена!'
                f'\n📊 Загалом проектів: {Portfolio.objects.count()}'
            )
        ) 