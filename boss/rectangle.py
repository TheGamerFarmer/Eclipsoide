


import pygame as pg

from .base import Box


class Rectangle(Box):
    """Boss/forme rectangulaire."""

    def __init__(self, x, y, width, height, color=(255, 255, 255), *groups):
        self.width = width
        self.height = height
        super().__init__(x, y, color, *groups)

    def _build_image(self) -> pg.Surface:
        surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
        pg.draw.rect(surface, self.color, surface.get_rect())
        return surface