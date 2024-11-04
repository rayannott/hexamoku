import random

from bots.bot import Bot
from hexagon import Hexagon


class RandomBot(Bot):
    def move(self) -> Hexagon:
        return random.choice(self.grid.none_hexagons())
    