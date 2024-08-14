import os
from django.urls import path,re_path
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from channels.security.websocket import AllowedHostsOriginValidator
from . import consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "chatbot.settings")

websocket_urlpatterns = [
    path('ws/chat/<uuid:room_name>/',consumers.ChatRoomConsumer.as_asgi()),
]

