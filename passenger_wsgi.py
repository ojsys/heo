import os
import sys

# cPanel Configuration - UPDATE THESE VALUES
CPANEL_USERNAME = 'heoeziok'
APP_NAME = 'heo'
PYTHON_VERSION = '3.12'

# Project directory
project_home = f'/home/{CPANEL_USERNAME}/{APP_NAME}'

# Add project directory to sys.path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# cPanel virtualenv paths
# cPanel creates virtualenvs at: /home/username/virtualenv/appname/python_version/
venv_base = f'/home/{CPANEL_USERNAME}/virtualenv/{APP_NAME}/{PYTHON_VERSION}'
venv_paths = [
    os.path.join(venv_base, 'lib', f'python{PYTHON_VERSION}', 'site-packages'),
    os.path.join(venv_base, 'lib64', f'python{PYTHON_VERSION}', 'site-packages'),
]

for venv_path in venv_paths:
    if os.path.exists(venv_path) and venv_path not in sys.path:
        sys.path.insert(0, venv_path)

# Use PyMySQL as MySQLdb replacement (MUST be after path setup)
import pymysql
pymysql.install_as_MySQLdb()

# Load environment variables from .env file
env_path = os.path.join(project_home, '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heo_foundation.settings')

# Setup Django and get WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
