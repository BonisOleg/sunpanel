from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from .models import Product, Portfolio, Review
from django.db.models import Q, Avg
from django.db import models


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
        
        # Додаю товари до контексту
        context['products'] = Product.objects.filter(in_stock=True).order_by('-featured', 'name')  # Всі товари в наявності (рекомендовані першими)
        context['featured_products'] = Product.objects.filter(featured=True, in_stock=True)[:4]  # Рекомендовані товари
        
        return context


class PortfolioView(TemplateView):
    template_name = 'mainapp/portfolio.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Портфоліо проєктів — GreenSolarTech',
            'description': 'Готові проєкти сонячних електростанцій від GreenSolarTech. Приватні та комерційні СЕС по всій Україні.',
            'keywords': 'портфоліо сонячних електростанцій, готові проєкти СЕС, приватні сонячні станції',
            'portfolio_projects': Portfolio.objects.all().order_by('-featured', '-completion_date'),
            'featured_projects': Portfolio.objects.filter(featured=True)[:3]
        })
        return context


class CatalogView(TemplateView):
    template_name = 'mainapp/catalog.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Отримуємо параметри фільтрації
        category = self.request.GET.get('category')
        brand = self.request.GET.get('brand')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        
        # Базовий запит
        products = Product.objects.filter(in_stock=True)
        
        # Фільтрація
        if category:
            products = products.filter(category__icontains=category)
        if brand:
            products = products.filter(brand__icontains=brand)
        if price_min:
            products = products.filter(price__gte=price_min)
        if price_max:
            products = products.filter(price__lte=price_max)
        
        # Унікальні категорії та бренди для фільтрів
        categories = Product.objects.values_list('category', flat=True).distinct()
        brands = Product.objects.values_list('brand', flat=True).distinct()
        
        # Товари по категоріях для каруселей
        inverters = products.filter(category__icontains='інвертор').order_by('-featured', 'name')[:10]
        solar_panels = products.filter(category__icontains='панель').order_by('-featured', 'name')[:10]
        batteries = products.filter(category__icontains='акумулятор').order_by('-featured', 'name')[:10]
        backup_kits = products.filter(category__icontains='комплект').order_by('-featured', 'name')[:10]
        
        context.update({
            'title': 'Каталог товарів — GreenSolarTech',
            'description': 'Повний каталог обладнання для сонячних електростанцій: інвертори, панелі, акумулятори, комплекти.',
            'keywords': 'каталог сонячного обладнання, інвертори, сонячні панелі, акумулятори',
            'categories': categories,
            'brands': brands,
            'selected_category': category,
            'selected_brand': brand,
            'price_min': price_min,
            'price_max': price_max,
            'inverters': inverters,
            'solar_panels': solar_panels,
            'batteries': batteries,
            'backup_kits': backup_kits,
        })
        return context


class CategoryView(TemplateView):
    template_name = 'mainapp/category.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_key = kwargs.get('category')
        
        # Маппінг англійських ключів URL на українські категорії
        category_mapping = {
            'inverters': 'інвертор',
            'solar-panels': 'сонячна панель', 
            'batteries': 'акумулятор',
            'backup-power': 'комплект резервного живлення'
        }
        
        # Отримуємо українську назву категорії
        ukrainian_category = category_mapping.get(category_key, category_key)
        
        # Отримуємо параметри фільтрації
        brand = self.request.GET.get('brand')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        # Базовий запит для категорії
        products = Product.objects.filter(in_stock=True, category__icontains=ukrainian_category)
        
        # Фільтрація
        if brand:
            products = products.filter(brand__icontains=brand)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        
        # Унікальні бренди для цієї категорії
        brands = Product.objects.filter(category__icontains=ukrainian_category).values_list('brand', flat=True).distinct()
        
        # Назви категорій для відображення
        category_names = {
            'inverters': 'Інвертори',
            'solar-panels': 'Сонячні панелі', 
            'batteries': 'Акумуляторні батареї',
            'backup-power': 'Комплекти резервного живлення'
        }
        
        category_name = category_names.get(category_key, category_key.title())
        
        context.update({
            'title': f'{category_name} — GreenSolarTech',
            'description': f'Каталог {category_name.lower()} для сонячних електростанцій від провідних виробників.',
            'keywords': f'{category_name.lower()}, сонячне обладнання, GreenSolarTech',
            'products': products.order_by('-featured', 'name'),
            'category_name': category_name,
            'category_key': category_key,
            'brands': brands,
            'selected_brand': brand,
            'min_price': min_price,
            'max_price': max_price
        })
        return context


class ReviewsView(TemplateView):
    template_name = 'mainapp/reviews.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Відгуки клієнтів — GreenSolarTech',
            'description': 'Відгуки наших клієнтів про будівництво сонячних електростанцій та якість обслуговування.',
            'keywords': 'відгуки про сонячні електростанції, відгуки клієнтів GreenSolarTech',
            'reviews': Review.objects.filter(is_published=True).order_by('-created_at'),
            'average_rating': Review.objects.filter(is_published=True).aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0
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
    <url>
        <loc>https://greensolalrtech.com/portfolio/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://greensolalrtech.com/catalog/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://greensolalrtech.com/reviews/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
</urlset>'''
    return HttpResponse(xml_content, content_type='application/xml')


def robots_txt(request):
    """Генерація robots.txt для SEO"""
    txt_content = '''User-agent: *
Allow: /
Sitemap: https://greensolalrtech.com/sitemap.xml'''
    return HttpResponse(txt_content, content_type='text/plain')
