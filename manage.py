#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Force production settings for Render deployment
    if 'render.com' in os.environ.get('RENDER_EXTERNAL_URL', '') or os.environ.get('RENDER_SERVICE_NAME'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_production')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
