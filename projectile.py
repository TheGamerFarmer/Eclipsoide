import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, *groups, speed, origin):
        super().__init__(*groups)

        self.speed = speed

        self.image = pygame.Surface((6, 16))
        self.image.fill("yellow")

        self.rect = self.image.get_rect(midbottom=origin)
        self.position = pygame.Vector2(self.rect.midbottom)

    def update(self, dt):
        movement = pygame.Vector2(0, -1)

        self.position += movement * self.speed * dt
        self.rect.midbottom = self.position
        if self.rect.bottom <= 0:
            self.kill()

