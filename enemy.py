# Utilisation de pygame avec un préfixe plus simple
import pygame as pg
# Accès à la classe Random
import random

from datas import Datas
from player import Player
from projectile import Projectile
from particle import Particle

# Une balle qui rebondie sur les bords et des paddles
class Enemy(pg.sprite.Sprite):
    SPAWN_EXTRA_PROPORTION = 3
    MIN_SPEED_Y = 80
    MAX_SPEED_Y = 120
    MIN_SPEED_X = 30
    MAX_SPEED_X = 80
    ASTEROID_SIZE = 70
    TIME_BETWEEN_SHOOT = 2000
    HIT_FLASH_DURATION = 90  # ms de flash blanc quand touché

    # Traînée de débris derrière l'astéroïde en chute (poussière de roche)
    DEBRIS_DELAY = 90  # ms entre deux particules de débris
    DEBRIS_COLOR_START = (180, 140, 90)
    DEBRIS_COLOR_END = (80, 60, 40)

    image_set: bool = False
    image: pg.Surface
    image_shoot_set: bool = False
    image_shoot: list[pg.Surface]

    size = (ASTEROID_SIZE,ASTEROID_SIZE)

    def __init__(self,screen: pg.Surface, player: Player, datas: Datas, *groups):
        # Appel du constructeur la super classe
        pg.sprite.Sprite.__init__(self, *groups)

        self.datas = datas
        # Décalage aléatoire pour que les astéroïdes n'émettent pas leurs
        # débris tous en même temps
        self.debris_timer = random.uniform(0, Enemy.DEBRIS_DELAY)

        # Points de vie de l'ennemie
        self.life = 60

        self.time = 0

        # La surface (image) à afficher de ce sprite
        self.surface = pg.Surface(self.size)

        if not Enemy.image_set:
            Enemy.image = pg.image.load('images/asteroide.png')
            Enemy.image = pg.transform.scale(Enemy.image, self.size)
            Enemy.image_set = True

        if not Enemy.image_shoot_set:
            Enemy.image_shoot = [pg.image.load(f'images/laser/enemy/laser_asteroide_{i}.png') for i in range(4)]
            Enemy.image_shoot = [pg.transform.scale(image, (6, 16)) for image in Enemy.image_shoot]
            Enemy.image_shoot_set = True

        self.image = pg.transform.rotate(Enemy.image, random.randint(-180, 180))
        self.surface.blit(self.image, (0,0))

        # Version "flashée" en blanc de l'image, affichée brièvement quand touché
        self.normal_image = self.image
        self.flash_image = self._build_flash_image(self.image)
        self.hit_flash_timer = 0

        self.player = player
        self.screen = screen
        # Recupère le rectangle de la surface du Sprite
        self.rect = self.surface.get_rect()

        screenWith = Enemy.ASTEROID_SIZE * self.SPAWN_EXTRA_PROPORTION

        self.initPosition = pg.Vector2(random.randint(-screenWith, screen.get_width() + screenWith), random.randint(-Enemy.ASTEROID_SIZE * Enemy.SPAWN_EXTRA_PROPORTION, -Enemy.ASTEROID_SIZE))
        self.rect.move_ip(self.initPosition)


        # Vecteur de mouvement
        self.speedY = random.randrange(Enemy.MIN_SPEED_Y, Enemy.MAX_SPEED_Y, 1) / 1000.0
        self.speedX = random.randrange(Enemy.MIN_SPEED_X, Enemy.MAX_SPEED_X, 1) / 1000.0

        self.speedY = max(self.speedX, self.speedY)

        if self.initPosition.x > screen.get_width() / 2.0:
            self.speedX = -self.speedX

        self.movement = pg.Vector2(self.speedX, self.speedY)

    @staticmethod
    def _build_flash_image(image: pg.Surface) -> pg.Surface:
        flash = image.copy()
        flash.fill((255, 255, 255, 0), special_flags=pg.BLEND_RGBA_ADD)
        return flash

    def update(self,dt):
        """ Met à jour la position de la balle  """
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
            self.image = self.flash_image if self.hit_flash_timer > 0 else self.normal_image

        oldPos = pg.Vector2(self.rect.center)

        if (self.time + dt) % Enemy.TIME_BETWEEN_SHOOT < dt:
            playerRect = self.player.rect
            direction = pg.Vector2(playerRect.center) - oldPos
            if direction.length() > 0:
                Projectile(oldPos, 0.15, direction.normalize(), Enemy.image_shoot, (255, 0, 0), self.datas.projectiles_group, trail_end_color=(255, 60, 20))

        # Déplace la position de la raquette en fonction du veteur de mouvement
        # Calcule le vecteur déplacement
        self.time += dt
        # Modifie la position
        newPos = self.initPosition + (self.movement * self.time)

        if newPos.y > self.screen.get_height() + Enemy.ASTEROID_SIZE:
            self.kill()

        self.rect.x = int(newPos.x)
        self.rect.y = int(newPos.y)

        self._emit_debris(dt)

    def _emit_debris(self, dt):
        self.debris_timer -= dt
        if self.debris_timer > 0:
            return
        self.debris_timer = Enemy.DEBRIS_DELAY

        # Émis sur le bord arrière de l'astéroïde (à l'opposé de sa direction),
        # avec une légère dérive dans ce même sens pour qu'il reste "en retard"
        direction = -self.movement.normalize() if self.movement.length_squared() > 0 else pg.Vector2(0, -1)
        spawn_pos = pg.Vector2(self.rect.center) + direction * (Enemy.ASTEROID_SIZE * random.uniform(0.25, 0.45))
        spawn_pos += pg.Vector2(random.uniform(-6, 6), random.uniform(-6, 6))

        velocity = direction * random.uniform(0.015, 0.04)

        Particle(spawn_pos, velocity, Enemy.DEBRIS_COLOR_START, Enemy.DEBRIS_COLOR_END, self.datas.particles_group)

    def hited(self, damage: int):
        self.life -= damage
        self.hit_flash_timer = Enemy.HIT_FLASH_DURATION
        if self.life <= 0:
            self.kill()

    @classmethod
    def check_hits(cls, datas: Datas, damage: int, collided=Projectile.collide) -> list[tuple["Enemy", bool]]:
        """ Applique les dégâts des tirs du joueur touchant des ennemis.
        Retourne la liste des (ennemi, vient_de_mourir) pour chaque impact,
        pour laisser l'appelant gérer les récompenses (pièces, coeurs, etc.) """
        hits = []
        # noinspection bad-argument-type
        collisions = pg.sprite.groupcollide(datas.projectiles_group, datas.enemies_group, dokilla=True, dokillb=False, collided=collided)
        for enemies in collisions.values():
            for enemy in enemies:
                if type(enemy) == cls:
                    was_alive = enemy.life > 0
                    enemy.hited(damage)
                    hits.append((enemy, was_alive and enemy.life <= 0))
        return hits