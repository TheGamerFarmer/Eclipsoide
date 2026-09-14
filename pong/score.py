# Utilisation de pygame avec un préfixe plus simple
import pygame as pg


# Gestion d'un score affiché en haut de l'écran
class Score(pg.sprite.Sprite):
    """ Score des deux joueurs et son affichage """

    def __init__(self, *groups):
        # Appel du constructeur la super classe
        pg.sprite.Sprite.__init__(self, *groups)
        # Initialisation du score du joueur gauche et droit
        self.scoreL = 0
        self.scoreR = 0
        # Crée un objet avec la font par défaut
        self.font = pg.font.Font(None, 200)
        # La surface (image) à afficher de ce sprite
        self.image = self.font.render(f'{self.scoreL} {self.scoreR}', True, "green")
        # Recupère le rectangle de la surface à afficher
        self.rect = self.image.get_rect()

    def setLoc(self, midtop):
        """ Positionne le score """
        self.loc = midtop
        # Recalcule le rectangle de l'image
        self.rect = self.image.get_rect()
        # Positionne
        self.rect.midtop = midtop

    def add(self, l, r):
        """ Ajoute un point à gauche et/ou à droite """
        self.scoreL += l
        self.scoreR += r
        # Recalcule l'image
        self.image = self.font.render(f'{self.scoreL} {self.scoreR}', True, "green")
        self.rect = self.image.get_rect()
        self.rect.midtop = self.loc