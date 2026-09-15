import pygame as pg

from .base import Box


class Triangle(Box):
    """Boss/forme triangulaire (isocèle, pointe vers le haut)."""

    def __init__(self, x, y, base_width, height, color=(255, 255, 255), *groups):
        self.base_width = base_width
        self.height = height
        super().__init__(x, y, color, *groups)

    def _build_image(self) -> pg.Surface:
        surface = pg.Surface((self.base_width, self.height), pg.SRCALPHA)
        points = [
            (self.base_width / 2, 0),
            (0, self.height),
            (self.base_width, self.height),
        ]
        pg.draw.polygon(surface, self.color, points)
        return surface