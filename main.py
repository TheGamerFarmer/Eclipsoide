#!/usr/bin/env python3
# Pour lancer directement l'exécution à partir du sell si le fichier a les droits d'exécution

import sys

# Utilisation de pygame avec un préfixe plus simple
import pygame as pg

import audio
import settings
from Menu.main_menu import MainMenu as main_menu
from Menu.menu_credit import MenuCredit
from Menu.menu_option import MenuOption
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
        screen = pg.display.set_mode((1024, 768), pg.FULLSCREEN | pg.SCALED)
    else:
        screen = pg.display.set_mode((1024, 768), pg.RESIZABLE | pg.SCALED)

    menu = main_menu(1024, 768)
    options_menu = MenuOption(1024, 768)
    credit_menu = MenuCredit(1024, 768)

    # Initialisation du module de gestion des fonts
    pg.font.init()
    # Donne un nom à la fenêtre
    pg.display.set_caption("Eclipsoïde")

    start_menu = True
    #menu_pause =False
    game_over_running = False
    pause = PauseMenu(1024, 768)
    while True:
        # On s'assure de revenir au menu principal par défaut
        active_menu = menu

        if start_menu:
            audio.play_music(audio.MENU_MUSIC)

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
                    audio.play_music(audio.GAME_MUSIC)

                    # On ne recrée pas la fenêtre ici pour garder une transition ultra-fluide
                    clock = pg.time.Clock()
                    eclipsoide = Eclipsoide(screen)

                elif action == "quit":
                    pg.quit()
                    sys.exit()

                # Menu options
                elif action == "option":
                    active_menu = options_menu
                elif action == "credit":
                    active_menu = credit_menu
                elif action == "back":
                    active_menu = menu
                    audio.apply_settings()

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
            # Pas de pg.event.get() ici : isRunning() consomme déjà la file
            # (QUIT compris). En lire une seconde fois volerait les touches.
            dt = clock.tick(60)

            if Eclipsoide.pause:
                audio.set_paused(True)
                # Le menu affiche le score de la partie en cours
                pause.set_score(eclipsoide.player.coins)
                pause.draw(screen)
                pg.display.flip()
            while Eclipsoide.pause:
                clock.tick(0)
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
                        eclipsoide = Eclipsoide(screen)
                    elif action == "quit":
                        pg.quit()
                        sys.exit()
                    elif action == "menu":
                        start_menu = True
                        Eclipsoide.pause = False
                        eclipsoide.isEnded = True

                    elif action == "option":
                        active_menu = options_menu
                        while active_menu == options_menu:
                            clock.tick(0)
                            for evt in pg.event.get():
                                if evt.type == pg.QUIT:
                                    pg.quit()
                                    sys.exit()
                                sub_action = options_menu.handle_event(evt)
                                if sub_action == "back":
                                    active_menu = pause
                                    audio.apply_settings()
                                # pleine écran
                                elif sub_action == "toggle_fullscreen":
                                    if settings.OPTIONS["fullscreen"]:
                                        screen = pg.display.set_mode((1024, 768), pg.FULLSCREEN | pg.SCALED)
                                    else:
                                        screen = pg.display.set_mode((1024, 768), pg.RESIZABLE | pg.SCALED)
                                active_menu.draw(screen)
                                pg.display.flip()
                        eclipsoide.draw()
                        pause.draw(screen)
                        pg.display.flip()
                    elif event.type == pg.KEYDOWN:
                        # Les deux touches de pause reprennent aussi la partie
                        if event.key in (pg.K_ESCAPE, pg.K_p):
                            Eclipsoide.pause = False
                            eclipsoide.draw()

            # Sortie de pause (reprise, restart ou retour menu)
            audio.set_paused(False)

            # Met à jour le jeu sachant que dt millisecondes se sont écoulées
            eclipsoide.update(dt)

            screen.fill((0, 0, 0))
            eclipsoide.draw()
            pg.display.flip()


        if start_menu == False:
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
                    eclipsoide = Eclipsoide(screen)
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