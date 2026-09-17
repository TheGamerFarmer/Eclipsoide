import pygame as pg
from coin_popup import CoinPopup
from datas import Datas
from player import Player
from particle import Particle


class Coin(pg.sprite.Sprite):
    SIZE = (16, 16)
    FRAME_SPEED = 0.006

    MIN_SPEED = 0.05       # pixels/ms au moment du drop
    MAX_SPEED = 0.9        # pixels/ms vitesse d'aspiration max
    ACCELERATION = 0.0025  # pixels/ms^2

    # Petite traînée lumineuse pendant l'aspiration vers le joueur
    TRAIL_DELAY = 30  # ms entre deux particules de traînée
    TRAIL_COLOR_START = (255, 230, 120)
    TRAIL_COLOR_END = (255, 180, 40)

    images_set: bool = False
    images: list[pg.Surface]

    def __init__(self, position: pg.Vector2, player: Player, *groups, datas: Datas = None):
        super().__init__(*groups)

        if not Coin.images_set:
            Coin.images = [pg.image.load(f'images/ui/Coins/coin_{i}.png') for i in range(5)]
            Coin.images = [pg.transform.scale(image, Coin.SIZE) for image in Coin.images]
            Coin.images_set = True

        self.player = player
        self.datas = datas
        self.position = pg.Vector2(position)
        self.speed = Coin.MIN_SPEED
        self.trail_timer = 0

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

        if self.datas is not None:
            self.trail_timer -= dt
            if self.trail_timer <= 0:
                self.trail_timer = Coin.TRAIL_DELAY
                velocity = -direction.normalize() * 0.03 if direction.length_squared() > 0 else pg.Vector2()
                Particle(self.position, velocity, Coin.TRAIL_COLOR_START, Coin.TRAIL_COLOR_END, self.datas.particles_group)

    @classmethod
    def collect(cls, player, datas: Datas) -> bool:
        """ Ramasse les pièces au contact du joueur (aspirées automatiquement vers lui) et
        affiche leur popup de gain. Retourne True si au moins une pièce a été ramassée """
        collected = pg.sprite.spritecollide(player, datas.coins_group, dokill=True)
        if not collected:
            return False

        player.add_coins(len(collected) * player.get_coins_value())
        for coin in collected:
            CoinPopup(pg.Vector2(coin.rect.center), player.get_coins_value(), datas.popups_group)
        return True
