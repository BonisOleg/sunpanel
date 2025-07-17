from django.urls import path
from . import views

app_name = 'mainapp'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('portfolio/', views.PortfolioView.as_view(), name='portfolio'),
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('catalog/<str:category>/', views.CategoryView.as_view(), name='category'),
    path('reviews/', views.ReviewsView.as_view(), name='reviews'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
    path('robots.txt', views.robots_txt, name='robots'),
] 