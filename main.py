#!/usr/bin/env python3
# Pour lancer directement l'exécution à partir du sell si le fichier a les droits d'exécution

# Utilisation de pygame avec un préfixe plus simple
import pygame as pg
# Utilisation de la classe Pong du module pong, sans prefixe
from pong import Pong
from message import Message
from Menu.main_menu import MainMenu as main_menu

# Fonction principale
def main():
    pg.init()
    screen = pg.display.set_mode((1024,768))
    menu = main_menu(1024, 768)

    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running =False
            action = menu.handle_event(event)
            if action =="start":
                print("Lancer le game")
            elif action =="quit":
                running = False

        menu.draw(screen)
        pg.display.flip()

    pg.quit()


# Appel automatiquement la fonction main si pas utilisé comme module
# Laisse la possibilité d'include la fonction main() dans un autre code en tant que module
if __name__ == "__main__":
    main()