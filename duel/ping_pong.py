import math
import uuid
import asyncio

class PingPongGameManager():
    def __init__(self):
        self.games = {}

    def create_game(self, participant1, participant2, on_update):
        game_id = f"game_{uuid.uuid4().hex}"
        game = PingPong(on_update)
        task = asyncio.create_task(game.game_loop())
        self.games[game_id] = game

        return game_id

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
            await self.on_update({"ball_x": self.ball_x, "ball_y": self.ball_y})
            await asyncio.sleep(self.timedelta)
            self.tick += 1

    def fixed_update(self):
        self.ball_x = 100 * math.sin(self.tick * self.timedelta * math.pi * 2) + self.width / 2
        self.ball_y = 100 * math.cos(self.tick * self.timedelta * math.pi * 2) + self.height / 2
