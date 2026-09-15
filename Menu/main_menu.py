#Start
#Option
#LeaderBoard?
#Exit

import pygame as pg
from . import ui_element


class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.font = pg.font.SysFont('ComicSans', 20)
        self.titre_font = pg.font.SysFont('ComicSans', 50)

        center_x = screen_height//2 -100

        self.buttons = {
            "start" : ui_element.Button(center_x, 250, 200, 50, "Start Game", self.font),
            "option" : ui_element.Button(center_x , 350 , 200 , 50 , "Options" , self.font),
            "quit" : ui_element.Button(center_x, 450, 200, 50, "Guit", self.font)
        }

    def draw(self, surface):
        surface.fill((10,10,30))
        titre = self.titre_font.render("ECLIPSOIDE",True,(255,244,255))
        surface.blit(titre, titre.get_rect(center = (surface.get_width()//2,120)))

        for button in self.buttons.values():
            button.draw(surface)

    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.handle_event(event):
                return name
        return None

