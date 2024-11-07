import json
from collections import deque

import pygame
from pygame import Vector2
import pyperclip

from game import Game
from hexagon import HexagonalGridGUIWrapper, Hexagon, State, BORDER_WIDTH, Coordinate
from front_utils import BLACK, GREEN, MAGENTA, ORANGE, BLUE


class GameScreen:
    def __init__(
        self,
        screen: pygame.Surface,
        hex_radius: int,
    ):
        self.screen = screen
        self.game = Game(num_rings=6)
        self.gui_grid = HexagonalGridGUIWrapper(
            self.game.grid,
            hex_radius,
            Vector2(self.screen.get_rect().center),
            self.screen,
        )
        self.running = True

        self.move_queue: deque[Coordinate] = deque()

    def reset_game(self):
        self.game = Game(6)
        self.gui_grid.reset_with_grid(self.game.grid)
        self.move_queue: deque[Coordinate] = deque()

    def run(self):
        pygame.display.set_caption("Hexagonal Grid Rings")
        while self.running:
            self.screen.fill(BLACK)

            self.gui_grid.draw(self.game.is_over)

            mouse_pos = Vector2(pygame.mouse.get_pos())
            hex_hovering = self.gui_grid.hexagon_hovering(mouse_pos)
            if hex_hovering:
                self.gui_grid.highlight_hexagon(
                    hex_hovering,
                    (ORANGE if self.game.current_player == State.ONE else BLUE)
                    if not self.game.is_over
                    else GREEN,
                    width=BORDER_WIDTH * 3 // 2,
                )

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
                        if self.game.bot is None:
                            print("No bot assigned")
                            continue
                        if self.game.bot.bot_player_state == self.game.current_player:
                            hex_ = self.game.bot.move()
                            self.clicked_hex(hex_)
                        else:
                            print("It's not the bot's turn")
                    elif event.key == pygame.K_c:
                        self.gui_grid.toggle_display_coordinates()
                    elif event.key == pygame.K_m:
                        self.gui_grid.toggle_display_move_labels()
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_s:
                        self.game.save_game()
                    elif event.key == pygame.K_q:
                        if pygame.key.get_mods() & pygame.KMOD_CTRL:
                            self.populate_queue_from_clipboard()
                            continue
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            while self.move_queue:
                                self.pop_from_queue()
                            continue
                        if not self.move_queue:
                            print("Queue is empty")
                            continue
                        self.pop_from_queue()
                    elif event.key == pygame.K_d:
                        print("-- debug --")
                        print("Current player:", self.game.current_player)
                        print("Moves", self.game.grid._moves)
                        print(
                            f"Is over: {self.game.is_over}; Verdict: {self.game.verdict}"
                        )
                        print(self.game._victory_sequence)
                elif event.type == pygame.MOUSEMOTION:
                    ...
            pygame.display.update()

    def _parse_data(self, data: str) -> list[Coordinate]:
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError:
            print(f"Invalid JSON: {data}")
            return []

        if isinstance(json_data, dict):
            moves_lst = json_data.get("moves", [])
            return [Coordinate(move) for move in moves_lst]
        if isinstance(json_data, list):
            return [Coordinate(move) for move in json_data]
        print(f"Unexpected JSON data: {json_data}")
        return []

    def populate_queue_from_clipboard(self):
        data = pyperclip.paste()
        moves = self._parse_data(data)
        self.move_queue.extend(moves)
        print(f"Populated queue with {len(moves)} moves.")
    
    def pop_from_queue(self):
        coord = self.move_queue.popleft()
        hex_ = self.game.grid.at(coord)
        self.clicked_hex(hex_)
        print(
            f"Retrieved move from queue: {coord}. Remaining: {len(self.move_queue)} moves."
        )

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
