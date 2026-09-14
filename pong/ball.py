# Utilisation de pygame avec un préfixe plus simple
import pygame as pg

# Une balle qui rebondie sur les bords et des paddles
class Ball(pg.sprite.Sprite):
    """ Une balle qui rebondit """
    # Taille largeur, hauteur de la balle
    size = (20,20)

    def __init__(self,*groups):
        # Appel du constructeur la super classe
        pg.sprite.Sprite.__init__(self, *groups)
        # La surface (image) à afficher de ce sprite
        self.image = pg.Surface(self.size)
        # Recupère le rectangle de la surface du Sprite
        self.rect = self.image.get_rect()
        # Donne une couleur
        self.image.fill("blue")
        # Vecteur de mouvement
        self.movement = pg.Vector2(0.5,0.6)

    def setPlayground(self,rect : pg.Rect):
        """ Définit le rectangle de la zone de mouvement de la balle """
        self.playground = rect

    def setL(self,sprite,velocity):
        """ Positionne la balle au centre gauche du sprite,
        et initialise son vecteur vitesse """
        pos = sprite.rect.midleft
        x = pos[0] - self.size[0]
        y = pos[1] - self.size[1]/2
        self.rect.update((x,y),self.size)
        self.movement =  pg.Vector2(velocity)

    def setR(self,sprite,velocity):
        """ Positionne la balle au centre droit du sprite,
         et initialise son vecteur vitesse """
        pos = sprite.rect.midright
        x = pos[0] + self.size[0]
        y = pos[1] + self.size[1]/2
        self.rect.update((x,y),self.size)
        self.movement =  pg.Vector2(velocity)

    def update(self,dt):
        """ Met à jour la position de la balle  """
        # Déplace la position de la raquette en fonction du veteur de mouvement
        # Calcule le vecteur déplacement
        depl = self.movement * dt
        # Modifie la position
        self.rect.move_ip(depl)
        # Calcule les rebonts sur le haut et le bas
        if self.rect.top <= self.playground.top:
            # Rebond du haut
            self.rect.top = self.playground.top
            self.movement.reflect_ip((0,1))
        if self.rect.bottom >= self.playground.bottom:
            # Rebond du bas
            self.rect.bottom = self.playground.bottom
            self.movement.reflect_ip((0,-1))

    def bounce(self, sprite):
        """ La balle rebondit sur le sprite """
        # Simplification du problème : on considère que l'objet a une epaisseur nulle
        # Il suffit alors simplement de savoir si le rebond est sur la gauche ou la droite
        # C'est en fonction de l'orientation du vecteur vitesse par rapport à la vecticale
        # Le produit scalaire calcul le cosinus de l'angle par rapport à la verticale
        orientation = self.movement.dot((0,-1))
        # D'ou vient la balle par rapport au sprite ?
        if orientation > 0:
            # vient de la gauche
            self.movement.reflect_ip((-1,0))
        else:
            # vient de la droite
            self.movement.reflect_ip((1,0))