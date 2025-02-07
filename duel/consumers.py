import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer

class DuelConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive_json(self, content):
        message = content["message"]
        await self.send_json({"message": message})
