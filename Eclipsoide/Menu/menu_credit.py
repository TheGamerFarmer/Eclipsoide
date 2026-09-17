import os
import pygame as pg
from . import ui_element
from .menu_fx import MenuFx, FadeIn

UI_BASE_PATH = "Eclipsoide/images/ui"

# Même position relative du soleil que sur le menu principal, pour la cohérence
SUN_CENTER_RATIO = (0.5, 0.28)


class MenuCredit:
    # Fondu d'entrée, rejoué à chaque fois que ce menu redevient actif
    TRANSITION_DURATION = 400  # ms

    def __init__(self, screen_width, screen_height):
        # Image de fond
        self.bg_image = pg.image.load('Eclipsoide/images/backgroundWellcom.png').convert()
        self.bg_image = pg.transform.scale(self.bg_image, (screen_width, screen_height))

        self.fx = MenuFx()
        self.fade = FadeIn(self.TRANSITION_DURATION)
        self.sun_center = (screen_width * SUN_CENTER_RATIO[0], screen_height * SUN_CENTER_RATIO[1])

        # Polices
        font_path = os.path.join(UI_BASE_PATH, "Font", "Kenney Future.ttf")
        self.titre_font = pg.font.Font(font_path, 50)
        self.subtitle_font = pg.font.Font(font_path, 28)

        self.font_bold = pg.font.SysFont("arial", 18, bold=True)
        self.font_link = pg.font.SysFont("arial", 15, bold=True)
        self.btn_font = pg.font.Font(font_path, 20)

        # Panneau
        panel_path = os.path.join(UI_BASE_PATH, "PNG", "Grey", "Default", "button_square_flat.png")
        self.panel_img = pg.image.load(panel_path).convert_alpha()
        self.panel_img = pg.transform.scale(self.panel_img, (960, 520))
        self.panel_img.set_alpha(210)
        self.panel_rect = self.panel_img.get_rect(center=(screen_width // 2, 380))

        # Bouton Retour
        btn_normal = os.path.join(UI_BASE_PATH, "PNG", "Red", "Default", "button_rectangle_depth_flat.png")
        self.btn_back = ui_element.Button(screen_width // 2 - 150, 660, 300, 60, "Retour", self.btn_font, btn_normal)

        # Liste des assets
        self.assets = [
            ("UI : kenney", "https://kenney.nl/assets/ui-pack"),
            ("Vaisseau : foozlecc", "https://foozlecc.itch.io/void-main-ship"),
            ("Coins : laredgames", "https://laredgames.itch.io/gems-coins-free"),
            ("Asteroïd : foozlecc", "https://foozlecc.itch.io/void-environment-pack"),
            ("Background : screamingbrainstudios", "https://screamingbrainstudios.itch.io/seamless-space-backgrounds"),
            ("Soleil : grinnch", "https://grinnch.itch.io/pixel-sun"),
            ("Boss : RSL Labs", "https://opengameart.org/content/boss-ships")
        ]

        # liste devs
        self.devs = [
            "DIGNOIRE Erwan",
            "MATHERET Raphael",
            "MISSOUM Romain",
            "ONIONKITON Esdras Florian",
            "PLANQUETTE Romain"
        ]

    def on_shown(self):
        """ À appeler chaque fois que ce menu redevient actif : relance le fondu d'entrée """
        self.fade.on_shown()

    def draw(self, surface):
        self.fade.wrap_draw(surface, self._draw_content)

    def _draw_content(self, surface):
        surface.blit(self.bg_image, (0, 0))
        self.fx.draw_sun(surface, self.sun_center)

        # Titre
        titre_center = (surface.get_width() // 2, 70)
        self.fx.draw_title_glow(surface, self.titre_font, "CREDITS", titre_center)
        titre = self.titre_font.render("CREDITS", True, (255, 255, 255))
        surface.blit(titre, titre.get_rect(center=titre_center))
        pg.draw.line(surface, (0, 120, 215), (surface.get_width() // 2 - 150, 110),
                     (surface.get_width() // 2 + 150, 110), 2)

        surface.blit(self.panel_img, self.panel_rect)

        # section ressource
        asset_title = self.subtitle_font.render("Ressources", True, (240, 240, 245))
        surface.blit(asset_title, (140, 180))

        y_offset = 225
        for nom, lien in self.assets:
            # Nom de l'asset
            surf_nom = self.font_bold.render(nom, True, (255, 255, 255))
            surface.blit(surf_nom, (140, y_offset))

            # Lien
            surf_lien = self.font_link.render(lien, True, (170, 245, 255))
            surface.blit(surf_lien, (155, y_offset + 18))

            y_offset += 42

        # section devs
        dev_title = self.subtitle_font.render("Developpeurs", True, (240, 240, 245))
        surface.blit(dev_title, (630, 180))

        y_offset = 240
        for dev in self.devs:
            texte_surf = self.font_bold.render(dev, True, (255, 255, 255))
            surface.blit(texte_surf, (630, y_offset))
            y_offset += 50

        self.btn_back.draw(surface)

    def handle_event(self, event):
        if self.btn_back.handle_event(event):
            return "back"
        return None