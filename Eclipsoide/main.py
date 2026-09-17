#!/usr/bin/env python3
# Pour lancer directement l'exécution à partir du sell si le fichier a les droits d'exécution
# Utilisation de pygame avec un préfixe plus simple
import gc
import os
import pygame as pg
import sys

# Les ressources sont référencées depuis la racine du projet (ex: 'Eclipsoide/images/...'),
# on s'y place pour que le jeu se lance quel que soit le répertoire courant
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import audio
import settings
from Menu.main_menu import MainMenu as main_menu
from Menu.menu_credit import MenuCredit
from Menu.menu_leaderboard import MenuLeaderboard
from Menu.menu_option import MenuOption
from Menu.menu_pause import PauseMenu
from eclipsoide import Eclipsoide

# Fondu depuis le noir au tout début d'une partie (nouvelle ou relancée),
# symétrique au fondu vers le noir déjà en place à la mort du joueur
GAME_START_FADE_DURATION = 400  # ms


def draw_start_fade(screen, start_time):
    if start_time is None:
        return
    elapsed = pg.time.get_ticks() - start_time
    if elapsed >= GAME_START_FADE_DURATION:
        return
    alpha = 255 - int(255 * (elapsed / GAME_START_FADE_DURATION))
    overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    screen.blit(overlay, (0, 0))


# Fonction principale
def main():
    # Chargement des paramètres
    settings.load_settings()

    # Initialisation du package pygame
    pg.init()
    # Mode plein écran initial au démarrage si sauvegardé
    screen = settings.apply_display_mode()

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
    leaderboard = MenuLeaderboard(1024, 768)
    game_start_time = None
    while True:
        # On s'assure de revenir au menu principal par défaut
        active_menu = menu
        # Rejoue le fondu d'entrée à chaque retour sur le menu principal
        # (lancement du jeu, ou retour depuis une partie)
        menu.on_shown()

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
                    game_start_time = pg.time.get_ticks()

                elif action == "quit":
                    pg.quit()
                    sys.exit()

                # Menu options
                elif action == "option":
                    active_menu = options_menu
                    options_menu.on_shown()
                elif action == "credit":
                    active_menu = credit_menu
                    credit_menu.on_shown()
                elif action == "leaderboard":
                    active_menu = leaderboard
                    leaderboard.on_shown()
                elif action == "back":
                    active_menu = menu
                    audio.apply_settings()

                # pleine écran
                elif action == "toggle_fullscreen":
                    screen = settings.apply_display_mode()

            # On dessine le menu actif
            active_menu.draw(screen)
            pg.display.flip()

        # Boucle de jeu
        while eclipsoide.isRunning():
            # Pas de pg.event.get() ici : isRunning() consomme déjà la file
            # (QUIT compris). En lire une seconde fois volerait les touches.
            dt = min(clock.tick(60), 100)

            if eclipsoide.pause:
                audio.set_paused(True)
                # Le menu affiche le score de la partie en cours, et rejoue son
                # fondu d'entrée à chaque nouvelle mise en pause
                pause.set_score(eclipsoide.player.score)
                pause.on_shown()
                pause.draw(screen)
                pg.display.flip()
            while eclipsoide.pause:
                clock.tick(0)
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                    action = pause.handle_event(event)
                    if action == "resume":
                        eclipsoide.pause = False
                        eclipsoide.hud.trigger_resume_flash()
                        eclipsoide.draw()
                    elif action == "restart":
                        eclipsoide.pause = False
                        killed = sum(len(g) for g in eclipsoide.datas.groups)
                        print(f"[RESTART-pause] {killed} sprites à tuer")
                        for group in eclipsoide.datas.groups:
                            for sprite in list(group.sprites()):
                                sprite.kill()
                            group.empty()
                        clock = pg.time.Clock()
                        gc.collect()
                        eclipsoide = Eclipsoide(screen)
                        game_start_time = pg.time.get_ticks()
                        print("[RESTART-pause] Nouvelle partie OK")
                    elif action == "quit":
                        pg.quit()
                        sys.exit()
                    elif action == "menu":
                        start_menu = True
                        eclipsoide.pause = False
                        eclipsoide.isEnded = True

                    elif action == "option":
                        active_menu = options_menu
                        options_menu.on_shown()
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
                                    screen = settings.apply_display_mode()
                                active_menu.draw(screen)
                                pg.display.flip()
                        eclipsoide.draw()
                        pause.draw(screen)
                        pg.display.flip()
                    elif event.type == pg.KEYDOWN:
                        # Échap marche toujours ; l'autre touche est réassignable dans les options
                        if event.key in (pg.K_ESCAPE, settings.OPTIONS["keybinds"]["pause"]):
                            eclipsoide.pause = False
                            eclipsoide.hud.trigger_resume_flash()
                            eclipsoide.draw()

                # Redessine à chaque tick (pas seulement après une action) pour
                # que le fondu d'entrée de la pause ait le temps de s'animer
                if eclipsoide.pause:
                    pause.draw(screen)
                    pg.display.flip()

            # Sortie de pause (reprise, restart ou retour menu)
            audio.set_paused(False)

            # Met à jour le jeu sachant que dt millisecondes se sont écoulées
            eclipsoide.update(dt)

            screen.fill((0, 0, 0))
            eclipsoide.draw()
            draw_start_fade(screen, game_start_time)
            pg.display.flip()


        if start_menu == False:
            game_over_running = True
            eclipsoide.menu_game_over.on_shown()
        while game_over_running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                action = eclipsoide.menu_game_over.handle_event(event)
                if action == "retry":
                    game_over_running = False
                    killed = sum(len(g) for g in eclipsoide.datas.groups)
                    print(f"[RETRY] {killed} sprites à tuer")
                    for group in eclipsoide.datas.groups:
                        for sprite in list(group.sprites()):
                            sprite.kill()
                        group.empty()
                    del eclipsoide
                    clock = pg.time.Clock()
                    gc.collect()
                    eclipsoide = Eclipsoide(screen)
                    game_start_time = pg.time.get_ticks()
                    print("[RETRY] Nouvelle partie OK")
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