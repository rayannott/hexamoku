from abc import ABC, abstractmethod

from hexagon import HexagonalGrid, Hexagon, State


class Bot(ABC):
    def __init__(self, grid: HexagonalGrid, bot_player_state: State):
        self.grid = grid
        self.bot_player_state = bot_player_state

    @abstractmethod
    def move(self) -> Hexagon:
        pass
