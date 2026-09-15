import os
import pygame as pg
from . import ui_element

UI_BASE_PATH = "images/ui"


class MainMenu:
    def __init__(self, screen_width, screen_height):
        # --- IMAGE DE FOND ---
        self.bg_image = pg.image.load('images/backgroundWellcom.png').convert()
        self.bg_image = pg.transform.scale(self.bg_image, (screen_width, screen_height))

        font_path = os.path.join(UI_BASE_PATH, "Font", "Kenney Future.ttf")
        self.titre_font = pg.font.Font(font_path, 60)
        self.font = pg.font.Font(font_path, 26)

        # Tailles agrandies pour les boutons
        btn_width = 300
        btn_height = 75

        center_x = screen_width // 2 - (btn_width // 2)

        # Chemins des images pour les boutons
        btn_normal = os.path.join(UI_BASE_PATH, "PNG", "Blue", "Default", "button_rectangle_depth_flat.png")
        btn_quit = os.path.join(UI_BASE_PATH, "PNG", "Red", "Default", "button_rectangle_depth_flat.png")

        self.buttons = {
            "start": ui_element.Button(center_x, 250, btn_width, btn_height, "Start Game", self.font, btn_normal),
            "option": ui_element.Button(center_x, 360, btn_width, btn_height, "Options", self.font, btn_normal),
            "credit": ui_element.Button(center_x, 470, btn_width, btn_height, "Credit", self.font, btn_normal),
            "quit": ui_element.Button(center_x, 580, btn_width, btn_height, "Quit", self.font, btn_quit)
        }

    def draw(self, surface):
        # Affichage du fond
        surface.blit(self.bg_image, (0, 0))

        # Affichage du titre et de son ombre
        titre_shadow = self.titre_font.render("ECLIPSOIDE", True, (0, 80, 150))
        surface.blit(titre_shadow, titre_shadow.get_rect(center=(surface.get_width() // 2 + 4, 104)))

        titre = self.titre_font.render("ECLIPSOIDE", True, (255, 255, 255))
        surface.blit(titre, titre.get_rect(center=(surface.get_width() // 2, 100)))

        pg.draw.line(surface, (0, 120, 215), (surface.get_width() // 2 - 200, 150),
                     (surface.get_width() // 2 + 200, 150), 2)

        # Affichage des boutons
        for button in self.buttons.values():
            button.draw(surface)

    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.handle_event(event):
                return name
        return None