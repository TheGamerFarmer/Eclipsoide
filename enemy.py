# Utilisation de pygame avec un préfixe plus simple
import pygame as pg
# Accès à la classe Random
import random

from player import Player
from projectile import Projectile

# Une balle qui rebondie sur les bords et des paddles
class Enemy(pg.sprite.Sprite):
    SPAWN_EXTRA_PROPORTION = 3
    MIN_SPEED_Y = 80
    MAX_SPEED_Y = 120
    MIN_SPEED_X = 30
    MAX_SPEED_X = 80
    ASTEROID_SIZE = 70
    TIME_BETWEEN_SHOOT = 1000

    image_set: bool = False
    image: pg.Surface
    image_shoot_set: bool = False
    image_shoot: list[pg.Surface]

    size = (ASTEROID_SIZE,ASTEROID_SIZE)

    def __init__(self,screen: pg.Surface, player: Player, *groups):
        # Appel du constructeur la super classe
        pg.sprite.Sprite.__init__(self, *groups)

        # Points de vie de l'ennemie
        self.life = 100

        self.time = 0

        # La surface (image) à afficher de ce sprite
        self.surface = pg.Surface(self.size)

        if not Enemy.image_set:
            Enemy.image = pg.image.load('images/asteroide.png')
            Enemy.image = pg.transform.scale(Enemy.image, self.size)
            Enemy.image_set = True

        if not Enemy.image_shoot_set:
            Enemy.image_shoot = [pg.image.load(f'images/laser/enemy/laser_asteroide_{i}.png') for i in range(4)]
            Enemy.image_shoot = [pg.transform.scale(image, (6, 16)) for image in Enemy.image_shoot]
            Enemy.image_shoot_set = True

        self.image = pg.transform.rotate(Enemy.image, random.randint(-180, 180))
        self.surface.blit(self.image, (0,0))

        self.player = player
        self.screen = screen
        # Recupère le rectangle de la surface du Sprite
        self.rect = self.surface.get_rect()

        screenWith = Enemy.ASTEROID_SIZE * self.SPAWN_EXTRA_PROPORTION

        self.initPosition = pg.Vector2(random.randint(-screenWith, screen.get_width() + screenWith), random.randint(-Enemy.ASTEROID_SIZE * Enemy.SPAWN_EXTRA_PROPORTION, -Enemy.ASTEROID_SIZE))
        self.rect.move_ip(self.initPosition)


        # Vecteur de mouvement
        self.speedY = random.randrange(Enemy.MIN_SPEED_Y, Enemy.MAX_SPEED_Y, 1) / 1000.0
        self.speedX = random.randrange(Enemy.MIN_SPEED_X, Enemy.MAX_SPEED_X, 1) / 1000.0

        self.speedY = max(self.speedX, self.speedY)

        if self.initPosition.x > screen.get_width() / 2.0:
            self.speedX = -self.speedX

        self.movement = pg.Vector2(self.speedX, self.speedY)

    def update(self,dt):
        """ Met à jour la position de la balle  """
        oldPos = pg.Vector2(self.rect.center)

        if (self.time + dt) % Enemy.TIME_BETWEEN_SHOOT < dt:
            playerRect = self.player.rect
            direction = pg.Vector2(playerRect.center) - oldPos
            if direction.length() > 0:
                Projectile(oldPos, 0.2, direction.normalize(), Enemy.image_shoot, self.groups()[0])

        # Déplace la position de la raquette en fonction du veteur de mouvement
        # Calcule le vecteur déplacement
        self.time += dt
        # Modifie la position
        newPos = self.initPosition + (self.movement * self.time)

        if newPos.y > self.screen.get_height() + Enemy.ASTEROID_SIZE:
            self.kill()

        self.rect.x = int(newPos.x)
        self.rect.y = int(newPos.y)

    def hited(self, damage: int):
        self.life -= damage
        if self.life <= 0:
            self.kill()