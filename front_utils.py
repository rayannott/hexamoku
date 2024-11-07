from pygame import Color


WHITE = Color("white")
BLACK = Color("black")
RED = Color("red")
GREEN = Color("green")
BLUE = Color("blue")
ORANGE = Color("orange")
MAGENTA = Color("magenta")
PINK = Color("#cf02be")
GRAY = Color("gray")


def dim_color(color: Color, factor: float) -> Color:
    if factor == 1:
        return color
    return Color(
        int(color.r * factor),
        int(color.g * factor),
        int(color.b * factor),
    )
