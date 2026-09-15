import pygame as pg
from projectile import Projectile

class Player(pg.sprite.Sprite):
    size = (30, 26)
    image_shoot_set: bool = False
    image_shoot: list[pg.Surface]

    def __init__(self, screen: pg.Surface, speed: float, projectilsGroup: pg.sprite.AbstractGroup, *groups):
        super().__init__(*groups)

        self.speed = speed
        self.projectilsGroup = projectilsGroup
        self.screen = screen

        self.is_alive = True

        self.coins = 0

        self.fire_delay = 300
        self.fire_timer = 0

        if not Player.image_shoot_set:
            Player.image_shoot = [pg.image.load(f'images/laser/player/laser_player_{i}.png') for i in range(4)]
            Player.image_shoot = [pg.transform.scale(image, (6, 16)) for image in Player.image_shoot]
            Player.image_shoot_set = True

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

        if self.fire_timer <= 0:
            Projectile(pg.Vector2(self.rect.center), 0.4, pg.Vector2(0, -1), Player.image_shoot, (0, 255, 0), self.projectilsGroup)
            self.fire_timer = self.fire_delay

    def on_hit(self):
        self.is_alive = False
        self.kill()

    def add_coins(self, amount: int):
        self.coins += amount