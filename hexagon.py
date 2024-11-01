import math
from dataclasses import dataclass, field
from enum import Enum, auto

import pygame
from pygame import Vector2, Color

from front_utils import WHITE, BLACK, BLUE, ORANGE, dim_color


pygame.font.init()
FONT = pygame.font.Font(None, 30)


class Coordinate(tuple[int, int, int]):
    def __add__(self, other: "Coordinate") -> "Coordinate":
        return Coordinate((self[0] + other[0], self[1] + other[1], self[2] + other[2]))

    def get_ring_number(self) -> int:
        return max(map(abs, self))


DIRECTIONS: list[Coordinate] = list(
    map(
        Coordinate,
        (
            (+1, 0, -1),
            (+1, -1, 0),
            (0, -1, +1),
            (-1, 0, +1),
            (-1, +1, 0),
            (0, +1, -1),
        ),
    )
)


HEXAGON_POINT_VECTORS: list[Vector2] = [
    Vector2(
        math.cos(math.pi / 3 * n - math.pi / 6), math.sin(math.pi / 3 * n - math.pi / 6)
    )
    for n in range(6)
]


class State(Enum):
    NONE = auto()
    ONE = auto()
    TWO = auto()

    @property
    def color(self) -> Color:
        return STATE_COLOR_MAP[self]

    def __repr__(self) -> str:
        return f"{self.name}"


STATE_COLOR_MAP = {
    State.NONE: BLACK,
    State.ONE: ORANGE,
    State.TWO: BLUE,
}


BORDER_WIDTH = 4


@dataclass
class Hexagon:
    coordinate: Coordinate
    state: State = State.NONE
    _neighbours: dict[Coordinate, "Hexagon"] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Hex({self.coordinate})"

    def _get_neighbors_from(
        self, hexagons: dict[Coordinate, "Hexagon"]
    ) -> dict[Coordinate, "Hexagon"]:
        res = {}
        for dir_ in DIRECTIONS:
            new_coord = self.coordinate + dir_
            hex_ = hexagons.get(new_coord)
            if hex_:
                res[new_coord] = hex_
        return res

    def get_neighbors(self) -> dict[Coordinate, "Hexagon"]:
        return self._neighbours

    def set_state(self, state: State) -> None:
        self.state = state


def spawn_hexagonal_ring_coordinates(n_rings: int) -> dict[int, set[Coordinate]]:
    coords: dict[int, set[Coordinate]] = {0: {Coordinate((0, 0, 0))}}
    for ring_number in range(1, n_rings):
        this_ring_coords = set()
        for hex_ in coords[ring_number - 1]:
            for dir_ in DIRECTIONS:
                new_coord = hex_ + dir_
                if new_coord.get_ring_number() == ring_number:
                    this_ring_coords.add(new_coord)
        coords[ring_number] = this_ring_coords
    return coords


class HexagonalGrid:
    """Hexagonal graph topology."""

    def __init__(self, number_rings: int):
        self._coordinates = spawn_hexagonal_ring_coordinates(number_rings)
        self.hexagons: dict[Coordinate, Hexagon] = {}
        self.grid: dict[Coordinate, set[Coordinate]] = {}
        for coords in self._coordinates.values():
            for coord in coords:
                self.hexagons[coord] = Hexagon(coord)
        for coord, hex_ in self.hexagons.items():
            hex_._neighbours = hex_._get_neighbors_from(self.hexagons)
            self.grid[coord] = set(hex_._neighbours.keys())

        self._moves = []

    def at(self, coord: Coordinate) -> Hexagon:
        return self.hexagons[coord]

    def none_hexagons(self) -> list[Hexagon]:
        return [hex_ for hex_ in self.hexagons.values() if hex_.state == State.NONE]

    def _neighbourhood_coordinates(
        self, coordinate: Coordinate, radius: int
    ) -> set[Coordinate]:
        if radius == 0:
            return {coordinate}
        if radius == 1:
            return self.grid[coordinate]
        neighbourhood = set()
        for coord in self.grid[coordinate]:
            neighbourhood |= self._neighbourhood_coordinates(coord, radius - 1)
        return neighbourhood

    def neighbourhood(self, coordinate: Coordinate, radius: int) -> list[Hexagon]:
        return [
            self.hexagons[coord]
            for coord in self._neighbourhood_coordinates(coordinate, radius)
        ]

    def _connected_component_coordinates(self, hexagon: Hexagon) -> set[Coordinate]:
        visited = set()
        stack = [hexagon.coordinate]
        while stack:
            current = stack.pop()
            visited.add(current)
            for neighbour in self.grid[current]:
                if (
                    neighbour not in visited
                    and self.hexagons[neighbour].state == hexagon.state
                ):
                    stack.append(neighbour)
        return visited

    def connected_component(self, hexagon: Hexagon) -> list[Hexagon]:
        return [
            self.hexagons[coord]
            for coord in self._connected_component_coordinates(hexagon)
        ]

    def register_move(self, coordinate: Coordinate) -> None:
        self._moves.append(coordinate)


