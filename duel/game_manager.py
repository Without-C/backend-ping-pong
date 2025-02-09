import uuid
import asyncio
from .ping_pong import PingPong


class PingPongGameManager:
    def __init__(self):
        self.games = {}

    def create_game(self, participant1, participant2, on_update):
        game_id = f"game_{uuid.uuid4().hex}"
        game = PingPong(participant1, participant2, on_update)
        task = asyncio.create_task(game.run())
        self.games[game_id] = game

        return game_id

    def on_event(self, game_id, participant, event):
        self.games[game_id].on_event(participant, event)
