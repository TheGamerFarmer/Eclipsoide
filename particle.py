import random
import pygame as pg

class Particle(pg.sprite.Sprite):
    """ Petit point coloré qui s'estompe avec le temps (utilisé pour les traînées) """
    LIFETIME = 280       # ms
    MIN_SIZE = 2
    MAX_SIZE = 5

    def __init__(self, position: pg.Vector2, velocity: pg.Vector2,
                 color_start: tuple[int, int, int] = (255, 220, 120),
                 color_end: tuple[int, int, int] = (255, 60, 20), *groups):
        super().__init__(*groups)

        self.position = pg.Vector2(position)
        self.velocity = pg.Vector2(velocity)
        self.color_start = pg.Color(*color_start)
        self.color_end = pg.Color(*color_end)

        self.time = 0
        self.lifetime = Particle.LIFETIME * random.uniform(0.7, 1.2)
        self.size = random.uniform(Particle.MIN_SIZE, Particle.MAX_SIZE)

        self.image = self._build_image(0.0)
        self.rect = self.image.get_rect(center=self.position)

    def _build_image(self, progress: float) -> pg.Surface:
        # Le point rétrécit et change de couleur en vieillissant
        radius = max(1, self.size * (1 - progress))
        diameter = int(radius * 2) + 1
        surface = pg.Surface((diameter, diameter), pg.SRCALPHA)
        color = self.color_start.lerp(self.color_end, progress)
        alpha = int(255 * (1 - progress))
        pg.draw.circle(surface, (color.r, color.g, color.b, alpha), (diameter // 2, diameter // 2), radius)
        return surface

    def update(self, dt):
        self.time += dt
        progress = self.time / self.lifetime
        if progress >= 1.0:
            self.kill()
            return

        self.position += self.velocity * dt
        self.image = self._build_image(progress)
        self.rect = self.image.get_rect(center=self.position)
