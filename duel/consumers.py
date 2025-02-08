import uuid
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .utils_match_manager import MatchManager

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
            group_name = f"match_{uuid.uuid4().hex}"
            for player_channel_name in match_result:
                await self.channel_layer.group_add(group_name, player_channel_name)

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
