import os
import pygame as pg

class Explosion(pg.sprite.Sprite):
    """ Animation d'explosion jouée une fois puis auto-détruite (Eclipsoide/images/explosion) """
    FRAME_COUNT = 8
    FRAME_DURATION = 45  # ms par frame
    SIZE = (110, 110)

    raw_images_set: bool = False
    raw_images: list[pg.Surface]
    images_set: bool = False
    images: list[pg.Surface]  # cache partagé pour la taille par défaut (SIZE)

    def __init__(self, position: pg.Vector2, *groups, size: tuple[int, int] = None):
        super().__init__(*groups)

        if not Explosion.raw_images_set:
            Explosion.raw_images = [
                pg.image.load(os.path.join('Eclipsoide/images', 'explosion', f'explosion_{i}.png'))
                for i in range(Explosion.FRAME_COUNT)
            ]
            Explosion.raw_images_set = True

        if size is None or size == Explosion.SIZE:
            # Cas courant (ennemis) : un seul jeu d'images partagé par toutes les instances
            if not Explosion.images_set:
                Explosion.images = [pg.transform.scale(image, Explosion.SIZE) for image in Explosion.raw_images]
                Explosion.images_set = True
            self.images = Explosion.images
        else:
            # Taille sur mesure (ex: boss) : mis à l'échelle une fois pour cette instance
            self.images = [pg.transform.scale(image, size) for image in Explosion.raw_images]

        self.center = pg.Vector2(position)
        self.time = 0

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.center)

    def update(self, dt):
        self.time += dt
        frame_index = int(self.time / Explosion.FRAME_DURATION)

        if frame_index >= Explosion.FRAME_COUNT:
            self.kill()
            return

        self.image = self.images[frame_index]
        self.rect = self.image.get_rect(center=self.center)
