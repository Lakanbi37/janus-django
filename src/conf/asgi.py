"""
ASGI config for twitch project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""
import dotenv
import os
from pathlib import Path

from channels.auth import AuthMiddlewareStack
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from websocket.events import EventStreamConsumer

ROOT_DIR = Path(__file__).resolve().parent.parent

dotenv.read_dotenv(ROOT_DIR / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("stream/<slug:code>", EventStreamConsumer.as_asgi())
        ])
    )

})
