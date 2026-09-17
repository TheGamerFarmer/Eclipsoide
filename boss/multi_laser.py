import pygame as pg
import math
from projectile import Projectile


class MultiLaser(pg.sprite.Sprite):
    # millisecondes d'avertissement avant le tir
    WARNING_DURATION = 1200
    TELEGRAPH_COLOR = (255, 50, 50)
    MAX_ALPHA = 100
    LASER_SPEED = 0.35
    LASER_COLOR = (255, 30, 30)
    LASER_TRAIL = (150, 0, 0)

    def __init__(self, origin_pos, datas, angle_start, spread, count, laser_images, *groups):
        super().__init__(*groups)
        self.origin_pos = origin_pos
        self.datas = datas
        self.angle_start = angle_start
        self.spread = spread
        self.count = count
        self.laser_images = laser_images

        self.time = 0
        self.screen_height = datas.screen.get_height()
        self.screen_width = datas.screen.get_width()

        # On calcule les angles
        self.angles_deg = []
        angle_step = spread / max(1, count - 1) if count > 1 else 0
        for i in range(count):
            self.angles_deg.append(angle_start + i * angle_step)

        self.image = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)
        self.rect = self.image.get_rect()

    def _draw_telegraphs(self, alpha: int):
        self.image.fill((0, 0, 0, 0))

        # pour chaque angle on dessine une longue ligne semi-transparente
        for angle_deg in self.angles_deg:
            angle_rad = math.radians(angle_deg)
            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)

            # on prolonge la ligne en dehors de l'écran pour être sûr de tout couvrir
            length = self.screen_height * 1.5
            end_pos = (self.origin_pos[0] + dx * length, self.origin_pos[1] + dy * length)

            # On dessine une ligne
            pg.draw.line(self.image, (*self.TELEGRAPH_COLOR, alpha), self.origin_pos, end_pos, width=8)

    def _fire_lasers(self):
        origin = pg.Vector2(self.origin_pos)

        for angle_deg in self.angles_deg:
            angle_rad = math.radians(angle_deg)
            direction = pg.Vector2(math.cos(angle_rad), math.sin(angle_rad))
            Projectile(origin, self.LASER_SPEED, direction, self.laser_images, self.LASER_COLOR,
                       self.datas.enemy_projectiles_group, trail_end_color=self.LASER_TRAIL)

    def update(self, dt):
        self.time += dt

        if self.time >= self.WARNING_DURATION:
            self._fire_lasers()
            self.kill()
            return

        progress = self.time / self.WARNING_DURATION

        if progress < 0.8:
            alpha = int(self.MAX_ALPHA * (progress / 0.8))
        else:
            pulse = math.sin(self.time * 0.05)
            alpha = int(self.MAX_ALPHA * (0.5 + 0.5 * pulse))

        self._draw_telegraphs(alpha)