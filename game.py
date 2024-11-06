import pathlib
import json
import datetime
from pprint import pprint

from hexagon import HexagonalGrid, State, Hexagon, Coordinate
from bots.bot import Bot


SAVES_FILE = pathlib.Path("games") / "games.jsonl"


class Game:
    def __init__(self, num_rings: int):
        self.grid = HexagonalGrid(num_rings)
        self.current_move = 0
        self.is_over = False
        self.verdict = State.NONE

        self.bot = None

        self._victory_sequence: set[Coordinate] = set()

    @property
    def current_player(self) -> State:
        return State.ONE if self.current_move % 2 == 0 else State.TWO

    def assign_bot(self, bot_type: type[Bot], **kwargs) -> None:
        self.bot = bot_type(self.grid, **kwargs)

    def move(self, hex_: Hexagon) -> bool:
        if hex_.state != State.NONE:
            return False
        # TODO: maybe the first move cannot be in the center AND the first ring?
        if self.current_move == 0 and (hex_.coordinate == (0, 0, 0) or hex_.coordinate.get_ring_number() == 1):
            print("First move cannot be in the center or the first ring")
            return False
        hex_.set_state(self.current_player)
        self.current_move += 1
        self.grid.register_move(hex_.coordinate)
        return True

    def check_win(self, last_clicked_hex: Hexagon) -> bool:
        winning_seq = self.grid.get_winning_sequence(last_clicked_hex)
        self._victory_sequence = winning_seq
        return bool(winning_seq)

    def process_last_click(self, last_clicked_hex: Hexagon) -> None:
        won = self.check_win(last_clicked_hex)
        has_moves = bool(self.grid.none_hexagons())
        if won:
            self.is_over = True
            self.verdict = last_clicked_hex.state
            print(f"Player {self.verdict} wins!")
            return
        if not has_moves:
            self.is_over = True
            print("Draw!")
            return

    def save_game(self):
        verdict = (
            (self.verdict.name.lower() if self.verdict != State.NONE else "draw")
            if self.is_over
            else None
        )
        with SAVES_FILE.open("a") as f:
            game_data = {
                "verdict": verdict,
                "moves": [list(move) for move in self.grid._moves],
                "date": datetime.datetime.now().isoformat(),
            }
            print(json.dumps(game_data), file=f)
            pprint(game_data)
