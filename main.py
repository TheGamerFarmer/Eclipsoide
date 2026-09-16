#!/usr/bin/env python3
# Pour lancer directement l'exécution à partir du sell si le fichier a les droits d'exécution

# Utilisation de pygame avec un préfixe plus simple
import pygame as pg
import sys
import settings
from Menu.menu_option import MenuOption
from Menu.main_menu import MainMenu as main_menu
from eclipsoide import Eclipsoide


# Fonction principale
def main():
    # Chargement des paramètres
    settings.load_settings()

    # Initialisation du package pygame
    pg.init()

    # Mode plein écran initial au démarrage si sauvegardé
    if settings.OPTIONS["fullscreen"]:
        screen = pg.display.set_mode((1024, 768), pg.FULLSCREEN | pg.SCALED)
    else:
        screen = pg.display.set_mode((1024, 768), pg.RESIZABLE | pg.SCALED)

    menu = main_menu(1024, 768)
    options_menu = MenuOption(1024, 768)

    # Initialisation du module de gestion des fonts
    pg.font.init()
    # Donne un nom à la fenêtre
    pg.display.set_caption("Eclipsoïde")

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

                    # On ne recrée pas la fenêtre ici pour garder une transition ultra-fluide
                    clock = pg.time.Clock()
                    eclipsoide = Eclipsoide(screen)

                elif action == "quit":
                    pg.quit()
                    sys.exit()

                # Menu options
                elif action == "option":
                    active_menu = options_menu
                elif action == "back":
                    active_menu = menu

                # pleine écran
                elif action == "toggle_fullscreen":
                    if settings.OPTIONS["fullscreen"]:
                        screen = pg.display.set_mode((1024, 768), pg.FULLSCREEN | pg.SCALED)
                    else:
                        screen = pg.display.set_mode((1024, 768), pg.RESIZABLE | pg.SCALED)

            # On dessine le menu actif
            active_menu.draw(screen)
            pg.display.flip()

        # Boucle de jeu
        while eclipsoide.isRunning():
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            dt = clock.tick(60)
            eclipsoide.update(dt)

            screen.fill((0, 0, 0))
            eclipsoide.draw()
            pg.display.flip()

        game_over_running = True
        while game_over_running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                action = eclipsoide.menu_game_over.handle_event(event)
                if action == "retry":
                    game_over_running = False
                    del eclipsoide
                    eclipsoide = Eclipsoide(game_surface)
                elif action == "menu":
                    start_menu = True
                    game_over_running = False
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