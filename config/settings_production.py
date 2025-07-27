"""
Production settings for Render deployment WITH media files as static
Оптимізовано для ідеального деплою без проблем з зображеннями
"""
import os
from pathlib import Path
from .settings import *

# SECURITY
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-production-key-change-me')

# Hosts
ALLOWED_HOSTS = [
    'greensolartech.com.ua',
    'www.greensolartech.com.ua', 
    'greensolartech.onrender.com',
    'sunpanel.onrender.com',
    '.onrender.com',
    '.render.com',
    'localhost',
    '127.0.0.1',
]

# Database - PostgreSQL on Render (using DATABASE_URL)
import dj_database_url

# Render автоматично створює DATABASE_URL
try:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    
    # Перевіряємо чи DATABASE_URL існує
    if not os.environ.get('DATABASE_URL'):
        raise ValueError("DATABASE_URL not found")
        
except (ValueError, Exception):
    # Fallback до SQLite якщо PostgreSQL недоступна
    print("⚠️ PostgreSQL недоступна, використовуємо SQLite")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Static files configuration with WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Статичні файли
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# МЕДІА ФАЙЛИ - ВИПРАВЛЕННЯ КОНФЛІКТУ
# Медіа файли мають окремий URL щоб не конфліктувати зі статичними
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'staticfiles', 'media')

# Додаємо і static і media папки до статичних директорій для WhiteNoise
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    # Додаємо media папку щоб WhiteNoise міг її обслуговувати
    ('media', os.path.join(BASE_DIR, 'media')),
]

# WhiteNoise налаштування для оптимальної роботи з медіа та статикою
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True  
WHITENOISE_STATIC_PREFIX = '/static/'
WHITENOISE_MAX_AGE = 31536000  # 1 рік кеш для статики
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'ico', 'woff', 'woff2']

# Додаткові налаштування для обслуговування медіа через WhiteNoise
WHITENOISE_ROOT = os.path.join(BASE_DIR, 'staticfiles')
WHITENOISE_INDEX_FILE = True

# Додаткові налаштування для медіа файлів
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'GreenSolarTech.pe@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = f'GreenSolarTech <{EMAIL_HOST_USER}>'
CONTACT_EMAIL = EMAIL_HOST_USER

# Security settings for production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_HSTS_SECONDS = 3600  # Для безпеки HTTPS

# Performance та кеш
CONN_MAX_AGE = 60

# Налаштування завантаження файлів для production
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB

# Logging оптимізований для Render
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'mainapp': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Django налаштування для стабільної роботи на Render
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
TIME_ZONE = 'Europe/Kiev'
USE_TZ = True

# Оптимізація для production
if not DEBUG:
    # Кешування шаблонів
    TEMPLATES[0]['APP_DIRS'] = False
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ] 