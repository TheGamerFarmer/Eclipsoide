import os
import math
import random
import pygame as pg
from shop import Shop

import settings

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

    # Record affiché sous le compteur : gris tant qu'il n'est pas battu, vert ensuite
    RECORD_COLOR = (200, 200, 210)
    RECORD_BEATEN_COLOR = (80, 255, 140)
    SCORE_Y = 40
    RECORD_Y = 60

    # Célébration jouée une seule fois, à l'instant précis où le score dépasse
    # le record : gerbe de particules dorées depuis le vaisseau + texte bref
    RECORD_CELEBRATION_DURATION = 900  # ms
    RECORD_CELEBRATION_PARTICLE_COUNT = 14
    RECORD_CELEBRATION_COLOR = (255, 215, 90)
    RECORD_CELEBRATION_TEXT_COLOR = (255, 230, 120)
    RECORD_CELEBRATION_SPEED_MIN = 0.05  # pixels/ms
    RECORD_CELEBRATION_SPEED_MAX = 0.20
    HEARTS_Y = 84
    # Fond arrondi derrière chaque coeur, pour que les emplacements vides
    # (juste un contour fin) restent visibles sur un fond d'écran chargé
    HEART_BG_COLOR = (255, 255, 255, 140)
    HEART_BG_PADDING = 3
    HEART_BG_RADIUS = 6
    # Animation du bouclier (images/shield/) autour du vaisseau tant qu'il est
    # actif, avec un pic de taille bref quand un coup est bloqué et un
    # clignotement d'avertissement juste avant qu'il ne s'éteigne
    SHIELD_FRAME_COUNT = 12
    SHIELD_SIZE = (56, 56)
    SHIELD_FRAME_DELAY = 45  # ms entre deux frames de l'animation
    SHIELD_PULSE_DURATION = 250  # ms
    SHIELD_PULSE_SCALE = 0.25  # +25% de taille au pic
    SHIELD_WARNING_THRESHOLD = 1200  # ms restantes à partir desquelles ça clignote
    SHIELD_WARNING_BLINK_INTERVAL = 120  # ms entre chaque clignotement

    # Tremblement d'écran pour les gros moments (mort du boss) : amplitude qui
    # décroît linéairement jusqu'à la fin de la durée
    SHAKE_DURATION = 500     # ms
    SHAKE_MAGNITUDE = 16     # px, amplitude max au tout début

    # Choc de caméra (zoom-in bref) à l'apparition du boss : décroît comme le
    # tremblement, combiné à un petit tremblement plus court pour le "poids" de l'impact
    ZOOM_PUNCH_DURATION = 450    # ms
    ZOOM_PUNCH_MAGNITUDE = 0.10  # +10% de zoom au pic
    BOSS_SPAWN_SHAKE_DURATION = 200
    BOSS_SPAWN_SHAKE_MAGNITUDE = 5

    # Compteurs (pièces/score) qui "roulent" jusqu'à la valeur cible au lieu de
    # sauter instantanément : vitesse proportionnelle à l'écart restant, avec un
    # minimum pour ne jamais traîner indéfiniment sur un petit delta
    COUNTER_CATCHUP_SPEED = 0.006  # fraction de l'écart comblée par ms
    COUNTER_MIN_STEP = 1            # points par frame au minimum tant que la cible n'est pas atteinte

    # Bannière "NIVEAU X" affichée brièvement au centre de l'écran quand un
    # palier de boss est vaincu et que le suivant démarre
    LEVEL_BANNER_DURATION = 2200  # ms
    LEVEL_BANNER_FADE_IN = 300    # ms
    LEVEL_BANNER_FADE_OUT = 600   # ms, décomptées depuis la fin
    LEVEL_BANNER_COLOR = (255, 220, 80)

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
        self.record_font = pg.font.Font(os.path.join('images/ui', 'Font', 'Kenney Future.ttf'), 14)
        self.level_banner_font = pg.font.Font(os.path.join('images/ui', 'Font', 'Kenney Future.ttf'), 56)
        self.record_celebration_font = pg.font.Font(os.path.join('images/ui', 'Font', 'Kenney Future.ttf'), 30)
        # Record figé au lancement de la partie : c'est lui que le joueur cherche à battre
        self.record = settings.best_score()
        # Valeurs affichées, qui rattrapent progressivement les vraies valeurs du joueur
        self.displayed_score = player.score
        self.displayed_coins = player.coins
        self.coin_icon = pg.transform.scale(pg.image.load('images/ui/Coins/coin_0.png'), (24, 24))
        self.heart_full_icon = pg.transform.scale(pg.image.load('images/ui/Hearts/heart_full.png'), (22, 22))
        self.heart_empty_icon = pg.transform.scale(pg.image.load('images/ui/Hearts/heart_empty.png'), (22, 22))
        self.shield_images = [
            pg.transform.scale(pg.image.load(f'images/shield/shield_{i}.png'), self.SHIELD_SIZE)
            for i in range(self.SHIELD_FRAME_COUNT)
        ]

        self.vignette_surface = self._build_vignette(self.VIGNETTE_COLOR)

        self.hit_flash_timer = 0
        self.heal_flash_timer = 0
        self.coin_pop_timer = 0
        self.shield_pulse_timer = 0
        self.shake_timer = 0
        self.shake_duration = self.SHAKE_DURATION
        self.shake_magnitude = self.SHAKE_MAGNITUDE
        self.zoom_timer = 0
        self.zoom_duration = self.ZOOM_PUNCH_DURATION
        self.zoom_magnitude = self.ZOOM_PUNCH_MAGNITUDE
        self.level_banner_timer = 0
        self.level_banner_stage = 1
        self.record_beaten_announced = False
        self.record_celebration_timer = 0
        self.record_celebration_particles: list[tuple[float, float]] = []

        self.shop = Shop(self.screen, self.player)

    # Déclenchement des effets, appelé par Eclipsoide au moment des événements

    def trigger_hit_flash(self):
        self.hit_flash_timer = self.HIT_FLASH_DURATION

    def trigger_heal_flash(self):
        self.heal_flash_timer = self.HEAL_FLASH_DURATION

    def trigger_coin_pop(self):
        self.coin_pop_timer = self.COIN_POP_DURATION

    def trigger_shield_pulse(self):
        self.shield_pulse_timer = self.SHIELD_PULSE_DURATION

    def trigger_shake(self, duration: float = None, magnitude: float = None):
        self.shake_duration = duration if duration is not None else self.SHAKE_DURATION
        self.shake_timer = self.shake_duration
        self.shake_magnitude = magnitude if magnitude is not None else self.SHAKE_MAGNITUDE

    def trigger_zoom_punch(self, duration: float = None, magnitude: float = None):
        self.zoom_duration = duration if duration is not None else self.ZOOM_PUNCH_DURATION
        self.zoom_timer = self.zoom_duration
        self.zoom_magnitude = magnitude if magnitude is not None else self.ZOOM_PUNCH_MAGNITUDE

    def trigger_level_banner(self, stage: int):
        self.level_banner_timer = self.LEVEL_BANNER_DURATION
        self.level_banner_stage = stage

    def _trigger_record_celebration(self):
        self.record_celebration_timer = self.RECORD_CELEBRATION_DURATION
        self.record_celebration_particles = [
            (random.uniform(0, 2 * math.pi), random.uniform(self.RECORD_CELEBRATION_SPEED_MIN, self.RECORD_CELEBRATION_SPEED_MAX))
            for _ in range(self.RECORD_CELEBRATION_PARTICLE_COUNT)
        ]

    # Mise à jour

    def update_timers(self, dt):
        """ Décomptes des flashs/pop : toujours appelé, même pendant une pause de gameplay
        (séquence de mort), pour que les effets déjà lancés terminent proprement """
        self.hit_flash_timer = max(0, self.hit_flash_timer - dt)
        self.heal_flash_timer = max(0, self.heal_flash_timer - dt)
        self.coin_pop_timer = max(0, self.coin_pop_timer - dt)
        self.shield_pulse_timer = max(0, self.shield_pulse_timer - dt)
        self.shake_timer = max(0, self.shake_timer - dt)
        self.zoom_timer = max(0, self.zoom_timer - dt)
        self.level_banner_timer = max(0, self.level_banner_timer - dt)
        self.record_celebration_timer = max(0, self.record_celebration_timer - dt)

        # Déclenché une seule fois par partie, pile à l'instant où le score
        # dépasse le record (figé au lancement de la partie)
        if not self.record_beaten_announced and self.player.score > self.record:
            self.record_beaten_announced = True
            self._trigger_record_celebration()

        self._advance_counters(dt)

    def _advance_counter(self, current: int, target: int, dt: float) -> int:
        """ Rapproche current de target : vitesse proportionnelle à l'écart
        restant (ralentit en approchant), avec un minimum d'1 point/frame """
        if current == target:
            return target
        diff = target - current
        step = diff * self.COUNTER_CATCHUP_SPEED * dt
        if abs(step) < self.COUNTER_MIN_STEP:
            step = self.COUNTER_MIN_STEP if diff > 0 else -self.COUNTER_MIN_STEP
        if abs(step) >= abs(diff):
            return target
        return current + int(step)

    def _advance_counters(self, dt):
        self.displayed_score = self._advance_counter(self.displayed_score, self.player.score, dt)
        self.displayed_coins = self._advance_counter(self.displayed_coins, self.player.coins, dt)

    def get_shake_offset(self) -> tuple[int, int]:
        """ Décalage aléatoire à appliquer au rendu, amplitude qui décroît
        linéairement jusqu'à la fin du tremblement """
        if self.shake_timer <= 0:
            return 0, 0
        magnitude = self.shake_magnitude * (self.shake_timer / self.shake_duration)
        return int(random.uniform(-magnitude, magnitude)), int(random.uniform(-magnitude, magnitude))

    def get_zoom_scale(self) -> float:
        """ Échelle à appliquer au rendu, >1 juste après le déclenchement puis
        qui redescend linéairement à 1 (zoom-in bref, façon "impact caméra") """
        if self.zoom_timer <= 0:
            return 1.0
        return 1.0 + self.zoom_magnitude * (self.zoom_timer / self.zoom_duration)

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
        if self.player.lives > self.LOW_HEALTH_THRESHOLD or self.player.max_lives <= 1:
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

    def draw_shield(self):
        """ Anime le bouclier (images/shield/) autour du vaisseau tant qu'il est
        actif : grossit brièvement quand un coup est bloqué, clignote juste avant
        de s'éteindre. À dessiner par-dessus le vaisseau, pas dans l'overlay HUD """
        if self.player.shield_timer <= 0:
            return

        frame_index = int(self.time / self.SHIELD_FRAME_DELAY) % self.SHIELD_FRAME_COUNT
        frame = self.shield_images[frame_index]

        pulse = self.shield_pulse_timer / self.SHIELD_PULSE_DURATION if self.shield_pulse_timer > 0 else 0
        scale = 1 + self.SHIELD_PULSE_SCALE * pulse
        if scale != 1.0:
            size = (max(1, int(self.SHIELD_SIZE[0] * scale)), max(1, int(self.SHIELD_SIZE[1] * scale)))
            frame = pg.transform.smoothscale(frame, size)

        if self.player.shield_timer <= self.SHIELD_WARNING_THRESHOLD:
            blinking_off = (int(self.player.shield_timer) // self.SHIELD_WARNING_BLINK_INTERVAL) % 2 == 0
            if blinking_off:
                frame = frame.copy()
                frame.set_alpha(90)

        self.screen.blit(frame, frame.get_rect(center=self.player.rect.center))

    def _draw_coin_counter(self):
        icon_rect = self.coin_icon.get_rect(topleft=(10, 10))
        coin_text = self.coin_font.render(str(self.displayed_coins), True, (255, 220, 80))
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

    def _draw_record(self):
        beaten = self.player.score > self.record
        color = self.RECORD_BEATEN_COLOR if beaten else self.RECORD_COLOR
        if beaten:
            record_text = self.record_font.render(f"RECORD : {self.displayed_score}", True, color)
        else:
            record_text = self.record_font.render(f"RECORD : {self.record}", True, color)
        self.screen.blit(record_text, (10, self.RECORD_Y))

    def _draw_score(self):
        color = self.RECORD_BEATEN_COLOR
        score_text = self.record_font.render(f"SCORE : {self.displayed_score}", True, color)
        self.screen.blit(score_text, (10, self.SCORE_Y))

    def _draw_hearts(self):
        icon_w, icon_h = self.heart_full_icon.get_size()

        # Un seul fond qui s'étire pour couvrir tous les emplacements de coeurs,
        # plutôt qu'un fond répété derrière chacun
        span_w = (self.player.max_lives - 1) * 26 + icon_w
        bg_size = (span_w + self.HEART_BG_PADDING * 2, icon_h + self.HEART_BG_PADDING * 2)
        bg_surface = pg.Surface(bg_size, pg.SRCALPHA)
        pg.draw.rect(bg_surface, self.HEART_BG_COLOR, bg_surface.get_rect(), border_radius=self.HEART_BG_RADIUS)
        self.screen.blit(bg_surface, (10 - self.HEART_BG_PADDING, self.HEARTS_Y - self.HEART_BG_PADDING))

        for i in range(self.player.max_lives):
            x = 10 + i * 26
            icon = self.heart_full_icon if i < self.player.lives else self.heart_empty_icon
            self.screen.blit(icon, (x, self.HEARTS_Y))

            icon = self.heart_full_icon if i < self.player.lives else self.heart_empty_icon
            self.screen.blit(icon, (x, self.HEARTS_Y))

    def draw_overlay(self):
        """ Dessine, par-dessus le jeu, les flashs, la vignette de vie basse puis le HUD (pièces/vies) """
        self._draw_full_screen_flash(self.hit_flash_timer, self.HIT_FLASH_DURATION, self.HIT_FLASH_COLOR, self.HIT_FLASH_MAX_ALPHA)
        self._draw_heal_glow()
        self._draw_low_health_vignette()

        self._draw_coin_counter()
        self._draw_record()
        self._draw_score()
        self._draw_hearts()
        self._draw_level_banner()
        self._draw_record_celebration()

        self.shop.draw()

    def _draw_level_banner(self):
        if self.level_banner_timer <= 0:
            return

        elapsed = self.LEVEL_BANNER_DURATION - self.level_banner_timer
        if elapsed < self.LEVEL_BANNER_FADE_IN:
            alpha = 255 * (elapsed / self.LEVEL_BANNER_FADE_IN)
        elif self.level_banner_timer < self.LEVEL_BANNER_FADE_OUT:
            alpha = 255 * (self.level_banner_timer / self.LEVEL_BANNER_FADE_OUT)
        else:
            alpha = 255
        alpha = max(0, min(255, int(alpha)))

        center = (self.screen.get_width() // 2, self.screen.get_height() // 2 - 40)
        text = f"NIVEAU {self.level_banner_stage}"

        shadow = self.level_banner_font.render(text, True, (0, 0, 0))
        shadow.set_alpha(alpha)
        self.screen.blit(shadow, shadow.get_rect(center=(center[0] + 3, center[1] + 3)))

        banner = self.level_banner_font.render(text, True, self.LEVEL_BANNER_COLOR)
        banner.set_alpha(alpha)
        self.screen.blit(banner, banner.get_rect(center=center))

    def _draw_record_celebration(self):
        if self.record_celebration_timer <= 0:
            return

        elapsed = self.RECORD_CELEBRATION_DURATION - self.record_celebration_timer
        progress = elapsed / self.RECORD_CELEBRATION_DURATION
        alpha = max(0, min(255, int(255 * (1 - progress))))

        center = pg.Vector2(self.player.rect.center)
        for angle, speed in self.record_celebration_particles:
            offset = pg.Vector2(math.cos(angle), math.sin(angle)) * speed * elapsed
            pos = center + offset
            radius = max(1, int(4 * (1 - progress)))
            particle_surface = pg.Surface((radius * 2 + 2, radius * 2 + 2), pg.SRCALPHA)
            pg.draw.circle(particle_surface, (*self.RECORD_CELEBRATION_COLOR, alpha), (radius + 1, radius + 1), radius)
            self.screen.blit(particle_surface, particle_surface.get_rect(center=pos))

        text = self.record_celebration_font.render("NOUVEAU RECORD !", True, self.RECORD_CELEBRATION_TEXT_COLOR)
        text.set_alpha(alpha)
        text_pos = (self.player.rect.centerx, self.player.rect.top - 40)
        self.screen.blit(text, text.get_rect(center=text_pos))

    def handle_event(self, event):
        self.shop.handle_event(event)
