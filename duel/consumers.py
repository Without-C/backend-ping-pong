import asyncio
import uuid

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

    async def try_matchmaking(self):
        async with self.lock:
            if len(self.queue) >= self.required_player_count:
                players = []
                for _ in range(self.required_player_count):
                    players.append(self.queue.pop())
                return players
            return None

matchmaking = Matchmaking(2)

class DuelConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # 소켓 연결
        await self.accept()

        # 대기 큐에 추가
        await matchmaking.add_waiting_participant(self.channel_name)

        # 충분한 수의 대기자가 모인 경우 group 생성
        match_result = await matchmaking.try_matchmaking()
        if match_result:
            group_name = f"match_{uuid.uuid4().hex}"
            for player_channel_name in match_result:
                await self.channel_layer.group_add(group_name, player_channel_name)

            await self.channel_layer.group_send(group_name, {"type": "group.message", "message": "match maked"})

    async def disconnect(self, close_code):
        await matchmaking.remove_waiting_participant(self.channel_name)

    async def receive_json(self, content):
        message = content["message"]
        await self.send_json({"message": message})

    async def group_message(self, event):
        message = event["message"]
        await self.send_json({"message": message})