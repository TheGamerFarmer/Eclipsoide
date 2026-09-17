import pygame as pg
from . import ui_element
from .menu_fx import FadeIn
import os

UI_BASE_PATH = "Eclipsoide/images/ui"

class GameOver:
    # Fondu d'entrée, rejoué à chaque fois que l'écran de game over s'affiche
    TRANSITION_DURATION = 500  # ms

    def __init__(self, screen_width, screen_height):
        self.bg_image = pg.image.load('Eclipsoide/images/backgroundGameOver.png').convert()
        self.bg_image = pg.transform.scale(self.bg_image, (screen_width, screen_height))
        self.fade = FadeIn(self.TRANSITION_DURATION)
        font_path = os.path.join(UI_BASE_PATH, "Font", "Kenney Future.ttf")
        self.titre_font = pg.font.Font(font_path, 60)
        self.font = pg.font.Font(font_path, 26)
        self.score_font = pg.font.Font(font_path, 30)

        # Score de la partie et historique, renseignés par le jeu au game over
        self.score = 0
        self.history = []


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

    def set_score(self, score, history=()):
        """ Renseigne le score de la partie et l'historique à afficher """
        self.score = score
        self.history = list(history)

    def on_shown(self):
        """ À appeler chaque fois que cet écran redevient actif : relance le fondu d'entrée """
        self.fade.on_shown()

    def draw(self, surface):
        self.fade.wrap_draw(surface, self._draw_content)

    def _draw_content(self, surface):
        surface.blit(self.bg_image, (0, 0))
        titre = self.titre_font.render("GAME OVER", True, (255, 244, 255))
        surface.blit(titre, titre.get_rect(center=(surface.get_width() // 2, 120)))

        # Score de la partie, juste sous le titre
        score = self.score_font.render(f"Score : {self.score}", True, (255, 220, 80))
        surface.blit(score, score.get_rect(center=(surface.get_width() // 2, 180)))

        # Les 3 parties précédentes, de la plus récente à la plus ancienne
        if self.history:
            resume = "  ·  ".join(str(s) for s in self.history)
            historique = self.font.render(f"Parties precedentes : {resume}", True, (170, 170, 190))
            surface.blit(historique, historique.get_rect(center=(surface.get_width() // 2, 215)))

        for button in self.buttons.values():
            button.draw(surface)

    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.handle_event(event):
                return name
        return None