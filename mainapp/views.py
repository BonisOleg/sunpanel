from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .models import Product, Portfolio, Review, ProductImage, Category, Brand
from .forms import ReviewForm
from django.db.models import Q, Avg
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
import json
from datetime import datetime


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
                'phones': ['+380737230675'],
                'email': 'GreenSolarTech.pe@gmail.com',
                'telegram': '@GreenSolarTech',
                'address': 'БЦ Центр вулиця Васильківська, 34, Київ, 02000',
                'production_capacity': 1.8,  # МВт встановлено
                'storage_area': 18,  # приватних СЕС
                'stock_capacity': 4,  # комерційних СЕС
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
        
        # Додаю товари до контексту з оптимізацією запитів
        context['products'] = Product.objects.filter(in_stock=True).select_related('category', 'brand').prefetch_related('images').order_by('-featured', 'name')  # Всі товари в наявності (рекомендовані першими)
        context['featured_products'] = Product.objects.filter(featured=True, in_stock=True).select_related('category', 'brand').prefetch_related('images')[:4]  # Рекомендовані товари
        
        return context


class PortfolioView(TemplateView):
    template_name = 'mainapp/portfolio.html'
    
    def get_project_images(self, project_prefix):
        """Отримує всі фото проекту за префіксом"""
        import os
        from django.conf import settings
        
        portfolio_path = os.path.join(settings.MEDIA_ROOT, 'portfolio')
        if not os.path.exists(portfolio_path):
            return []
            
        images = []
        for filename in os.listdir(portfolio_path):
            if filename.startswith(project_prefix) and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Виключаємо main файли оскільки це дублікати
                if not filename.endswith('_main.jpg'):
                    images.append(f'portfolio/{filename}')
        
        return sorted(images)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # ✅ БЕЗПЕЧНЕ отримання проектів з fallback
        try:
            # Спробуємо отримати проекти за ID
            project1 = Portfolio.objects.filter(id=4).first()
            project2 = Portfolio.objects.filter(id=5).first()  
            project3 = Portfolio.objects.filter(id=6).first()
            
            # Якщо проектів за ID немає, створюємо їх або беремо існуючі
            if not project1:
                project1, created = Portfolio.objects.get_or_create(
                    title__icontains='17.2',
                    defaults={
                        'title': 'Приватна СЕС потужністю 17.2 кВт',
                        'description': 'Приватна сонячна електростанція потужністю 17.2 кВт для резервного живлення приватного будинку.',
                        'location': 'Київська область',
                        'power_capacity': '17.2 кВт',
                        'project_type': 'Приватна СЕС',
                        'client_name': 'Приватний клієнт',
                        'image': 'portfolio/project1_main.jpg'
                    }
                )
            
            if not project2:
                project2, created = Portfolio.objects.get_or_create(
                    title__icontains='43',
                    defaults={
                        'title': 'Комерційна СЕС потужністю 43 кВт',
                        'description': 'Комерційна сонячна електростанція потужністю 43 кВт для підприємства.',
                        'location': 'Львівська область',
                        'power_capacity': '43 кВт',
                        'project_type': 'Комерційна СЕС',
                        'client_name': 'Промислове підприємство',
                        'image': 'portfolio/project2_main.jpg'
                    }
                )
                
            if not project3:
                project3, created = Portfolio.objects.get_or_create(
                    title__icontains='10.6',
                    defaults={
                        'title': 'Приватна СЕС потужністю 10.6 кВт',
                        'description': 'Приватна сонячна електростанція потужністю 10.6 кВт для енергонезалежності.',
                        'location': 'Дніпропетровська область', 
                        'power_capacity': '10.6 кВт',
                        'project_type': 'Приватна СЕС',
                        'client_name': 'Приватний клієнт',
                        'image': 'portfolio/project3_main.jpg'
                    }
                )
                
        except Exception as e:
            # ✅ BACKUP: створюємо базові проекти якщо щось не так
            print(f"Portfolio fallback mode: {e}")
            
            project1, _ = Portfolio.objects.get_or_create(
                title='Приватна СЕС потужністю 17.2 кВт',
                defaults={
                    'description': 'Приватна сонячна електростанція потужністю 17.2 кВт.',
                    'location': 'Київська область',
                    'power_capacity': '17.2 кВт',
                    'project_type': 'Приватна СЕС',
                    'image': 'portfolio/project1_main.jpg'
                }
            )
            
            project2, _ = Portfolio.objects.get_or_create(
                title='Комерційна СЕС потужністю 43 кВт',
                defaults={
                    'description': 'Комерційна сонячна електростанція потужністю 43 кВт.',
                    'location': 'Львівська область',
                    'power_capacity': '43 кВт', 
                    'project_type': 'Комерційна СЕС',
                    'image': 'portfolio/project2_main.jpg'
                }
            )
            
            project3, _ = Portfolio.objects.get_or_create(
                title='Приватна СЕС потужністю 10.6 кВт',
                defaults={
                    'description': 'Приватна сонячна електростанція потужністю 10.6 кВт.',
                    'location': 'Дніпропетровська область',
                    'power_capacity': '10.6 кВт',
                    'project_type': 'Приватна СЕС',
                    'image': 'portfolio/project3_main.jpg'
                }
            )
        
        context.update({
            'title': 'Портфоліо проєктів — GreenSolarTech',
            'description': 'Готові проєкти сонячних електростанцій від GreenSolarTech. Приватні та комерційні СЕС по всій Україні.',
            'keywords': 'портфоліо сонячних електростанцій, готові проєкти СЕС, приватні сонячні станції',
            'project1': project1,
            'project2': project2,
            'project3': project3
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
        
        # Базовий запит з оптимізацією
        products = Product.objects.filter(in_stock=True).select_related('category', 'brand').prefetch_related('images')
        
        # Фільтрація
        if category:
            products = products.filter(category__name__icontains=category)
        if brand:
            products = products.filter(brand__name__icontains=brand)
        if price_min:
            products = products.filter(price__gte=price_min)
        if price_max:
            products = products.filter(price__lte=price_max)
        
        # Унікальні категорії та бренди для фільтрів - лише ті що мають товари в наявності
        categories = Category.objects.filter(
            product__in_stock=True,
            is_active=True
        ).values_list('name', flat=True).distinct().order_by('name')
        
        brands = Brand.objects.filter(
            product__in_stock=True,
            is_active=True
        ).values_list('name', flat=True).distinct().order_by('name')
        
        # Товари по категоріях для каруселей (підтримка українських та російських назв)
        inverters = products.filter(
            Q(category__name__icontains='Інвертор') | Q(category__name__icontains='Инвертор')
        ).order_by('-featured', 'name')[:10]
        
        solar_panels = products.filter(
            Q(category__name__icontains='панел') | Q(category__name__icontains='панел')
        ).order_by('-featured', 'name')[:10]
        
        batteries = products.filter(
            Q(category__name__icontains='Акумулятор') | Q(category__name__icontains='Аккумулятор')
        ).order_by('-featured', 'name')[:10]
        
        backup_kits = products.filter(
            Q(category__name__icontains='комплект') | 
            Q(category__name__icontains='резервного') |
            Q(category__name__icontains='живлення')
        ).order_by('-featured', 'name')[:10]
        
        context.update({
            'title': 'Каталог товарів — GreenSolarTech',
            'description': 'Повний каталог обладнання для сонячних електростанцій: інвертори, панелі, акумулятори, комплекти.',
            'keywords': 'каталог сонячного обладнання, інвертори, сонячні панелі, акумулятори',
            'products': products.order_by('-featured', 'name'),  # Всі товари для загального каталогу
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
        
        # Маппінг англійських ключів URL на фільтри категорій (підтримка українських та російських назв)
        category_mapping = {
            'inverters': ['Інвертор', 'Инвертор'],
            'solar-panels': ['панел', 'панел'], 
            'batteries': ['Акумулятор', 'Аккумулятор'],
            'backup-power': ['комплект', 'комплек']
        }
        
        # Отримуємо ключові слова для категорії
        category_keywords = category_mapping.get(category_key, [category_key])
        
        # Отримуємо параметри фільтрації
        brand = self.request.GET.get('brand')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        # Базовий запит для категорії з підтримкою множинних ключових слів
        category_filter = Q()
        for keyword in category_keywords:
            category_filter |= Q(category__name__icontains=keyword)
        
        products = Product.objects.filter(in_stock=True).filter(category_filter).select_related('category', 'brand').prefetch_related('images')
        
        # Фільтрація
        if brand:
            products = products.filter(brand__name__icontains=brand)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        
        # Унікальні бренди для цієї категорії з оптимізацією
        brands = Brand.objects.filter(
            product__in=Product.objects.filter(category_filter, in_stock=True),
            is_active=True
        ).values_list('name', flat=True).distinct().order_by('name')
        
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


class ReviewsView(View):
    template_name = 'mainapp/reviews.html'
    
    def get(self, request):
        form = ReviewForm()
        context = {
            'title': 'Відгуки клієнтів — GreenSolarTech',
            'description': 'Відгуки наших клієнтів про будівництво сонячних електростанцій та якість обслуговування.',
            'keywords': 'відгуки про сонячні електростанції, відгуки клієнтів GreenSolarTech',
            'reviews': Review.objects.filter(is_published=True).order_by('-created_at'),
            'average_rating': Review.objects.filter(is_published=True).aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0,
            'total_reviews': Review.objects.filter(is_published=True).count(),
            'form': form
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_published = False  # Модерація перед публікацією
            review.save()
            messages.success(request, 'Дякуємо за ваш відгук! Він буде опублікований після модерації.')
            return redirect('mainapp:reviews')
        
        # Якщо форма невалідна, показуємо помилки
        context = {
            'title': 'Відгуки клієнтів — GreenSolarTech',
            'description': 'Відгуки наших клієнтів про будівництво сонячних електростанцій та якість обслуговування.',
            'keywords': 'відгуки про сонячні електростанції, відгуки клієнтів GreenSolarTech',
            'reviews': Review.objects.filter(is_published=True).order_by('-created_at'),
            'average_rating': Review.objects.filter(is_published=True).aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0,
            'total_reviews': Review.objects.filter(is_published=True).count(),
            'form': form
        }
        return render(request, self.template_name, context)


def sitemap_xml(request):
    """Генерація sitemap.xml для SEO"""
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://greensolartech.com.ua/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>monthly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://greensolartech.com.ua/portfolio/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://greensolartech.com.ua/catalog/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://greensolartech.com.ua/reviews/</loc>
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
Sitemap: https://greensolartech.com.ua/sitemap.xml'''
    return HttpResponse(txt_content, content_type='text/plain')


class ProductDetailView(TemplateView):
    template_name = 'mainapp/product_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = kwargs.get('product_id')
        
        # Отримуємо товар або 404 з оптимізацією
        product = get_object_or_404(
            Product.objects.select_related('category', 'brand').prefetch_related('images'),
            id=product_id, 
            in_stock=True
        )
        
        # Отримуємо всі зображення товару (вже завантажені через prefetch_related)
        product_images = product.images.all().order_by('order', 'id')
        
        # Якщо немає додаткових зображень, використовуємо основне
        if not product_images and product.image:
            main_image = product  # ✅ ПЕРЕДАЄМО ОБ'ЄКТ ТОВАРУ, НЕ ImageField!
        else:
            main_image = product_images.first() if product_images else product  # ✅ ОБ'ЄКТ ProductImage або Product!
        
        # Схожі товари (з тієї ж категорії або бренду) з оптимізацією
        similar_products = Product.objects.filter(
            Q(category=product.category) | Q(brand=product.brand),
            in_stock=True
        ).exclude(id=product.id).select_related('category', 'brand').prefetch_related('images')[:6]
        
        context.update({
            'title': f'{product.name} — GreenSolarTech',
            'description': f'{product.name} від {product.brand}. {product.description[:150]}...',
            'keywords': f'{product.name}, {product.brand}, {product.category}, сонячне обладнання',
            'product': product,
            'product_images': product_images,
            'main_image': main_image,
            'similar_products': similar_products,
        })
        
        return context


# API Views
@method_decorator(csrf_exempt, name='dispatch')
class CallbackAPIView(View):
    """API для обробки заявок зворотного зв'язку"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Валідація данних
            name = data.get('name', '').strip()
            phone = data.get('phone', '').strip()
            message = data.get('message', '').strip()
            
            if not name:
                return JsonResponse({'error': 'Імʼя є обовʼязковим'}, status=400)
            
            if not phone:
                return JsonResponse({'error': 'Телефон є обовʼязковим'}, status=400)
            
            # Підготовка email листа
            subject = f'Нова заявка на зворотний звʼязок - {name}'
            
            email_message = f"""
Нова заявка на зворотний звʼязок з сайту GreenSolarTech

Ім'я: {name}
Телефон: {phone}
Повідомлення: {message if message else 'Не вказано'}

Дата та час: {datetime.now().strftime('%d.%m.%Y о %H:%M')}

---
Автоматичне повідомлення з сайту greensolartech.com.ua
            """
            
            # Відправка email
            try:
                send_mail(
                    subject=subject,
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Заявку успішно відправлено'
                })
                
            except Exception as email_error:
                print(f"Помилка відправки email: {email_error}")
                return JsonResponse({
                    'error': 'Помилка відправки заявки. Спробуйте пізніше.'
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Невірний формат данних'}, status=400)
        except Exception as e:
            print(f"Загальна помилка API: {e}")
            return JsonResponse({'error': 'Внутрішня помилка сервера'}, status=500)
    
    def get(self, request):
        return JsonResponse({'error': 'Метод не дозволений'}, status=405)


@method_decorator(csrf_exempt, name='dispatch')
class OrderAPIView(View):
    """API для обробки замовлень з корзини"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Валідація данних
            name = data.get('name', '').strip()
            phone = data.get('phone', '').strip()
            email = data.get('email', '').strip()
            comment = data.get('comment', '').strip()
            items = data.get('items', [])
            total = data.get('total', 0)
            
            if not name:
                return JsonResponse({'error': 'Імʼя є обовʼязковим'}, status=400)
            
            if not phone:
                return JsonResponse({'error': 'Телефон є обовʼязковим'}, status=400)
            
            if not email:
                return JsonResponse({'error': 'Email є обовʼязковим'}, status=400)
            
            if not items:
                return JsonResponse({'error': 'Корзина пуста'}, status=400)
            
            # Формування списку товарів
            items_list = []
            for item in items:
                item_text = f"• {item.get('name', 'Невідомий товар')} x {item.get('quantity', 1)} шт. - ₴{item.get('price', 0)}"
                items_list.append(item_text)
            
            items_text = '\n'.join(items_list)
            
            # Підготовка email листа
            subject = f'Нове замовлення #{datetime.now().strftime("%Y%m%d%H%M")} - {name}'
            
            email_message = f"""
Нове замовлення з сайту GreenSolarTech

ДАНІ ЗАМОВНИКА:
Ім'я: {name}
Телефон: {phone}
Email: {email}

ТОВАРИ:
{items_text}

ЗАГАЛЬНА СУМА: ₴{total}

КОМЕНТАР: {comment if comment else 'Не вказано'}

Дата та час: {datetime.now().strftime('%d.%m.%Y о %H:%M')}

---
Автоматичне повідомлення з сайту greensolartech.com.ua
            """
            
            # Відправка email
            try:
                send_mail(
                    subject=subject,
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Замовлення успішно відправлено'
                })
                
            except Exception as email_error:
                print(f"Помилка відправки email замовлення: {email_error}")
                return JsonResponse({
                    'error': 'Помилка відправки замовлення. Спробуйте пізніше.'
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Невірний формат данних'}, status=400)
        except Exception as e:
            print(f"Загальна помилка API замовлень: {e}")
            return JsonResponse({'error': 'Внутрішня помилка сервера'}, status=500)
    
    def get(self, request):
        return JsonResponse({'error': 'Метод не дозволений'}, status=405)
