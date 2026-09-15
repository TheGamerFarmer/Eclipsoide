import os
# Utilisation de pygame avec un préfixe plus simple
import pygame as pg
# Accès à la classe Enemy
from enemy import Enemy
from player import Player
from coin import Coin
from coin_popup import CoinPopup

# Définition du jeu Pong
class Eclipsoide:
    # time between wave in milliseconds
    TIME_BETWEEN_WAVE = 5000
    VITESSE_BOSS = 0.1  # pixels par milliseconde
    SUN_SIZE = 200

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

        self.bg_image = pg.image.load('images/background1.png')
        self.bg_image = pg.transform.scale(self.bg_image, (screen.get_width(), screen.get_height()))

        self.sun_image = pg.image.load('images/sun.png')
        self.sun_image = pg.transform.scale(self.sun_image, (self.SUN_SIZE, self.SUN_SIZE))

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
                    return False
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

        if (self.time + dt) % self.TIME_BETWEEN_WAVE < dt:
            nbEnemies: int = int(self.time / self.TIME_BETWEEN_WAVE)
            for i in range(0, nbEnemies):
                Enemy(self.screen, self.player, self.enemy_projectiles_group, self.enemies_group)

        self.time += dt

        # Collisions entre le joueur et les ennemies
        if pg.sprite.spritecollide(self.player, self.enemies_group, dokill=False):
            self.player.on_hit()

        # Collisions entre le joueur et les projectiles ennemies
        if pg.sprite.spritecollide(self.player, self.enemy_projectiles_group, dokill=True):
            self.player.on_hit()

        # Collisions entre les projectiles du joueur et les ennemies
        collisions = pg.sprite.groupcollide(self.projectiles_group, self.enemies_group, dokilla=True, dokillb=False)
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
            Eclipsoide.pause = True

        # Met à jours tous les sprites en fonction du temps qui a passé
        self.enemies_group.update(dt)
        self.player_group.update(dt)
        self.projectiles_group.update(dt)
        self.enemy_projectiles_group.update(dt)
        self.coins_group.update(dt)
        self.popups_group.update(dt)
        self.particles_group.update(dt)

    def draw(self):
        """ Dessine le nouvel état du jeu """
        # Redessine le fond entier
        self.screen.blit(self.bg_image, (0, 0))
        self.screen.blit(self.sun_image, (self.screen.get_width() / 2 - self.SUN_SIZE / 2, self.SUN_SIZE / 4))
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