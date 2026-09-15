import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, origin, speed: int, direction: pygame.Vector2, *groups):
        super().__init__(*groups)

        self.speed = speed
        self.direction = direction

        self.image = pygame.Surface((6, 16))
        self.image.fill("yellow")

        self.rect = self.image.get_rect(midbottom=origin)
        self.position = pygame.Vector2(self.rect.midbottom)

    def update(self, dt):
        self.position += self.direction * self.speed * dt
        self.rect.midbottom = self.position
        if self.rect.bottom <= 0:
            self.kill()

