#!/usr/bin/env python3
# Pour lancer directement l'exécution à partir du sell si le fichier a les droits d'exécution

# Utilisation de pygame avec un préfixe plus simple
import pygame as pg
# Utilisation de la classe Pong du module pong, sans prefixe
from eclipsoide import Eclilpsoide

# Fonction principale
def main():
    # Initialisation du package pygame
    pg.init()
    # Initalisation du module de gestion des fonts
    pg.font.init()
    # Donne un nom à la fenêtre
    pg.display.set_caption("PONG")
    # Taille de l'écran
    screenSize = (1024,768)
    # Crée la surface qui va servir de surface de jeu
    screen = pg.display.set_mode(screenSize)
    # Crée un objet horloge pour gerer le temps entre deux images
    clock = pg.time.Clock()
    # Nombre de millisecondes entre deux images
    dt = 0
    # Création d'une instance du jeu, donne l'écran où il faut dessiner
    pong = Eclilpsoide(screen)

    # Boucle de jeu
    while pong.isRunning():
        # Limite la vitesse à 6O images max par secondes
        # Calcule le temps réel entre deux images en millisecondes
        dt = clock.tick(60)

        # Met à jour le jeu sachant que dt millisecondes se sont écoulées
        pong.update(dt)

        # Demande au jeu d'afficher sur l'écran (screen) son nouvel état
        pong.draw()

        # Bascule le nouvel état de l'écran
        pg.display.flip()

    # Attend 4s avant de fermer la fenêtre
    t = 0
    while t < 4000:
        dt = clock.tick(60)
        t += dt

    # Fin utilisation de pygame
    pg.quit()


# Appel automatiquement la fonction main si pas utilisé comme module
# Laisse la possibilité d'include la fonction main() dans un autre code en tant que module
if __name__ == "__main__":
    main()