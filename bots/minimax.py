from hexagon import HexagonalGrid, State, Hexagon
from bots.bot import Bot


def evaluate(grid: HexagonalGrid, last_move: Hexagon | None = None) -> float:
    if last_move is None:
        return 0
    win_seq = grid.get_winning_sequence(last_move)
    if win_seq:
        return 1 if last_move.state == State.ONE else -1
    return 0


def minimax(
    grid: HexagonalGrid,
    depth: int,
    maximizing: bool,
    alpha: float,
    beta: float,
    last_move: Hexagon | None = None,
) -> float:
    _none_hexs = grid.none_hexagons()

    # Check for terminal condition: win or max depth
    evaluation = evaluate(grid, last_move)
    if depth == 0 or evaluation != 0 or not _none_hexs:
        return evaluation

    if maximizing:
        max_eval = -1
        for hex_ in _none_hexs:
            hex_.set_state(State.ONE)
            eval_ = minimax(grid, depth - 1, False, alpha, beta, hex_)
            hex_.set_state(State.NONE)
            max_eval = max(max_eval, eval_)
            alpha = max(alpha, eval_)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = 1
        for hex_ in _none_hexs:
            hex_.set_state(State.TWO)
            eval_ = minimax(grid, depth - 1, True, alpha, beta, hex_)
            hex_.set_state(State.NONE)
            min_eval = min(min_eval, eval_)
            beta = min(beta, eval_)
            if beta <= alpha:
                break
        return min_eval


class MinimaxBot(Bot):
    def __init__(self, grid: HexagonalGrid, bot_player_state: State, depth: int = 3):
        super().__init__(grid, bot_player_state)
        self.depth = depth

    def move(self) -> Hexagon:
        alpha, beta = -1, 1
        maximizing = self.bot_player_state == State.ONE
        best_eval = -1 if maximizing else 1
        best_move = None

        available_moves = self.grid.none_hexagons()
        for hex_ in available_moves:
            hex_.set_state(self.bot_player_state)
            eval_ = minimax(
                self.grid,
                self.depth,
                not maximizing,  # Switch turn
                alpha,
                beta,
                hex_,
            )
            hex_.set_state(State.NONE)

            # Update best move based on maximizing or minimizing strategy
            if (maximizing and eval_ > best_eval) or (not maximizing and eval_ < best_eval):
                best_eval = eval_
                best_move = hex_

            # Update alpha/beta for pruning
            if maximizing:
                alpha = max(alpha, best_eval)
            else:
                beta = min(beta, best_eval)

            # Prune the remaining moves if possible
            if beta <= alpha:
                break

        if best_move is None:
            print("No valid moves")
            return hex_
        return best_move
