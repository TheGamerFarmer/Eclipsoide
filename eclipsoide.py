# Utilisation de pygame avec un préfixe plus simple
import pygame as pg
# Accès à la classe Enemy
from enemy import Enemy
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
        self.all : pg.sprite.RenderUpdates = pg.sprite.RenderUpdates()

        # Le boss lâche des bombes, la touche B les fait exploser
        self.boss = Triangle(400, 50, 120, 100, (255, 60, 60), self.all,
                             detonate_key=pg.K_b, bounds=screen.get_rect())
        self.boss_direction = 1

        # Cible de test (remplace le joueur pour simuler les collisions)
        self.cible = Rectangle(100, screen.get_height() - 80, 60, 30, self.COULEUR_CIBLE, self.all)
        self.cible_direction = 1
        self.cible_vie = self.VIE_CIBLE
        self.flash_timer = 0
        # Explosions ayant déjà touché la cible (une explosion = des dégâts une seule fois)
        self.explosions_ayant_touche: set[pg.sprite.Sprite] = set()

        self.font = pg.font.Font(None, 32)

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

    def _patrouiller(self, sprite: Rectangle | Triangle, direction: int, vitesse: float, dt: int) -> int:
        """Déplace un sprite horizontalement et le fait rebondir sur les bords. Retourne la direction."""
        sprite.move(direction * vitesse * dt, 0)
        if sprite.rect.left <= 0:
            sprite.rect.left = 0
            return 1
        if sprite.rect.right >= self.screen.get_width():
            sprite.rect.right = self.screen.get_width()
            return -1
        return direction

    def _set_couleur_cible(self, couleur: tuple[int, int, int]) -> None:
        if self.cible.color != couleur:
            self.cible.color = couleur
            self.cible.image = self.cible._build_image()

    def _collisions_bombes(self, dt: int) -> None:
        """Simulation de collision entre les bombes du boss et la cible."""
        # Oublie les explosions terminées
        self.explosions_ayant_touche = {b for b in self.explosions_ayant_touche if b.alive()}

        # collide_mask : collision au pixel près (bombe/explosion ronde vs rectangle)
        touchees = pg.sprite.spritecollide(self.cible, self.boss.bombs, False, pg.sprite.collide_mask)
        for bombe in touchees:
            if not bombe.exploding:
                # Une bombe qui tombe sur la cible explose au contact
                bombe.explode()
            if bombe not in self.explosions_ayant_touche:
                self.explosions_ayant_touche.add(bombe)
                self.cible_vie -= self.DEGATS_EXPLOSION
                self.flash_timer = self.DUREE_FLASH
                print(f"Cible touchée ! vie = {max(self.cible_vie, 0)}")

        if self.cible_vie <= 0:
            print("Cible détruite, réinitialisation de la simulation")
            self.cible_vie = self.VIE_CIBLE

        # Flash blanc quand la cible vient d'être touchée
        self.flash_timer = max(self.flash_timer - dt, 0)
        self._set_couleur_cible(self.COULEUR_CIBLE_TOUCHEE if self.flash_timer > 0 else self.COULEUR_CIBLE)

    def update(self,dt : int):
        """
        Met à jour l'état du jeux en fonction du temps dt écoulé
        et des touches préssées par le joueur
        """
        # Si le jeu est en pause, ne modifie plus rien
        if Eclilpsoide.pause:
            return

        self.boss_direction = self._patrouiller(self.boss, self.boss_direction, self.VITESSE_BOSS, dt)
        self.cible_direction = self._patrouiller(self.cible, self.cible_direction, self.VITESSE_CIBLE, dt)

        if (self.time + dt) % self.TIME_BETWEEN_WAVE < dt:
            nbEnemies: int = int(self.time / self.TIME_BETWEEN_WAVE)
            for i in range(0, nbEnemies):
                Enemy(self.screen, self.all)

        self.time += dt
        # Met à jours tous les sprites en fonction du temps qui a passé
        self.all.update(dt)

        self._collisions_bombes(dt)

    def draw(self):
        """ Dessine le nouvel état du jeu """
        # Redessine le fond entier
        self.screen.blit(self.bg_image, (0, 0))
        # Dessine tous les sprites dans la surface de l'écran
        self.all.draw(self.screen)

        texte = self.font.render(f"Vie cible : {max(self.cible_vie, 0)}   [B] détoner", True, (255, 255, 255))
        self.screen.blit(texte, (10, 10))
