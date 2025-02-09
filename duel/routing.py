from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("api/ping-pong/duel/ws/", consumers.DuelConsumer.as_asgi()),
]
