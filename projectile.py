import pygame as pg
from pygame.math import Vector2

class Projectile(pg.sprite.Sprite):
    FRAME_SPEED: float = 0.01
    time = 0

    GLOW_PADDING = 10
    GLOW_LAYERS = 4
    GLOW_MAX_ALPHA = 90

    # Traînée de vitesse : dégradé du glow_color vers trail_end_color, d'autant plus longue que le tir est rapide
    TRAIL_LENGTH_SCALE = 150  # px de traînée par pixel/ms de vitesse
    TRAIL_MIN_LENGTH = 14
    TRAIL_MAX_LENGTH = 70
    TRAIL_STEPS = 16
    DEFAULT_TRAIL_END_COLOR = (255, 255, 255)

    def __init__(self, origin: Vector2, speed: float, direction: pg.Vector2, textures: list[pg.Surface], glow_color: tuple[int, int, int] = None, *groups, trail_end_color: tuple[int, int, int] = None):
        super().__init__(*groups)
        self.all = all
        self.speed = speed
        self.direction = direction
        self.origin = origin
        self.frameIndex = 0
        self.glow_color = glow_color
        self.trail_end_color = trail_end_color if trail_end_color else self.DEFAULT_TRAIL_END_COLOR

        self.trail_length = self._compute_trail_length()
        # Décalage entre le point d'origine du tir et le coin supérieur gauche
        # de l'image finale (glow + traînée inclus dans la surface)
        self.anchor_offset = Vector2(self.GLOW_PADDING, self.GLOW_PADDING) + Vector2(self.trail_length, self.trail_length)

        angle = pg.Vector2(0, -1).angle_to(direction)
        rotated_textures = [pg.transform.rotate(texture, -angle) for texture in textures]
        self.images = [self._build_frame(texture) for texture in rotated_textures]
        self.image = self.images[0]

        self.rect = self.image.get_rect()
        self.rect.move_ip(origin - self.anchor_offset)

        # Hitbox de collision : la taille réelle du tir, sans le halo ni la
        # traînée (qui sont purement visuels et ne doivent pas la faire toucher
        # des ennemis à distance)
        self.hitbox = pg.Rect(0, 0, *textures[0].get_size())
        self.hitbox.topleft = (int(origin.x), int(origin.y))

    def _compute_trail_length(self) -> int:
        if not self.glow_color:
            return 0
        return int(min(self.TRAIL_MAX_LENGTH, max(self.TRAIL_MIN_LENGTH, self.speed * self.TRAIL_LENGTH_SCALE)))

    def _build_frame(self, texture: pg.Surface) -> pg.Surface:
        if not self.glow_color:
            return texture

        pad = self.GLOW_PADDING + self.trail_length
        width = texture.get_width() + pad * 2
        height = texture.get_height() + pad * 2
        frame = pg.Surface((width, height), pg.SRCALPHA)

        # Le halo reste calé sur la taille de la texture, pas sur la traînée
        core_center = (pad + texture.get_width() // 2, pad + texture.get_height() // 2)
        core_radius = max(texture.get_width(), texture.get_height()) // 2 + self.GLOW_PADDING
        for layer in range(self.GLOW_LAYERS, 0, -1):
            radius = int(core_radius * (layer / self.GLOW_LAYERS))
            alpha = int(self.GLOW_MAX_ALPHA * (1 - layer / (self.GLOW_LAYERS + 1)))
            glow_layer = pg.Surface((width, height), pg.SRCALPHA)
            pg.draw.circle(glow_layer, (*self.glow_color, alpha), core_center, radius)
            frame.blit(glow_layer, (0, 0), special_flags=pg.BLEND_RGBA_ADD)

        if self.trail_length > 0:
            self._draw_trail(frame, core_center, texture.get_width())

        frame.blit(texture, (pad, pad))
        return frame

    def _draw_trail(self, frame: pg.Surface, attach_point: tuple[int, int], texture_width: int):
        start_color = pg.Color(*self.glow_color)
        end_color = pg.Color(*self.trail_end_color)
        base_radius = max(3, texture_width * 0.5)

        for step in range(self.TRAIL_STEPS, 0, -1):
            t = step / self.TRAIL_STEPS
            offset = -self.direction * t * self.trail_length
            pos = (int(attach_point[0] + offset.x), int(attach_point[1] + offset.y))
            radius = max(1, int(base_radius * (1 - t * 0.75)))
            color = start_color.lerp(end_color, t)
            alpha = max(0, min(255, int(self.GLOW_MAX_ALPHA * 1.6 * (1 - t) ** 1.2)))

            segment = pg.Surface(frame.get_size(), pg.SRCALPHA)
            pg.draw.circle(segment, (color.r, color.g, color.b, alpha), pos, radius)
            frame.blit(segment, (0, 0), special_flags=pg.BLEND_RGBA_ADD)

    @staticmethod
    def collide(a: pg.sprite.Sprite, b: pg.sprite.Sprite) -> bool:
        """ Collision utilisant la hitbox du projectile plutôt que son rect visuel
        (halo + traînée), quel que soit le côté (a ou b) qui porte le projectile """
        rect_a = getattr(a, 'hitbox', a.rect)
        rect_b = getattr(b, 'hitbox', b.rect)
        return rect_a.colliderect(rect_b)

    def update(self, dt):
        self.time += dt
        self.frameIndex += dt * self.FRAME_SPEED
        self.image = self.images[int(self.frameIndex) % len(self.images)]

        newPos = self.origin + (self.direction * self.speed * self.time)

        self.rect.x = int(newPos.x - self.anchor_offset.x)
        self.rect.y = int(newPos.y - self.anchor_offset.y)
        self.hitbox.topleft = (int(newPos.x), int(newPos.y))

        if self.rect.bottom <= 0:
            self.kill()
