"""
WSGI Configuration File for PythonAnywhere Deployment
======================================================
Follow these steps on PythonAnywhere:
1. Open the "Web" tab in your PythonAnywhere Dashboard.
2. In the "Code" section, click on the "WSGI configuration file" link
   (e.g., /var/www/<your_username>_pythonanywhere_com_wsgi.py).
3. Delete all the existing default contents in that file and paste
   the code below.
4. Replace '<YOUR_PYTHONANYWHERE_USERNAME>' with your actual PythonAnywhere username!
5. Save the file and click the green "Reload <your_username>.pythonanywhere.com" button.
"""

import os
import sys

# Replace this with your actual PythonAnywhere username!
# Example: If your username is 'paras', the path will be '/home/paras/apiproject'
USERNAME = '<YOUR_PYTHONANYWHERE_USERNAME>'
PROJECT_PATH = f'/home/{USERNAME}/apiproject'

# Add project directory to python path
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'apiproject.settings'

# Optional: Set production environment variables
# os.environ['DEBUG'] = 'False'
# os.environ['SECRET_KEY'] = 'your-production-secret-key-here'

# Load the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

