import os
import sys

from heo_pro.wsgi import application

# Add your application directory to Python path
sys.path.insert(0, os.path.dirname(__file__))