import math
import pygame as pg


class MenuFx:
    """ Éléments d'ambiance animés partagés par les écrans de menu qui utilisent
    le fond étoilé (soleil qui tourne/pulse/brille, lueur pulsante de titre).
    Horloge basée sur pg.time.get_ticks() : ces écrans n'ont pas de notion de
    pause/mort à gérer, contrairement au Hud en jeu. """

    SUN_SIZE = 220
    SUN_ROTATION_SPEED = 0.006  # degrés/ms
    SUN_PULSE_PERIOD = 3000     # ms
    SUN_PULSE_AMPLITUDE = 0.035
    SUN_GLOW_COLOR = (255, 170, 60)
    SUN_GLOW_LAYERS = 3
    SUN_GLOW_PADDING = 25
    SUN_GLOW_MAX_ALPHA = 55
    SUN_GLOW_PULSE_RADIUS = 10
    SUN_GLOW_PULSE_ALPHA = 20

    TITLE_GLOW_COLOR = (80, 180, 255)
    TITLE_GLOW_PERIOD = 2200  # ms
    TITLE_GLOW_MIN_ALPHA = 40
    TITLE_GLOW_MAX_ALPHA = 130
    TITLE_GLOW_SCALE = 1.06  # léger, pour ne pas "dédoubler" les lettres sur les titres longs

    def __init__(self, sun_size: int = None):
        self.sun_size = sun_size if sun_size is not None else self.SUN_SIZE
        self.sun_image = pg.transform.scale(pg.image.load('images/sun.png'), (self.sun_size, self.sun_size))

    def draw_sun(self, surface: pg.Surface, center: tuple[float, float]):
        now = pg.time.get_ticks()
        angle = (now * self.SUN_ROTATION_SPEED) % 360
        pulse_wave = math.sin(now * (2 * math.pi / self.SUN_PULSE_PERIOD))
        pulse_scale = 1 + self.SUN_PULSE_AMPLITUDE * pulse_wave

        self._draw_sun_glow(surface, center, pulse_wave)

        rotated_sun = pg.transform.rotozoom(self.sun_image, angle, pulse_scale)
        surface.blit(rotated_sun, rotated_sun.get_rect(center=center))

    def _draw_sun_glow(self, surface: pg.Surface, center: tuple[float, float], pulse_wave: float):
        base_radius = self.sun_size / 2
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

        surface.blit(glow_surface, glow_surface.get_rect(center=center))

    def draw_title_glow(self, surface: pg.Surface, font: pg.font.Font, text: str, center: tuple[float, float]):
        """ Lueur douce et pulsante derrière un titre ; l'appelant dessine
        ensuite son propre texte net (+ ombre éventuelle) par-dessus """
        now = pg.time.get_ticks()
        pulse = (math.sin(now * (2 * math.pi / self.TITLE_GLOW_PERIOD)) + 1) / 2
        alpha = int(self.TITLE_GLOW_MIN_ALPHA + (self.TITLE_GLOW_MAX_ALPHA - self.TITLE_GLOW_MIN_ALPHA) * pulse)

        glow_text = font.render(text, True, self.TITLE_GLOW_COLOR)
        size = (int(glow_text.get_width() * self.TITLE_GLOW_SCALE), int(glow_text.get_height() * self.TITLE_GLOW_SCALE))
        glow_text = pg.transform.smoothscale(glow_text, size)
        glow_text.set_alpha(alpha)
        surface.blit(glow_text, glow_text.get_rect(center=center))
