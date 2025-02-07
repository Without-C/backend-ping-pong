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

class DuelConsumer(AsyncJsonWebsocketConsumer):
    matchmaking = Matchmaking(2)

    async def connect(self):
        # 초기화
        self.group_name = None

        # 소켓 연결 허용
        await self.accept()

        # 대기 큐에 추가
        await self.matchmaking.add_waiting_participant(self.channel_name)

        # 충분한 수의 대기자가 모인 경우 매치매이킹
        match_result = await self.matchmaking.try_matchmaking()
        if match_result:
            group_name = f"match_{uuid.uuid4().hex}"
            for player_channel_name in match_result:
                await self.channel_layer.group_add(group_name, player_channel_name)

            # 매치매이킹이 이루어진 후 대상자들에게 그룹 이름 통보
            await self.channel_layer.group_send(group_name, {"type": "group.assign", "group_name": group_name})

    async def disconnect(self, close_code):
        # 대기자 큐에 있었다면 삭제
        await self.matchmaking.remove_waiting_participant(self.channel_name)

        # 연결이 끊겼을 때 속해있던 그룹이 있으면 탈퇴
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        message = content["message"]
        await self.send_json({"message": message})
    
    async def group_assign(self, event):
        """
        매치매이킹이 이루어졌을 때 호출됨
        """
        self.group_name = event["group_name"]
        await self.send_json({"message": "match maked"})