class HexagonalGridGUIWrapper:
    def __init__(
        self,
        grid: HexagonalGrid,
        radius: int,
        center_pos: Vector2,
        surface: pygame.Surface,
    ):
        self.radius = radius
        self.center_pos = center_pos
        self.surface = surface
        self.reset_with_grid(grid)

    def _calculate_positions(self) -> dict[Coordinate, Vector2]:
        positions = {}
        sqrt3 = math.sqrt(3)
        q_vec = Vector2(sqrt3 / 2, 1 / 2)
        r_vec = Vector2(0, -1)
        s_vec = Vector2(-sqrt3 / 2, 1 / 2)
        for coord in self.grid.hexagons:
            pos = (
                self.center_pos
                + self.radius * q_vec * coord[0]
                + self.radius * r_vec * coord[1]
                + self.radius * s_vec * coord[2]
            )
            positions[coord] = pos
        return positions

    def _calculate_polygons(self) -> dict[Coordinate, list[Vector2]]:
        polygon_points = {}
        for coord, pos in self.positions.items():
            points = []
            for vec in HEXAGON_POINT_VECTORS:
                points.append(pos + vec * self.radius)
            polygon_points[coord] = points
        return polygon_points

    def draw(self, dimmed: bool) -> None:
        for coord, points in self.polygons.items():
            pygame.draw.polygon(
                self.surface,
                dim_color(
                    self.grid.hexagons[coord].state.color,
                    0.5 if dimmed and (coord not in self._victory_sequence_copy) else 1,
                ),
                points,  # type: ignore
            )
            pygame.draw.polygon(self.surface, WHITE, points, BORDER_WIDTH)  # type: ignore

            # add text of the coordinate
            if self._display_coordinate_labels:
                text = FONT.render(",".join(map(str, coord)), True, WHITE)
                text_rect = text.get_rect(center=self.positions[coord])
                self.surface.blit(text, text_rect)
        if self._display_move_indices:
            for i, coord in enumerate(self.grid._moves, 1):
                text = FONT.render(str(i), True, WHITE)
                text_rect = text.get_rect(
                    center=self.positions[coord]
                    + HEXAGON_POINT_VECTORS[1] * self.radius * 0.75
                )
                self.surface.blit(text, text_rect)
        for args in self._hexagons_to_highlight:
            self.highlight_hexagon(*args)

    def hexagon_hovering(self, pos: Vector2) -> Hexagon | None:
        _min_sq_dist = float("inf")
        closest_hex = None
        for coord, hex_ in self.grid.hexagons.items():
            if (dist := (self.positions[coord] - pos).length_squared()) < _min_sq_dist:
                _min_sq_dist = dist
                closest_hex = hex_
        if _min_sq_dist > self.radius**2:
            return None
        return closest_hex

    def toggle_display_coordinates(self) -> None:
        self._display_coordinate_labels = not self._display_coordinate_labels

    def toggle_display_move_labels(self) -> None:
        self._display_move_indices = not self._display_move_indices

    def highlight_hexagon(self, hexagon: Hexagon, color: Color) -> None:
        pygame.draw.polygon(
            self.surface,
            color,
            self.polygons[hexagon.coordinate],  # type: ignore
            BORDER_WIDTH,
        )

    def reset_with_grid(self, grid: HexagonalGrid) -> None:
        self.grid = grid
        self.positions = self._calculate_positions()
        self.polygons = self._calculate_polygons()

        self._display_coordinate_labels = False
        self._display_move_indices = False
        self._hexagons_to_highlight: list[tuple[Hexagon, Color]] = []
        self._victory_sequence_copy: set[Coordinate] = set()
