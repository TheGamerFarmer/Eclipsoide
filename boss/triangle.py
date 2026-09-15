import pygame as pg
from typing import Any
from .base import Box


from .bomb import Bomb

class Triangle(Box):
    """
    Boss/forme triangulaire (isocèle, pointe vers le haut).

    Lâche régulièrement des bombes depuis sa base. Quand le bouton
    spécial (detonate_key) est pressé, toutes ses bombes explosent.
    """

    BOMB_INTERVAL = 1500  # millisecondes entre deux bombes
    MAX_BOMBS = 5

    def __init__(
        self,
        x,
        y,
        base_width,
        height,
        color=(255, 255, 255),
        *groups,
        detonate_key: int = pg.K_b,
        bounds: pg.Rect | None = None,
    ):
        self.base_width = base_width
        self.height = height
        self.detonate_key = detonate_key
        self.bounds = bounds
        # Groupe des bombes de ce boss (pour les collisions côté jeu)
        self.bombs: pg.sprite.Group = pg.sprite.Group()
        self.bomb_timer = 0
        self._detonate_was_pressed = False
        super().__init__(x, y, color, *groups)

    def _build_image(self) -> pg.Surface:
        surface = pg.Surface((self.base_width, self.height), pg.SRCALPHA)
        points = [
            (self.base_width / 2, 0),
            (0, self.height),
            (self.base_width, self.height),
        ]
        pg.draw.polygon(surface, self.color, points)
        return surface

    def drop_bomb(self) -> Bomb | None:
        """Lâche une bombe sous la base du triangle, si la limite n'est pas atteinte."""
        active = [b for b in self.bombs if not b.exploding]
        if len(active) >= self.MAX_BOMBS:
            return None
        # La bombe rejoint les mêmes groupes que le boss (donc affichée/mise à jour)
        return Bomb(self.rect.midbottom, self.bounds, self.bombs, *self.groups())

    def detonate(self) -> None:
        """Fait exploser toutes les bombes lâchées par ce boss."""
        for bomb in self.bombs:
            bomb.explode()

    def handle_event(self, event: pg.event.Event) -> None:
        """
        Alternative à l'écoute clavier dans update() : à appeler depuis
        la boucle d'événements du jeu si on préfère.
        """
        if event.type == pg.KEYDOWN and event.key == self.detonate_key:
            self.detonate()

    def update(self, *args: Any, **kwargs: Any) -> None:
        dt: int = args[0] if args else 0

        # Largage périodique des bombes
        self.bomb_timer += dt
        if self.bomb_timer >= self.BOMB_INTERVAL:
            self.bomb_timer -= self.BOMB_INTERVAL
            self.drop_bomb()

        # Écoute du bouton spécial (front montant : une détonation par appui)
        pressed = pg.key.get_pressed()[self.detonate_key]
        if pressed and not self._detonate_was_pressed:
            self.detonate()
        self._detonate_was_pressed = pressed
