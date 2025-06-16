from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse


class IndexView(TemplateView):
    template_name = 'mainapp/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Arkuda Pellet — Деревні пелети з України',
            'description': 'Виробництво деревних пелет європейської якості у Рівненській області. Сертифіковано EN A1/A2. Доставка по Україні та Європі.',
            'keywords': 'деревні пелети, паливні пелети, Arkuda Pellet, Рівненська область, EN A1, EN A2, біопаливо',
            'company_info': {
                'name': 'Arkuda Pellet',
                'phones': ['+380500344881', '+380634952145'],
                'address': 'Рівненська область, Сарненський район, Україна',
                'production_capacity': 2500,  # тонн/міс
                'storage_area': 2000,  # м²
                'stock_capacity': 2000,  # тонн
            },
            'pellet_types': [
                {
                    'name': 'EN A1',
                    'diameter': '6 мм',
                    'ash_content': '< 0.7%',
                    'calorific_value': '4.6-5.3 кВт/кг',
                    'features': ['Найвища якість', 'Мінімум золи', 'Максимум тепла']
                },
                {
                    'name': 'EN A2', 
                    'diameter': '6-8 мм',
                    'ash_content': '< 1.2%',
                    'calorific_value': '4.3-5.0 кВт/кг',
                    'features': ['Відмінна якість', 'Економічно', 'Стабільне горіння']
                }
            ],
            'advantages': [
                {
                    'icon': '💰',
                    'title': 'Економічно',
                    'description': 'Дешевше за газ у 2-3 рази. Стабільна ціна протягом року.',
                },
                {
                    'icon': '🔒',
                    'title': 'Безпечно',
                    'description': 'Пресована деревина не вибухає. Безпечне зберігання та використання.',
                },
                {
                    'icon': '🌱',
                    'title': 'Екологічно',
                    'description': '100% деревина без хімії. Мінімальний викид CO₂ при згорянні.',
                }
            ],
            'production_stages': [
                {'step': 1, 'title': 'Закупівля сировини', 'description': 'Відбір якісної деревини'},
                {'step': 2, 'title': 'Переробка', 'description': 'Подрібнення та сушіння'},
                {'step': 3, 'title': 'Виробництво', 'description': 'Пресування у пелети'},
                {'step': 4, 'title': 'Зберігання', 'description': 'Складські приміщення 2000 м²'},
                {'step': 5, 'title': 'Узгодження', 'description': 'Контроль якості та сертифікація'},
                {'step': 6, 'title': 'Доставка', 'description': 'Логістика по Україні та Європі'},
                {'step': 7, 'title': 'Оплата', 'description': 'Зручні способи розрахунку'},
            ],
            'fuel_comparison': [
                {
                    'fuel': 'Пелети',
                    'heat_value': '4500 кВт/кг',
                    'ash': '0.7%',
                    'co2': 'Низький',
                    'sulfur': '< 0.03%',
                    'highlight': True
                },
                {
                    'fuel': 'Дрова',
                    'heat_value': '3000 кВт/кг', 
                    'ash': '1-3%',
                    'co2': 'Середній',
                    'sulfur': '< 0.05%',
                    'highlight': False
                },
                {
                    'fuel': 'Вугілля',
                    'heat_value': '5000 кВт/кг',
                    'ash': '8-15%',
                    'co2': 'Високий',
                    'sulfur': '0.5-3%',
                    'highlight': False
                },
                {
                    'fuel': 'Газ',
                    'heat_value': '9500 кВт/м³',
                    'ash': '0%',
                    'co2': 'Середній',
                    'sulfur': '0%',
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
        <loc>https://arkudapellet.com/</loc>
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
Sitemap: https://arkudapellet.com/sitemap.xml'''
    return HttpResponse(txt_content, content_type='text/plain')
