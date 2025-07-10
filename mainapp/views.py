from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse


class IndexView(TemplateView):
    template_name = 'mainapp/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'GreenSolarTech — Сонячні електростанції в Україні',
            'description': 'Проектування та будівництво сонячних електростанцій під ключ. Понад 50 МВт встановлених потужностей. Зелений тариф та енергонезалежність.',
            'keywords': 'сонячні електростанції, сонячні панелі, GreenSolarTech, Київ, зелений тариф, альтернативна енергетика',
            'company_info': {
                'name': 'GreenSolarTech',
                'phones': ['+380500344881', '+380634952145'],
                'address': 'Київська область, м. Київ, Україна',
                'production_capacity': 50,  # МВт встановлено
                'storage_area': 105,  # приватних СЕС
                'stock_capacity': 22,  # комерційних СЕС
            },
            'panel_types': [
                {
                    'name': 'Монокристалічні',
                    'power': '540-700 Вт',
                    'efficiency': 'до 22%',
                    'warranty': '25 років',
                    'features': ['Найвища якість', 'Максимум енергії', 'Надійність']
                },
                {
                    'name': 'Полікристалічні', 
                    'power': '440-550 Вт',
                    'efficiency': 'до 20%',
                    'warranty': '20-25 років',
                    'features': ['Відмінна якість', 'Економічно', 'Стабільна генерація']
                }
            ],
            'advantages': [
                {
                    'icon': '💰',
                    'title': 'Економічно',
                    'description': 'Окупність за 5-7 років. Зелений тариф для продажу електроенергії.',
                },
                {
                    'icon': '⚡',
                    'title': 'Енергонезалежність',
                    'description': 'Власна електроенергія цілодобово. Резервне живлення при відключеннях.',
                },
                {
                    'icon': '🌱',
                    'title': 'Екологічно',
                    'description': '100% чиста енергія сонця. Зниження викидів CO₂.',
                }
            ],
            'project_stages': [
                {'step': 1, 'title': 'Консультація', 'description': 'Безкоштовний виїзд інженера'},
                {'step': 2, 'title': 'Проектування', 'description': 'Розробка індивідуального проєкту'},
                {'step': 3, 'title': 'Узгодження', 'description': 'Отримання дозволів та підключення'},
                {'step': 4, 'title': 'Постачання', 'description': 'Доставка обладнання на об\'єкт'},
                {'step': 5, 'title': 'Монтаж', 'description': 'Професійне встановлення станції'},
                {'step': 6, 'title': 'Пуско-налагодження', 'description': 'Тестування та введення в експлуатацію'},
                {'step': 7, 'title': 'Сервіс', 'description': 'Гарантійне та післягарантійне обслуговування'},
            ],
            'energy_comparison': [
                {
                    'fuel': 'Сонячна енергія',
                    'heat_value': '0.05-0.15 €/кВт·год',
                    'ash': '0 г/кВт·год',
                    'co2': '100% відновлювана',
                    'sulfur': 'Повна',
                    'highlight': True
                },
                {
                    'fuel': 'Мережева електроенергія',
                    'heat_value': '0.20-0.30 €/кВт·год', 
                    'ash': '400-800 г/кВт·год',
                    'co2': 'Частково',
                    'sulfur': 'Обмежена',
                    'highlight': False
                },
                {
                    'fuel': 'Дизель-генератор',
                    'heat_value': '0.40-0.60 €/кВт·год',
                    'ash': '1200 г/кВт·год',
                    'co2': 'Ні',
                    'sulfur': 'Відсутня',
                    'highlight': False
                },
                {
                    'fuel': 'Природний газ',
                    'heat_value': '0.25-0.35 €/кВт·год',
                    'ash': '600 г/кВт·год',
                    'co2': 'Ні',
                    'sulfur': 'Залежна',
                    'highlight': False
                }
            ],
            'distances_to_borders': [
                {'country': 'Польща', 'distance': '205-432 км'},
                {'country': 'Словаччина', 'distance': '586 км'},
                {'country': 'Угорщина', 'distance': '581 км'},
            ]
        })
        return context


def sitemap_xml(request):
    """Генерація sitemap.xml для SEO"""
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://greensolalrtech.com/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>monthly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>'''
    return HttpResponse(xml_content, content_type='application/xml')


def robots_txt(request):
    """Генерація robots.txt для SEO"""
    txt_content = '''User-agent: *
Allow: /
Sitemap: https://greensolalrtech.com/sitemap.xml'''
    return HttpResponse(txt_content, content_type='text/plain')
