import os
import math
import pygame as pg
from shop import Shop

class Hud:
    """ Regroupe l'affichage d'état du joueur et les effets d'écran qui en
    découlent (soleil animé, flashs de dégâts/soin, vignette de vie basse,
    compteur de pièces, coeurs) pour garder Eclipsoide concentré sur la
    logique de jeu plutôt que sur le rendu """

    # Rotation lente + légère pulsation/glow du soleil
    SUN_SIZE = 200
    SUN_ROTATION_SPEED = 0.006  # degrés par milliseconde (~1 tour par minute)
    SUN_PULSE_PERIOD = 3000     # ms pour un cycle complet de pulsation
    SUN_PULSE_AMPLITUDE = 0.035 # variation de taille (+/- 3.5%)
    SUN_GLOW_COLOR = (255, 170, 60)
    SUN_GLOW_LAYERS = 3
    SUN_GLOW_PADDING = 25
    SUN_GLOW_MAX_ALPHA = 55
    SUN_GLOW_PULSE_RADIUS = 10
    SUN_GLOW_PULSE_ALPHA = 20

    # Flash rouge plein écran, bref, au moment exact où un coup est encaissé
    HIT_FLASH_DURATION = 180  # ms
    HIT_FLASH_COLOR = (255, 30, 30)
    HIT_FLASH_MAX_ALPHA = 130

    # Au moment où une vie est récupérée : une aura qui irradie doucement
    # depuis le vaisseau (volontairement différente du flash de dégâts, plus
    # lente et localisée, pour ne pas donner l'impression d'un coup encaissé)
    HEAL_FLASH_DURATION = 500  # ms
    HEAL_FLASH_COLOR = (80, 255, 140)
    HEAL_GLOW_MAX_RADIUS = 150
    HEAL_GLOW_MAX_ALPHA = 150
    HEAL_GLOW_LAYERS = 4

    # Fondu rouge sur les bords quand il ne reste plus qu'un coeur
    LOW_HEALTH_THRESHOLD = 1
    VIGNETTE_COLOR = (200, 0, 0)
    VIGNETTE_PULSE_PERIOD = 700  # ms pour un cycle de pulsation (effet "battement")
    VIGNETTE_MIN_ALPHA = 50
    VIGNETTE_MAX_ALPHA = 140
    # Rayon (proportion de la distance centre -> coin) à partir duquel le
    # fondu commence à apparaître : en dessous, l'écran reste intact
    VIGNETTE_INNER_RATIO = 0.55

    # Petit "pop" (grossit puis revient à la normale) sur le compteur de pièces
    COIN_POP_DURATION = 220  # ms
    COIN_POP_AMPLITUDE = 0.45  # +45% de taille au pic

    def __init__(self, screen: pg.Surface, player):
        self.screen = screen
        self.player = player

        self.sun_image = pg.image.load('images/sun.png')
        self.sun_image = pg.transform.scale(self.sun_image, (self.SUN_SIZE, self.SUN_SIZE))
        self.sun_angle = 0.0
        self.sun_center = (screen.get_width() / 2, self.SUN_SIZE * 0.75)
        # Horloge propre au HUD (pulsations du soleil/vignette) : gelée quand
        # Eclipsoide choisit de ne pas appeler advance() (ex: séquence de mort)
        self.time = 0.0

        self.coin_font = pg.font.Font(os.path.join('images/ui', 'Font', 'Kenney Future.ttf'), 24)
        self.coin_icon = pg.transform.scale(pg.image.load('images/ui/Coins/coin_0.png'), (24, 24))
        self.heart_full_icon = pg.transform.scale(pg.image.load('images/ui/Hearts/heart_full.png'), (22, 22))
        self.heart_empty_icon = pg.transform.scale(pg.image.load('images/ui/Hearts/heart_empty.png'), (22, 22))

        self.vignette_surface = self._build_vignette(self.VIGNETTE_COLOR)

        self.hit_flash_timer = 0
        self.heal_flash_timer = 0
        self.coin_pop_timer = 0

        self.shop = Shop(self.screen, self.player)

    # --- Déclenchement des effets, appelé par Eclipsoide au moment des événements ---

    def trigger_hit_flash(self):
        self.hit_flash_timer = self.HIT_FLASH_DURATION

    def trigger_heal_flash(self):
        self.heal_flash_timer = self.HEAL_FLASH_DURATION

    def trigger_coin_pop(self):
        self.coin_pop_timer = self.COIN_POP_DURATION

    # --- Mise à jour ---

    def update_timers(self, dt):
        """ Décomptes des flashs/pop : toujours appelé, même pendant une pause de gameplay
        (séquence de mort), pour que les effets déjà lancés terminent proprement """
        self.hit_flash_timer = max(0, self.hit_flash_timer - dt)
        self.heal_flash_timer = max(0, self.heal_flash_timer - dt)
        self.coin_pop_timer = max(0, self.coin_pop_timer - dt)

    def advance(self, dt):
        """ Fait avancer l'horloge du soleil (rotation + pulsation) : à n'appeler
        que pendant le gameplay normal, pas pendant une séquence figée """
        self.sun_angle = (self.sun_angle + self.SUN_ROTATION_SPEED * dt) % 360
        self.time += dt

    # --- Rendu ---

    def draw_sun(self):
        """ Dessine le soleil avec une légère rotation continue et une pulsation de taille/glow """
        pulse_wave = math.sin(self.time * (2 * math.pi / self.SUN_PULSE_PERIOD))
        pulse_scale = 1 + self.SUN_PULSE_AMPLITUDE * pulse_wave

        self._draw_sun_glow(pulse_wave)

        rotated_sun = pg.transform.rotozoom(self.sun_image, self.sun_angle, pulse_scale)
        self.screen.blit(rotated_sun, rotated_sun.get_rect(center=self.sun_center))

    def _draw_sun_glow(self, pulse_wave: float):
        base_radius = self.SUN_SIZE / 2
        max_radius = base_radius + self.SUN_GLOW_PADDING + self.SUN_GLOW_PULSE_RADIUS * pulse_wave
        size = int(max_radius * 2)
        glow_surface = pg.Surface((size, size), pg.SRCALPHA)
        glow_center = (size // 2, size // 2)

        for layer in range(self.SUN_GLOW_LAYERS, 0, -1):
            radius = int(max_radius * (layer / self.SUN_GLOW_LAYERS))
            alpha = (self.SUN_GLOW_MAX_ALPHA + self.SUN_GLOW_PULSE_ALPHA * pulse_wave) * (1 - layer / (self.SUN_GLOW_LAYERS + 1))
            alpha = max(0, min(255, int(alpha)))
            layer_surface = pg.Surface((size, size), pg.SRCALPHA)
            pg.draw.circle(layer_surface, (*self.SUN_GLOW_COLOR, alpha), glow_center, radius)
            glow_surface.blit(layer_surface, (0, 0), special_flags=pg.BLEND_RGBA_ADD)

        self.screen.blit(glow_surface, glow_surface.get_rect(center=self.sun_center))

    def _build_vignette(self, color: tuple[int, int, int]) -> pg.Surface:
        """ Construit une fois un dégradé radial rouge, transparent au centre et
        de plus en plus visible vers les bords/coins. Calculé à basse résolution
        (c'est un simple dégradé, pas de détail à préserver) puis lissé en
        l'agrandissant, pour éviter une boucle pixel par pixel sur tout l'écran """
        width, height = self.screen.get_width(), self.screen.get_height()
        small_w, small_h = 80, 60
        small = pg.Surface((small_w, small_h), pg.SRCALPHA)

        cx, cy = small_w / 2, small_h / 2
        max_dist = math.hypot(cx, cy)
        for y in range(small_h):
            for x in range(small_w):
                dist_ratio = math.hypot(x - cx, y - cy) / max_dist
                t = max(0.0, min(1.0, (dist_ratio - self.VIGNETTE_INNER_RATIO) / (1 - self.VIGNETTE_INNER_RATIO)))
                alpha = int(255 * t ** 2)
                small.set_at((x, y), (*color, alpha))

        return pg.transform.smoothscale(small, (width, height))

    def _draw_low_health_vignette(self):
        if self.player.lives > self.LOW_HEALTH_THRESHOLD:
            return

        pulse = (math.sin(self.time * (2 * math.pi / self.VIGNETTE_PULSE_PERIOD)) + 1) / 2
        alpha = int(self.VIGNETTE_MIN_ALPHA + (self.VIGNETTE_MAX_ALPHA - self.VIGNETTE_MIN_ALPHA) * pulse)
        self.vignette_surface.set_alpha(alpha)
        self.screen.blit(self.vignette_surface, (0, 0))

    def _draw_full_screen_flash(self, timer: float, duration: float, color: tuple[int, int, int], max_alpha: int):
        if timer <= 0:
            return

        ratio = timer / duration
        alpha = int(max_alpha * ratio)
        flash = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        flash.fill((*color, alpha))
        self.screen.blit(flash, (0, 0))

    def _draw_heal_glow(self):
        if self.heal_flash_timer <= 0:
            return

        # 0 au déclenchement -> 1 en fin d'effet
        elapsed = 1 - (self.heal_flash_timer / self.HEAL_FLASH_DURATION)
        # L'aura s'étend vite puis ralentit (ease-out) et s'estompe en s'étirant
        radius = int(self.HEAL_GLOW_MAX_RADIUS * math.sin(elapsed * math.pi / 2))
        fade = (1 - elapsed) ** 1.5
        if radius <= 0 or fade <= 0:
            return

        size = radius * 2
        glow_surface = pg.Surface((size, size), pg.SRCALPHA)
        glow_center = (radius, radius)

        for layer in range(self.HEAL_GLOW_LAYERS, 0, -1):
            layer_radius = int(radius * (layer / self.HEAL_GLOW_LAYERS))
            alpha = int(self.HEAL_GLOW_MAX_ALPHA * fade * (1 - layer / (self.HEAL_GLOW_LAYERS + 1)))
            alpha = max(0, min(255, alpha))
            layer_surface = pg.Surface((size, size), pg.SRCALPHA)
            pg.draw.circle(layer_surface, (*self.HEAL_FLASH_COLOR, alpha), glow_center, layer_radius)
            glow_surface.blit(layer_surface, (0, 0), special_flags=pg.BLEND_RGBA_ADD)

        self.screen.blit(glow_surface, glow_surface.get_rect(center=self.player.rect.center))

    def _draw_coin_counter(self):
        icon_rect = self.coin_icon.get_rect(topleft=(10, 10))
        coin_text = self.coin_font.render(str(self.player.coins), True, (255, 220, 80))
        text_rect = coin_text.get_rect(topleft=(40, 10))

        scale = 1.0
        if self.coin_pop_timer > 0:
            elapsed = 1 - (self.coin_pop_timer / self.COIN_POP_DURATION)
            scale = 1 + self.COIN_POP_AMPLITUDE * math.sin(math.pi * elapsed)

        icon_surface = self.coin_icon
        text_surface = coin_text
        if scale != 1.0:
            icon_surface = pg.transform.smoothscale(self.coin_icon, (max(1, int(icon_rect.width * scale)), max(1, int(icon_rect.height * scale))))
            text_surface = pg.transform.smoothscale(coin_text, (max(1, int(text_rect.width * scale)), max(1, int(text_rect.height * scale))))

        self.screen.blit(icon_surface, icon_surface.get_rect(center=icon_rect.center))
        self.screen.blit(text_surface, text_surface.get_rect(center=text_rect.center))

    def _draw_hearts(self):
        for i in range(self.player.MAX_LIVES):
            icon = self.heart_full_icon if i < self.player.lives else self.heart_empty_icon
            self.screen.blit(icon, (10 + i * 26, 44))

    def draw_overlay(self):
        """ Dessine, par-dessus le jeu, les flashs, la vignette de vie basse puis le HUD (pièces/vies) """
        self._draw_full_screen_flash(self.hit_flash_timer, self.HIT_FLASH_DURATION, self.HIT_FLASH_COLOR, self.HIT_FLASH_MAX_ALPHA)
        self._draw_heal_glow()
        self._draw_low_health_vignette()

        self._draw_coin_counter()
        self._draw_hearts()

        self.shop.draw()

    def handle_event(self, event):
        self.shop.handle_event(event)
