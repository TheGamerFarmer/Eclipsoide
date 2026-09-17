import pygame as pg
import os

from boss.bomb import Bomb
from coin_popup import CoinPopup
from datas import Datas
from explosion import Explosion
from hud import Hud
from player import Player


class Boss(pg.sprite.Sprite):
    """
    Interface commune pour touts les bosses du jeu.
    """
    BOSS_SIZE = 70
    GROW_DURATION = 2000
    BOSS_MAX_SIZE = 620
    # Chaque boss vaincu rend le suivant 1,5 fois plus résistant
    BOSS_LIFE_GROWTH = 1.5
    BOMB_INTERVAL = 1500  # millisecondes entre deux bombes
    MAX_BOMBS = 5
    SPEED = 0.1  # pixels par milliseconde
    FRAME_DURATION = 100  # millisecondes par image d'animation

    # Le boss a LIVES "vies" (les crans de la barre). Au premier palier chacune
    # encaisse LIFE_PER_SEGMENT points, soit 3 à 4 tirs du joueur (40 par tir).
    LIFE_PER_SEGMENT = 140
    LIVES = 20
    LIFE = LIVES * LIFE_PER_SEGMENT  # 2800 pv, environ 70 tirs

    # Barre de vie affichée en haut de l'écran
    BAR_WIDTH_RATIO = 0.6  # proportion de la largeur de l'écran
    BAR_HEIGHT = 18
    BAR_MARGIN = 14
    BAR_BACK_COLOR = (60, 20, 30)
    BAR_FILL_COLOR = (230, 70, 70)
    BAR_BORDER_COLOR = (255, 255, 255)
    BAR_MIN_SEGMENT = 6  # en dessous, on n'affiche plus les séparations

    HIT_FLASH_DURATION = 90  # ms de flash blanc quand touché
    DAMAGE_POPUP_COLOR = (255, 255, 255)

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
        flash.fill((255, 255, 255, 0), special_flags=pg.BLEND_RGBA_ADD)
        return flash

    def _set_image(self, image: pg.Surface) -> None:
        """ Fixe l'apparence "normale" du boss et prépare sa version flashée en
        blanc (rejouée brièvement à chaque coup) ; à rappeler chaque fois que
        l'image change (arrivée, palier suivant) """
        self.normal_image = image
        self.flash_image = self._build_flash_image(image)
        self.image = self.normal_image if self.hit_flash_timer <= 0 else self.flash_image

    def __init__(self, datas: Datas, player: Player, *groups):
        pg.sprite.Sprite.__init__(self, *groups)

        self.datas = datas
        self.player = player
        self.is_spawn = False

        self.max_life = int(Boss.LIFE * Boss.BOSS_LIFE_GROWTH ** (self.datas.stage - 1))
        self.life = self.max_life

        self._base_image = pg.image.load('images/boss1.png').convert_alpha()
        self.hit_flash_timer = 0
        self._set_image(self._base_image)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.normal_image)

        self.bomb_timer = 0
        self._detonate_was_pressed = False

        self.boss_bar_font = pg.font.Font(os.path.join('images/ui', 'Font', 'Kenney Future.ttf'), 24)

    def _boss_vaincu(self):
        """ Le boss explose, le palier suivant démarre : les vagues reprennent """
        Explosion(pg.Vector2(self.rect.center), self.datas.explosions_group)
        self.datas.bombs_group.empty()
        self.is_spawn = False
        self.datas.stage += 1
        self.max_life = int(Boss.LIFE * Boss.BOSS_LIFE_GROWTH ** (self.datas.stage - 1))
        self.life = self.max_life
        self.hit_flash_timer = 0
        self._set_image(self._base_image)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.normal_image)
        self.bomb_timer = 0
        # Remettre l'horloge à zéro relance les vagues d'ennemis, puis l'arrivée
        # du boss suivant une fois TIME_BEFORE_BOSS écoulé
        self.datas.time = 0

    def update(self, dt) -> None:
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
            self.image = self.flash_image if self.hit_flash_timer > 0 else self.normal_image

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

        if self.is_spawn:
            self.bomb_timer += dt
            if self.bomb_timer >= self.BOMB_INTERVAL:
                self.bomb_timer -= self.BOMB_INTERVAL
                self.drop_bomb()

            self.datas.bombs_group.update(dt)

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
        remplissage = int(width * self.life / self.max_life)
        if remplissage > 0:
            pg.draw.rect(surface, self.BAR_FILL_COLOR, pg.Rect(x, y, remplissage, self.BAR_HEIGHT))

        # Séparations entre les vies, tant qu'elles restent lisibles
        pas = width / Boss.LIVES
        if pas >= self.BAR_MIN_SEGMENT:
            for i in range(1, Boss.LIVES):
                sep_x = x + int(i * pas)
                pg.draw.line(surface, self.BAR_BORDER_COLOR, (sep_x, y), (sep_x, y + self.BAR_HEIGHT - 1))

        pg.draw.rect(surface, self.BAR_BORDER_COLOR, contour, 2)

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
        """Lâche une bombe depuis le bas du boss, si la limite n'est pas atteinte."""
        active = [b for b in self.datas.bombs_group if not b.exploding]
        if len(active) >= self.MAX_BOMBS:
            return None
        return Bomb(self._mouth(), self.datas.screen, self.datas.bombs_group)

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