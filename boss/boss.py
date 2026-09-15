import pygame as pg
from typing import Any
from .base import Box

from .bomb import Bomb


class Boss(Box):
    """
    Boss générique (lune, soleil...) : patrouille horizontalement et lâche
    régulièrement des bombes qui explosent au bout de Bomb.FUSE_TIME, ou
    quand le bouton spécial (detonate_key) est pressé si on en a défini un.

    Par défaut le boss est rond. L'image de fond est modifiable : on passe
    un chemin ou une Surface (paramètre image ou méthode set_image()), elle
    est redimensionnée et découpée à la forme du boss. Sans image, la forme
    est dessinée avec la couleur color.

    Pour une autre forme, surcharger _draw_shape() (voir Triangle).
    """

    BOMB_INTERVAL = 1500  # millisecondes entre deux bombes
    MAX_BOMBS = 5
    SPEED = 0.1  # pixels par milliseconde

    def __init__(
            self,
            x,
            y,
            width,
            height,
            color=(255, 255, 255),
            *groups,
            image: str | pg.Surface | None = None,
            detonate_key: int | None = None,
            bounds: pg.Rect | None = None,
    ):
        self.width = width
        self.height = height
        self.detonate_key = detonate_key
        self.bounds = bounds
        self.bg_image = self._load_image(image)
        self.direction = 1
        # Groupe des bombes de ce boss : c'est le boss qui les met à jour
        # et les dessine, elles fonctionnent donc même s'il n'est dans aucun groupe
        self.bombs: pg.sprite.Group = pg.sprite.Group()
        self.bomb_timer = 0
        self._detonate_was_pressed = False
        super().__init__(x, y, color, *groups)

    @staticmethod
    def _load_image(image: str | pg.Surface | None) -> pg.Surface | None:
        if isinstance(image, str):
            return pg.image.load(image).convert_alpha()
        return image

    def _draw_shape(self, surface: pg.Surface, color) -> None:
        """Dessine la forme du boss (un disque/ellipse par défaut)."""
        pg.draw.ellipse(surface, color, surface.get_rect())

    def _build_image(self) -> pg.Surface:
        surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
        if self.bg_image is None:
            self._draw_shape(surface, self.color)
            return surface

        # Masque blanc à la forme du boss, puis on ne garde de l'image
        # que les pixels à l'intérieur (BLEND_RGBA_MIN)
        self._draw_shape(surface, (255, 255, 255, 255))
        scaled = pg.transform.smoothscale(self.bg_image.convert_alpha(), (self.width, self.height))
        surface.blit(scaled, (0, 0), special_flags=pg.BLEND_RGBA_MIN)
        return surface

    def set_image(self, image: str | pg.Surface | None) -> None:
        """Change l'image de fond du boss (None pour revenir à la couleur unie)."""
        self.bg_image = self._load_image(image)
        self._refresh_image()

    def set_color(self, color: tuple[int, int, int]) -> None:
        """Change la couleur (utilisée seulement quand il n'y a pas d'image)."""
        self.color = color
        self._refresh_image()

    def _refresh_image(self) -> None:
        center = self.rect.center
        self.image = self._build_image()
        self.rect = self.image.get_rect(center=center)

    def drop_bomb(self) -> Bomb | None:
        """Lâche une bombe sous le boss, si la limite n'est pas atteinte."""
        active = [b for b in self.bombs if not b.exploding]
        if len(active) >= self.MAX_BOMBS:
            return None
        return Bomb(self.rect.midbottom, self.bounds, self.bombs)

    def detonate(self) -> None:
        """Fait exploser toutes les bombes lâchées par ce boss."""
        for bomb in self.bombs:
            bomb.explode()

    def bombs_hitting(self, target: pg.sprite.Sprite) -> list[Bomb]:
        """
        Retourne les bombes qui touchent target (collision au pixel près).
        Une bombe qui tombe sur la cible explose au contact.
        """
        hits = pg.sprite.spritecollide(target, self.bombs, False, pg.sprite.collide_mask)
        for bomb in hits:
            bomb.explode()
        return hits

    def draw_bombs(self, surface: pg.Surface) -> None:
        """Dessine les bombes/explosions du boss (à appeler après le draw des groupes)."""
        self.bombs.draw(surface)

    def handle_event(self, event: pg.event.Event) -> None:
        """
        Alternative à l'écoute clavier dans update() : à appeler depuis
        la boucle d'événements du jeu si on préfère.
        """
        if self.detonate_key is not None and event.type == pg.KEYDOWN and event.key == self.detonate_key:
            self.detonate()

    def _patrol(self, dt: int) -> None:
        """Déplace le boss horizontalement et le fait rebondir sur les bords de bounds."""
        if self.bounds is None:
            return
        self.move(self.direction * self.SPEED * dt, 0)
        if self.rect.left <= self.bounds.left:
            self.rect.left = self.bounds.left
            self.direction = 1
        elif self.rect.right >= self.bounds.right:
            self.rect.right = self.bounds.right
            self.direction = -1

    def update(self, *args: Any, **kwargs: Any) -> None:
        dt: int = args[0] if args else 0

        self._patrol(dt)

        # Largage périodique des bombes
        self.bomb_timer += dt
        if self.bomb_timer >= self.BOMB_INTERVAL:
            self.bomb_timer -= self.BOMB_INTERVAL
            self.drop_bomb()

        self.bombs.update(dt)

        # Écoute du bouton spécial (front montant : une détonation par appui)
        if self.detonate_key is not None:
            pressed = pg.key.get_pressed()[self.detonate_key]
            if pressed and not self._detonate_was_pressed:
                self.detonate()
            self._detonate_was_pressed = pressed
