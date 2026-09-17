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

    def __init__(self, pos, player, datas, *groups):
        super().__init__(*groups)
        self.datas = datas
        self.player = player

        self.life = 100
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

        self.trail_timer -= dt
        if self.trail_timer <= 0:
            self.trail_timer = 40
            velocity = -self.direction * 0.05
            spawn_pos = self.pos + pg.Vector2(random.uniform(-4, 4), random.uniform(-4, 4))
            Particle(spawn_pos, velocity, (200, 50, 255), (100, 0, 150), self.datas.particles_group)

            pulse = 1 + 0.15 * math.sin(self.time * 0.01)
            new_size = (int(self.SIZE[0] * pulse), int(self.SIZE[1] * pulse))
            self.image = pg.transform.smoothscale(self.base_image, new_size)
            self.rect = self.image.get_rect(center=self.rect.center)

        # destruction si le drone sort vraiment très loin de l'écran par le bas
        if self.pos.y > self.datas.screen.get_height() + 100:
            self.kill()