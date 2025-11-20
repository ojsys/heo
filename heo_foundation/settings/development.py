"""
Development settings for HEO Foundation project.
Use this for local development.
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email - Console backend for development (prints emails to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Site URL for development
SITE_URL = config('SITE_URL', default='http://localhost:8000')

# Disable security features for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Cache - Local memory for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Logging configuration for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Debug toolbar (optional - uncomment if you have django-debug-toolbar installed)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
# INTERNAL_IPS = ['127.0.0.1']
