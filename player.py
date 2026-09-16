import random
import pygame as pg
from projectile import Projectile
from particle import Particle

class Player(pg.sprite.Sprite):
    size = (30, 26)
    image_shoot_set: bool = False
    image_shoot: list[pg.Surface]

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

    TRAIL_DELAY = 12  # ms entre deux particules de moteur
    TRAIL_COLOR_START = (255, 230, 140)
    TRAIL_COLOR_END = (255, 80, 20)

    MAX_LIVES = 3
    INVINCIBILITY_DURATION = 1200  # ms d'invincibilité après un coup
    BLINK_INTERVAL = 100           # ms entre chaque clignotement pendant l'invincibilité

    def __init__(self, screen: pg.Surface, speed: float, projectilsGroup: pg.sprite.AbstractGroup,
                 particlesGroup: pg.sprite.AbstractGroup, *groups):
        super().__init__(*groups)

        self.speed = speed
        self.projectilsGroup = projectilsGroup
        self.particlesGroup = particlesGroup
        self.screen = screen

        self.is_alive = True
        self.lives = Player.MAX_LIVES
        self.invincible_timer = 0

        self.coins = 0

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

        self.image = Player.damage_images[0]
        self.rect = self.image.get_rect()
        self.rect.move_ip(screen.get_width() / 2 - self.size[0] / 2, screen.get_height() - 50)
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
        self.rect.clamp_ip(self.screen.get_rect())
        self.position = pg.Vector2(self.rect.midbottom)

        self.fire_timer -= dt

        if self.fire_timer <= 0:
            Projectile(pg.Vector2(self.rect.center), 0.4, pg.Vector2(0, -1), Player.image_shoot, (0, 255, 0), self.projectilsGroup)
            self.fire_timer = self.fire_delay

        self._emit_trail(dt, movement)

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

        Particle(spawn_pos, velocity, Player.TRAIL_COLOR_START, Player.TRAIL_COLOR_END, self.particlesGroup)

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

    def add_coins(self, amount: int):
        self.coins += amount