import pygame as pg
from coin_popup import CoinPopup

class ShieldPickup(pg.sprite.Sprite):
    """ Bouclier rare qui drop des ennemis : bloque tous les coups pendant
    quelques secondes (aspiré vers le joueur comme les pièces/coeurs). Ne se
    cumule pas : en ramasser un autre pendant qu'il est actif relance juste
    le minuteur (voir Player.SHIELD_DURATION) """
    FRAME_COUNT = 12
    SIZE = (26, 26)
    FRAME_DELAY = 60  # ms entre deux frames de l'icône (juste pour le pickup)

    MIN_SPEED = 0.05       # pixels/ms au moment du drop
    MAX_SPEED = 0.9        # pixels/ms vitesse d'aspiration max
    ACCELERATION = 0.0025  # pixels/ms^2

    images_set: bool = False
    images: list[pg.Surface]

    def __init__(self, position: pg.Vector2, player, *groups):
        super().__init__(*groups)

        if not ShieldPickup.images_set:
            ShieldPickup.images = [
                pg.transform.scale(pg.image.load(f'Eclipsoide/images/shield/shield_{i}.png'), ShieldPickup.SIZE)
                for i in range(ShieldPickup.FRAME_COUNT)
            ]
            ShieldPickup.images_set = True

        self.player = player
        self.position = pg.Vector2(position)
        self.speed = ShieldPickup.MIN_SPEED
        self.time = 0.0

        self.image = ShieldPickup.images[0]
        self.rect = self.image.get_rect(center=self.position)

    @classmethod
    def collect(cls, player, shields_group: pg.sprite.AbstractGroup, popups_group: pg.sprite.AbstractGroup, popup_color: tuple[int, int, int]) -> bool:
        """ Ramasse le bouclier au contact du joueur : relance le minuteur à sa
        durée max (ne se cumule pas). Retourne True si au moins un a été ramassé """
        collected = pg.sprite.spritecollide(player, shields_group, dokill=True)
        if not collected:
            return False

        player.shield_timer = player.SHIELD_DURATION
        CoinPopup(pg.Vector2(collected[-1].rect.center), 1, popups_group, color=popup_color, prefix="+")
        return True

    def update(self, dt):
        self.time += dt
        frame = int(self.time / ShieldPickup.FRAME_DELAY) % ShieldPickup.FRAME_COUNT
        self.image = ShieldPickup.images[frame]

        # Aspiration : le bouclier accélère en se dirigeant vers le joueur
        direction = pg.Vector2(self.player.rect.center) - self.position
        if direction.length_squared() > 0:
            self.speed = min(self.speed + ShieldPickup.ACCELERATION * dt, ShieldPickup.MAX_SPEED)
            self.position += direction.normalize() * self.speed * dt

        self.rect = self.image.get_rect(center=self.position)
