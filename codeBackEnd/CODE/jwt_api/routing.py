# chat/routing.py
from django.urls import re_path
from . import consumers
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]