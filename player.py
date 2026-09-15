import pygame
import constantes
from projectile import Projectile

class Player(pygame.sprite.Sprite):
    def __init__(self, *groups, screen, speed, projectiles):
        super().__init__(*groups)

        self.speed = speed
        self.screen = screen
        self.projectiles = projectiles

        self.fire_delay = 0.3
        self.fire_timer = 0

        self.image = pygame.Surface((30, 30))
        self.image.fill("white")

        self.rect = self.image.get_rect(midbottom=(constantes.SCREEN_SIZE[0] // 2, constantes.SCREEN_SIZE[1] - 50))
        self.position = pygame.Vector2(self.rect.midbottom)

    def update(self, dt):
        keystate = pygame.key.get_pressed()
        movement = pygame.Vector2()

        if keystate[pygame.K_z]:
            movement.y -= 1
        if keystate[pygame.K_s]:
            movement.y += 1
        if keystate[pygame.K_q]:
            movement.x -= 1
        if keystate[pygame.K_d]:
            movement.x += 1

        if movement.length_squared() != 0:
            movement = movement.normalize()

        self.position += movement * self.speed * dt
        self.rect.midbottom = self.position
        self.rect.clamp_ip(self.screen.get_rect())
        self.position = pygame.Vector2(self.rect.midbottom)

        self.fire_timer -= (dt / 1000)

        if self.fire_timer <= 0 and keystate[pygame.K_SPACE]:
            Projectile(self.projectiles, origin=self.rect.midtop, speed=0.4, direction=pygame.Vector2(0, -1))
            self.fire_timer = self.fire_delay