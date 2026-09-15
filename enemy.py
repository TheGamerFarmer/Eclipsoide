# Utilisation de pygame avec un préfixe plus simple
import pygame as pg
# Accès à la classe Random
import random

from pygame.sprite import RenderUpdates


# Une balle qui rebondie sur les bords et des paddles
class Enemy(pg.sprite.Sprite):
    SPAWN_EXTRA_PROPORTION = 7.0
    MIN_SPEED_Y = 80
    MAX_SPEED_Y = 120
    MIN_SPEED_X = 30
    MAX_SPEED_X = 80

    """ Une balle qui rebondit """
    # Taille largeur, hauteur de la balle
    size = (20,20)
    time = 0
    life = 100

    def __init__(self,screen: pg.Surface, all: RenderUpdates , *groups):
        # Appel du constructeur la super classe
        pg.sprite.Sprite.__init__(self, *groups)
        # La surface (image) à afficher de ce sprite
        self.image = pg.Surface(self.size)
        self.screen = screen
        self.all = all
        # Recupère le rectangle de la surface du Sprite
        self.rect = self.image.get_bounding_rect()

        screenWith = int(screen.get_width() / self.SPAWN_EXTRA_PROPORTION)

        self.initPosition = pg.Vector2(random.randint(-screenWith, screen.get_width() + screenWith), random.randint(-int(screen.get_height() / self.SPAWN_EXTRA_PROPORTION), -20))
        self.rect.move_ip(self.initPosition.x, self.initPosition.y)

        # Donne une couleur
        self.image.fill("red")

        # Vecteur de mouvement
        self.speedY = random.randrange(self.MIN_SPEED_Y, self.MAX_SPEED_Y, 1) / 1000.0
        self.speedX = random.randrange(self.MIN_SPEED_X, self.MAX_SPEED_X, 1) / 1000.0

        self.speedY = max(self.speedX, self.speedY)

        if self.initPosition.x > screen.get_width() / 2.0:
            self.speedX = -self.speedX

        self.movement = pg.Vector2(self.speedX, self.speedY)
        self.all.add(self)

    def update(self,dt):
        """ Met à jour la position de la balle  """
        # Déplace la position de la raquette en fonction du veteur de mouvement
        # Calcule le vecteur déplacement
        self.time += dt
        # Modifie la position
        newPos = self.initPosition + (self.movement * self.time)

        if newPos.y > self.screen.get_height() + 20:
            self.all.remove(self)

        self.rect.x = int(newPos.x)
        self.rect.y = int(newPos.y)