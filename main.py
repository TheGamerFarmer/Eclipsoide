#!/usr/bin/env python3
# Pour lancer directement l'exécution à partir du sell si le fichier a les droits d'exécution

# Utilisation de pygame avec un préfixe plus simple
import pygame as pg
import sys
import settings
from Menu.menu_option import MenuOption
from Menu.main_menu import MainMenu as main_menu
from Menu.menu_pause import PauseMenu
from eclipsoide import Eclipsoide


# Fonction principale
def main():
    # Chargement des paramètres
    settings.load_settings()

    # Initialisation du package pygame
    pg.init()

    # Mode plein écran initial au démarrage si sauvegardé
    if settings.OPTIONS["fullscreen"]:
        screen = pg.display.set_mode((1024, 768), pg.FULLSCREEN)
    else:
        # On initialise en mode RESIZABLE pour éviter les micro-coupures de fenêtrage
        screen = pg.display.set_mode((1024, 768), pg.RESIZABLE)

    menu = main_menu(1024, 768)
    options_menu = MenuOption(1024, 768)

    # Initialisation du module de gestion des fonts
    pg.font.init()
    # Donne un nom à la fenêtre
    pg.display.set_caption("Eclipsoïde")

    # Ratio du moniteur (ex: 16/9)
    monitor = pg.display.Info()
    aspect_ratio = monitor.current_w / monitor.current_h

    # Résolution fixe du jeu (ratio moniteur)
    GAME_W = 1024
    GAME_H = int(GAME_W / aspect_ratio)
    game_surface = pg.Surface((GAME_W, GAME_H))

    start_menu = True
    menu_pause =False
    pause = PauseMenu(GAME_W, GAME_H)
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
                    eclipsoide = Eclipsoide(game_surface)

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
                        screen = pg.display.set_mode((1024, 768), pg.FULLSCREEN)
                    else:
                        screen = pg.display.set_mode((1024, 768), pg.RESIZABLE)

            # On dessine le menu actif
            active_menu.draw(screen)
            pg.display.flip()

        # Boucle de jeu
        while eclipsoide.isRunning():
            # Limite la vitesse à 60 images max par secondes
            # Calcule le temps réel entre deux images en millisecondes
            dt = clock.tick(60)

            if Eclipsoide.pause:
                menu_pause = True

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            if Eclipsoide.pause:
                pause.draw(screen)
                pg.display.flip()
            while Eclipsoide.pause:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                    action = pause.handle_event(event)
                    if action == "resume":
                        Eclipsoide.pause = False
                        eclipsoide.draw()
                    elif action == "restart":
                        Eclipsoide.pause = False
                        eclipsoide = Eclipsoide(game_surface)
                    elif action == "quit":
                        pg.quit()
                        sys.exit()
                    elif action == "option":
                        active_menu = options_menu
                        options_menu.draw(screen)

                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            Eclipsoide.pause = not Eclipsoide.pause




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