from django.contrib import admin
from .models import Product, Portfolio, Review, ProductImage, Category, Brand

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'alt_text', 'is_main', 'order')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'in_stock', 'featured', 'created_at']
    list_filter = ['category', 'brand', 'in_stock', 'featured', 'created_at']
    search_fields = ['name', 'brand__name', 'model', 'category__name']
    list_editable = ['in_stock', 'featured']
    prepopulated_fields = {}
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'description', 'price', 'image')
        }),
        ('Характеристики', {
            'fields': ('category', 'brand', 'model', 'power', 'efficiency', 'warranty', 'country')
        }),
        ('Статус', {
            'fields': ('in_stock', 'featured')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return ['created_at']
        return []


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'power_capacity', 'project_type', 'completion_date', 'featured', 'created_at']
    list_filter = ['project_type', 'featured', 'completion_date', 'created_at']
    search_fields = ['title', 'location', 'client_name', 'project_type']
    list_editable = ['featured']
    date_hierarchy = 'completion_date'
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'description', 'image')
        }),
        ('Деталі проєкту', {
            'fields': ('location', 'power_capacity', 'project_type', 'client_name', 'completion_date')
        }),
        ('Статус', {
            'fields': ('featured',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return ['created_at']
        return []


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'rating', 'project_type', 'location', 'is_published', 'created_at']
    list_filter = ['rating', 'project_type', 'is_published', 'created_at']
    search_fields = ['client_name', 'client_position', 'review_text', 'location']
    list_editable = ['is_published']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Інформація про клієнта', {
            'fields': ('client_name', 'client_position')
        }),
        ('Відгук', {
            'fields': ('review_text', 'rating')
        }),
        ('Деталі проєкту', {
            'fields': ('project_type', 'location')
        }),
        ('Статус', {
            'fields': ('is_published',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return ['created_at']
        return []


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return ['created_at']
        return []


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'website', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'website']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'logo', 'description', 'website')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return ['created_at']
        return []
