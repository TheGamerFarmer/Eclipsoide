import pygame as pg
from . import ui_element
import os

UI_BASE_PATH = "images/ui"

class GameOver:
    def __init__(self, screen_width, screen_height):
        self.bg_image = pg.image.load('images/backgroundGameOver.png').convert()
        self.bg_image = pg.transform.scale(self.bg_image, (screen_width, screen_height))
        font_path = os.path.join(UI_BASE_PATH, "Font", "Kenney Future.ttf")
        self.titre_font = pg.font.Font(font_path, 60)
        self.font = pg.font.Font(font_path, 26)


        btn_width = 300
        btn_height = 75

        center_x = screen_width // 2 - (btn_width // 2)

        btn_normal = os.path.join(UI_BASE_PATH, "PNG", "Blue", "Default", "button_rectangle_depth_flat.png")
        btn_quit = os.path.join(UI_BASE_PATH, "PNG", "Red", "Default", "button_rectangle_depth_flat.png")

        self.buttons = {
            "retry": ui_element.Button(center_x, 250, btn_width, btn_height, "Retry", self.font,btn_normal),
            "menu": ui_element.Button(center_x, 350, btn_width, btn_height, "Menu", self.font,btn_normal),
            "quit": ui_element.Button(center_x, 450, btn_width, btn_height, "Quit", self.font,btn_quit)

        }

    def draw(self, surface):

        surface.blit(self.bg_image, (0, 0))
        titre = self.titre_font.render("GAME OVER", True, (255, 244, 255))
        surface.blit(titre, titre.get_rect(center=(surface.get_width() // 2, 120)))

        for button in self.buttons.values():
            button.draw(surface)

    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.handle_event(event):
                return name
        return None