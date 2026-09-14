# Utilisation de pygame avec un préfixe plus simple
import pygame as pg


class Message():
    """ Affichage d'un message au centre de l'écran """

    def __init__(self, screen):
        # Crée un objet avec la font par défaut
        self.font = pg.font.Font(None, 100)
        # Conserve la surface où afficher
        self.screen = screen

    def print(self, message):
        """ Affiche le message au centre """
        # Calcule l'image à afficher
        image = self.font.render(f'{message}', True, "green")
        # La position où l'afficher
        rect = image.get_rect()
        # Force la position au centre de l'écran
        rect.center = (self.screen.get_width() / 2, self.screen.get_height() / 2)
        # Finalement affiche le message sur la surface
        self.screen.blit(image, rect)