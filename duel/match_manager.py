import asyncio
from typing import List, Optional

class MatchManager:
    def __init__(self, required_player_count: int):
        self.lock: asyncio.Lock = asyncio.Lock()
        self.queue: List[str] = []
        self.required_player_count: int = required_player_count

    async def add_waiting_participant(self, identifier: str):
        async with self.lock:
            self.queue.append(identifier)
    
    async def remove_waiting_participant(self, identifier: str):
        async with self.lock:
            if identifier in self.queue:
                self.queue.remove(identifier)

    async def try_matchmaking(self) -> Optional[List[str]]:
        async with self.lock:
            if len(self.queue) >= self.required_player_count:
                players = []
                for _ in range(self.required_player_count):
                    players.append(self.queue.pop())
                return players
            return None
