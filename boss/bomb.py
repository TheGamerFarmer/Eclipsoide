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
    FUSE_TIME = 2500  # millisecondes avant explosion automatique

    # Bombe assortie au boss : roche sombre parcourue de braises
    ROCK_COLOR = (58, 44, 42)
    ROCK_EDGE_COLOR = (96, 74, 66)
    EMBER_COLOR = (255, 140, 45)
    GLOW_COLOR = (255, 110, 30)
    GLOW_RADIUS = 6  # halo autour de la bombe
    GLOW_MAX_ALPHA = 90  # sous le seuil des masques : le halo ne fait pas de dégâts

    EXPLOSION_COLOR = (255, 160, 0)
    EXPLOSION_CORE_COLOR = (255, 230, 150)

    def __init__(self, center: tuple[int, int], screen: pg.Surface | None = None, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.screen = screen
        self.pos = pg.Vector2(center)
        self.exploding = False
        self.explosion_time = 0
        self.fuse_time = 0
        self.image = self._build_bomb_image()
        self.rect = self.image.get_rect(center=center)

    def _build_bomb_image(self) -> pg.Surface:
        size = (self.RADIUS + self.GLOW_RADIUS) * 2
        surface = pg.Surface((size, size), pg.SRCALPHA)
        centre = (size // 2, size // 2)

        # Halo de braise, du plus large (discret) au plus proche (marqué)
        for i in range(self.GLOW_RADIUS, 0, -1):
            alpha = int(self.GLOW_MAX_ALPHA * (1 - i / (self.GLOW_RADIUS + 1)))
            pg.draw.circle(surface, (*self.GLOW_COLOR, alpha), centre, self.RADIUS + i)

        # Corps rocheux
        pg.draw.circle(surface, self.ROCK_COLOR, centre, self.RADIUS)
        # Quelques braises à la surface de la roche
        cx, cy = centre
        for dx, dy, r in ((-3, -2, 2), (2, 1, 2), (-1, 4, 1), (4, -3, 1)):
            pg.draw.circle(surface, self.EMBER_COLOR, (cx + dx, cy + dy), r)
        # Liseré clair pour détacher la bombe du fond
        pg.draw.circle(surface, self.ROCK_EDGE_COLOR, centre, self.RADIUS, 2)
        return surface

    def _build_explosion_image(self, radius: int) -> pg.Surface:
        size = max(radius * 2, 1)
        surface = pg.Surface((size, size), pg.SRCALPHA)
        centre = (radius, radius)
        pg.draw.circle(surface, self.EXPLOSION_COLOR, centre, radius)
        # Coeur plus clair, comme les braises de la bombe
        pg.draw.circle(surface, self.EXPLOSION_CORE_COLOR, centre, max(1, int(radius * 0.55)))
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

        # Explose toute seule une fois la mèche consumée
        self.fuse_time += dt
        if self.fuse_time >= self.FUSE_TIME:
            self.explode()
            return

        self.pos.y += self.SPEED_Y * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Supprime la bombe si elle sort de l'écran
        if self.rect.top > self.screen.get_height() + Bomb.RADIUS:
            self.kill()
