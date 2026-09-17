import os
import pygame as pg
from . import ui_element
from .menu_fx import MenuFx

UI_BASE_PATH = "images/ui"


class MainMenu:
    SUN_CENTER = (0.5, 0.28)  # proportion de la largeur/hauteur de l'écran

    # Fondu d'entrée, rejoué à chaque retour sur ce menu
    TRANSITION_DURATION = 600  # ms

    def __init__(self, screen_width, screen_height):
        self.bg_image = pg.image.load('images/backgroundWellcom.png').convert()
        self.bg_image = pg.transform.scale(self.bg_image, (screen_width, screen_height))

        self.fx = MenuFx()
        self.sun_center = (screen_width * self.SUN_CENTER[0], screen_height * self.SUN_CENTER[1])

        font_path = os.path.join(UI_BASE_PATH, "Font", "Kenney Future.ttf")
        self.titre_font = pg.font.Font(font_path, 60)
        self.font = pg.font.Font(font_path, 26)

        btn_width = 300
        btn_height = 75

        center_x = screen_width // 2 - (btn_width // 2)

        # Chemins des images pour les boutons
        btn_normal = os.path.join(UI_BASE_PATH, "PNG", "Blue", "Default", "button_rectangle_depth_flat.png")
        btn_quit = os.path.join(UI_BASE_PATH, "PNG", "Red", "Default", "button_rectangle_depth_flat.png")

        self.buttons = {
            "start": ui_element.Button(center_x, 200, btn_width, btn_height, "Start Game", self.font, btn_normal),
            "option": ui_element.Button(center_x, 310, btn_width, btn_height, "Options", self.font, btn_normal),
            "credit": ui_element.Button(center_x, 420, btn_width, btn_height, "Credit", self.font, btn_normal),
            "leaderboard": ui_element.Button(center_x, 530, btn_width, btn_height, "Leaderboard", self.font, btn_normal),
            "quit": ui_element.Button(center_x, 640, btn_width, btn_height, "Quit", self.font, btn_quit)
        }

        self._shown_at = None

    def on_shown(self):
        """ À appeler chaque fois que ce menu redevient actif : relance le fondu d'entrée """
        self._shown_at = pg.time.get_ticks()

    def _transition_progress(self) -> float:
        """ 0 à l'arrivée -> 1 une fois le fondu terminé (ou si jamais déclenché) """
        if self._shown_at is None:
            return 1.0
        elapsed = pg.time.get_ticks() - self._shown_at
        if elapsed >= self.TRANSITION_DURATION:
            return 1.0
        return elapsed / self.TRANSITION_DURATION

    def draw(self, surface):
        progress = self._transition_progress()

        if progress >= 1.0:
            self._draw_content(surface)
            return

        # Fondu d'entrée : le contenu est dessiné sur un tampon puis blitté
        # avec une opacité croissante (ease-out)
        buffer = pg.Surface(surface.get_size())
        self._draw_content(buffer)
        eased = 1 - (1 - progress) ** 2
        buffer.set_alpha(int(255 * eased))
        surface.fill((0, 0, 0))
        surface.blit(buffer, (0, 0))

    def _draw_content(self, surface):
        # Affichage du fond
        surface.blit(self.bg_image, (0, 0))

        self.fx.draw_sun(surface, self.sun_center)
        self._draw_title(surface)

        # Affichage des boutons
        for button in self.buttons.values():
            button.draw(surface)

    def _draw_title(self, surface):
        center_x = surface.get_width() // 2
        center = (center_x, 100)

        self.fx.draw_title_glow(surface, self.titre_font, "ECLIPSOÏDE", center)

        # Titre net + ombre, par-dessus la lueur
        titre_shadow = self.titre_font.render("ECLIPSOÏDE", True, (0, 80, 150))
        surface.blit(titre_shadow, titre_shadow.get_rect(center=(center_x + 4, 104)))

        titre = self.titre_font.render("ECLIPSOÏDE", True, (255, 255, 255))
        surface.blit(titre, titre.get_rect(center=center))

        pg.draw.line(surface, (0, 120, 215), (center_x - 200, 150), (center_x + 200, 150), 2)

    def handle_event(self, event):
        for name, button in self.buttons.items():
            if button.handle_event(event):
                return name
        return None
