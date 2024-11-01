import pygame

from game_screen import GameScreen


pygame.init()


def main():
    WIDTH, HEIGHT = 1200, 1200
    hex_radius = 60
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    game_screen = GameScreen(screen, hex_radius)
    game_screen.run()


if __name__ == "__main__":
    main()
