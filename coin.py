import pygame as pg

class Coin(pg.sprite.Sprite):
    SIZE = (16, 16)
    FRAME_SPEED = 0.006
    VALUE = 20

    MIN_SPEED = 0.05       # pixels/ms au moment du drop
    MAX_SPEED = 0.9        # pixels/ms vitesse d'aspiration max
    ACCELERATION = 0.0025  # pixels/ms^2

    images_set: bool = False
    images: list[pg.Surface]

    def __init__(self, position: pg.Vector2, player, *groups):
        super().__init__(*groups)

        if not Coin.images_set:
            Coin.images = [pg.image.load(f'images/ui/Coins/coin_{i}.png') for i in range(5)]
            Coin.images = [pg.transform.scale(image, Coin.SIZE) for image in Coin.images]
            Coin.images_set = True

        self.player = player
        self.position = pg.Vector2(position)
        self.speed = Coin.MIN_SPEED

        self.frameIndex = 0.0
        self.image = Coin.images[0]
        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt):
        self.frameIndex += dt * Coin.FRAME_SPEED
        self.image = Coin.images[int(self.frameIndex) % len(Coin.images)]

        # Aspiration : la pièce accélère en se dirigeant vers le joueur
        direction = pg.Vector2(self.player.rect.center) - self.position
        if direction.length_squared() > 0:
            self.speed = min(self.speed + Coin.ACCELERATION * dt, Coin.MAX_SPEED)
            self.position += direction.normalize() * self.speed * dt

        self.rect.center = self.position
