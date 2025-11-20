"""
Settings package for HEO Foundation.

Usage:
    - Development: DJANGO_SETTINGS_MODULE=heo_foundation.settings.development
    - Production: DJANGO_SETTINGS_MODULE=heo_foundation.settings.production

Or set DJANGO_ENV in your .env file:
    - DJANGO_ENV=development
    - DJANGO_ENV=production
"""
from decouple import config

# Determine which settings to use based on environment
env = config('DJANGO_ENV', default='development')

if env == 'production':
    from .production import *
else:
    from .development import *
