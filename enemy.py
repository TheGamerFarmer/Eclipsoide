# Utilisation de pygame avec un préfixe plus simple
import pygame as pg
# Accès à la classe Random
import random


# Une balle qui rebondie sur les bords et des paddles
class Enemy(pg.sprite.Sprite):
    SPAWN_EXTRA_PROPORTION = 3
    MIN_SPEED_Y = 80
    MAX_SPEED_Y = 120
    MIN_SPEED_X = 30
    MAX_SPEED_X = 80
    ASTEROID_SIZE = 85

    image = None

    size = (ASTEROID_SIZE,ASTEROID_SIZE)

    def __init__(self, *groups, screen: pg.Surface):
        # Appel du constructeur la super classe
        pg.sprite.Sprite.__init__(self, *groups)

        # Points de vie de l'ennemie
        self.life = 100

        self.time = 0

        # La surface (image) à afficher de ce sprite
        if Enemy.image is None:
            Enemy.image = pg.image.load('images/asteroide.png')
            Enemy.image = pg.transform.scale(Enemy.image, self.size)
        self.image = pg.transform.rotate(Enemy.image, random.randint(-180, 180))
        self.screen = screen
        # Recupère le rectangle de la surface du Sprite
        self.rect = self.image.get_rect()

        screenWith = Enemy.ASTEROID_SIZE * self.SPAWN_EXTRA_PROPORTION

        self.initPosition = pg.Vector2(random.randint(-screenWith, screen.get_width() + screenWith), random.randint(-Enemy.ASTEROID_SIZE * Enemy.SPAWN_EXTRA_PROPORTION, -Enemy.ASTEROID_SIZE))
        self.rect.move_ip(self.initPosition.x, self.initPosition.y)


        # Vecteur de mouvement
        self.speedY = random.randrange(Enemy.MIN_SPEED_Y, Enemy.MAX_SPEED_Y, 1) / 1000.0
        self.speedX = random.randrange(Enemy.MIN_SPEED_X, Enemy.MAX_SPEED_X, 1) / 1000.0

        self.speedY = max(self.speedX, self.speedY)

        if self.initPosition.x > screen.get_width() / 2.0:
            self.speedX = -self.speedX

        self.movement = pg.Vector2(self.speedX, self.speedY)

    def update(self,dt):
        """ Met à jour la position de la balle  """
        # Déplace la position de la raquette en fonction du veteur de mouvement
        # Calcule le vecteur déplacement
        self.time += dt
        # Modifie la position
        newPos = self.initPosition + (self.movement * self.time)

        if newPos.y > self.screen.get_height() + 20:
            self.kill()

        self.rect.x = int(newPos.x)
        self.rect.y = int(newPos.y)

    def hited(self, damage: int):
        self.life -= damage
        if self.life <= 0:
            self.kill()