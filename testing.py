import random

import pygame
from pygame import Vector2

from hexagon import HexagonalGrid, HexagonalGridGUIWrapper, State
from front_utils import WHITE, BLACK, RED, GREEN, BLUE, ORANGE, MAGENTA, GRAY

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hexagonal Grid Rings")

# Main loop
running = True
radius = 50
num_rings = 6  # Number of rings around the central hexagon

grid = HexagonalGrid(num_rings)
gui_grid = HexagonalGridGUIWrapper(
    grid, radius, Vector2(WIDTH // 2, HEIGHT // 2), screen
)


while running:
    screen.fill(BLACK)

    # Draw hexagonal grid
    gui_grid.draw()

    mouse_pos = Vector2(pygame.mouse.get_pos())
    hex_hovering = gui_grid.hexagon_hovering(mouse_pos)
    if hex_hovering:
        gui_grid.highlight_hexagon(hex_hovering)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            hex_clicked = gui_grid.hexagon_hovering(mouse_pos)
            if not hex_clicked:
                continue
            print(hex_clicked)
            if event.button == 1:
                hex_clicked.set_state(State.ONE)
            elif event.button == 2:
                hex_clicked.set_state(State.NONE)
            elif event.button == 3:
                hex_clicked.set_state(State.TWO)
            else:
                print(hex_clicked, event.button)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                ...
            elif event.key == pygame.K_c:
                gui_grid.toggle_display_coordinates()
        elif event.type == pygame.MOUSEMOTION:
            ...
    # Update display
    pygame.display.flip()

# Quit pygame
pygame.quit()
