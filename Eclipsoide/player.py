import math
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
    damage: float = 20.0
    # Référence pour le halo des tirs : au-dessus de ce seuil de dégâts (ex.
    # améliorations), le halo grossit ; en dessous, il rétrécit
    BASE_DAMAGE = 60

    # Texture du vaisseau selon le pourcentage de vie restant : le premier
    # seuil (proportion minimale) dont on est au-dessus ou égal s'applique
    DAMAGE_TEXTURES = [
        (0.75, 'Eclipsoide/images/ship/ship-0.png'),
        (0.50, 'Eclipsoide/images/ship/ship-1.png'),
        (0.25, 'Eclipsoide/images/ship/ship-2.png'),
        (0.0, 'Eclipsoide/images/ship/ship-3.png'),
    ]
    damage_images_set: bool = False
    damage_images: list[pg.Surface]

    SHOOT_SOUND_PATH = 'Eclipsoide/audios/shoot-dragon.mp3'
    shoot_sound_set: bool = False
    shoot_sound: pg.mixer.Sound | None = None

    PLAYER_SPEED = 0.4

    # Léger flottement vertical quand le vaisseau est à l'arrêt, qui s'installe
    # et se dissipe en douceur plutôt que de s'activer/désactiver brutalement
    BOB_AMPLITUDE = 3     # px
    BOB_PERIOD = 1400     # ms pour un cycle complet
    BOB_EASE_SPEED = 0.006  # vitesse d'installation/dissipation de l'intensité

    # Traînée plus dense en mouvement qu'à l'arrêt : l'intervalle entre deux
    # particules se resserre dès que le vaisseau se déplace
    TRAIL_DELAY_IDLE = 26    # ms entre particules à l'arrêt
    TRAIL_DELAY_MOVING = 8   # ms entre particules en mouvement
    TRAIL_COLOR_START = (255, 230, 140)
    TRAIL_COLOR_END = (255, 80, 20)

    INVINCIBILITY_DURATION = 1200  # ms d'invincibilité après un coup
    BLINK_INTERVAL = 100           # ms entre chaque clignotement pendant l'invincibilité

    # Bouclier : bloque tous les coups pendant sa durée (ne se cumule pas -
    # en ramasser un autre pendant qu'il est actif relance juste le minuteur)
    SHIELD_DURATION = 6000  # ms

    # Résultat de on_hit()/check_hits() : distingue un coup ignoré (invincibilité),
    # bloqué par le bouclier, ou réellement encaissé (perte de vie)
    HIT_IGNORED = 'ignored'
    HIT_SHIELDED = 'shielded'
    HIT_TAKEN = 'hit'

    def __init__(self, datas: Datas, *groups):
        super().__init__(*groups)

        self.datas = datas

        self.is_alive = True
        self.max_lives = 1
        self.lives = self.max_lives
        self.invincible_timer = 0
        self.godmode = False
        self.shield_timer = 0
        self.heart_drop_chance = 0

        self.coins = 0
        self.score = 0

        self.fire_delay = 500
        self.fire_timer = 0

        self.trail_timer = 0

        self.nb_shot = 1

        if not Player.image_shoot_set:
            Player.image_shoot = [pg.image.load(f'Eclipsoide/images/laser/player/laser_player_{i}.png') for i in range(4)]
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
        self.rect.move_ip(datas.screen.get_width() / 2 - self.size[0] / 2, datas.screen.get_height() - 110)

        self.hitbox = pg.Rect(0, 0, self.hitbox_size[0], self.hitbox_size[1])
        self.hitbox.center = self.rect.center

        self.position = pg.Vector2(self.rect.midbottom)
        self.bob_time = 0
        self.bob_intensity = 0.0

    def update(self, dt):
        self._update_damage_texture()
        self._update_invincibility(dt)
        self.shield_timer = max(0, self.shield_timer - dt)

        keystate = pg.key.get_pressed()
        movement = pg.Vector2()

        # Les flèches marchent toujours, quels que soient les touches
        # réassignées dans les options (filet de sécurité)
        keybinds = settings.OPTIONS["keybinds"]
        if keystate[keybinds["up"]] or keystate[pg.K_UP]:
            movement.y -= 1
        if keystate[keybinds["down"]] or keystate[pg.K_DOWN]:
            movement.y += 1
        if keystate[keybinds["left"]] or keystate[pg.K_LEFT]:
            movement.x -= 1
        if keystate[keybinds["right"]] or keystate[pg.K_RIGHT]:
            movement.x += 1
        if keystate[pg.K_g]:
            self.godmode = not self.godmode

        if movement.length_squared() != 0:
            movement = movement.normalize()

        self.position += movement * Player.PLAYER_SPEED * dt
        self.rect.midbottom = self.position
        self.rect.clamp_ip(self.datas.screen.get_rect())
        self.position = pg.Vector2(self.rect.midbottom)

        # Flottement idle : recalculé depuis self.position (jamais intégré à
        # elle) pour ne pas dériver, avec une intensité qui s'installe/se
        # dissipe en douceur au lieu de basculer net dès qu'on bouge
        moving = movement.length_squared() != 0
        target_intensity = 0.0 if moving else 1.0
        self.bob_intensity += (target_intensity - self.bob_intensity) * min(1.0, Player.BOB_EASE_SPEED * dt)
        self.bob_time += dt
        if self.bob_intensity > 0.001:
            bob_offset = int(Player.BOB_AMPLITUDE * self.bob_intensity * math.sin(self.bob_time * (2 * math.pi / Player.BOB_PERIOD)))
            self.rect.y += bob_offset

        self.hitbox.center = self.rect.center

        self.fire_timer -= dt

        if self.fire_timer <= 0:
            glow_scale = self.damage / Player.BASE_DAMAGE
            for i in range(self.nb_shot):
                offset_x = int(20 * (i - (self.nb_shot - 1) / 2))
                Projectile(pg.Vector2(self.rect.centerx + offset_x, self.rect.centery), 1, pg.Vector2(0, -1),
                           Player.image_shoot, (0, 255, 0), self.datas.projectiles_group, glow_scale=glow_scale)

            self.fire_timer = self.fire_delay
            self._play_shoot_sound()

        self._emit_trail(dt, movement)

    def _play_shoot_sound(self):
        if Player.shoot_sound is None or not settings.OPTIONS["sfx"]:
            return
        # Volume relu à chaque tir pour suivre les changements du menu options
        Player.shoot_sound.set_volume(settings.OPTIONS["sfx_volume"] / 100)
        Player.shoot_sound.play()

    def _emit_trail(self, dt, movement: pg.Vector2):
        self.trail_timer -= dt
        if self.trail_timer > 0:
            return
        moving = movement.length_squared() > 0
        self.trail_timer = Player.TRAIL_DELAY_MOVING if moving else Player.TRAIL_DELAY_IDLE

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
        ratio = self.lives / self.max_lives
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

    def on_hit(self) -> str:
        """ Retourne HIT_IGNORED (invincibilité en cours), HIT_SHIELDED (bouclier
        actif, coup bloqué) ou HIT_TAKEN (vie perdue) """
        # Le bouclier bloque tout, sans consommer l'invincibilité : un contact
        # prolongé pendant sa durée n'a donc aucun effet secondaire à gérer
        if self.shield_timer > 0:
            return Player.HIT_SHIELDED

        # Pendant l'invincibilité qui suit un coup, on ignore les collisions
        # supplémentaires (sinon rester au contact d'un ennemi vide toutes
        # les vies en un seul passage)
        if self.invincible_timer > 0:
            return Player.HIT_IGNORED

        if self.godmode == True and self.lives == 1:
            return Player.HIT_IGNORED

        self.invincible_timer = Player.INVINCIBILITY_DURATION

        self.lives -= 1
        if self.lives <= 0:
            self.is_alive = False
            self.kill()

        return Player.HIT_TAKEN

    def check_hits(self, enemies_group, enemy_projectiles_group, boss, collided=Projectile.collide) -> str:
        """ Vérifie les collisions qui blessent le joueur (contact ennemi, tir
        ennemi, bombe du boss). Retourne le résultat du premier coup réellement
        encaissé (HIT_TAKEN/HIT_SHIELDED), ou HIT_IGNORED si aucun """
        result = Player.HIT_IGNORED

        if pg.sprite.spritecollide(self, enemies_group, dokill=False, collided=collided):
            outcome = self.on_hit()
            if outcome != Player.HIT_IGNORED:
                result = outcome

        # (on collisionne sur la hitbox du tir, pas sur son rect visuel qui
        # inclut le halo et la traînée)
        # noinspection bad-argument-type
        if pg.sprite.spritecollide(self, enemy_projectiles_group, dokill=True, collided=collided):
            outcome = self.on_hit()
            if outcome != Player.HIT_IGNORED:
                result = outcome

        # Le boss existe dès le début de la partie mais reste "éteint" (rect à
        # sa position par défaut, coin supérieur gauche) tant qu'il n'a pas
        # spawné : sans ce garde-fou, cette zone tue le joueur au contact
        if boss is not None and boss.is_spawn:
            if boss.bombs_hitting(self):
                outcome = self.on_hit()
                if outcome != Player.HIT_IGNORED:
                    result = outcome
            if boss.boss_hitting(self):
                outcome = self.on_hit()
                if outcome != Player.HIT_IGNORED:
                    result = outcome


        return result

    def get_coins_value(self):
        return 10 * pow(1.5, self.datas.stage - 1)

    def add_coins(self, amount: int):
        self.coins += amount
        self.score += amount