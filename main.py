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
    pg.display.set_caption("Eclipsoide")

    # Ratio du moniteur (ex: 16/9)
    monitor = pg.display.Info()
    aspect_ratio = monitor.current_w / monitor.current_h

    # Résolution fixe du jeu (ratio moniteur)
    GAME_W = 1024
    GAME_H = int(GAME_W / aspect_ratio)
    game_surface = pg.Surface((GAME_W, GAME_H))

    # Fenêtre redimensionnable, taille initiale = résolution du jeu
    screen = pg.display.set_mode((GAME_W, GAME_H), pg.RESIZABLE)

    # Crée un objet horloge pour gerer le temps entre deux images
    clock = pg.time.Clock()
    # Création d'une instance du jeu, donne la surface de rendu fixe
    eclipsoide = Eclilpsoide(game_surface)

    # Boucle de jeu
    while eclipsoide.isRunning():
        # Limite la vitesse à 60 images max par secondes
        # Calcule le temps réel entre deux images en millisecondes
        dt = clock.tick(60)

        # Met à jour le jeu sachant que dt millisecondes se sont écoulées
        eclipsoide.update(dt)

        # Demande au jeu d'afficher sur la surface de rendu son nouvel état
        eclipsoide.draw()

        # Scale la surface de rendu pour remplir la fenêtre en gardant le ratio
        win_w, win_h = screen.get_size()
        scale_w = win_w
        scale_h = int(win_w / aspect_ratio)
        if scale_h > win_h:
            scale_h = win_h
            scale_w = int(win_h * aspect_ratio)

        scaled = pg.transform.scale(game_surface, (scale_w, scale_h))

        screen.fill((0, 0, 0))
        screen.blit(scaled, ((win_w - scale_w) // 2, (win_h - scale_h) // 2))

        # Bascule le nouvel état de l'écran
        pg.display.flip()

    # Fin utilisation de pygame
    pg.quit()


# Appel automatiquement la fonction main si pas utilisé comme module
# Laisse la possibilité d'include la fonction main() dans un autre code en tant que module
if __name__ == "__main__":
    main()