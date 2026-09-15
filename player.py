import pygame as pg
from projectile import Projectile

class Player(pg.sprite.Sprite):
    image_shoot = None
    size = (30, 26)

    def __init__(self, screen: pg.Surface, speed: float, projectilsGroup: pg.sprite.AbstractGroup, *groups):
        super().__init__(*groups)

        self.speed = speed
        self.projectilsGroup = projectilsGroup
        self.screen = screen

        self.is_alive = True

        self.fire_delay = 300
        self.fire_timer = 0

        if Player.image_shoot is None:
            Player.image_shoot = pg.image.load('images/asteroide.png')
            Player.image_shoot = pg.transform.scale(Player.image_shoot, (6, 16))

        self.surface = pg.Surface(self.size)
        self.image = pg.image.load('images/ship.png')
        self.image = pg.transform.scale(self.image, self.size)
        self.surface.blit(self.image, (0, 0))

        self.rect = self.surface.get_rect()
        self.rect.move_ip(screen.get_width() / 2 - self.size[0] / 2, screen.get_height() - 50)
        self.position = pg.Vector2(self.rect.midbottom)

    def update(self, dt):
        keystate = pg.key.get_pressed()
        movement = pg.Vector2()

        if keystate[pg.K_z] or keystate[pg.K_UP]:
            movement.y -= 1
        if keystate[pg.K_s] or keystate[pg.K_DOWN]:
            movement.y += 1
        if keystate[pg.K_q] or keystate[pg.K_LEFT]:
            movement.x -= 1
        if keystate[pg.K_d] or keystate[pg.K_RIGHT]:
            movement.x += 1

        if movement.length_squared() != 0:
            movement = movement.normalize()

        self.position += movement * self.speed * dt
        self.rect.midbottom = self.position
        self.rect.clamp_ip(self.screen.get_rect())
        self.position = pg.Vector2(self.rect.midbottom)

        self.fire_timer -= dt

        if self.fire_timer <= 0 and keystate[pg.K_SPACE]:
            Projectile(pg.Vector2(self.rect.center), 0.4, pg.Vector2(0, -1), [Player.image_shoot], self.projectilsGroup)
            self.fire_timer = self.fire_delay

    def on_hit(self):
        self.is_alive = False
        self.kill()