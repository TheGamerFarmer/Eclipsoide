import pygame as pg
from pygame.math import Vector2

class Projectile(pg.sprite.Sprite):
    FRAME_SPEED: float = 0.01
    time = 0

    def __init__(self, origin: Vector2, speed: float, direction: pg.Vector2, textures: list[pg.Surface], *groups):
        super().__init__(*groups)
        self.all = all
        self.speed = speed
        self.direction = direction
        self.origin = origin
        self.frameIndex = 0

        self.surface = pg.Surface((6, 16))

        angle = pg.Vector2(0, -1).angle_to(direction)
        self.surface = pg.transform.rotate(self.surface, -angle)
        self.images = [pg.transform.rotate(texture, -angle) for texture in textures]
        self.image = self.images[0]
        self.surface.blit(self.image, (0, 0))

        self.rect = self.surface.get_rect()
        self.rect.move_ip(origin)

    def update(self, dt):
        self.time += dt
        self.frameIndex += dt * self.FRAME_SPEED
        self.image = self.images[int(self.frameIndex) % len(self.images)]

        newPos = self.origin + (self.direction * self.speed * self.time)

        self.rect.x = int(newPos.x)
        self.rect.y = int(newPos.y)

        if self.rect.bottom <= 0:
            self.kill()

