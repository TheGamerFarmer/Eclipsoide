import os
from xml.etree.ElementTree import tostring

import pygame as pg
from . import ui_element
from .menu_fx import MenuFx
import settings

UI_BASE_PATH = "Eclipsoide/images/ui"

# Même position relative du soleil que sur le menu principal, pour la cohérence
SUN_CENTER_RATIO = (0.5, 0.28)


class MenuLeaderboard:
    def __init__(self, screen_width, screen_height):
        self.scores = None
        self.bg_image = pg.image.load('Eclipsoide/images/backgroundWellcom.png').convert()
        self.bg_image = pg.transform.scale(self.bg_image, (screen_width, screen_height))

        self.fx = MenuFx()
        self.sun_center = (screen_width * SUN_CENTER_RATIO[0], screen_height * SUN_CENTER_RATIO[1])

        font_path = os.path.join(UI_BASE_PATH, "Font", "Kenney Future.ttf")
        self.titre_font = pg.font.Font(font_path, 46)
        self.subtitle_font = pg.font.Font(font_path, 22)
        self.font_bold = pg.font.Font(font_path, 24)
        self.btn_font = pg.font.Font(font_path, 22)

        panel_path = os.path.join(UI_BASE_PATH, "PNG", "Grey", "Default", "button_square_flat.png")
        self.panel_img = pg.image.load(panel_path).convert_alpha()
        self.panel_img = pg.transform.scale(self.panel_img, (700, 480))  # plus étroit, mieux centré
        self.panel_img.set_alpha(210)
        self.panel_rect = self.panel_img.get_rect(center=(screen_width // 2, 400))

        btn_normal = os.path.join(UI_BASE_PATH, "PNG", "Red", "Default", "button_rectangle_depth_flat.png")
        self.btn_back = ui_element.Button(screen_width // 2 - 130, 690, 260, 55, "Retour", self.btn_font,
                                          btn_normal)

    def updatescore(self):
        self.scores = settings.scores()
        self.scores.sort(reverse=True)


    def draw(self, surface):

        self.updatescore()

        surface.blit(self.bg_image, (0, 0))
        self.fx.draw_sun(surface, self.sun_center)

        titre_center = (surface.get_width() // 2, 60)
        self.fx.draw_title_glow(surface, self.titre_font, "Leaderboard", titre_center)
        titre = self.titre_font.render("Leaderboard", True, (255, 255, 255))
        surface.blit(titre, titre.get_rect(center=titre_center))
        pg.draw.line(surface, (0, 120, 215), (surface.get_width() // 2 - 150, 100),
                     (surface.get_width() // 2 + 150, 100), 2)

        surface.blit(self.panel_img, self.panel_rect)

        margin_x = 60
        margin_top = 35
        row_height = 42

        content_center_x = self.panel_rect.centerx
        content_top = self.panel_rect.top + margin_top

        max_rows = (self.panel_rect.height - margin_top - 20) // row_height
        visible_scores = self.scores[:max_rows]

        y = content_top
        for rank, score in enumerate(visible_scores, start=1):
            score_txt = f"{rank}.   {score}"
            match rank:
                case 1:
                    texte_surf = self.font_bold.render(score_txt, True, (255, 215, 0))
                case 2:
                    texte_surf = self.font_bold.render(score_txt, True, (120, 120, 120))
                case 3:
                    texte_surf = self.font_bold.render(score_txt, True, (206, 137, 70))
                case _:
                    texte_surf = self.font_bold.render(score_txt, True, (50, 50, 50))
            text_rect = texte_surf.get_rect(midtop=(content_center_x, y))
            underline_y = y + texte_surf.get_height() + 2
            line_start = (content_center_x - 50, underline_y)
            line_end = (content_center_x + 50, underline_y)
            pg.draw.line(surface, (50, 50, 90), line_start, line_end, 2)
            surface.blit(texte_surf, text_rect)
            y += row_height

        self.btn_back.draw(surface)

    def handle_event(self, event):
        if self.btn_back.handle_event(event):
            return "back"
        return None