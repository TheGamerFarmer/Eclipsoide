import os

import pygame as pg
from . import ui_element

UI_BASE_PATH = "Eclipsoide/images/ui"


class PauseMenu:
    # Fondu d'entrée, rejoué à chaque nouvelle mise en pause. Contrairement aux
    # écrans de menu classiques, il ne faut pas repartir d'un fond noir : la
    # partie gelée reste visible derrière, seul le panneau de pause s'estompe
    TRANSITION_DURATION = 250  # ms

    def __init__(self, screen_width, screen_height):

        self._shown_at: int | None = None

        font_path = os.path.join(UI_BASE_PATH, "Font", "Kenney Future.ttf")
        self.titre_font = pg.font.Font(font_path, 60)
        self.font = pg.font.Font(font_path, 26)
        self.score_font = pg.font.Font(font_path, 30)

        # Score en cours, renseigné par le jeu à chaque mise en pause
        self.score = 0


        btn_width = 300
        btn_height = 75

        center_x = screen_width // 2 - (btn_width // 2)

        btn_normal = os.path.join(UI_BASE_PATH, "PNG", "Blue", "Default", "button_rectangle_depth_flat.png")
        btn_quit = os.path.join(UI_BASE_PATH, "PNG", "Red", "Default", "button_rectangle_depth_flat.png")

        self.buttons = {
            "resume": ui_element.Button(center_x, 250, btn_width, btn_height, "Resume", self.font, btn_normal),
            "restart": ui_element.Button(center_x, 350, btn_width, btn_height, "Restart", self.font, btn_normal),
            "option": ui_element.Button(center_x, 450, btn_width, btn_height, "Option", self.font, btn_normal),
            "menu": ui_element.Button(center_x, 550, btn_width, btn_height, "Menu", self.font, btn_normal),
            "quit": ui_element.Button(center_x, 650, btn_width, btn_height, "Quit", self.font, btn_quit)
        }

    def set_score(self, score):
        """ Renseigne le score de la partie en cours """
        self.score = score

    def on_shown(self):
        """ À appeler chaque fois que la pause s'active : relance le fondu d'entrée """
        self._shown_at = pg.time.get_ticks()

    def _progress(self) -> float:
        if self._shown_at is None:
            return 1.0
        elapsed = pg.time.get_ticks() - self._shown_at
        if elapsed >= self.TRANSITION_DURATION:
            return 1.0
        return elapsed / self.TRANSITION_DURATION

    def draw(self, surface):
        progress = self._progress()
        if progress >= 1.0:
            self._draw_content(surface)
            return

        # Panneau de pause dessiné sur un tampon transparent puis blitté avec une
        # opacité croissante : la partie gelée reste visible en dessous pendant le fondu
        buffer = pg.Surface(surface.get_size(), pg.SRCALPHA)
        self._draw_content(buffer)
        eased = 1 - (1 - progress) ** 2
        buffer.set_alpha(int(255 * eased))
        surface.blit(buffer, (0, 0))

    def _draw_content(self, surface):
        overlay = pg.Surface(surface.get_size(), pg.SRCALPHA)
        overlay.fill((50, 0, 50, 90))
        surface.blit(overlay, (0, 0))

        titre = self.titre_font.render("PAUSED", True, (255, 244, 255))
        surface.blit(titre, titre.get_rect(center=(surface.get_width() // 2, 80)))

        # Score en cours, juste sous le titre
        score = self.score_font.render(f"SCORE : {self.score}", True, (255, 220, 80))
        surface.blit(score, score.get_rect(center=(surface.get_width() // 2, 190)))

        for button in self.buttons.values():
            button.draw(surface)

    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.handle_event(event):
                return name
        return None