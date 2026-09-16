import os
import pygame as pg

class Explosion(pg.sprite.Sprite):
    """ Animation d'explosion jouée une fois puis auto-détruite (images/explosion) """
    FRAME_COUNT = 8
    FRAME_DURATION = 45  # ms par frame
    SIZE = (110, 110)

    images_set: bool = False
    images: list[pg.Surface]

    def __init__(self, position: pg.Vector2, *groups):
        super().__init__(*groups)

        if not Explosion.images_set:
            Explosion.images = [
                pg.image.load(os.path.join('images', 'explosion', f'explosion_{i}.png'))
                for i in range(Explosion.FRAME_COUNT)
            ]
            Explosion.images = [pg.transform.scale(image, Explosion.SIZE) for image in Explosion.images]
            Explosion.images_set = True

        self.center = pg.Vector2(position)
        self.time = 0

        self.image = Explosion.images[0]
        self.rect = self.image.get_rect(center=self.center)

    def update(self, dt):
        self.time += dt
        frame_index = int(self.time / Explosion.FRAME_DURATION)

        if frame_index >= Explosion.FRAME_COUNT:
            self.kill()
            return

        self.image = Explosion.images[frame_index]
        self.rect = self.image.get_rect(center=self.center)
