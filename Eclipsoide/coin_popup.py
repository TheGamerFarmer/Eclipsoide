import os
import pygame as pg

class CoinPopup(pg.sprite.Sprite):
    DURATION = 600     # ms avant disparition
    RISE_SPEED = 0.03  # pixels/ms

    font_set: bool = False
    font: pg.font.Font

    def __init__(self, position: pg.Vector2, amount: int | float, *groups, color: tuple[int, int, int] = (255, 220, 80), prefix: str = "+"):
        super().__init__(*groups)

        if not CoinPopup.font_set:
            font_path = os.path.join('Eclipsoide/images/ui', 'Font', 'Kenney Future.ttf')
            CoinPopup.font = pg.font.Font(font_path, 18)
            CoinPopup.font_set = True

        self.position = pg.Vector2(position)
        self.time = 0

        self.base_image = CoinPopup.font.render(f"{prefix}{amount}", True, color)
        self.image = self.base_image
        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt):
        self.time += dt
        if self.time >= CoinPopup.DURATION:
            self.kill()
            return

        self.position.y -= CoinPopup.RISE_SPEED * dt

        alpha = max(0, 255 - int(255 * (self.time / CoinPopup.DURATION)))
        self.image = self.base_image.copy()
        self.image.set_alpha(alpha)
        self.rect = self.image.get_rect(center=self.position)
