"""
ASGI config for telemedicine project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from calls.routing import websocket_urlpatterns as call_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telemedicine.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat_websocket_urlpatterns + call_websocket_urlpatterns
        )
    ),
})
