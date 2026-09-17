import math
import pygame as pg
from coin_popup import CoinPopup
from datas import Datas
from particle import Particle


class HeartPickup(pg.sprite.Sprite):
    """ Coeur rare qui drop des ennemis et redonne une vie au joueur (aspiré comme les pièces) """
    SIZE = (20, 20)

    MIN_SPEED = 0.05       # pixels/ms au moment du drop
    MAX_SPEED = 0.9        # pixels/ms vitesse d'aspiration max
    ACCELERATION = 0.0025  # pixels/ms^2

    PULSE_PERIOD = 500    # ms pour un cycle de pulsation
    PULSE_AMPLITUDE = 0.15  # variation de taille (+/- 15%), pour le distinguer des pièces

    # Petite traînée lumineuse pendant l'aspiration vers le joueur
    TRAIL_DELAY = 30  # ms entre deux particules de traînée
    TRAIL_COLOR_START = (255, 150, 180)
    TRAIL_COLOR_END = (255, 60, 100)

    image_set: bool = False
    base_image: pg.Surface

    def __init__(self, position: pg.Vector2, player, *groups, datas: Datas = None):
        super().__init__(*groups)

        if not HeartPickup.image_set:
            HeartPickup.base_image = pg.image.load('Eclipsoide/images/ui/Hearts/heart_full.png')
            HeartPickup.base_image = pg.transform.scale(HeartPickup.base_image, HeartPickup.SIZE)
            HeartPickup.image_set = True

        self.player = player
        self.datas = datas
        self.position = pg.Vector2(position)
        self.speed = HeartPickup.MIN_SPEED
        self.time = 0.0
        self.trail_timer = 0

        self.image = HeartPickup.base_image
        self.rect = self.image.get_rect(center=self.position)

    @classmethod
    def collect(cls, player, datas: Datas, popup_color: tuple[int, int, int]) -> bool:
        """ Ramasse les coeurs au contact du joueur, une vie de plus par coeur (plafonné à la
        vie max). Retourne True si au moins une vie a réellement été récupérée """
        collected = pg.sprite.spritecollide(player, datas.hearts_group, dokill=True)
        healed = False
        for heart in collected:
            if player.lives < player.max_lives:
                player.lives += 1
                CoinPopup(pg.Vector2(heart.rect.center), 1, datas.popups_group, color=popup_color)
                healed = True
        return healed

    def update(self, dt):
        self.time += dt

        pulse = 1 + HeartPickup.PULSE_AMPLITUDE * math.sin(self.time * (2 * math.pi / HeartPickup.PULSE_PERIOD))
        size = (max(1, int(HeartPickup.SIZE[0] * pulse)), max(1, int(HeartPickup.SIZE[1] * pulse)))
        self.image = pg.transform.scale(HeartPickup.base_image, size)

        # Aspiration : le coeur accélère en se dirigeant vers le joueur
        direction = pg.Vector2(self.player.rect.center) - self.position
        if direction.length_squared() > 0:
            self.speed = min(self.speed + HeartPickup.ACCELERATION * dt, HeartPickup.MAX_SPEED)
            self.position += direction.normalize() * self.speed * dt

        self.rect = self.image.get_rect(center=self.position)

        if self.datas is not None:
            self.trail_timer -= dt
            if self.trail_timer <= 0:
                self.trail_timer = HeartPickup.TRAIL_DELAY
                velocity = -direction.normalize() * 0.03 if direction.length_squared() > 0 else pg.Vector2()
                Particle(self.position, velocity, HeartPickup.TRAIL_COLOR_START, HeartPickup.TRAIL_COLOR_END, self.datas.particles_group)
