import pygame as pg
import os

from .bomb import Bomb
from Eclipsoide.coin_popup import CoinPopup
from Eclipsoide.datas import Datas
from Eclipsoide.explosion import Explosion
from Eclipsoide.hud import Hud
from Eclipsoide.player import Player
import math
from Eclipsoide.boss.multi_laser import MultiLaser
from .tracker import Tracker
from Eclipsoide.spawn_ping import SpawnPing
from Eclipsoide.shockwave import Shockwave


class Boss(pg.sprite.Sprite):
    """
    Interface commune pour touts les bosses du jeu.
    """
    BOSS_SIZE = 70
    GROW_DURATION = 2000
    BOSS_MAX_SIZE = 620
    # Chaque boss vaincu rend le suivant 2 fois plus résistant
    BOSS_LIFE_GROWTH = 2
    BOMB_INTERVAL = 1500  # millisecondes entre deux bombes
    MAX_BOMBS = 5
    SPEED = 0.1  # pixels par milliseconde
    FRAME_DURATION = 100  # millisecondes par image d'animation

    # Le boss a LIVES "vies" (les crans de la barre). Au premier palier chacune
    # encaisse LIFE_PER_SEGMENT points, soit 3 à 4 tirs du joueur (40 par tir).
    LIFE_PER_SEGMENT = 560
    LIVES = 20
    LIFE = LIVES * LIFE_PER_SEGMENT  # 2800 pv, environ 70 tirs

    # Barre de vie affichée en haut de l'écran : le remplissage réel change de
    # couleur (vert -> jaune -> rouge) selon le % de vie restant, et une bande
    # claire ("drain") reste visible un instant derrière lui après un coup,
    # le temps qu'elle rattrape la nouvelle valeur, façon jauge de RPG
    BAR_WIDTH_RATIO = 0.6  # proportion de la largeur de l'écran
    BAR_HEIGHT = 18
    BAR_MARGIN = 14
    BAR_BACK_COLOR = (60, 20, 30)
    BAR_BORDER_COLOR = (255, 255, 255)
    BAR_MIN_SEGMENT = 6  # en dessous, on n'affiche plus les séparations
    BAR_FILL_COLOR_LOW = (220, 60, 60)
    BAR_FILL_COLOR_MID = (230, 200, 40)
    BAR_FILL_COLOR_HIGH = (70, 210, 90)
    BAR_DRAIN_COLOR = (255, 250, 220)
    BAR_DRAIN_SPEED = 0.35  # points de vie/ms rattrapés par la bande claire

    # Phase "enragée" sous ce seuil de vie : glow rouge pulsant derrière le
    # boss + halo autour de sa barre, pour signaler qu'il devient critique
    ENRAGE_THRESHOLD = 0.25
    ENRAGE_GLOW_COLOR = (255, 40, 40)
    ENRAGE_GLOW_PERIOD = 450  # ms, pulsation rapide façon "alerte"
    ENRAGE_GLOW_LAYERS = 3
    ENRAGE_GLOW_PADDING = 20
    ENRAGE_GLOW_PULSE_RADIUS = 15
    ENRAGE_GLOW_MAX_ALPHA = 110

    HIT_FLASH_DURATION = 90  # ms de flash blanc quand touché
    # Intensité du blanc ajouté (0-255) : moins que 255 pour laisser deviner la
    # texture du boss sous le flash plutôt que le faire disparaître entièrement
    HIT_FLASH_INTENSITY = 150
    DAMAGE_POPUP_COLOR = (255, 255, 255)
    # L'explosion de mort est mise à l'échelle du boss (pas le sprite d'origine,
    # 110px, qui serait ridicule à côté d'un boss de 620px) sans pour autant
    # être 1:1 (l'asset pixelise trop à cette taille)
    EXPLOSION_SIZE_RATIO = 0.55

    size = (BOSS_SIZE, BOSS_SIZE)

    @staticmethod
    def _load_images(image: str | pg.Surface | list[str | pg.Surface] | None) -> list[pg.Surface]:
        """Retourne la liste des images d'animation (vide si pas d'image)."""
        if image is None:
            return []
        if not isinstance(image, list):
            image = [image]
        return [pg.image.load(img).convert_alpha() if isinstance(img, str) else img for img in image]

    @staticmethod
    def _build_flash_image(image: pg.Surface) -> pg.Surface:
        flash = image.copy()
        intensity = Boss.HIT_FLASH_INTENSITY
        flash.fill((intensity, intensity, intensity, 0), special_flags=pg.BLEND_RGBA_ADD)
        return flash

    def _set_image(self, image: pg.Surface) -> None:
        """ Fixe l'apparence "normale" du boss et prépare sa version flashée en
        blanc (rejouée brièvement à chaque coup) ; à rappeler chaque fois que
        l'image change (arrivée, palier suivant) """
        self.normal_image = image
        self.flash_image = self._build_flash_image(image)
        self.image = self.normal_image if self.hit_flash_timer <= 0 else self.flash_image

    def __init__(self, datas: Datas, player: Player, hud, *groups):
        pg.sprite.Sprite.__init__(self, *groups)

        self.datas = datas
        self.player = player
        self.hud = hud
        self.is_spawn = False

        self.max_life = int(Boss.LIFE * Boss.BOSS_LIFE_GROWTH ** (self.datas.stage - 1))
        self.life = self.max_life
        self.bar_display_life = self.life
        self.time = 0

        self._base_image = pg.image.load('Eclipsoide/images/boss1.png').convert_alpha()
        self.hit_flash_timer = 0
        self._set_image(self._base_image)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.normal_image)

        self.bomb_timer = 0
        self._detonate_was_pressed = False
        self.multi_laser_timer = 0
        self.tracker_timer = 0
        self.boss_bar_font = pg.font.Font(os.path.join('Eclipsoide/images/ui', 'Font', 'Kenney Future.ttf'), 24)

        if not hasattr(Boss, 'laser_images'):
            images = [pg.image.load(f'Eclipsoide/images/laser/enemy/laser_asteroide_{i}.png').convert_alpha() for i in range(4)]
            Boss.laser_images = [pg.transform.scale(img, (14, 38)) for img in images]

    def _boss_vaincu(self):
        """ Le boss explose, le palier suivant démarre : les vagues reprennent """
        explosion_size = (int(self.rect.width * self.EXPLOSION_SIZE_RATIO), int(self.rect.height * self.EXPLOSION_SIZE_RATIO))
        Explosion(pg.Vector2(self.rect.center), self.datas.explosions_group, size=explosion_size)
        Shockwave(pg.Vector2(self.rect.center), self.datas.explosions_group,
                  min_radius=self.rect.width * 0.15, max_radius=self.rect.width * 0.9)
        self.hud.trigger_shake()
        self.datas.bombs_group.empty()
        self.is_spawn = False
        self.datas.stage += 1
        self.hud.trigger_level_banner(self.datas.stage)
        self.max_life = int(Boss.LIFE * Boss.BOSS_LIFE_GROWTH ** (self.datas.stage - 1))
        self.life = self.max_life
        self.bar_display_life = self.life
        self.hit_flash_timer = 0
        self._set_image(self._base_image)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.normal_image)
        self.bomb_timer = 0
        # Remettre l'horloge à zéro relance les vagues d'ennemis, puis l'arrivée
        # du boss suivant une fois TIME_BEFORE_BOSS écoulé
        self.datas.time = 0
        self.time = 0

        for sprite in list(self.datas.enemies_group):
            if isinstance(sprite, Tracker):
                sprite.kill()
                Explosion(pg.Vector2(sprite.rect.center), self.datas.explosions_group)

    def update(self, dt) -> None:
        self.time += dt

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
            self.image = self.flash_image if self.hit_flash_timer > 0 else self.normal_image

        if self.bar_display_life > self.life:
            self.bar_display_life = max(self.life, self.bar_display_life - self.BAR_DRAIN_SPEED * dt)

        # Les bombes du boss explosent au contact du joueur et le tuent
        if  self.bombs_hitting(self.player):
            self.player.on_hit()

        # Les tirs du joueur entament la vie du boss
        if self.is_spawn:
            for position in self.check_hits(self.datas.projectiles_group, self.player.damage):
                CoinPopup(pg.Vector2(position), round(self.player.damage), self.datas.popups_group,
                          color=self.DAMAGE_POPUP_COLOR, prefix="-")
            if not self.is_alive:
                self._boss_vaincu()

        # Le boss sprite prend le relais de l'animation d'arrivée une fois la croissance finie
        if not self.is_spawn and self.datas.time > Datas.TIME_BEFORE_BOSS + self.GROW_DURATION:
            self.is_spawn = True
            screen = self.datas.screen
            scaled = pg.transform.scale(self._base_image, (Boss.BOSS_MAX_SIZE, Boss.BOSS_MAX_SIZE))
            self._set_image(scaled)
            bossX = int(screen.get_width() / 2 - Boss.BOSS_MAX_SIZE / 2)
            bossY = int((Hud.SUN_SIZE / 4) + (Hud.SUN_SIZE / 2) - Boss.BOSS_MAX_SIZE / 2)
            self.rect = self.image.get_rect(topleft=(bossX, bossY))
            self.mask = pg.mask.from_surface(self.normal_image)
            self.hud.trigger_zoom_punch()
            self.hud.trigger_shake(self.hud.BOSS_SPAWN_SHAKE_DURATION, self.hud.BOSS_SPAWN_SHAKE_MAGNITUDE)

        if self.is_spawn:
            bomb_cooldown = self.BOMB_INTERVAL // 2 if self._is_enraged() else self.BOMB_INTERVAL
            laser_cooldown = 2500 if self._is_enraged() else 5000
            tracker_cooldown = 4000 if self._is_enraged() else 8000

            self.bomb_timer += dt
            if self.bomb_timer >= bomb_cooldown:
                self.bomb_timer -= bomb_cooldown
                self.drop_bomb()

            self.datas.bombs_group.update(dt)

            # laser
            self.multi_laser_timer += dt
            if self.multi_laser_timer >= laser_cooldown:
                self.multi_laser_timer -= laser_cooldown
                self.fire_multi_laser()

            # tracker
            self.tracker_timer += dt
            if self.tracker_timer >= tracker_cooldown:
                self.tracker_timer -= tracker_cooldown
                self.fire_tracker()

    @property
    def is_alive(self) -> bool:
        return self.life > 0

    def hited(self, damage: int) -> None:
        """Inflige des dégâts au boss (même nom que Enemy.hited)."""
        self.life = max(0, self.life - damage)
        self.hit_flash_timer = Boss.HIT_FLASH_DURATION

    @staticmethod
    def collide(boss: "Boss", projectile: pg.sprite.Sprite) -> bool:
        """Collision tir -> boss : hitbox du tir contre la forme réelle du boss (son masque)."""
        # noinspection unresolved-references
        rect = getattr(projectile, 'hitbox', projectile.rect)
        if not boss.rect.colliderect(rect):
            return False
        offset = (rect.x - boss.rect.x, rect.y - boss.rect.y)
        return boss.mask.overlap(pg.Mask(rect.size, fill=True), offset) is not None

    def check_hits(self, projectiles_group, damage: int, collided=None) -> list[tuple[int, int]]:
        """ Applique les dégâts des tirs touchant le boss. Retourne la position de
        chaque impact, pour laisser l'appelant afficher les nombres de dégâts """
        # noinspection bad-argument-type
        touches = pg.sprite.spritecollide(self, projectiles_group, dokill=True, collided=collided or Boss.collide)
        positions = []
        for touch in touches:
            self.hited(damage)
            positions.append(touch.rect.center)
        return positions

    @classmethod
    def _bar_fill_color(cls, ratio: float) -> tuple[int, int, int]:
        """ Dégradé vert -> jaune -> rouge selon la proportion de vie restante """
        ratio = max(0.0, min(1.0, ratio))
        if ratio >= 0.5:
            t = (ratio - 0.5) / 0.5
            low, high = cls.BAR_FILL_COLOR_MID, cls.BAR_FILL_COLOR_HIGH
        else:
            t = ratio / 0.5
            low, high = cls.BAR_FILL_COLOR_LOW, cls.BAR_FILL_COLOR_MID
        return tuple(int(low[i] + (high[i] - low[i]) * t) for i in range(3))

    def _is_enraged(self) -> bool:
        return self.is_spawn and self.max_life > 0 and 0 < self.life / self.max_life <= self.ENRAGE_THRESHOLD

    def draw_enrage_glow(self, surface: pg.Surface, center: tuple[float, float], radius: float) -> None:
        """ Halo rouge pulsant, affiché derrière le boss quand sa vie passe sous
        ENRAGE_THRESHOLD, pour signaler qu'il devient critique """
        if not self._is_enraged():
            return

        pulse = (math.sin(self.time * (2 * math.pi / self.ENRAGE_GLOW_PERIOD)) + 1) / 2
        max_radius = radius + self.ENRAGE_GLOW_PADDING + self.ENRAGE_GLOW_PULSE_RADIUS * pulse
        size = int(max_radius * 2)
        glow_surface = pg.Surface((size, size), pg.SRCALPHA)
        glow_center = (size // 2, size // 2)

        for layer in range(self.ENRAGE_GLOW_LAYERS, 0, -1):
            layer_radius = int(max_radius * (layer / self.ENRAGE_GLOW_LAYERS))
            alpha = (self.ENRAGE_GLOW_MAX_ALPHA * (0.6 + 0.4 * pulse)) * (1 - layer / (self.ENRAGE_GLOW_LAYERS + 1))
            alpha = max(0, min(255, int(alpha)))
            layer_surface = pg.Surface((size, size), pg.SRCALPHA)
            pg.draw.circle(layer_surface, (*self.ENRAGE_GLOW_COLOR, alpha), glow_center, layer_radius)
            glow_surface.blit(layer_surface, (0, 0), special_flags=pg.BLEND_RGBA_ADD)

        surface.blit(glow_surface, glow_surface.get_rect(center=center))

    def draw_life_bar(self, surface: pg.Surface) -> None:
        """
        Dessine la barre de vie du boss en haut de la surface (à appeler avec le HUD).
        La barre est découpée en autant de crans que le boss a de vies.
        """
        width = int(surface.get_width() * self.BAR_WIDTH_RATIO)
        x = (surface.get_width() - width) // 2
        y = self.BAR_MARGIN
        contour = pg.Rect(x, y, width, self.BAR_HEIGHT)

        pg.draw.rect(surface, self.BAR_BACK_COLOR, contour)

        # Bande claire qui rattrape la vraie vie après un coup, dessinée derrière
        # le remplissage réel pour rester visible comme une traînée qui se résorbe
        drain_width = int(width * self.bar_display_life / self.max_life)
        if drain_width > 0:
            pg.draw.rect(surface, self.BAR_DRAIN_COLOR, pg.Rect(x, y, drain_width, self.BAR_HEIGHT))

        remplissage = int(width * self.life / self.max_life)
        if remplissage > 0:
            fill_color = self._bar_fill_color(self.life / self.max_life)
            pg.draw.rect(surface, fill_color, pg.Rect(x, y, remplissage, self.BAR_HEIGHT))

        # Séparations entre les vies, tant qu'elles restent lisibles
        pas = width / Boss.LIVES
        if pas >= self.BAR_MIN_SEGMENT:
            for i in range(1, Boss.LIVES):
                sep_x = x + int(i * pas)
                pg.draw.line(surface, self.BAR_BORDER_COLOR, (sep_x, y), (sep_x, y + self.BAR_HEIGHT - 1))

        pg.draw.rect(surface, self.BAR_BORDER_COLOR, contour, 2)

        if self._is_enraged():
            pulse = (math.sin(self.time * (2 * math.pi / self.ENRAGE_GLOW_PERIOD)) + 1) / 2
            alpha = int(90 + 100 * pulse)
            halo_rect = contour.inflate(10, 10)
            halo_surface = pg.Surface(halo_rect.size, pg.SRCALPHA)
            pg.draw.rect(halo_surface, (*self.ENRAGE_GLOW_COLOR, alpha), halo_surface.get_rect(), width=4, border_radius=6)
            surface.blit(halo_surface, halo_rect.topleft)

    def _mouth(self) -> tuple[int, int]:
        """
        Point d'où sortent les bombes : le bas de la silhouette du boss.
        On descend la colonne centrale du masque jusqu'au dernier pixel plein,
        sinon les bombes apparaîtraient sous le rect, dans le vide.
        """
        cx = self.image.get_width() // 2
        for y in range(self.image.get_height() - 1, -1, -1):
            if self.mask.get_at((cx, y)):
                return self.rect.x + cx, self.rect.y + y
        return self.rect.midbottom

    def drop_bomb(self) -> Bomb | None:
        """Lâche une bombe depuis le bas du boss ciblée vers le joueur."""
        active = [b for b in self.datas.bombs_group if isinstance(b, Bomb) and not b.exploding]
        if len(active) >= self.MAX_BOMBS:
            return None

        # On récupère les positions
        mouth_pos = pg.Vector2(self._mouth())
        player_pos = pg.Vector2(self.player.rect.center)

        # Calcul du vecteur (Destination - Origine)
        direction = player_pos - mouth_pos
        if direction.length_squared() > 0:
            direction = direction.normalize()
        else:
            direction = pg.Vector2(0, 1)

        # On ajoute la vitesse
        speed = Bomb.SPEED_Y * 2 if self._is_enraged() else Bomb.SPEED_Y
        velocity = direction * speed

        # On crée la bombe
        return Bomb(self._mouth(), velocity, self.datas.screen, self.datas.bombs_group)

    def detonate(self) -> None:
        """Fait exploser toutes les bombes lâchées par ce boss."""
        for bomb in self.datas.bombs_group:
            bomb.explode()

    def bombs_hitting(self, target: pg.sprite.Sprite) -> list[Bomb]:
        """
        Retourne les bombes qui touchent target (collision au pixel près).
        Une bombe qui tombe sur la cible explose au contact.
        """
        # noinspection bad-argument-type
        hits = pg.sprite.spritecollide(target, self.datas.bombs_group, False, pg.sprite.collide_mask)
        for bomb in hits:
            bomb.explode()
        return hits

    def boss_hitting(self, target: pg.sprite.Sprite):
        """
        Retourne les bombes qui touchent target (collision au pixel près).
        Une bombe qui tombe sur la cible explose au contact.
        """
        # noinspection bad-argument-type
        hits = pg.sprite.spritecollide(target, self.datas.boss_group, False, pg.sprite.collide_mask)
        return hits

    def fire_multi_laser(self):
        spread = 80
        count = 11 if self._is_enraged() else 7

        mouth_pos = pg.Vector2(self._mouth())
        player_pos = pg.Vector2(self.player.rect.center)
        direction = player_pos - mouth_pos

        if direction.length_squared() > 0:
            center_angle = math.degrees(math.atan2(direction.y, direction.x))
        else:
            center_angle = 90

        start_angle = center_angle - (spread / 2)

        telegraph = MultiLaser(self._mouth(), self.datas, start_angle, spread, count, Boss.laser_images)
        self.datas.bombs_group.add(telegraph)

    def fire_tracker(self):
        mouth_pos = pg.Vector2(self._mouth())
        SpawnPing(mouth_pos, self.datas.particles_group)
        Tracker(mouth_pos, self.player, self.datas, self.datas.enemies_group)
