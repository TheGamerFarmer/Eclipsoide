import pygame as pg
import math
import random
from particle import Particle
from projectile import Projectile

class Tracker(pg.sprite.Sprite):

    SIZE = (30, 30)
    # un peu plus lent que les bombes pour laisser le temps de l'esquiver
    SPEED = 0.12
    TURN_SPEED = 0.003

    # Halo qui grandit/s'intensifie à mesure que le drone se rapproche du
    # joueur, pour accentuer la menace imminente
    PROXIMITY_GLOW_COLOR = (255, 80, 220)
    PROXIMITY_MAX_RADIUS = 26   # px, rayon du halo à distance minimale
    PROXIMITY_MIN_DISTANCE = 60   # distance sous laquelle le halo est à son maximum
    PROXIMITY_MAX_DISTANCE = 400  # distance au-delà de laquelle il n'y a plus de halo
    PROXIMITY_GLOW_MAX_ALPHA = 160
    PROXIMITY_GLOW_LAYERS = 3

    def __init__(self, pos, player, datas, *groups):
        super().__init__(*groups)
        self.datas = datas
        self.player = player

        self.life = int(100 * (3 ** (self.datas.stage - 1)))
        self.time = 0

        # création du visuel
        self.base_image = pg.Surface(self.SIZE, pg.SRCALPHA)
        center = (self.SIZE[0] // 2, self.SIZE[1] // 2)
        pg.draw.circle(self.base_image, (180, 50, 255, 150), center, 15)
        pg.draw.circle(self.base_image, (255, 150, 255, 255), center, 8)

        self.image = self.base_image
        self.rect = self.image.get_rect(center=pos)

        self.pos = pg.Vector2(pos)
        self.direction = pg.Vector2(0, 1)
        self.trail_timer = 0

        self.hitbox = pg.Rect(0, 0, 24, 24)
        self.hitbox.center = self.rect.center

    def hited(self, damage: int):
        self.life -= damage
        if self.life <= 0:
            self.kill()

    def update(self, dt):
        self.time += dt

        hits = pg.sprite.spritecollide(self, self.datas.projectiles_group, dokill=True, collided=Projectile.collide)
        for hit in hits:
            self.hited(self.player.damage)

        target_pos = pg.Vector2(self.player.rect.center)
        desired_dir = target_pos - self.pos
        if desired_dir.length_squared() > 0:
            desired_dir = desired_dir.normalize()

        self.direction = self.direction.lerp(desired_dir, self.TURN_SPEED * dt)
        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()

        self.pos += self.direction * self.SPEED * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.hitbox.center = self.rect.center

        self.trail_timer -= dt
        if self.trail_timer <= 0:
            self.trail_timer = 40
            velocity = -self.direction * 0.05
            spawn_pos = self.pos + pg.Vector2(random.uniform(-4, 4), random.uniform(-4, 4))
            Particle(spawn_pos, velocity, (200, 50, 255), (100, 0, 150), self.datas.particles_group)

            self._rebuild_image()

        # destruction si le drone sort vraiment très loin de l'écran par le bas
        if self.pos.y > self.datas.screen.get_height() + 100:
            self.kill()

    def _proximity(self) -> float:
        """ 0 = joueur loin (pas de halo), 1 = à PROXIMITY_MIN_DISTANCE ou moins """
        distance = self.pos.distance_to(self.player.rect.center)
        span = self.PROXIMITY_MAX_DISTANCE - self.PROXIMITY_MIN_DISTANCE
        t = (self.PROXIMITY_MAX_DISTANCE - distance) / span
        return max(0.0, min(1.0, t))

    def _rebuild_image(self):
        pulse = 1 + 0.15 * math.sin(self.time * 0.01)
        drone_size = (int(self.SIZE[0] * pulse), int(self.SIZE[1] * pulse))
        drone = pg.transform.smoothscale(self.base_image, drone_size)

        proximity = self._proximity()
        glow_radius = self.PROXIMITY_MAX_RADIUS * proximity

        canvas_radius = max(drone_size) // 2 + int(glow_radius) + 4
        size = canvas_radius * 2
        surface = pg.Surface((size, size), pg.SRCALPHA)
        center = (size // 2, size // 2)

        if glow_radius > 1:
            base_alpha = self.PROXIMITY_GLOW_MAX_ALPHA * proximity
            for layer in range(self.PROXIMITY_GLOW_LAYERS, 0, -1):
                layer_radius = int(glow_radius * (layer / self.PROXIMITY_GLOW_LAYERS))
                layer_alpha = max(0, min(255, int(base_alpha * (1 - layer / (self.PROXIMITY_GLOW_LAYERS + 1)))))
                layer_surface = pg.Surface((size, size), pg.SRCALPHA)
                pg.draw.circle(layer_surface, (*self.PROXIMITY_GLOW_COLOR, layer_alpha), center, layer_radius)
                surface.blit(layer_surface, (0, 0), special_flags=pg.BLEND_RGBA_ADD)

        surface.blit(drone, drone.get_rect(center=center))
        self.image = surface
        self.rect = self.image.get_rect(center=self.rect.center)