import os

import pygame as pg
from . import ui_element

UI_BASE_PATH = "images/ui"


class PauseMenu:
    def __init__(self, screen_width, screen_height):
        self.font = pg.font.SysFont('ComicSans', 20)
        self.titre_font = pg.font.SysFont('ComicSans', 50)

        btn_width = 300
        btn_height = 75

        center_x = screen_width // 2 - (btn_width // 2)

        btn_normal = os.path.join(UI_BASE_PATH, "PNG", "Blue", "Default", "button_rectangle_depth_flat.png")
        btn_quit = os.path.join(UI_BASE_PATH, "PNG", "Red", "Default", "button_rectangle_depth_flat.png")

        self.buttons = {
            "resume": ui_element.Button(center_x, 250, btn_width, btn_height, "Resume", self.font, btn_normal),
            "restart": ui_element.Button(center_x, 350, btn_width, btn_height, "Restart", self.font, btn_normal),
            "option": ui_element.Button(center_x, 450, btn_width, btn_height, "Option", self.font, btn_normal),
            "quit": ui_element.Button(center_x, 550, btn_width, btn_height, "Quit", self.font, btn_quit)
        }

    def draw(self, surface):
        overlay = pg.Surface(surface.get_size(), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        titre = self.titre_font.render("PAUSED", True, (255, 244, 255))
        surface.blit(titre, titre.get_rect(center=(surface.get_width() // 2, 120)))

        for button in self.buttons.values():
            button.draw(surface)

    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.handle_event(event):
                return name
        return None