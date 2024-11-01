import pygame
from pygame import Vector2

from game import Game
from hexagon import HexagonalGridGUIWrapper, Hexagon
from front_utils import BLACK, GREEN, MAGENTA
from minimax import get_best_move


class GameScreen:
    def __init__(
        self,
        screen: pygame.Surface,
        hex_radius: int,
    ):
        self.screen = screen
        self.game = Game(6)
        self.gui_grid = HexagonalGridGUIWrapper(
            self.game.grid,
            hex_radius,
            Vector2(self.screen.get_rect().center),
            self.screen,
        )
        self.running = True

    def reset_game(self):
        self.game = Game(6)
        self.gui_grid.reset_with_grid(self.game.grid)

    def run(self):
        pygame.display.set_caption("Hexagonal Grid Rings")
        while self.running:
            self.screen.fill(BLACK)

            self.gui_grid.draw(self.game.is_over)

            mouse_pos = Vector2(pygame.mouse.get_pos())
            hex_hovering = self.gui_grid.hexagon_hovering(mouse_pos)
            if hex_hovering:
                self.gui_grid.highlight_hexagon(hex_hovering, GREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if hex_hovering:
                        self.clicked_hex(hex_hovering)
                    else:
                        print("Clicked outside of hexagons")
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        ...
                    elif event.key == pygame.K_c:
                        self.gui_grid.toggle_display_coordinates()
                    elif event.key == pygame.K_m:
                        self.gui_grid.toggle_display_move_labels()
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        best_move = get_best_move(self.game.grid, self.game.current_player, 3)
                        print("Best move:", best_move)
                    elif event.key == pygame.K_d:
                        print("-- debug --")
                        print("Current player:", self.game.current_player)
                        print("Moves", self.game.grid._moves)
                        print(
                            f"Is over: {self.game.is_over}; Verdict: {self.game.verdict}"
                        )
                elif event.type == pygame.MOUSEMOTION:
                    ...
            pygame.display.update()

    def clicked_hex(self, hex_: Hexagon) -> None:
        if self.game.is_over:
            print("Game is over")
            return
        if not hex_:
            return
        successful = self.game.move(hex_)
        if successful:
            self.game.process_last_click(hex_)
            self.gui_grid._hexagons_to_highlight = (
                [(hex_, MAGENTA)] if not self.game.is_over else []
            )
            self.gui_grid._victory_sequence_copy = self.game._victory_sequence.copy()
        else:
            print("Invalid move")
