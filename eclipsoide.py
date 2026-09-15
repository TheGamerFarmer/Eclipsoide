# Utilisation de pygame avec un préfixe plus simple
import pygame as pg
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

        # Objet sous groupe pour avoir la liste des sprites et automatiser la mise à jour par update()
        # Automatise aussi l'affichage : draw() par défaut affiche dans l'écran image à la position rect
        self.all = pg.sprite.RenderUpdates()

        # Groupe dédié aux ennemis, pour les détections de collision (tirs, joueur, ...)
        self.enemies = pg.sprite.Group()
        self.player_group = pg.sprite.Group()
        self.projeciles = pg.sprite.Group()
        self.player = Player(self.player_group, screen=self.screen, speed=0.3, projectiles=self.projeciles)
        self.player_group.add(self.player)

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

        if pg.sprite.spritecollide(self.player, self.enemies, dokill=False):
            self.player.on_hit()

        pg.sprite.groupcollide(self.projeciles, self.enemies, dokilla=True, dokillb=True)

        # Met à jours tous les sprites en fonction du temps qui a passé
        self.all.update(dt)
        self.enemies.update(dt)
        self.player_group.update(dt)
        self.projeciles.update(dt)

    def draw(self):
        """ Dessine le nouvel état du jeu """
        # Redessine le fond entier
        self.screen.blit(self.bg_image, (0, 0))
        # Dessine tous les sprites dans la surface de l'écran
        self.all.draw(self.screen)
        self.enemies.draw(self.screen)
        self.player_group.draw(self.screen)
        self.projeciles.draw(self.screen)