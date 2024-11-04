import pygame

from game_screen import GameScreen
from hexagon import State
from bots.randombot import RandomBot


pygame.init()


def main():
    WIDTH, HEIGHT = 1000, 1000
    hex_radius = 50
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    game_screen = GameScreen(screen, hex_radius)
    game_screen.game.assign_bot(RandomBot, bot_player_state=State.TWO)
    game_screen.run()


if __name__ == "__main__":
    main()
