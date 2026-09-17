import pygame as pg


class SpawnPing(pg.sprite.Sprite):
    """ Anneau qui s'agrandit et s'estompe : signale l'apparition d'un ennemi
    qui surgit sans télégraphe propre (ex. Tracker) """
    DURATION = 450  # ms
    START_RADIUS = 6
    END_RADIUS = 34
    COLOR = (200, 60, 255)
    WIDTH = 3
    MAX_ALPHA = 200

    def __init__(self, position: pg.Vector2, *groups):
        super().__init__(*groups)
        self.position = pg.Vector2(position)
        self.time = 0
        self.image = pg.Surface((1, 1), pg.SRCALPHA)
        self.rect = self.image.get_rect(center=self.position)
        self._redraw(0.0)

    def _redraw(self, progress: float) -> None:
        radius = self.START_RADIUS + (self.END_RADIUS - self.START_RADIUS) * progress
        alpha = max(0, int(self.MAX_ALPHA * (1 - progress)))
        size = int(radius * 2 + self.WIDTH * 2)
        surface = pg.Surface((size, size), pg.SRCALPHA)
        pg.draw.circle(surface, (*self.COLOR, alpha), (size // 2, size // 2), int(radius), self.WIDTH)
        self.image = surface
        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt):
        self.time += dt
        if self.time >= self.DURATION:
            self.kill()
            return
        self._redraw(self.time / self.DURATION)
