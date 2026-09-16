import random
import pygame as pg

from datas import Datas
from projectile import Projectile
from particle import Particle
import settings

class Player(pg.sprite.Sprite):
    size = (30, 26)
    hitbox_size = (10, 9)
    image_shoot_set: bool = False
    image_shoot: list[pg.Surface]
    image: pg.Surface
    rect: pg.Rect
    damage: int = 20

    # Texture du vaisseau selon le pourcentage de vie restant : le premier
    # seuil (proportion minimale) dont on est au-dessus ou égal s'applique
    DAMAGE_TEXTURES = [
        (0.75, 'images/ship/ship-0.png'),
        (0.50, 'images/ship/ship-1.png'),
        (0.25, 'images/ship/ship-2.png'),
        (0.0, 'images/ship/ship-3.png'),
    ]
    damage_images_set: bool = False
    damage_images: list[pg.Surface]

    SHOOT_SOUND_PATH = 'audios/shoot-dragon.mp3'
    shoot_sound_set: bool = False
    shoot_sound: pg.mixer.Sound | None = None

    TRAIL_DELAY = 12  # ms entre deux particules de moteur
    TRAIL_COLOR_START = (255, 230, 140)
    TRAIL_COLOR_END = (255, 80, 20)

    MAX_LIVES = 3
    INVINCIBILITY_DURATION = 1200  # ms d'invincibilité après un coup
    BLINK_INTERVAL = 100           # ms entre chaque clignotement pendant l'invincibilité

    def __init__(self, speed: float, datas: Datas, *groups):
        super().__init__(*groups)

        self.speed = speed
        self.datas = datas

        self.is_alive = True
        self.lives = Player.MAX_LIVES
        self.invincible_timer = 0

        self.coins = 0
        self.score = 0

        self.fire_delay = 300
        self.fire_timer = 0

        self.trail_timer = 0

        if not Player.image_shoot_set:
            Player.image_shoot = [pg.image.load(f'images/laser/player/laser_player_{i}.png') for i in range(4)]
            Player.image_shoot = [pg.transform.scale(image, (6, 16)) for image in Player.image_shoot]
            Player.image_shoot_set = True

        if not Player.damage_images_set:
            Player.damage_images = [
                pg.transform.scale(pg.image.load(path), self.size)
                for _, path in Player.DAMAGE_TEXTURES
            ]
            Player.damage_images_set = True

        if not Player.shoot_sound_set:
            # Le jeu doit rester jouable sans périphérique audio
            try:
                Player.shoot_sound = pg.mixer.Sound(Player.SHOOT_SOUND_PATH)
            except (pg.error, FileNotFoundError) as e:
                print(f"Impossible de charger le son de tir : {e}")
            Player.shoot_sound_set = True

        self.image = Player.damage_images[0]
        self.rect = self.image.get_rect()
        self.rect.move_ip(datas.screen.get_width() / 2 - self.size[0] / 2, datas.screen.get_height() - 50)

        self.hitbox = pg.Rect(0, 0, self.hitbox_size[0], self.hitbox_size[1])
        self.hitbox.center = self.rect.center

        self.position = pg.Vector2(self.rect.midbottom)

    def update(self, dt):
        self._update_damage_texture()
        self._update_invincibility(dt)

        keystate = pg.key.get_pressed()
        movement = pg.Vector2()

        if keystate[pg.K_z] or keystate[pg.K_UP]:
            movement.y -= 1
        if keystate[pg.K_s] or keystate[pg.K_DOWN]:
            movement.y += 1
        if keystate[pg.K_q] or keystate[pg.K_LEFT]:
            movement.x -= 1
        if keystate[pg.K_d] or keystate[pg.K_RIGHT]:
            movement.x += 1

        if movement.length_squared() != 0:
            movement = movement.normalize()

        self.position += movement * self.speed * dt
        self.rect.midbottom = self.position
        self.rect.clamp_ip(self.datas.screen.get_rect())
        self.position = pg.Vector2(self.rect.midbottom)
        self.hitbox.center = self.rect.center

        self.fire_timer -= dt

        if self.fire_timer <= 0:
            Projectile(pg.Vector2(self.rect.center), 0.4, pg.Vector2(0, -1), Player.image_shoot, (0, 255, 0), self.datas.projectiles_group)
            self.fire_timer = self.fire_delay
            self._play_shoot_sound()

        self._emit_trail(dt, movement)

    def _play_shoot_sound(self):
        if Player.shoot_sound is None or not settings.OPTIONS["sfx"]:
            return
        # Volume relu à chaque tir pour suivre les changements du menu options
        Player.shoot_sound.set_volume(settings.OPTIONS["volume"] / 100)
        Player.shoot_sound.play()

    def _emit_trail(self, dt, movement: pg.Vector2):
        self.trail_timer -= dt
        if self.trail_timer > 0:
            return
        self.trail_timer = Player.TRAIL_DELAY

        # Point d'émission au niveau du réacteur, légèrement décalé pour ne pas
        # coller pile sous le vaisseau
        spawn_pos = pg.Vector2(self.rect.midbottom) - pg.Vector2(0, 2)
        spawn_pos.x += random.uniform(-3, 3)

        # Le panache part vers le bas et s'oppose un peu au mouvement du vaisseau
        # pour donner un effet de traînée qui "reste en arrière"
        velocity = pg.Vector2(random.uniform(-0.02, 0.02), random.uniform(0.09, 0.16))
        velocity -= movement * 0.05

        Particle(spawn_pos, velocity, Player.TRAIL_COLOR_START, Player.TRAIL_COLOR_END, self.datas.particles_group)

    def _update_damage_texture(self):
        ratio = self.lives / Player.MAX_LIVES
        for index, (threshold, _) in enumerate(Player.DAMAGE_TEXTURES):
            if ratio >= threshold:
                self.image = Player.damage_images[index]
                return
        self.image = Player.damage_images[-1]

    def _update_invincibility(self, dt):
        if self.invincible_timer > 0:
            self.invincible_timer = max(0, self.invincible_timer - dt)

        # Réappliqué chaque frame (et pas seulement pendant l'invincibilité) car
        # self.image peut changer de texture de dégâts entre deux frames : sans
        # ça, la nouvelle texture garderait l'alpha laissé par son dernier usage
        if self.invincible_timer > 0:
            blinking_off = (self.invincible_timer // Player.BLINK_INTERVAL) % 2 == 0
            self.image.set_alpha(90 if blinking_off else 255)
        else:
            self.image.set_alpha(255)

    def on_hit(self) -> bool:
        """ Retourne True si le coup a réellement été encaissé (pour déclencher
        un feedback comme un flash d'écran), False s'il a été ignoré (invincibilité) """
        # Pendant l'invincibilité qui suit un coup, on ignore les collisions
        # supplémentaires (sinon rester au contact d'un ennemi vide toutes
        # les vies en un seul passage)
        if self.invincible_timer > 0:
            return False

        self.lives -= 1
        self.invincible_timer = Player.INVINCIBILITY_DURATION

        if self.lives <= 0:
            self.is_alive = False
            self.kill()

        return True

    def check_hits(self, enemies_group, enemy_projectiles_group, boss, collided=Projectile.collide) -> bool:
        """ Vérifie les collisions qui blessent le joueur (contact ennemi, tir
        ennemi, bombe du boss). Retourne True si un coup a réellement été encaissé
        (pour déclencher un feedback comme un flash d'écran) """
        hit = False
        # noinspection bad-argument-type
        if pg.sprite.spritecollide(self, enemies_group, dokill=False):
            hit = self.on_hit() or hit

        # (on collisionne sur la hitbox du tir, pas sur son rect visuel qui
        # inclut le halo et la traînée)
        # noinspection bad-argument-type
        if pg.sprite.spritecollide(self, enemy_projectiles_group, dokill=True, collided=collided):
            hit = self.on_hit() or hit

        if boss is not None and boss.bombs_hitting(self):
            hit = self.on_hit() or hit

        return hit

    def add_coins(self, amount: int):
        self.coins += amount
        self.score += amount