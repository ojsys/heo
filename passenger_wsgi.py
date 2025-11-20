import os
import sys

# Project directory
project_home = os.path.dirname(os.path.abspath(__file__))

# Add project directory to sys.path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Virtual environment configuration
# Change python_version to match your cPanel Python version (e.g., '3.9', '3.10', '3.11', '3.12')
python_version = '3.11'
venv_path = os.path.join(project_home, 'env', 'lib', f'python{python_version}', 'site-packages')

if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)
else:
    # Try alternative path structure for some cPanel setups
    alt_venv_path = os.path.join(project_home, 'env', 'lib64', f'python{python_version}', 'site-packages')
    if os.path.exists(alt_venv_path):
        sys.path.insert(0, alt_venv_path)

# Load environment variables from .env file
try:
    from python_decouple import config
    # python-decouple will automatically load from .env
except ImportError:
    # Fallback: manually load .env if python-decouple not available
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
