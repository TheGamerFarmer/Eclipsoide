import sys
import random
import math

# Utilisation de pygame avec un préfixe plus simple
import pygame as pg

import settings
from Menu.menu_game_over import GameOver
from boss.boss import Boss
from datas import Datas
from coin_popup import CoinPopup
# Accès à la classe Enemy
from enemy import Enemy
from player import Player
from coin import Coin
from explosion import Explosion
from heart_pickup import HeartPickup
from shield_pickup import ShieldPickup
from hud import Hud

# Définition du jeu Pong
class Eclipsoide:
    # Chance qu'un ennemi tué drop un coeur (uniquement si le joueur n'est pas déjà à vie max)
    HEART_POPUP_COLOR = (255, 90, 120)

    # Chance qu'un ennemi tué drop un bouclier (plus rare que les coeurs,
    # uniquement si le joueur n'en a pas déjà un actif)
    SHIELD_DROP_CHANCE = 0.01
    SHIELD_POPUP_COLOR = (150, 200, 255)

    # Nombres de dégâts flottants affichés sur les ennemis/le boss touchés
    DAMAGE_POPUP_COLOR = (255, 255, 255)

    # Télégraphe d'apparition : petit marqueur qui pulse en haut de l'écran
    # juste avant qu'un ennemi n'entre dans le champ (encore au-dessus, invisible)
    SPAWN_WARNING_DISTANCE = 150  # px au-dessus de l'écran, distance à partir de laquelle le marqueur apparaît
    SPAWN_WARNING_COLOR = (255, 140, 40)
    SPAWN_WARNING_PULSE_PERIOD = 260  # ms

    # Simulation de collision : une cible automatique qui patrouille en bas
    VITESSE_CIBLE = 0.25  # pixels par milliseconde
    VIE_CIBLE = 100
    DEGATS_EXPLOSION = 20
    DUREE_FLASH = 150  # millisecondes
    COULEUR_CIBLE = (0, 200, 255)
    COULEUR_CIBLE_TOUCHEE = (255, 255, 255)

    # Passe à False avant de livrer : coupe les raccourcis de debug (B / N)
    DEBUG = True

    # variable de classe pour mettre le jeu en pause pour débug
    pause = False
    time = 0

    def __del__(self):
        del self.player
        del self.datas
        del self.screen
        del self.boss
        del self.hud
        del self.isEnded
        del self.menu_game_over
        del self
        print("new Eclipsoide")


    def __init__(self,screen: pg.Surface):
        """ Création des attribut du jeux """
        # Conserve le lien vers l'objet surface ecran du jeux
        self.screen = screen
        # Surface intermédiaire utilisée pour le tremblement d'écran : tout le
        # rendu y est redirigé pendant l'effet, puis blitée sur l'écran réel
        # avec un décalage aléatoire (voir draw())
        self._frame_buffer = pg.Surface(screen.get_size())

        # Objet sous groupe pour avoir la liste des sprites et automatiser la mise à jour par update()
        # Automatise aussi l'affichage : draw() par défaut affiche dans l'écran image à la position rect
        self.datas = Datas(screen)

        self.pause = False

        # Création d'une instance du joueur
        self.player = Player(self.datas, self.datas.player_group)

        # Soleil animé, HUD (pièces/vies) et effets d'écran (flashs, vignette,
        # tremblement d'écran) : créé avant le boss, qui s'en sert pour trigger_shake()
        self.hud = Hud(screen, self.player)

        #Création du boss
        self.boss = Boss(self.datas, self.player, self.hud, self.datas.boss_group)

        self.menu_game_over = GameOver(self.screen.get_width(), self.screen.get_height())

        # Vrai si le jeu est fini
        self.isEnded = False
        # None tant que le joueur est vivant ; sinon, ms restantes avant le game over
        self.death_timer : int | None = None

    def isRunning(self):
        """
        Examine l'état du jeux et les actions pour savoir si le jeux continu
        Retourne vrai si le jeu n'est pas terminé
        """
        if self.isEnded:
            return False

        for event in pg.event.get():
            self.hud.handle_event(event)
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
                            settings.toggle_fullscreen()
                        case pg.K_ESCAPE | pg.K_p:
                            # alterne la pause
                            self.pause = not self.pause
        return True

    def update(self,dt : int):
        """
        Met à jour l'état du jeux en fonction du temps dt écoulé
        et des touches préssées par le joueur
        """
        # Si le jeu est en pause, ne modifie plus rien
        if self.pause:
            return

        self.hud.update_timers(dt)

        # Séquence de mort en cours : on laisse l'explosion du joueur se jouer
        # (le reste de la partie reste figé) avant de basculer sur le game over
        if self.death_timer is not None:
            self.death_timer -= dt
            self.datas.explosions_group.update(dt)
            self.datas.particles_group.update(dt)
            if self.death_timer <= 0:
                self.isEnded = True
            return

        self.hud.advance(dt)

        if (self.datas.time + dt) % Datas.TIME_BETWEEN_WAVE < dt and self.datas.time < Datas.TIME_BEFORE_BOSS:
            nbEnemies: int = int(self.datas.time / Datas.TIME_BETWEEN_WAVE / 6)
            for i in range(-2, nbEnemies):
                Enemy(self.screen, self.player, self.datas, self.datas.enemies_group)

        self.datas.time += dt

        # Le joueur encaisse les coups (contact ennemi, tir ennemi, bombe du boss)
        hit_outcome = self.player.check_hits(self.datas.enemies_group, self.datas.enemy_projectiles_group, self.boss)
        if hit_outcome == Player.HIT_TAKEN:
            self.hud.trigger_hit_flash()
        elif hit_outcome == Player.HIT_SHIELDED:
            self.hud.trigger_shield_pulse()

        # Collisions entre les projectiles du joueur et les ennemies
        for enemy, died in Enemy.check_hits(self.datas, self.player.damage):
            CoinPopup(pg.Vector2(enemy.rect.center), round(self.player.damage, 0), self.datas.popups_group, color=self.DAMAGE_POPUP_COLOR, prefix="-")
            if died:
                # Rapproche l'arrivée du boss : tuer plus vite le fait venir plus tôt
                self.datas.time += Datas.KILL_TIME_BONUS
                Coin(pg.Vector2(enemy.rect.center), self.player, self.datas.coins_group, datas=self.datas)
                Explosion(pg.Vector2(enemy.rect.center), self.datas.explosions_group)
                if self.player.lives < self.player.max_lives and random.random() < self.player.heart_drop_chance:
                    HeartPickup(pg.Vector2(enemy.rect.center), self.player, self.datas.hearts_group, datas=self.datas)
                if self.player.shield_timer <= 0 and random.random() < self.SHIELD_DROP_CHANCE:
                    ShieldPickup(pg.Vector2(enemy.rect.center), self.player, self.datas.shields_group)

        # Le joueur ramasse les pièces et les coeurs qu'il croise (aspirés
        # automatiquement vers lui) ; chaque classe gère sa propre collecte
        if Coin.collect(self.player, self.datas):
            self.hud.trigger_coin_pop()

        if HeartPickup.collect(self.player, self.datas, self.HEART_POPUP_COLOR):
            self.hud.trigger_heal_flash()

        ShieldPickup.collect(self.player, self.datas.shields_group, self.datas.popups_group, self.SHIELD_POPUP_COLOR)

        if not self.player.is_alive:
            self.death_timer = Datas.DEATH_COOLDOWN
            Explosion(pg.Vector2(self.player.rect.center), self.datas.explosions_group)
            # L'historique est lu avant l'ajout : il ne contient que les parties précédentes
            historique = settings.last_scores(3)
            settings.add_score(self.player.score)
            self.menu_game_over.set_score(self.player.score, historique)

        # Met à jours tous les sprites en fonction du temps qui a passé
        for group in self.datas.groups:
            group.update(dt)

    def _draw_spawn_warnings(self):
        """ Marqueur triangulaire pulsant en haut de l'écran, tant qu'un ennemi
        approche par le haut sans être encore visible (rect entièrement au-dessus) """
        for enemy in self.datas.enemies_group:
            distance = -enemy.rect.bottom
            if not (0 < distance <= self.SPAWN_WARNING_DISTANCE):
                continue

            # 0 = vient d'entrer dans la zone d'alerte, 1 = sur le point d'apparaître
            proximity = 1 - (distance / self.SPAWN_WARNING_DISTANCE)
            pulse = (math.sin(self.datas.time * (2 * math.pi / self.SPAWN_WARNING_PULSE_PERIOD)) + 1) / 2
            alpha = max(0, min(255, int(70 + 150 * proximity * (0.5 + 0.5 * pulse))))
            size = 7 + int(6 * proximity)

            x = max(size, min(self.screen.get_width() - size, enemy.rect.centerx))
            marker = pg.Surface((size * 2, size), pg.SRCALPHA)
            pg.draw.polygon(marker, (*self.SPAWN_WARNING_COLOR, alpha), [(0, 0), (size * 2, 0), (size, size)])
            self.screen.blit(marker, (x - size, 4))

    def draw(self):
        """ Dessine le nouvel état du jeu, avec un éventuel tremblement et/ou zoom
        d'écran (déclenchés ex. par la mort ou l'arrivée du boss) : le rendu est
        redirigé vers une surface intermédiaire, puis blité sur l'écran réel avec
        un décalage et/ou un agrandissement qui décroissent avec le temps restant """
        shaking = self.hud.shake_timer > 0
        zooming = self.hud.zoom_timer > 0
        if shaking or zooming:
            real_screen, self.screen = self.screen, self._frame_buffer
            self.hud.screen = self._frame_buffer
            self.hud.shop.screen = self._frame_buffer

        self._draw_frame()

        if shaking or zooming:
            self.screen = real_screen
            self.hud.screen = real_screen
            self.hud.shop.screen = real_screen
            self.screen.fill((0, 0, 0))

            offset = self.hud.get_shake_offset() if shaking else (0, 0)
            scale = self.hud.get_zoom_scale() if zooming else 1.0
            if scale != 1.0:
                w, h = self._frame_buffer.get_size()
                zoomed = pg.transform.smoothscale(self._frame_buffer, (int(w * scale), int(h * scale)))
                center = (w // 2 + offset[0], h // 2 + offset[1])
                self.screen.blit(zoomed, zoomed.get_rect(center=center))
            else:
                self.screen.blit(self._frame_buffer, offset)

    def _draw_frame(self):
        initPos = self.screen.get_width() + Boss.BOSS_SIZE
        finalPos = self.screen.get_width() / 2 - Hud.SUN_SIZE / 2

        currentPos = initPos - ((initPos - finalPos) / Datas.TIME_BEFORE_BOSS * self.datas.time)

        # Croissance après l'arrivée
        grow_time = min(max(self.datas.time - Datas.TIME_BEFORE_BOSS, 0), Boss.GROW_DURATION)
        grow_ratio = grow_time / Boss.GROW_DURATION
        current_size = int(Boss.BOSS_SIZE + (Boss.BOSS_MAX_SIZE - Boss.BOSS_SIZE) * grow_ratio)
        scaled_boss = pg.transform.scale(self.boss.image, (current_size, current_size))

        bossX = max(self.screen.get_width() / 2 - current_size / 2, currentPos)

        if self.datas.time > Datas.TIME_BEFORE_BOSS:
            bossX = self.screen.get_width() / 2 - current_size / 2

        self.screen.blit(self.datas.bg_image1, (0, 0))

        self.datas.bg_image2.set_alpha(int(grow_ratio * 255))
        self.screen.blit(self.datas.bg_image2, (0, 0))

        self.hud.draw_sun()

        # Halo rouge pulsant derrière le boss une fois sa vie sous le seuil critique
        boss_center = (bossX + current_size / 2, (Hud.SUN_SIZE / 4) + (Hud.SUN_SIZE / 2))
        self.boss.draw_enrage_glow(self.screen, boss_center, current_size / 2)

        # Animation d'arrivée : tant que le sprite Boss n'existe pas encore
        self.screen.blit(scaled_boss, (bossX, (Hud.SUN_SIZE / 4) + (Hud.SUN_SIZE / 2) - (current_size / 2)))

        # Barre de vie du boss et palier courant, en haut au centre
        if self.boss.is_spawn:
            self.boss.draw_life_bar(self.screen)
            niveau = self.boss.boss_bar_font.render(f"BOSS NIV. {self.datas.stage}", True, (255, 255, 255))
            self.screen.blit(niveau, niveau.get_rect(center=(self.screen.get_width() // 2, 50)))
        if self.boss.is_spawn:
            self.datas.bombs_group.draw(self.screen)

        # Dessine tous les sprites dans la surface de l'écran
        self.datas.enemies_group.draw(self.screen)
        self.datas.player_group.draw(self.screen)
        self.datas.projectiles_group.draw(self.screen)
        self.datas.enemy_projectiles_group.draw(self.screen)
        self.datas.coins_group.draw(self.screen)
        self.datas.popups_group.draw(self.screen)
        self.datas.particles_group.draw(self.screen)
        self.datas.explosions_group.draw(self.screen)
        self.datas.hearts_group.draw(self.screen)
        self.datas.shields_group.draw(self.screen)
        self.datas.bombs_group.draw(self.screen)

        # Flashs de dégâts/soin, vignette de vie basse, compteur de pièces, vies
        self._draw_spawn_warnings()
        self.hud.draw_overlay()
        self.hud.draw_shield()