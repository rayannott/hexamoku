from random import choices

from hexagon import HexagonalGrid, State, Coordinate


def get_moves_for(grid: HexagonalGrid, player: State) -> list[Coordinate]:
    """
    Get all possible moves for a given player.

    grid: The game grid.
    player: The player to get the moves for.
    """
    ccs = grid._connected_components()
    _best = []
    _best_len = 0
    for cc in ccs:
        if cc[0].state == player:
            if len(cc) > _best_len:
                _best = cc
                _best_len = len(cc)
    if len(ccs) == 1 or _best_len < 2:
        none_hexes = grid.none_hexagons()
        return choices([hex_.coordinate for hex_ in none_hexes], k=min(7, len(none_hexes)))
    res = []
    for hex_ in _best:
        for coord, hex_neigh in hex_.get_neighbors().items():
            if hex_neigh.state == State.NONE:
                res.append(coord)
    return res


def evaluate(grid: HexagonalGrid, maximizing: bool) -> float:
    """
    Evaluate the current state of the game.

    grid: The game grid.
    maximizing: True if it's the maximizing player's turn (player ONE).
    """
    # assert len(grid._moves) % 2 == (0 if maximizing else 1)
    if len(grid._moves) < 2:
        return 0.0
    winning_me_len = len(grid._get_best_sequence(grid.hexagons[grid._moves[-1]]))
    winning_opponent_len = len(grid._get_best_sequence(grid.hexagons[grid._moves[-2]])
    )
    if winning_me_len >= 5:
        return 1.0
    if winning_opponent_len >= 5:
        return -1.0
    return (winning_me_len - winning_opponent_len) / 5.0


def minimax(
    grid: HexagonalGrid, depth: int, alpha: float, beta: float, maximizing: bool
) -> float:
    """
    Minimax algorithm with alpha-beta pruning.

    grid: The game grid.
    depth: The maximum depth to search.
    alpha: The best value that the maximizing player currently can guarantee.
    beta: The best value that the minimizing player currently can guarantee.
    maximizing: True if it's the maximizing player's turn (player ONE).
    """
    if depth == 0:
        return evaluate(grid, maximizing)

    if maximizing:
        max_eval = -1
        for move in get_moves_for(grid, State.ONE):
            # make move:
            grid.register_move(move)
            eval_ = minimax(grid, depth - 1, alpha, beta, False)
            # undo:
            last_move = grid._moves.pop()
            grid.hexagons[last_move].state = State.NONE

            max_eval = max(max_eval, eval_)
            alpha = max(alpha, eval_)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = 1
        for move in get_moves_for(grid, State.TWO):
            # make move:
            grid.register_move(move)
            eval_ = minimax(grid, depth - 1, alpha, beta, True)
            # undo:
            last_move = grid._moves.pop()
            grid.hexagons[last_move].state = State.NONE

            min_eval = min(min_eval, eval_)
            beta = min(beta, eval_)
            if beta <= alpha:
                break
        return min_eval


def get_best_move(grid: HexagonalGrid, for_player: State, depth: int) -> Coordinate | None:
    """
    Get the best move for a given player.

    grid: The game grid.
    depth: The maximum depth to search.
    """
    best_move = None
    best_eval = -1 if for_player == State.ONE else 1
    for move in get_moves_for(grid, for_player):
        # make move:
        grid.register_move(move)
        eval_ = minimax(grid, depth, -1, 1, for_player == State.ONE)
        # undo:
        last_move = grid._moves.pop()
        grid.hexagons[last_move].state = State.NONE

        if (for_player == State.ONE and eval_ > best_eval) or (
            for_player == State.TWO and eval_ < best_eval
        ):
            best_eval = eval_
            best_move = move
    return best_move
