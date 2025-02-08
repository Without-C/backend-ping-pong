import uuid
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .match_manager import MatchManager
from .ping_pong import PingPongGameManager

class DuelConsumer(AsyncJsonWebsocketConsumer):
    match_manager = MatchManager(2)
    game_manager = PingPongGameManager()

    async def connect(self):
        # 초기화
        self.group_name = None

        # 소켓 연결 허용
        await self.accept()

        # 환영 메시지
        await self.send_json({"type": "wait"})

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

        async def on_update(game_state):
            await self.channel_layer.group_send(group_name, {"type": "game.on.update", "game_state": game_state})

        game_id = self.game_manager.create_game(player1_channel_name, player2_channel_name, on_update)

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
        action = content["action"]
    
    async def group_assign(self, event):
        """
        매치매이킹이 이루어졌을 때 호출됨
        """
        self.group_name = event["group_name"]
        await self.send_json({"type": "start"})

    async def group_exit(self, event):
        """
        매치매이킹이 이루어진 이후 누군가 나가면 호출됨
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.send_json({"type": "opponent_exit"})

    async def game_on_update(self, event):
        await self.send_json({"type": "game_state", "game_state": event["game_state"]})
