import pygame as pg
from .boss import Boss


class Triangle(Boss):
    """
    Boss triangulaire (isocèle, pointe vers le haut).

    Même comportement que Boss (bombes, patrouille, image de fond),
    seule la forme change.
    """

    def __init__(self, x, y, base_width, height, color=(255, 255, 255), *groups, **kwargs):
        super().__init__(x, y, base_width, height, color, *groups, **kwargs)

    @property
    def base_width(self):
        return self.width

    def _draw_shape(self, surface: pg.Surface, color) -> None:
        points = [
            (self.width / 2, 0),
            (0, self.height),
            (self.width, self.height),
        ]
        pg.draw.polygon(surface, color, points)
