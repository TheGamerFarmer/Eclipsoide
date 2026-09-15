import pygame as pg
import constantes
from projectile import Projectile
from pygame.sprite import RenderUpdates

class Player(pg.sprite.Sprite):
    image_shoot = None

    def __init__(self, all: RenderUpdates, screen: pg.Surface, speed: float, *groups):
        super().__init__(*groups)

        self.all = all
        self.speed = speed
        self.screen = screen

        self.fire_delay = 0.3
        self.fire_timer = 0

        if Player.image_shoot is None:
            Player.image_shoot = pg.image.load('images/asteroide.png')
            Player.image_shoot = pg.transform.scale(Player.image_shoot, (6, 16))

        self.image = pg.Surface((30, 30))
        self.image.fill("white")

        self.rect = self.image.get_rect(midbottom=(constantes.SCREEN_SIZE[0] // 2, constantes.SCREEN_SIZE[1] - 50))
        self.position = pg.Vector2(self.rect.midbottom)
        all.add(self)

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

        self.fire_timer -= (dt / 1000)

        if self.fire_timer <= 0 and keystate[pg.K_SPACE]:
            Projectile(self.all, pg.Vector2(self.rect.center), 0.4, pg.Vector2(0, -1), [Player.image_shoot])
            self.fire_timer = self.fire_delay