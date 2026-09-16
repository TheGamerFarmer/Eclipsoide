import os
import pygame as pg
from . import ui_element
import settings

UI_BASE_PATH = "images/ui"


class MenuOption:
    def __init__(self, screen_width, screen_height):
        self.bg_image = pg.image.load('images/backgroundWellcom.png').convert()
        self.bg_image = pg.transform.scale(self.bg_image, (screen_width, screen_height))

        font_path = os.path.join(UI_BASE_PATH, "Font", "Kenney Future.ttf")
        self.titre_font = pg.font.Font(font_path, 50)
        self.subtitle_font = pg.font.Font(font_path, 28)
        self.font = pg.font.Font(font_path, 20)
        self.keys_font = pg.font.SysFont("arial", 22, bold=True)

        btn_normal = os.path.join(UI_BASE_PATH, "PNG", "Red", "Default", "button_rectangle_depth_flat.png")
        key_square = os.path.join(UI_BASE_PATH, "PNG", "Grey", "Default", "button_square_depth_flat.png")
        key_rect = os.path.join(UI_BASE_PATH, "PNG", "Grey", "Default", "button_rectangle_depth_flat.png")
        check_off = os.path.join(UI_BASE_PATH, "PNG", "Blue", "Default", "check_square_grey.png")
        check_on = os.path.join(UI_BASE_PATH, "PNG", "Blue", "Default", "check_square_grey_checkmark.png")
        slider_track = os.path.join(UI_BASE_PATH, "PNG", "Blue", "Default", "slide_horizontal_grey.png")
        slider_handle = os.path.join(UI_BASE_PATH, "PNG", "Blue", "Default", "slide_hangle.png")

        # Panneau de fond
        panel_path = os.path.join(UI_BASE_PATH, "PNG", "Grey", "Default", "button_square_flat.png")
        self.panel_img = pg.image.load(panel_path).convert_alpha()
        self.panel_img = pg.transform.scale(self.panel_img, (960, 520))
        self.panel_img.set_alpha(210)
        self.panel_rect = self.panel_img.get_rect(center=(screen_width // 2, 380))

        # Bouton Retour
        self.btn_back = ui_element.Button(screen_width // 2 - 150, 660, 300, 60, "Retour", self.font, btn_normal)

        # Éléments interactifs
        start_vol = settings.OPTIONS["volume"]
        start_music = settings.OPTIONS["music"]
        start_sfx = settings.OPTIONS["sfx"]
        start_fs = settings.OPTIONS["fullscreen"]

        self.slider_volume = ui_element.Slider(140, 350, 300, 0, 100, start_vol, slider_track, slider_handle)
        self.check_music = ui_element.Checkbox(140, 420, "Musique", self.font, check_off, check_on, start_music)
        self.check_sfx = ui_element.Checkbox(140, 480, "Bruitages", self.font, check_off, check_on, start_sfx)
        self.check_fullscreen = ui_element.Checkbox(140, 540, "Plein ecran", self.font, check_off, check_on, start_fs)

        # Touches du clavier
        self.visual_keys = [
            ui_element.Button(770, 240, 50, 50, "Z", self.keys_font, key_square, text_color=(40, 40, 40)),
            ui_element.Button(715, 295, 50, 50, "Q", self.keys_font, key_square, text_color=(40, 40, 40)),
            ui_element.Button(770, 295, 50, 50, "S", self.keys_font, key_square, text_color=(40, 40, 40)),
            ui_element.Button(825, 295, 50, 50, "D", self.keys_font, key_square, text_color=(40, 40, 40)),
            ui_element.Button(715, 380, 160, 50, "ECHAP", self.keys_font, key_rect, text_color=(40, 40, 40))
        ]

    def draw(self, surface):
        surface.blit(self.bg_image, (0, 0))

        titre = self.titre_font.render("OPTIONS", True, (255, 255, 255))
        surface.blit(titre, titre.get_rect(center=(surface.get_width() // 2, 70)))
        pg.draw.line(surface, (0, 120, 215), (surface.get_width() // 2 - 150, 110),
                     (surface.get_width() // 2 + 150, 110), 2)

        surface.blit(self.panel_img, self.panel_rect)

        # REGLAGES
        audio_titre = self.subtitle_font.render("Reglages", True, (240, 240, 245))
        surface.blit(audio_titre, (140, 180))

        vol_text = self.font.render(f"Volume : {int(self.slider_volume.val)}%", True, (255, 255, 255))
        surface.blit(vol_text, (140, 300))

        self.slider_volume.draw(surface)
        self.check_music.draw(surface)
        self.check_sfx.draw(surface)
        self.check_fullscreen.draw(surface)

        # CONTROLES
        ctrl_titre = self.subtitle_font.render("Controles", True, (240, 240, 245))
        surface.blit(ctrl_titre, (630, 180))

        surf_dep = self.font.render("Mouvement :", True, (255, 255, 255))
        surface.blit(surf_dep, (520, 270))

        surf_pause = self.font.render("Pause :", True, (255, 255, 255))
        surface.blit(surf_pause, (520, 395))

        for key_btn in self.visual_keys:
            key_btn.draw(surface)

        self.btn_back.draw(surface)

    def handle_event(self, event):
        self.slider_volume.handle_event(event)
        self.check_music.handle_event(event)
        self.check_sfx.handle_event(event)

        # Plein écran
        if self.check_fullscreen.handle_event(event):
            settings.OPTIONS["fullscreen"] = self.check_fullscreen.is_checked
            settings.save_settings()
            return "toggle_fullscreen"

        if self.btn_back.handle_event(event):
            settings.OPTIONS["volume"] = self.slider_volume.val
            settings.OPTIONS["music"] = self.check_music.is_checked
            settings.OPTIONS["sfx"] = self.check_sfx.is_checked

            settings.save_settings()
            return "back"

        return None