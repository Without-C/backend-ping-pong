import uuid
import math
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .match_manager import MatchManager

class PingPong():
    def __init__(self, on_update):
        self.width = 600
        self.height = 400
        self.tick = 0
        self.timedelta = 1 / 60
        self.ball_x = 0
        self.ball_y = 0

        self.on_update = on_update

    async def game_loop(self):
        while True:
            self.fixed_update()
            self.on_update({"message": "ball", "background": "red", "ball_x": self.ball_x, "ball_y": self.ball_y})
            await asyncio.sleep(self.timedelta)
            self.timedelta += 1

    async def fixed_update(self):
        self.ball.x = 100 * math.sin(self.tick * self.timedelta * 360 / math.pi)
        self.ball.y = 100 * math.cos(self.tick * self.timedelta * 360 / math.pi)

class PingPongGameManager():
    def __init__(self):
        self.games = {}

    def create_game(self, participant1, participant2, on_update):
        game_id = f"match_{uuid.uuid4().hex}"
        game = PingPong(on_update)
        task = asyncio.create_task(game.game_loop())
        self.games[game_id] = game

        return game_id

class DuelConsumer(AsyncJsonWebsocketConsumer):
    match_manager = MatchManager(2)

    async def connect(self):
        # 초기화
        self.group_name = None

        # 소켓 연결 허용
        await self.accept()

        # 환영 메시지
        await self.send_json({"message": "Welcome", "background": "black"})

        # 대기 큐에 추가
        await self.match_manager.add_waiting_participant(self.channel_name)

        # 충분한 수의 대기자가 모인 경우 매치매이킹
        match_result = await self.match_manager.try_matchmaking()
        if match_result:
            await self.make_room(match_result)

    async def make_room(self, match_result):
        group_name = f"match_{uuid.uuid4().hex}"
        player1_channel_name = match_result[0]
        player2_channel_name = match_result[1]

        # 매치매이킹 대상자들을 같은 그룹에 추가
        await self.channel_layer.group_add(group_name, player1_channel_name)
        await self.channel_layer.group_add(group_name, player2_channel_name)

        # 매치매이킹이 이루어진 후 대상자들에게 그룹 이름 통보
        await self.channel_layer.group_send(group_name, {"type": "group.assign", "group_name": group_name})

    async def disconnect(self, close_code):
        # 대기자 큐에 있었다면 삭제
        await self.match_manager.remove_waiting_participant(self.channel_name)

        # 속해있던 그룹이 있으면
        if self.group_name:
            # 같은 그룹에 있던 유저에게 탈퇴를 알림
            await self.channel_layer.group_send(self.group_name, {"type": "group.exit", "channel_name": self.channel_name})
            # 그룹에서 나가기
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        message = content["message"]
        await self.send_json({"message": message})
    
    async def group_assign(self, event):
        """
        매치매이킹이 이루어졌을 때 호출됨
        """
        self.group_name = event["group_name"]
        await self.send_json({"message": "Match matched", "background": "green"})

    async def group_exit(self, event):
        """
        매치매이킹이 이루어진 이후 누군가 나가면 호출됨
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.send_json({"message": "Opponent exited", "background": "blue"})
