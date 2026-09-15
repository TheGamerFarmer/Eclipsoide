import pygame as pg
from pygame.math import Vector2

class Projectile(pg.sprite.Sprite):
    FRAME_SPEED: float = 0.01
    time = 0

    GLOW_PADDING = 10
    GLOW_LAYERS = 4
    GLOW_MAX_ALPHA = 90

    def __init__(self, origin: Vector2, speed: float, direction: pg.Vector2, textures: list[pg.Surface], glow_color: tuple[int, int, int] = None, *groups):
        super().__init__(*groups)
        self.all = all
        self.speed = speed
        self.direction = direction
        self.origin = origin
        self.frameIndex = 0
        self.glow_color = glow_color

        angle = pg.Vector2(0, -1).angle_to(direction)
        rotated_textures = [pg.transform.rotate(texture, -angle) for texture in textures]
        self.images = [self._build_frame(texture) for texture in rotated_textures]
        self.image = self.images[0]

        self.rect = self.image.get_rect()
        self.rect.move_ip(origin - Vector2(self.GLOW_PADDING, self.GLOW_PADDING))

    def _build_frame(self, texture: pg.Surface) -> pg.Surface:
        if not self.glow_color:
            return texture

        width = texture.get_width() + self.GLOW_PADDING * 2
        height = texture.get_height() + self.GLOW_PADDING * 2
        frame = pg.Surface((width, height), pg.SRCALPHA)

        center = (width // 2, height // 2)
        max_radius = max(width, height) // 2
        for layer in range(self.GLOW_LAYERS, 0, -1):
            radius = int(max_radius * (layer / self.GLOW_LAYERS))
            alpha = int(self.GLOW_MAX_ALPHA * (1 - layer / (self.GLOW_LAYERS + 1)))
            glow_layer = pg.Surface((width, height), pg.SRCALPHA)
            pg.draw.circle(glow_layer, (*self.glow_color, alpha), center, radius)
            frame.blit(glow_layer, (0, 0), special_flags=pg.BLEND_RGBA_ADD)

        frame.blit(texture, (self.GLOW_PADDING, self.GLOW_PADDING))
        return frame

    def update(self, dt):
        self.time += dt
        self.frameIndex += dt * self.FRAME_SPEED
        self.image = self.images[int(self.frameIndex) % len(self.images)]

        newPos = self.origin + (self.direction * self.speed * self.time)

        self.rect.x = int(newPos.x - self.GLOW_PADDING)
        self.rect.y = int(newPos.y - self.GLOW_PADDING)

        if self.rect.bottom <= 0:
            self.kill()

