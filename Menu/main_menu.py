import os
import sys
import pygame as pg
from . import ui_element

UI_BASE_PATH = "images/ui"


class MainMenu:
    def __init__(self, screen_width, screen_height):
        font_path = os.path.join(UI_BASE_PATH, "Font", "Kenney Future.ttf")
        self.titre_font = pg.font.Font(font_path, 60)
        self.font = pg.font.SysFont('ComicSans', 20)

        center_x = screen_width // 2 - 100

        self.buttons = {
            "start": ui_element.Button(center_x, 250, 200, 50, "Start Game", self.font),
            "option": ui_element.Button(center_x, 350, 200, 50, "Options", self.font),
            "credit": ui_element.Button(center_x, 450, 200, 50, "Credit", self.font),
            "quit": ui_element.Button(center_x, 550, 200, 50, "Quit", self.font)
        }

    def draw(self, surface):
        surface.fill((10, 10, 30))

        titre_shadow = self.titre_font.render("ECLIPSOIDE", True, (0, 80, 150))
        surface.blit(titre_shadow, titre_shadow.get_rect(center=(surface.get_width() // 2 + 4, 104)))

        titre = self.titre_font.render("ECLIPSOIDE", True, (255, 255, 255))
        surface.blit(titre, titre.get_rect(center=(surface.get_width() // 2, 100)))

        pg.draw.line(surface, (0, 120, 215), (surface.get_width() // 2 - 200, 150),
                     (surface.get_width() // 2 + 200, 150), 2)

        for button in self.buttons.values():
            button.draw(surface)

    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.handle_event(event):
                return name
        return None