"""
Module de base : Box hérite à la fois de pygame.sprite.Sprite (pour
s'intégrer dans les Group/collisions/rendu natifs de pygame) et de ABC
(pour forcer chaque forme concrète à fournir sa propre image).
"""

from abc import ABC, abstractmethod

import pygame as pg


class Box(pg.sprite.Sprite, ABC):
    """
    Interface commune pour toutes les hitbox/formes du jeu.

    Chaque sous-classe doit implémenter _build_image(), qui retourne la
    Surface représentant la forme (dessinée sur fond transparent).
    Box s'occupe ensuite de placer cette image dans self.rect à (x, y).
    """

    def __init__(self, x: float, y: float, color: tuple[int, int, int] = (255, 255, 255), *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.color = color
        self.image = self._build_image()
        self.rect = self.image.get_rect(topleft=(x, y))

    @abstractmethod
    def _build_image(self) -> pg.Surface:
        """Construit et retourne la Surface de la forme (fond transparent)."""
        raise NotImplementedError

    def move(self, dx: float, dy: float) -> None:
        """Déplace la forme (utile pour le vaisseau ou les ennemis mobiles)."""
        self.rect.x += dx
        self.rect.y += dy

    def collides_with(self, other: "Box") -> bool:
        """Collision native pygame via les rect (rapide, suffisant en général)."""
        return self.rect.colliderect(other.rect)

    def update(self, *args, **kwargs) -> None:
        """
        Hook appelé par Group.update(). Ne fait rien par défaut ;
        les sous-classes (ennemi, boss...) peuvent le surcharger pour
        leur comportement (déplacement, tir, etc.).
        """
        pass