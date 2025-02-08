import math
import uuid
import asyncio

class KeyState:
    def __init__(self):
        self.key_state = {}

    def set_key_state(self, key, state):
        if state == "press":
            self.key_state[key] = True
        elif state == "release":
            self.key_state[key] = False

    def get_key_state(self, key):
        return self.key_state.get(key, False)

class PingPongGameManager():
    def __init__(self):
        self.games = {}

    def create_game(self, participant1, participant2, on_update):
        game_id = f"game_{uuid.uuid4().hex}"
        game = PingPong(participant1, participant2, on_update)
        task = asyncio.create_task(game.game_loop())
        self.games[game_id] = game

        return game_id

    def on_event(self, game_id, participant, event):
        self.games[game_id].on_event(participant, event);

class PingPong():
    def __init__(self, player1, player2, on_update):
        self.width = 600
        self.height = 400
        self.tick = 0
        self.timedelta = 1 / 60
        self.ball_x = 0
        self.ball_y = 0
        self.paddle_speed = 5

        self.on_update = on_update
        self.player1 = player1
        self.player2 = player2
        self.player1_key_state = KeyState()
        self.player2_key_state = KeyState()
        self.player1_paddle_y = self.height / 2
        self.player2_paddle_y = self.height / 2

    async def game_loop(self):
        while True:
            self.fixed_update()
            await self.on_update({"ball_x": self.ball_x, "ball_y": self.ball_y, "player1_paddle_y": self.player1_paddle_y, "player2_paddle_y": self.player2_paddle_y})
            await asyncio.sleep(self.timedelta)
            self.tick += 1

    def fixed_update(self):
        self.ball_x = 100 * math.sin(self.tick * self.timedelta * math.pi * 2) + self.width / 2
        self.ball_y = 100 * math.cos(self.tick * self.timedelta * math.pi * 2) + self.height / 2

        if self.player1_key_state.get_key_state("ArrowUp") or self.player1_key_state.get_key_state("w"):
            self.player1_paddle_y -= self.paddle_speed
        if self.player1_key_state.get_key_state("ArrowDown") or self.player1_key_state.get_key_state("s"):
            self.player1_paddle_y += self.paddle_speed

        if self.player2_key_state.get_key_state("ArrowUp") or self.player2_key_state.get_key_state("w"):
            self.player2_paddle_y -= self.paddle_speed
        if self.player2_key_state.get_key_state("ArrowDown") or self.player2_key_state.get_key_state("s"):
            self.player2_paddle_y += self.paddle_speed

    def on_event(self, participant, event):
        action = event["action"]
        if action == "key":
            key = event["key"]
            state = event["state"]

            if participant == self.player1:
                self.player1_key_state.set_key_state(key, state)
            elif participant == self.player2:
                self.player2_key_state.set_key_state(key, state)
