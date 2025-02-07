import asyncio

from channels.generic.websocket import AsyncJsonWebsocketConsumer

class Matchmaking:
    def __init__(self, required_player_count):
        self.lock = asyncio.Lock()
        self.queue = []
        self.required_player_count = required_player_count

    async def add_waiting_participant(self, channel_name):
        async with self.lock:
            self.queue.append(channel_name)
    
    async def remove_waiting_participant(self, channel_name):
        async with self.lock:
            if channel_name in self.queue:
                self.queue.remove(channel_name)

matchmaking = Matchmaking(2)

class DuelConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await matchmaking.add_waiting_participant(self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await matchmaking.remove_waiting_participant(self.channel_name)

    async def receive_json(self, content):
        message = content["message"]
        await self.send_json({"message": message})
