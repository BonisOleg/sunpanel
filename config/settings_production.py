"""
Production settings for Render deployment WITHOUT external media services
All media files will be served as static files
"""
import os
from pathlib import Path
from .settings import *

# SECURITY
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-production-key-change-me')

# Hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1', 
    '.onrender.com',
    '.render.com',
    'greensolartech.onrender.com'
]

# Database - PostgreSQL on Render
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'greensolartech'),
        'USER': os.environ.get('DATABASE_USER', 'greensolartech'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}

# Static files configuration with WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ⚡ КРИТИЧНО: Медіа файли як статичні файли
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Додаємо медіа файли до статичних
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    # Медіа файли будуть копіюватися до static/media/
]

# WhiteNoise налаштування
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

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

# Performance
CONN_MAX_AGE = 60

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
} 