from hexagon import HexagonalGrid, State, Hexagon, Coordinate


class Game:
    def __init__(self, num_rings: int):
        self.grid = HexagonalGrid(num_rings)
        self.current_move = 0
        self.is_over = False
        self.verdict = State.NONE

        self._victory_sequence: set[Coordinate] = set()

    @property
    def current_player(self) -> State:
        return State.ONE if self.current_move % 2 == 0 else State.TWO

    def move(self, hex_: Hexagon) -> bool:
        if hex_.state != State.NONE:
            return False
        hex_.set_state(self.current_player)
        self.current_move += 1
        self.grid.register_move(hex_.coordinate)
        return True

    def check_win(self, last_clicked_hex: Hexagon) -> bool:
        conn_component = self.grid.connected_component(last_clicked_hex)
        coord = last_clicked_hex.coordinate
        axes = ([], [], [])
        for i, coord in enumerate(coord):
            for hex_ in conn_component:
                if hex_.coordinate[i] == coord:
                    axes[i].append(hex_.coordinate)
        for axis in axes:
            if len(axis) >= 5:
                self._victory_sequence = set(axis)
                return True
        return False

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
