# Utilisation de pygame avec un préfixe plus simple
import pygame as pg

# Définition d'une raquette pour jouer à Pong
class Paddle(pg.sprite.Sprite):
    """ Les raquettes du jeux """
    # Variables de classes pour toutes les raquettes
    # Taille largeur, hauteur des raquettes, fixes
    size = (40,80)

    def __init__(self,*groups):
        # Appel du constructeur la super classe
        pg.sprite.Sprite.__init__(self, *groups)
        # Chaque sprite doit avoir son attribut de type Surface.image pour s'afficher
        # et Surface.rect pour se positionner
        # ATTENTION : size ici est un attribut de classe !
        self.image = pg.Surface(Paddle.size)
        # Recupère le rectangle de la surface du Sprite
        self.rect = self.image.get_rect()
        # Donne une couleur à la raquette
        self.image.fill("green")
        # Initialise une vitesse en pixels par millisecondes
        self.speed = 0.8
        # Mouvement : 0 immobile, +1 descend, ou -1 monte
        self.movement = 0

    def setLoc(self,x, min, max):
        """ Definit les positions horizontale en x, et min et max en vertical """
        self.min = min
        self.max = max
        # Change la position horizontal du rectangle qui définit la position
        self.rect.move_ip((x,0))

    def update(self,dt):
        """ Met à jour la position du paddle """
        # Déplace la position de la raquette en fonction du mouvement demandé
        # Calcule le déplacement
        depl = self.speed * self.movement * dt
        # Modifie la position de la raquette
        self.rect.move_ip((0,depl))
        # Regarde si le déplacement est possible et corrige à la position min ou max
        # ATTENTION : on ne maitise pas le nombre de pixels exact du déplacement donc
        # cette manière de calculer permet à la raquette de toujours aller aux valeurs min et max
        if self.rect.top <= self.min:
            self.rect.top = self.min
        if self.rect.bottom >= self.max:
            self.rect.bottom = self.max

    def up(self):
        """ Demande de déplacer la raquette vers le haut """
        self.movement = -1

    def down(self):
        """ Demande de déplacer la raquette vers le bas """
        self.movement = 1

    def stop(self):
        """ Demande de garder la raquette immobile """
        self.movement = 0