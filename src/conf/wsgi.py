"""
WSGI config for twitch project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import dotenv
import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application

ROOT_DIR = Path(__file__).resolve().parent.parent

dotenv.read_dotenv(ROOT_DIR / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf')

application = get_wsgi_application()
