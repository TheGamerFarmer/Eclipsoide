import sys
import random

# Utilisation de pygame avec un préfixe plus simple
import pygame as pg

import settings
from Menu.menu_game_over import GameOver
from boss import Boss
# Accès à la classe Enemy
from enemy import Enemy
from player import Player
from coin import Coin
from explosion import Explosion
from heart_pickup import HeartPickup
from hud import Hud

def collide_projectile(a: pg.sprite.Sprite, b: pg.sprite.Sprite) -> bool:
    """ Collision utilisant la hitbox du projectile plutôt que son rect visuel (halo + traînée) """
    rect_a = getattr(a, 'hitbox', a.rect)
    rect_b = getattr(b, 'hitbox', b.rect)
    return rect_a.colliderect(rect_b)

def collide_boss(boss: pg.sprite.Sprite, projectile: pg.sprite.Sprite) -> bool:
    """ Collision tir -> boss : hitbox du tir contre la forme réelle du boss (son masque) """
    rect = getattr(projectile, 'hitbox', projectile.rect)
    if not boss.rect.colliderect(rect):
        return False
    offset = (rect.x - boss.rect.x, rect.y - boss.rect.y)
    return boss.mask.overlap(pg.Mask(rect.size, fill=True), offset) is not None

# Définition du jeu Pong
class Eclipsoide:
    # time between wave in milliseconds
    TIME_BETWEEN_WAVE = 5000
    VITESSE_BOSS = 0.1  # pixels par milliseconde
    TIME_BEFORE_BOSS = 10000
    BOSS_SIZE = 70
    GROW_DURATION = 2000
    BOSS_MAX_SIZE = 620
    # Chaque boss vaincu rend le suivant 1,5 fois plus résistant
    BOSS_LIFE_GROWTH = 1.5

    # Délai (explosion du joueur) avant d'afficher l'écran de game over
    DEATH_COOLDOWN = 1300  # ms

    # Chance qu'un ennemi tué drop un coeur (uniquement si le joueur n'est pas déjà à vie max)
    HEART_DROP_CHANCE = 0.12
    HEART_POPUP_COLOR = (255, 90, 120)

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

    def __init__(self,screen: pg.Surface):
        """ Création des attribut du jeux """
        # Conserve le lien vers l'objet surface ecran du jeux
        self.screen = screen

        self.bg_image1 = pg.image.load('images/backgroundGame1.png')
        self.bg_image1 = pg.transform.scale(self.bg_image1, (screen.get_width(), screen.get_height()))
        self.bg_image2 = pg.image.load('images/backgroundGame2.png')
        self.bg_image2 = pg.transform.scale(self.bg_image2, (screen.get_width(), screen.get_height()))

        self.boss_image = pg.image.load('images/boss1.png')

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
        self.boss_group = pg.sprite.Group()
        self.boss = None
        # Palier courant : le boss revient de plus en plus fort après chaque victoire
        self.boss_level = 1

        # Création d'une instance du joueur
        self.player = Player(screen, 0.3, self.projectiles_group, self.particles_group, self.player_group)
        # Création du groupe du joueur

        # Soleil animé, HUD (pièces/vies) et effets d'écran (flashs, vignette)
        self.hud = Hud(screen, self.player)

        self.menu_game_over = GameOver(self.screen.get_width(), self.screen.get_height())

        # Vrai si le jeu est fini
        self.isEnded = False
        # None tant que le joueur est vivant ; sinon, ms restantes avant le game over
        self.death_timer = None

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
                        case pg.K_ESCAPE | pg.K_p:
                            # alterne la pause
                            Eclipsoide.pause = not Eclipsoide.pause
                        case pg.K_b if self.DEBUG:
                            # DEBUG : saute directement à la phase boss
                            self.time = max(self.time, self.TIME_BEFORE_BOSS)
                        case pg.K_n if self.DEBUG:
                            # DEBUG : quitte la phase boss et repart en phase vagues
                            self._exit_boss()
        return True

    def _boss_life(self) -> int:
        """ Vie du boss au palier courant : celle du palier précédent x BOSS_LIFE_GROWTH """
        return int(Boss.LIFE * self.BOSS_LIFE_GROWTH ** (self.boss_level - 1))

    def _boss_vaincu(self):
        """ Le boss explose, le palier suivant démarre : les vagues reprennent """
        Explosion(pg.Vector2(self.boss.rect.center), self.explosions_group)
        self.boss.bombs.empty()
        self.boss.kill()
        self.boss = None
        self.boss_level += 1
        # Remettre l'horloge à zéro relance les vagues d'ennemis, puis l'arrivée
        # du boss suivant une fois TIME_BEFORE_BOSS écoulé
        self.time = 0

    def _exit_boss(self):
        """ DEBUG : supprime le boss et ses bombes, et remet le jeu en phase vagues """
        if self.boss is not None:
            self.boss.bombs.empty()
            self.boss.kill()
            self.boss = None
        # Remet l'horloge au début : les vagues reprennent et l'animation
        # d'arrivée du boss recommence depuis la droite
        self.time = 0

    def update(self,dt : int):
        """
        Met à jour l'état du jeux en fonction du temps dt écoulé
        et des touches préssées par le joueur
        """
        # Si le jeu est en pause, ne modifie plus rien
        if Eclipsoide.pause:
            return

        self.hud.update_timers(dt)

        # Séquence de mort en cours : on laisse l'explosion du joueur se jouer
        # (le reste de la partie reste figé) avant de basculer sur le game over
        if self.death_timer is not None:
            self.death_timer -= dt
            self.explosions_group.update(dt)
            self.particles_group.update(dt)
            if self.death_timer <= 0:
                self.isEnded = True
            return

        self.hud.advance(dt)

        if (self.time + dt) % self.TIME_BETWEEN_WAVE < dt and self.time < self.TIME_BEFORE_BOSS:
            nbEnemies: int = int(self.time / self.TIME_BETWEEN_WAVE / 2)
            for i in range(-2, nbEnemies):
                Enemy(self.screen, self.player, self.enemy_projectiles_group, self.enemies_group)

        self.time += dt

        # Collisions entre le joueur et les ennemies
        if pg.sprite.spritecollide(self.player, self.enemies_group, dokill=False):
            if self.player.on_hit():
                self.hud.trigger_hit_flash()

        # Collisions entre le joueur et les projectiles ennemies
        # (on collisionne sur la hitbox du tir, pas sur son rect visuel qui
        # inclut le halo et la traînée)
        if pg.sprite.spritecollide(self.player, self.enemy_projectiles_group, dokill=True, collided=collide_projectile):
            if self.player.on_hit():
                self.hud.trigger_hit_flash()

        # Les bombes du boss explosent au contact du joueur et le tuent
        if self.boss is not None and self.boss.bombs_hitting(self.player):
            self.player.on_hit()

        # Les tirs du joueur entament la vie du boss
        if self.boss is not None:
            touches = pg.sprite.spritecollide(self.boss, self.projectiles_group, dokill=True, collided=collide_boss)
            for _ in touches:
                self.boss.hited(40)
            if not self.boss.is_alive:
                self._boss_vaincu()

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

        # Le joueur ramasse les pièces et les coeurs qu'il croise (aspirés
        # automatiquement vers lui) ; chaque classe gère sa propre collecte
        if Coin.collect(self.player, self.coins_group, self.popups_group):
            self.hud.trigger_coin_pop()

        if HeartPickup.collect(self.player, self.hearts_group, self.popups_group, self.HEART_POPUP_COLOR):
            self.hud.trigger_heal_flash()

        if self.player.is_alive == False:
            self.death_timer = self.DEATH_COOLDOWN
            Explosion(pg.Vector2(self.player.rect.center), self.explosions_group)
            # L'historique est lu avant l'ajout : il ne contient que les parties précédentes
            historique = settings.last_scores(3)
            settings.add_score(self.player.score)
            self.menu_game_over.set_score(self.player.score, historique)

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
        # Le boss sprite prend le relais de l'animation d'arrivée une fois la croissance finie
        if self.boss is None and self.time > self.TIME_BEFORE_BOSS + self.GROW_DURATION:
            self.boss = Boss(
                self.screen.get_width() / 2 - self.BOSS_MAX_SIZE / 2,
                (self.hud.SUN_SIZE / 4) + (self.hud.SUN_SIZE / 2) - (self.BOSS_MAX_SIZE / 2),
                self.BOSS_MAX_SIZE, self.BOSS_MAX_SIZE,
                (255, 255, 255),
                self.boss_group,
                image='images/boss1.png',
                bounds=self.screen.get_rect(),
                life=self._boss_life(),
            )
        self.boss_group.update(dt)

    def draw(self):
        """ Dessine le nouvel état du jeu """
        # Redessine le fond entier

        initPos = self.screen.get_width() + self.BOSS_SIZE
        finalPos = self.screen.get_width() / 2 - self.hud.SUN_SIZE / 2

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

        self.hud.draw_sun()

        # Animation d'arrivée : tant que le sprite Boss n'existe pas encore
        if self.boss is None:
            self.screen.blit(scaled_boss, (bossX, (self.hud.SUN_SIZE / 4) + (self.hud.SUN_SIZE / 2) - (current_size / 2)))

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
        self.boss_group.draw(self.screen)

        # Flashs de dégâts/soin, vignette de vie basse, compteur de pièces, vies
        self.hud.draw_overlay()

        # Barre de vie du boss et palier courant, en haut au centre
        if self.boss is not None:
            self.boss.draw_life_bar(self.screen)
            niveau = self.hud.coin_font.render(f"BOSS NIV. {self.boss_level}", True, (255, 255, 255))
            self.screen.blit(niveau, niveau.get_rect(center=(self.screen.get_width() // 2, 50)))
        if self.boss:
            self.boss.draw_bombs(self.screen)