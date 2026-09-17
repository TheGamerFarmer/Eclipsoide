import pygame as pg


class Shockwave(pg.sprite.Sprite):
    """ Anneau qui s'étend rapidement et s'estompe : accentue l'impact d'une
    grosse explosion (ex. mort du boss), en plus du tremblement d'écran """
    DURATION = 500  # ms
    COLOR = (255, 200, 120)
    START_WIDTH = 10
    END_WIDTH = 2
    MAX_ALPHA = 200

    def __init__(self, position: pg.Vector2, *groups, min_radius: float = 20, max_radius: float = 260):
        super().__init__(*groups)
        self.position = pg.Vector2(position)
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.time = 0
        self.image = pg.Surface((1, 1), pg.SRCALPHA)
        self.rect = self.image.get_rect(center=self.position)
        self._redraw(0.0)

    def _redraw(self, progress: float) -> None:
        radius = self.min_radius + (self.max_radius - self.min_radius) * progress
        width = max(1, int(self.START_WIDTH + (self.END_WIDTH - self.START_WIDTH) * progress))
        alpha = max(0, int(self.MAX_ALPHA * (1 - progress)))
        size = int(radius * 2 + width * 2)
        surface = pg.Surface((size, size), pg.SRCALPHA)
        pg.draw.circle(surface, (*self.COLOR, alpha), (size // 2, size // 2), int(radius), width)
        self.image = surface
        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt):
        self.time += dt
        if self.time >= self.DURATION:
            self.kill()
            return
        self._redraw(self.time / self.DURATION)
