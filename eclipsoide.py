import os
import sys
import random

import math
# Utilisation de pygame avec un préfixe plus simple
import pygame as pg

from Menu.menu_game_over import GameOver
# Accès à la classe Enemy
from enemy import Enemy
from player import Player
from coin import Coin
from coin_popup import CoinPopup
from explosion import Explosion
from heart_pickup import HeartPickup

def collide_projectile(a: pg.sprite.Sprite, b: pg.sprite.Sprite) -> bool:
    """ Collision utilisant la hitbox du projectile plutôt que son rect visuel (halo + traînée) """
    rect_a = getattr(a, 'hitbox', a.rect)
    rect_b = getattr(b, 'hitbox', b.rect)
    return rect_a.colliderect(rect_b)

# Définition du jeu Pong
class Eclipsoide:
    # time between wave in milliseconds
    TIME_BETWEEN_WAVE = 5000
    VITESSE_BOSS = 0.1  # pixels par milliseconde
    SUN_SIZE = 200
    TIME_BEFORE_BOSS = 300000
    BOSS_SIZE = 70
    GROW_DURATION = 2000
    BOSS_MAX_SIZE = 620

    # Rotation lente + légère pulsation/glow du soleil
    SUN_ROTATION_SPEED = 0.006  # degrés par milliseconde (~1 tour par minute)
    SUN_PULSE_PERIOD = 3000     # ms pour un cycle complet de pulsation
    SUN_PULSE_AMPLITUDE = 0.035 # variation de taille (+/- 3.5%)
    SUN_GLOW_COLOR = (255, 170, 60)
    SUN_GLOW_LAYERS = 3
    SUN_GLOW_PADDING = 25
    SUN_GLOW_MAX_ALPHA = 55
    SUN_GLOW_PULSE_RADIUS = 10
    SUN_GLOW_PULSE_ALPHA = 20

    # Délai (explosion du joueur) avant d'afficher l'écran de game over
    DEATH_COOLDOWN = 1300  # ms

    # Flash rouge plein écran, bref, au moment exact où un coup est encaissé
    HIT_FLASH_DURATION = 180  # ms
    HIT_FLASH_COLOR = (255, 30, 30)
    HIT_FLASH_MAX_ALPHA = 130

    # Même principe mais en vert, au moment où une vie est récupérée
    HEAL_FLASH_DURATION = 180  # ms
    HEAL_FLASH_COLOR = (40, 255, 90)
    HEAL_FLASH_MAX_ALPHA = 130

    # Fondu rouge sur les bords quand il ne reste plus qu'un coeur
    LOW_HEALTH_THRESHOLD = 1
    VIGNETTE_COLOR = (200, 0, 0)
    VIGNETTE_PULSE_PERIOD = 700  # ms pour un cycle de pulsation (effet "battement")
    VIGNETTE_MIN_ALPHA = 50
    VIGNETTE_MAX_ALPHA = 140

    # Chance qu'un ennemi tué drop un coeur (uniquement si le joueur n'est pas déjà à vie max)
    HEART_DROP_CHANCE = 0.12
    HEART_POPUP_COLOR = (255, 90, 120)

    # Petit "pop" (grossit puis revient à la normale) sur le compteur de pièces
    COIN_POP_DURATION = 220  # ms
    COIN_POP_AMPLITUDE = 0.45  # +45% de taille au pic

    # Simulation de collision : une cible automatique qui patrouille en bas
    VITESSE_CIBLE = 0.25  # pixels par milliseconde
    VIE_CIBLE = 100
    DEGATS_EXPLOSION = 20
    DUREE_FLASH = 150  # millisecondes
    COULEUR_CIBLE = (0, 200, 255)
    COULEUR_CIBLE_TOUCHEE = (255, 255, 255)

    # variable de classe pour mettre le jeu en pause pour débug
    pause = False
    time = 0

    def __init__(self,screen: pg.Surface):
        """ Création des attribut du jeux """
        # Conserve le lien vers l'objet surface ecran du jeux
        self.screen = screen

        self.bg_image1 = pg.image.load('images/backgroundGame1.png')
        self.bg_image1 = pg.transform.scale(self.bg_image1, (screen.get_width(), screen.get_height()))
        self.bg_image2 = pg.image.load('images/backgroundGame2.png')
        self.bg_image2 = pg.transform.scale(self.bg_image2, (screen.get_width(), screen.get_height()))

        self.sun_image = pg.image.load('images/sun.png')
        self.sun_image = pg.transform.scale(self.sun_image, (self.SUN_SIZE, self.SUN_SIZE))
        self.sun_angle = 0.0
        self.sun_center = (screen.get_width() / 2, self.SUN_SIZE * 0.75)

        self.boss_image = pg.image.load('images/boss1.png')
        self.boss_image = pg.transform.scale(self.boss_image, (self.BOSS_SIZE, self.BOSS_SIZE))

        # Objet sous groupe pour avoir la liste des sprites et automatiser la mise à jour par update()
        # Automatise aussi l'affichage : draw() par défaut affiche dans l'écran image à la position rect
        self.enemies_group = pg.sprite.Group()
        self.player_group = pg.sprite.Group()
        self.projectiles_group = pg.sprite.Group()
        self.enemy_projectiles_group = pg.sprite.Group()
        self.coins_group = pg.sprite.Group()
        self.popups_group = pg.sprite.Group()
        self.particles_group = pg.sprite.Group()
        self.explosions_group = pg.sprite.Group()
        self.hearts_group = pg.sprite.Group()

        self.coin_font = pg.font.Font(os.path.join('images/ui', 'Font', 'Kenney Future.ttf'), 24)
        self.coin_icon = pg.transform.scale(pg.image.load('images/ui/Coins/coin_0.png'), (24, 24))
        self.heart_full_icon = pg.transform.scale(pg.image.load('images/ui/Hearts/heart_full.png'), (22, 22))
        self.heart_empty_icon = pg.transform.scale(pg.image.load('images/ui/Hearts/heart_empty.png'), (22, 22))
        # Création d'une instance du joueur
        self.player = Player(screen, 0.3, self.projectiles_group, self.particles_group, self.player_group)
        # Création du groupe du joueur

        self.vignette_surface = self._build_vignette(self.VIGNETTE_COLOR)

        self.menu_game_over = GameOver(self.screen.get_width(), self.screen.get_height())

        # Vrai si le jeu est fini
        self.isEnded = False
        # None tant que le joueur est vivant ; sinon, ms restantes avant le game over
        self.death_timer = None
        self.hit_flash_timer = 0
        self.heal_flash_timer = 0
        self.coin_pop_timer = 0

    def isRunning(self):
        """
        Examine l'état du jeux et les actions pour savoir si le jeux continu
        Retourne vrai si le jeu n'est pas terminé
        """
        if self.isEnded:
            return False

        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    # On ferme la fenêtre
                    pg.quit()
                    sys.exit(0)

                # Un appui sur une touche
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_f:
                            # Touche 'f' passe en fullscreen ou revient en mode window
                            pg.display.toggle_fullscreen()
                        case pg.K_ESCAPE:
                            # alterne la pause
                            Eclipsoide.pause = not Eclipsoide.pause
        return True

    def update(self,dt : int):
        """
        Met à jour l'état du jeux en fonction du temps dt écoulé
        et des touches préssées par le joueur
        """
        # Si le jeu est en pause, ne modifie plus rien
        if Eclipsoide.pause:
            return

        self.hit_flash_timer = max(0, self.hit_flash_timer - dt)
        self.heal_flash_timer = max(0, self.heal_flash_timer - dt)
        self.coin_pop_timer = max(0, self.coin_pop_timer - dt)

        # Séquence de mort en cours : on laisse l'explosion du joueur se jouer
        # (le reste de la partie reste figé) avant de basculer sur le game over
        if self.death_timer is not None:
            self.death_timer -= dt
            self.explosions_group.update(dt)
            self.particles_group.update(dt)
            if self.death_timer <= 0:
                self.isEnded = True
            return

        self.sun_angle = (self.sun_angle + self.SUN_ROTATION_SPEED * dt) % 360
        
        if (self.time + dt) % self.TIME_BETWEEN_WAVE < dt and self.time < self.TIME_BEFORE_BOSS:
            nbEnemies: int = int(self.time / self.TIME_BETWEEN_WAVE / 2)
            for i in range(-2, nbEnemies):
                Enemy(self.screen, self.player, self.enemy_projectiles_group, self.enemies_group)

        self.sun_angle = (self.sun_angle + self.SUN_ROTATION_SPEED * dt) % 360


        self.time += dt

        # Collisions entre le joueur et les ennemies
        if pg.sprite.spritecollide(self.player, self.enemies_group, dokill=False):
            if self.player.on_hit():
                self.hit_flash_timer = self.HIT_FLASH_DURATION

        # Collisions entre le joueur et les projectiles ennemies
        # (on collisionne sur la hitbox du tir, pas sur son rect visuel qui
        # inclut le halo et la traînée)
        if pg.sprite.spritecollide(self.player, self.enemy_projectiles_group, dokill=True, collided=collide_projectile):
            if self.player.on_hit():
                self.hit_flash_timer = self.HIT_FLASH_DURATION

        # Collisions entre les projectiles du joueur et les ennemies
        collisions = pg.sprite.groupcollide(self.projectiles_group, self.enemies_group, dokilla=True, dokillb=False, collided=collide_projectile)
        if collisions:
            for enemies in collisions.values():
                for enemy in enemies:
                    if type(enemy) == Enemy:
                        was_alive = enemy.life > 0
                        enemy.hited(40)
                        if was_alive and enemy.life <= 0:
                            Coin(pg.Vector2(enemy.rect.center), self.player, self.coins_group)
                            Explosion(pg.Vector2(enemy.rect.center), self.explosions_group)
                            if self.player.lives < Player.MAX_LIVES and random.random() < self.HEART_DROP_CHANCE:
                                HeartPickup(pg.Vector2(enemy.rect.center), self.player, self.hearts_group)

        # Le joueur ramasse les pièces qu'il croise (aspirées automatiquement vers lui)
        collected_coins = pg.sprite.spritecollide(self.player, self.coins_group, dokill=True)
        if collected_coins:
            self.player.add_coins(len(collected_coins) * Coin.VALUE)
            self.coin_pop_timer = self.COIN_POP_DURATION
            for coin in collected_coins:
                CoinPopup(pg.Vector2(coin.rect.center), Coin.VALUE, self.popups_group)

        # Le joueur ramasse les coeurs qu'il croise (une vie de plus, plafonnée au max)
        collected_hearts = pg.sprite.spritecollide(self.player, self.hearts_group, dokill=True)
        for heart in collected_hearts:
            if self.player.lives < Player.MAX_LIVES:
                self.player.lives += 1
                CoinPopup(pg.Vector2(heart.rect.center), 1, self.popups_group, color=self.HEART_POPUP_COLOR)
                self.heal_flash_timer = self.HEAL_FLASH_DURATION

        if self.player.is_alive == False:
            self.death_timer = self.DEATH_COOLDOWN
            Explosion(pg.Vector2(self.player.rect.center), self.explosions_group)

        # Met à jours tous les sprites en fonction du temps qui a passé
        self.enemies_group.update(dt)
        self.player_group.update(dt)
        self.projectiles_group.update(dt)
        self.enemy_projectiles_group.update(dt)
        self.coins_group.update(dt)
        self.hearts_group.update(dt)
        self.popups_group.update(dt)
        self.particles_group.update(dt)
        self.explosions_group.update(dt)

    def _draw_sun(self):
        """ Dessine le soleil avec une légère rotation continue et une pulsation de taille/glow """
        pulse_wave = math.sin(self.time * (2 * math.pi / self.SUN_PULSE_PERIOD))
        pulse_scale = 1 + self.SUN_PULSE_AMPLITUDE * pulse_wave

        self._draw_sun_glow(pulse_wave)

        rotated_sun = pg.transform.rotozoom(self.sun_image, self.sun_angle, pulse_scale)
        self.screen.blit(rotated_sun, rotated_sun.get_rect(center=self.sun_center))

    def _draw_sun_glow(self, pulse_wave: float):
        base_radius = self.SUN_SIZE / 2
        max_radius = base_radius + self.SUN_GLOW_PADDING + self.SUN_GLOW_PULSE_RADIUS * pulse_wave
        size = int(max_radius * 2)
        glow_surface = pg.Surface((size, size), pg.SRCALPHA)
        glow_center = (size // 2, size // 2)

        for layer in range(self.SUN_GLOW_LAYERS, 0, -1):
            radius = int(max_radius * (layer / self.SUN_GLOW_LAYERS))
            alpha = (self.SUN_GLOW_MAX_ALPHA + self.SUN_GLOW_PULSE_ALPHA * pulse_wave) * (1 - layer / (self.SUN_GLOW_LAYERS + 1))
            alpha = max(0, min(255, int(alpha)))
            layer_surface = pg.Surface((size, size), pg.SRCALPHA)
            pg.draw.circle(layer_surface, (*self.SUN_GLOW_COLOR, alpha), glow_center, radius)
            glow_surface.blit(layer_surface, (0, 0), special_flags=pg.BLEND_RGBA_ADD)

        self.screen.blit(glow_surface, glow_surface.get_rect(center=self.sun_center))

    # Rayon (proportion de la distance centre -> coin) à partir duquel le
    # fondu commence à apparaître : en dessous, l'écran reste intact
    VIGNETTE_INNER_RATIO = 0.55

    def _build_vignette(self, color: tuple[int, int, int]) -> pg.Surface:
        """ Construit une fois un dégradé radial rouge, transparent au centre et
        de plus en plus visible vers les bords/coins. Calculé à basse résolution
        (c'est un simple dégradé, pas de détail à préserver) puis lissé en
        l'agrandissant, pour éviter une boucle pixel par pixel sur tout l'écran """
        width, height = self.screen.get_width(), self.screen.get_height()
        small_w, small_h = 80, 60
        small = pg.Surface((small_w, small_h), pg.SRCALPHA)

        cx, cy = small_w / 2, small_h / 2
        max_dist = math.hypot(cx, cy)
        for y in range(small_h):
            for x in range(small_w):
                dist_ratio = math.hypot(x - cx, y - cy) / max_dist
                t = max(0.0, min(1.0, (dist_ratio - self.VIGNETTE_INNER_RATIO) / (1 - self.VIGNETTE_INNER_RATIO)))
                alpha = int(255 * t ** 2)
                small.set_at((x, y), (*color, alpha))

        return pg.transform.smoothscale(small, (width, height))

    def _draw_coin_counter(self):
        icon_rect = self.coin_icon.get_rect(topleft=(10, 10))
        coin_text = self.coin_font.render(str(self.player.coins), True, (255, 220, 80))
        text_rect = coin_text.get_rect(topleft=(40, 10))

        scale = 1.0
        if self.coin_pop_timer > 0:
            elapsed = 1 - (self.coin_pop_timer / self.COIN_POP_DURATION)
            scale = 1 + self.COIN_POP_AMPLITUDE * math.sin(math.pi * elapsed)

        icon_surface = self.coin_icon
        text_surface = coin_text
        if scale != 1.0:
            icon_surface = pg.transform.smoothscale(self.coin_icon, (max(1, int(icon_rect.width * scale)), max(1, int(icon_rect.height * scale))))
            text_surface = pg.transform.smoothscale(coin_text, (max(1, int(text_rect.width * scale)), max(1, int(text_rect.height * scale))))

        self.screen.blit(icon_surface, icon_surface.get_rect(center=icon_rect.center))
        self.screen.blit(text_surface, text_surface.get_rect(center=text_rect.center))

    def _draw_full_screen_flash(self, timer: float, duration: float, color: tuple[int, int, int], max_alpha: int):
        if timer <= 0:
            return

        ratio = timer / duration
        alpha = int(max_alpha * ratio)
        flash = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        flash.fill((*color, alpha))
        self.screen.blit(flash, (0, 0))

    def _draw_low_health_vignette(self):
        if self.player.lives > self.LOW_HEALTH_THRESHOLD:
            return

        pulse = (math.sin(self.time * (2 * math.pi / self.VIGNETTE_PULSE_PERIOD)) + 1) / 2
        alpha = int(self.VIGNETTE_MIN_ALPHA + (self.VIGNETTE_MAX_ALPHA - self.VIGNETTE_MIN_ALPHA) * pulse)
        self.vignette_surface.set_alpha(alpha)
        self.screen.blit(self.vignette_surface, (0, 0))

    def draw(self):
        """ Dessine le nouvel état du jeu """
        # Redessine le fond entier

        initPos = self.screen.get_width() + self.BOSS_SIZE
        finalPos = self.screen.get_width() / 2 - self.SUN_SIZE / 2

        currentPos = initPos - ((initPos - finalPos) / self.TIME_BEFORE_BOSS * self.time)

        # Croissance après l'arrivée
        grow_time = min(max(self.time - self.TIME_BEFORE_BOSS, 0), self.GROW_DURATION)
        grow_ratio = grow_time / self.GROW_DURATION
        current_size = int(self.BOSS_SIZE + (self.BOSS_MAX_SIZE - self.BOSS_SIZE) * grow_ratio)
        scaled_boss = pg.transform.scale(self.boss_image, (current_size, current_size))


        bossX = max(self.screen.get_width() / 2 - current_size / 2, currentPos)

        if self.time > self.TIME_BEFORE_BOSS:
            bossX = self.screen.get_width() / 2 - current_size / 2

        self.screen.blit(self.bg_image1, (0, 0))

        self.bg_image2.set_alpha(int(grow_ratio * 255))
        self.screen.blit(self.bg_image2, (0, 0))

        self._draw_sun()
        
        self.screen.blit(scaled_boss, (bossX, (self.SUN_SIZE / 4) + (self.SUN_SIZE / 2) - (current_size / 2)))

        # Dessine tous les sprites dans la surface de l'écran
        self.enemies_group.draw(self.screen)
        self.explosions_group.draw(self.screen)
        self.particles_group.draw(self.screen)
        self.player_group.draw(self.screen)
        self.projectiles_group.draw(self.screen)
        self.enemy_projectiles_group.draw(self.screen)
        self.coins_group.draw(self.screen)
        self.hearts_group.draw(self.screen)
        self.popups_group.draw(self.screen)

        self._draw_full_screen_flash(self.hit_flash_timer, self.HIT_FLASH_DURATION, self.HIT_FLASH_COLOR, self.HIT_FLASH_MAX_ALPHA)
        self._draw_full_screen_flash(self.heal_flash_timer, self.HEAL_FLASH_DURATION, self.HEAL_FLASH_COLOR, self.HEAL_FLASH_MAX_ALPHA)
        self._draw_low_health_vignette()

        # Affiche le compteur de pièces en haut à gauche
        self._draw_coin_counter()

        # Affiche les vies restantes juste en dessous (coeurs pleins/vides)
        for i in range(Player.MAX_LIVES):
            icon = self.heart_full_icon if i < self.player.lives else self.heart_empty_icon
            self.screen.blit(icon, (10 + i * 26, 44))