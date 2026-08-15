import os
import sys
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillswap.settings')

from django.core.wsgi import get_wsgi_application

# Initialize WSGI app for Vercel
app = get_wsgi_application()
handler = app


# Auto-migrate ephemeral database if on Vercel serverless environment
if os.environ.get("VERCEL"):
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
    except Exception as e:
        print(f"Vercel auto-migration log: {e}")
