# Utilisation de pygame avec un préfixe plus simple
import pygame as pg

from Menu.menu_game_over import GameOver
# Accès à la classe Enemy
from enemy import Enemy
from player import Player
from Menu import menu_pause

from boss import Rectangle, Triangle


# Définition du jeu Pong
class Eclilpsoide:
    # time between wave in milliseconds
    TIME_BETWEEN_WAVE = 5000
    VITESSE_BOSS = 0.1  # pixels par milliseconde

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

        # Groupe dédié aux ennemis, pour les détections de collision (tirs, joueur, ...)
        self.enemies = pg.sprite.Group()
        self.player_group = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.player = Player(self.player_group, screen=self.screen, speed=0.3, projectiles=self.projectiles)

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
                    return False
                # Un appui sur une touche
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_f:
                            # Touche 'f' passe en fullscreen ou revient en mode window
                            pg.display.toggle_fullscreen()
                        case pg.K_ESCAPE:
                            # alterne la pause
                            Eclilpsoide.pause = not Eclilpsoide.pause
        return True

    def update(self,dt : int):
        """
        Met à jour l'état du jeux en fonction du temps dt écoulé
        et des touches préssées par le joueur
        """
        # Si le jeu est en pause, ne modifie plus rien
        if Eclilpsoide.pause:
            return

        if (self.time + dt) % self.TIME_BETWEEN_WAVE < dt:
            nbEnemies: int = int(self.time / self.TIME_BETWEEN_WAVE)
            for i in range(0, nbEnemies):
                Enemy(self.enemies, screen=self.screen)

        self.time += dt

        # Collisions entre le joueur et les ennemies
        if pg.sprite.spritecollide(self.player, self.enemies, dokill=False):
            self.player.on_hit()

        # Collisions entre les projectiles du joueur et les ennemies
        pg.sprite.groupcollide(self.projectiles, self.enemies, dokilla=True, dokillb=True)

        if self.player.is_alive == False:
            self.isEnded = True

        # Met à jours tous les sprites en fonction du temps qui a passé
        self.enemies.update(dt)
        self.player_group.update(dt)
        self.projectiles.update(dt)

    def draw(self):
        """ Dessine le nouvel état du jeu """
        # Redessine le fond entier
        self.screen.blit(self.bg_image, (0, 0))
        # Dessine tous les sprites dans la surface de l'écran
        self.enemies.draw(self.screen)
        self.player_group.draw(self.screen)
        self.projectiles.draw(self.screen)