#!/usr/bin/env python3
# Pour lancer directement l'exécution à partir du sell si le fichier a les droits d'exécution

import pygame as pg
import sys

import settings
from Menu.menu_option import MenuOption

from Menu.main_menu import MainMenu as main_menu
from eclipsoide import Eclipsoide
from player import Player

# Fonction principale
def main():
    # Chargement des paramètres
    settings.load_settings()

    # Initialisation du package pygame
    pg.init()

    # mode pleine écran
    if settings.OPTIONS["fullscreen"]:
        screen = pg.display.set_mode((1024, 768), pg.FULLSCREEN)
    else:
        screen = pg.display.set_mode((1024, 768))

    menu = main_menu(1024, 768)
    options_menu = MenuOption(1024, 768)

    # Initalisation du module de gestion des fonts
    pg.font.init()
    # Donne un nom à la fenêtre
    pg.display.set_caption("ECLIPSOIDE")

    # Ratio du moniteur (ex: 16/9)
    monitor = pg.display.Info()
    aspect_ratio = monitor.current_w / monitor.current_h

    # Résolution fixe du jeu (ratio moniteur)
    GAME_W = 1024
    GAME_H = int(GAME_W / aspect_ratio)
    game_surface = pg.Surface((GAME_W, GAME_H))

    start_menu = True

    while True:
        # On s'assure de revenir au menu principal par défaut
        active_menu = menu

        while start_menu:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()  # Fermeture propre

                # On utilise active_menu pour gérer les événements
                action = active_menu.handle_event(event)

                if action == "start":
                    print("Lancer le game")
                    start_menu = False

                    # Application du plein écran au lancement du jeu
                    if settings.OPTIONS["fullscreen"]:
                        screen = pg.display.set_mode((GAME_W, GAME_H), pg.FULLSCREEN)
                    else:
                        screen = pg.display.set_mode((GAME_W, GAME_H), pg.RESIZABLE)

                    clock = pg.time.Clock()
                    eclipsoide = Eclipsoide(game_surface)

                elif action == "quit":
                    pg.quit()
                    sys.exit()

                # menu option
                elif action == "option":
                    active_menu = options_menu
                elif action == "back":
                    active_menu = menu

                # Bascule instantanée du plein écran
                elif action == "toggle_fullscreen":
                    if settings.OPTIONS["fullscreen"]:
                        screen = pg.display.set_mode((1024, 768), pg.FULLSCREEN)
                    else:
                        screen = pg.display.set_mode((1024, 768))

            # On dessine le menu actif
            active_menu.draw(screen)
            pg.display.flip()

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

        game_over_running = True
        while game_over_running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                action = eclipsoide.menu_game_over.handle_event(event)

                if action == "retry":
                    eclipsoide.isEnded = False
                    eclipsoide.player.is_alive = True
                    game_over_running = False
                    eclipsoide = Eclipsoide(game_surface)

                elif action == "menu":
                    start_menu = True
                    game_over_running = False

                    # --- RETOUR AU PLEIN ÉCRAN OU FENÊTRÉ (MENU) ---
                    if settings.OPTIONS["fullscreen"]:
                        screen = pg.display.set_mode((1024, 768), pg.FULLSCREEN)
                    else:
                        screen = pg.display.set_mode((1024, 768))

                elif action == "quit":
                    pg.quit()
                    sys.exit()

            screen.fill((0, 0, 0))
            eclipsoide.menu_game_over.draw(screen)
            pg.display.flip()


# Appel automatiquement la fonction main si pas utilisé comme module
# Laisse la possibilité d'include la fonction main() dans un autre code en tant que module
if __name__ == "__main__":
    main()