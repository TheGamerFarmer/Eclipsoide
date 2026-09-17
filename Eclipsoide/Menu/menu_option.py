import os
import pygame as pg
from . import ui_element
from .menu_fx import MenuFx, FadeIn
import settings

UI_BASE_PATH = "Eclipsoide/images/ui"

# Même position relative du soleil que sur le menu principal, pour la cohérence
SUN_CENTER_RATIO = (0.5, 0.28)


class MenuOption:
    # Fondu d'entrée, rejoué à chaque fois que ce menu redevient actif
    TRANSITION_DURATION = 400  # ms

    def __init__(self, screen_width, screen_height):
        self.bg_image = pg.image.load('Eclipsoide/images/backgroundWellcom.png').convert()
        self.bg_image = pg.transform.scale(self.bg_image, (screen_width, screen_height))

        self.fx = MenuFx()
        self.fade = FadeIn(self.TRANSITION_DURATION)
        self.sun_center = (screen_width * SUN_CENTER_RATIO[0], screen_height * SUN_CENTER_RATIO[1])

        font_path = os.path.join(UI_BASE_PATH, "Font", "Kenney Future.ttf")
        self.titre_font = pg.font.Font(font_path, 50)
        self.subtitle_font = pg.font.Font(font_path, 28)
        self.font = pg.font.Font(font_path, 20)
        self.keys_font = pg.font.SysFont("arial", 22, bold=True)
        # Certaines touches réassignées ont un nom long (ESPACE, RETURN...) qui
        # ne rentre pas dans les cases 50px prévues pour une lettre unique
        self.keys_font_small = pg.font.SysFont("arial", 13, bold=True)

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
        start_sfx_vol = settings.OPTIONS["sfx_volume"]
        start_music = settings.OPTIONS["music"]
        start_sfx = settings.OPTIONS["sfx"]
        start_fs = settings.OPTIONS["fullscreen"]

        self.slider_volume = ui_element.Slider(140, 300, 300, 0, 100, start_vol, slider_track, slider_handle)
        self.slider_sfx_volume = ui_element.Slider(140, 380, 300, 0, 100, start_sfx_vol, slider_track, slider_handle)
        self.check_music = ui_element.Checkbox(140, 430, "Music", self.font, check_off, check_on, start_music)
        self.check_sfx = ui_element.Checkbox(140, 480, "Sound effects", self.font, check_off, check_on, start_sfx)
        self.check_fullscreen = ui_element.Checkbox(140, 550, "full screen", self.font, check_off, check_on, start_fs)

        # Touche fixe, jamais réassignable (filet de sécurité)
        self.echap_button = ui_element.Button(715, 380, 105, 50, "ECHAP", self.keys_font, key_rect, text_color=(40, 40, 40))

        # Touches réassignables : cliquer dessus puis appuyer sur la nouvelle touche
        self.rebinding_action: str | None = None
        self.key_buttons = {
            "up": ui_element.Button(770, 240, 50, 50, "", self.keys_font, key_square, text_color=(40, 40, 40)),
            "left": ui_element.Button(715, 295, 50, 50, "", self.keys_font, key_square, text_color=(40, 40, 40)),
            "down": ui_element.Button(770, 295, 50, 50, "", self.keys_font, key_square, text_color=(40, 40, 40)),
            "right": ui_element.Button(825, 295, 50, 50, "", self.keys_font, key_square, text_color=(40, 40, 40)),
            # Alignée sur la rangée Q/S/D au-dessus, à côté d'ECHAP
            "pause": ui_element.Button(825, 380, 50, 50, "", self.keys_font, key_square, text_color=(40, 40, 40)),
        }

    def on_shown(self):
        """ À appeler chaque fois que ce menu redevient actif : relance le fondu d'entrée """
        self.fade.on_shown()

    def draw(self, surface):
        self.fade.wrap_draw(surface, self._draw_content)

    def _draw_content(self, surface):
        surface.blit(self.bg_image, (0, 0))
        self.fx.draw_sun(surface, self.sun_center)

        titre_center = (surface.get_width() // 2, 70)
        self.fx.draw_title_glow(surface, self.titre_font, "SETTINGS", titre_center)
        titre = self.titre_font.render("SETTINGS", True, (255, 255, 255))
        surface.blit(titre, titre.get_rect(center=titre_center))
        pg.draw.line(surface, (0, 120, 215), (surface.get_width() // 2 - 150, 110),
                     (surface.get_width() // 2 + 150, 110), 2)

        surface.blit(self.panel_img, self.panel_rect)

        # REGLAGES
        audio_titre = self.subtitle_font.render("Settings", True, (240, 240, 245))
        surface.blit(audio_titre, (140, 180))

        vol_text = self.font.render(f"Music : {int(self.slider_volume.val)}%", True, (255, 255, 255))
        surface.blit(vol_text, (140, 250))
        self.slider_volume.draw(surface)

        sfx_vol_text = self.font.render(f"Sound effects : {int(self.slider_sfx_volume.val)}%", True, (255, 255, 255))
        surface.blit(sfx_vol_text, (140, 350))
        self.slider_sfx_volume.draw(surface)

        self.check_music.draw(surface)
        self.check_sfx.draw(surface)
        # La touche F peut changer le mode en jeu : la case suit l'option réelle
        self.check_fullscreen.is_checked = settings.OPTIONS["fullscreen"]
        self.check_fullscreen.draw(surface)

        # CONTROLES
        ctrl_titre = self.subtitle_font.render("Controls", True, (240, 240, 245))
        surface.blit(ctrl_titre, (630, 180))

        hint_color = (0, 0, 0) if self.rebinding_action else (0, 0, 0)
        hint_text = "Press a key..." if self.rebinding_action else "(click a key to reassign it)"
        hint_surf = pg.font.SysFont("arial", 13, italic=True).render(hint_text, True, hint_color)
        surface.blit(hint_surf, (630, 205))

        surf_dep = self.font.render("Movement :", True, (255, 255, 255))
        surface.blit(surf_dep, (520, 270))

        surf_pause = self.font.render("Pause :", True, (255, 255, 255))
        surface.blit(surf_pause, (520, 395))

        keybinds = settings.OPTIONS["keybinds"]
        for action, key_btn in self.key_buttons.items():
            label = "..." if self.rebinding_action == action else pg.key.name(keybinds[action]).upper()
            key_btn.text = label
            key_btn.font = self.keys_font if len(label) <= 2 else self.keys_font_small
            key_btn.draw(surface)
        self.echap_button.draw(surface)

        self.btn_back.draw(surface)

    def handle_event(self, event):
        # En attente d'une touche pour la réassignation : capture le prochain
        # KEYDOWN et ignore tout le reste (clics, etc.) tant qu'on attend
        if self.rebinding_action is not None:
            if event.type == pg.KEYDOWN:
                if event.key != pg.K_ESCAPE:
                    settings.OPTIONS["keybinds"][self.rebinding_action] = event.key
                    settings.save_settings()
                self.rebinding_action = None
            return None

        self.slider_volume.handle_event(event)
        self.slider_sfx_volume.handle_event(event)
        self.check_music.handle_event(event)
        self.check_sfx.handle_event(event)

        for action, key_btn in self.key_buttons.items():
            if key_btn.handle_event(event):
                self.rebinding_action = action
                return None

        # Plein écran
        if self.check_fullscreen.handle_event(event):
            settings.OPTIONS["fullscreen"] = self.check_fullscreen.is_checked
            settings.save_settings()
            return "toggle_fullscreen"

        if self.btn_back.handle_event(event):
            settings.OPTIONS["volume"] = self.slider_volume.val
            settings.OPTIONS["sfx_volume"] = self.slider_sfx_volume.val
            settings.OPTIONS["music"] = self.check_music.is_checked
            settings.OPTIONS["sfx"] = self.check_sfx.is_checked

            settings.save_settings()
            return "back"

        return None