import pygame as pg
from . import ui_element

class GameOver:
    def __init__(self, screen_width, screen_height):
        self.font = pg.font.SysFont('ComicSans', 20)
        self.titre_font = pg.font.SysFont('ComicSans', 50)

        center_x = screen_height // 2 + 4

        self.bg_image = pg.image.load('images/backgroundGameOver.png')
        self.bg_image = pg.transform.scale(self.bg_image, (screen_width, screen_height))

        self.buttons = {
            "retry": ui_element.Button(center_x, 250, 200, 50, "Retry", self.font),
            "menu": ui_element.Button(center_x, 350, 200, 50, "Menu", self.font),
            "quit": ui_element.Button(center_x, 450, 200, 50, "Quit", self.font)
        }

    def draw(self, surface):

        surface.blit(self.bg_image, (0, 0))
        titre = self.titre_font.render("GAME OVER", True, (255, 244, 255))
        surface.blit(titre, titre.get_rect(center=(surface.get_width() // 2 , 120)))

        for button in self.buttons.values():
            button.draw(surface)

    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.handle_event(event):
                return name
        return None