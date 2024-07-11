from django.urls import re_path,path
from . import consumers
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
websocket_urlpatterns = [
    path('ws/chat/<uuid:room_name>/',consumers.ChatRoomConsumer.as_asgi())
    # re_path(r'ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatRoomConsumer.as_asgi()),
]