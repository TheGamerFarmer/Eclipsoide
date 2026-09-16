import os
import sys

import math
# Utilisation de pygame avec un préfixe plus simple
import pygame as pg

from Menu.menu_game_over import GameOver
# Accès à la classe Enemy
from enemy import Enemy
from player import Player
from coin import Coin
from coin_popup import CoinPopup

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

        self.coin_font = pg.font.Font(os.path.join('images/ui', 'Font', 'Kenney Future.ttf'), 24)
        self.coin_icon = pg.transform.scale(pg.image.load('images/ui/Coins/coin_0.png'), (24, 24))
        # Création d'une instance du joueur
        self.player = Player(screen, 0.3, self.projectiles_group, self.particles_group, self.player_group)
        # Création du groupe du joueur

        self.menu_game_over = GameOver(self.screen.get_width(), self.screen.get_height())

        # Vrai si le jeu est fini
        self.isEnded = False

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

        if (self.time + dt) % self.TIME_BETWEEN_WAVE < dt and self.time < self.TIME_BEFORE_BOSS:
            nbEnemies: int = int(self.time / self.TIME_BETWEEN_WAVE / 2)
            for i in range(-2, nbEnemies):
                Enemy(self.screen, self.player, self.enemy_projectiles_group, self.enemies_group)

        self.sun_angle = (self.sun_angle + self.SUN_ROTATION_SPEED * dt) % 360


        self.time += dt

        # Collisions entre le joueur et les ennemies
        if pg.sprite.spritecollide(self.player, self.enemies_group, dokill=False):
            self.player.on_hit()

        # Collisions entre le joueur et les projectiles ennemies
        # (on collisionne sur la hitbox du tir, pas sur son rect visuel qui
        # inclut le halo et la traînée)
        if pg.sprite.spritecollide(self.player, self.enemy_projectiles_group, dokill=True, collided=collide_projectile):
            self.player.on_hit()

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

        # Le joueur ramasse les pièces qu'il croise (aspirées automatiquement vers lui)
        collected_coins = pg.sprite.spritecollide(self.player, self.coins_group, dokill=True)
        if collected_coins:
            self.player.add_coins(len(collected_coins) * Coin.VALUE)
            for coin in collected_coins:
                CoinPopup(pg.Vector2(coin.rect.center), Coin.VALUE, self.popups_group)

        if self.player.is_alive == False:
            self.isEnded = True
            #Eclipsoide.pause = True

        # Met à jours tous les sprites en fonction du temps qui a passé
        self.enemies_group.update(dt)
        self.player_group.update(dt)
        self.projectiles_group.update(dt)
        self.enemy_projectiles_group.update(dt)
        self.coins_group.update(dt)
        self.popups_group.update(dt)
        self.particles_group.update(dt)

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

        self.screen.blit(self.sun_image, (self.screen.get_width() / 2 - self.SUN_SIZE / 2, self.SUN_SIZE / 4))

        self.screen.blit(scaled_boss, (bossX, (self.SUN_SIZE / 4) + (self.SUN_SIZE / 2) - (current_size / 2)))

        self._draw_sun()
        # Dessine tous les sprites dans la surface de l'écran
        self.enemies_group.draw(self.screen)
        self.particles_group.draw(self.screen)
        self.player_group.draw(self.screen)
        self.projectiles_group.draw(self.screen)
        self.enemy_projectiles_group.draw(self.screen)
        self.coins_group.draw(self.screen)
        self.popups_group.draw(self.screen)

        # Affiche le compteur de pièces en haut à gauche
        self.screen.blit(self.coin_icon, (10, 10))
        coin_text = self.coin_font.render(str(self.player.coins), True, (255, 220, 80))
        self.screen.blit(coin_text, (40, 10))