from typing import Any
import pygame as pg

class Bomb(pg.sprite.Sprite):
    """
    Bombe lâchée par le Triangle : tombe vers le bas jusqu'à ce que
    le bouton de détonation soit pressé, puis se transforme en explosion.
    """

    RADIUS = 10
    SPEED_Y = 0.15  # pixels par milliseconde
    EXPLOSION_RADIUS = 60
    EXPLOSION_DURATION = 300  # millisecondes
    COLOR = (40, 40, 40)
    EXPLOSION_COLOR = (255, 160, 0)

    def __init__(self, center: tuple[int, int], bounds: pg.Rect | None = None, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.bounds = bounds
        self.pos = pg.Vector2(center)
        self.exploding = False
        self.explosion_time = 0
        self.image = self._build_bomb_image()
        self.rect = self.image.get_rect(center=center)

    def _build_bomb_image(self) -> pg.Surface:
        size = self.RADIUS * 2
        surface = pg.Surface((size, size), pg.SRCALPHA)
        pg.draw.circle(surface, self.COLOR, (self.RADIUS, self.RADIUS), self.RADIUS)
        return surface

    def _build_explosion_image(self, radius: int) -> pg.Surface:
        size = max(radius * 2, 1)
        surface = pg.Surface((size, size), pg.SRCALPHA)
        pg.draw.circle(surface, self.EXPLOSION_COLOR, (radius, radius), radius)
        return surface

    def explode(self) -> None:
        """Déclenche l'explosion (sans effet si elle a déjà commencé)."""
        if self.exploding:
            return
        self.exploding = True
        self.explosion_time = 0

    def update(self, *args: Any, **kwargs: Any) -> None:
        dt: int = args[0] if args else 0

        if self.exploding:
            self.explosion_time += dt
            if self.explosion_time >= self.EXPLOSION_DURATION:
                self.kill()
                return
            # Le rayon grossit pendant la durée de l'explosion
            progress = self.explosion_time / self.EXPLOSION_DURATION
            radius = int(self.RADIUS + (self.EXPLOSION_RADIUS - self.RADIUS) * progress)
            self.image = self._build_explosion_image(radius)
            self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            return

        self.pos.y += self.SPEED_Y * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Supprime la bombe si elle sort de l'écran
        if self.bounds is not None and self.rect.top > self.bounds.bottom:
            self.kill()
