# Utilisation de pygame avec un préfixe plus simple
import pygame as pg
# Accès à la classe Paddle
from paddle import Paddle
# Accès à la classe Ball
from ball import Ball
# Accès à la classe Score
from score import Score
# Accès à la classe Message
from message import Message

# Définition du jeu Pong
class Pong:
    # variable de classe pour mettre le jeu en pause pour débug
    pause = False
    def __init__(self,screen: pg.Surface):
        """ Création des attribut du jeux """
        # Conserve le lien vers l'objet surface ecran du jeux
        self.screen = screen

        # Crée une surface pour le fond du jeu de même taille que la fenêtre
        self.background = pg.Surface(self.screen.get_size())
        self.background.fill((0,50,0))

        # Dessine le font d'écran une première fois
        self.screen.blit(self.background,(0,0))

        # Objet sous groupe pour avoir la liste des sprites et automatiser la mise à jour par update()
        # Automatise aussi l'affichage : draw() par défaut affiche dans l'écran image à la position rect
        self.all = pg.sprite.RenderUpdates()

        # Creation de la raquette de gauche et droite
        self.paddleL = Paddle()
        self.paddleR = Paddle()
        # Positionnement des raquettes
        self.paddleL.setLoc(0,0,self.screen.get_height())
        # Il faut dépplacer vers la gauche pour tenir compte de la taille de la raquette
        self.paddleR.setLoc(self.screen.get_width()-self.paddleR.rect.width,0,self.screen.get_height())

        # Ajoute au groupe pour l'envois des messages update() et draw()
        self.all.add(self.paddleL,self.paddleR)

        # Création de la balle
        self.ball = Ball()
        # Définit la zone de jeux
        self.ball.setPlayground(self.screen.get_rect())
        # Ajoute la balle à la liste des sprites
        self.all.add(self.ball)

        # Initialisation des scores des deux joueurs
        self.score = Score()
        # Place le score au centre de l'écran
        self.score.setLoc(self.screen.get_rect().midtop)
        # Ajoute le score à la liste des sprites
        self.all.add(self.score)

        # Initialise le score gagnant
        self.winScore = 5
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
                        case pg.K_ESCAPE:
                            return False
                        case pg.K_f:
                            # Touche 'f' passe en fullscreen ou revient en mode window
                            pg.display.toggle_fullscreen()
                        case pg.K_SPACE:
                            # alterne la pause
                            Pong.pause = not Pong.pause
        return True

    def update(self,dt : int):
        """
        Met à jour l'état du jeux en fonction du temps dt écoulé
        et des touches préssées par le joueur
        """
        # Si le jeu est en pause, ne modifie plus rien
        if Pong.pause:
            return
        # Calcule la table de toutes les touches pressées du clavier
        keystate = pg.key.get_pressed()

        # Fait bouger les raquettes en fonction des touches pressées
        if keystate[pg.K_UP]:
            self.paddleL.up()
        elif keystate[pg.K_DOWN]:
            self.paddleL.down()
        else:
            self.paddleL.stop()
        if keystate[pg.K_KP8]:
            self.paddleR.up()
        elif keystate[pg.K_KP2]:
            self.paddleR.down()
        else:
            self.paddleR.stop()

        # Met à jours tous les sprites en fonction du temps qui a passé
        self.all.update(dt)

        # Test la collision avec les raquettes
        if pg.sprite.collide_rect(self.paddleL,self.ball):
            # Fait rebondir la balle sur la raquette
            self.ball.bounce(self.paddleL)
        if pg.sprite.collide_rect(self.paddleR,self.ball):
            # Fait rebondir la balle sur la raquette
            self.ball.bounce(self.paddleR)

        # test si la balle est sortie de l'aire du jeux
        if not self.screen.get_rect().contains(self.ball.rect):
            if self.ball.rect.left <= 0:
                # Sortie à gauche
                self.score.add(1,0)
                self.serveL()
            else:
                # Sortie à droite
                self.score.add(0,1)
                self.serveR()
            # Est-ce la fin du jeu ?
            if self.score.scoreL >= self.winScore:
                Message(self.screen).print("Left payer wins !")
                self.isEnded = True
            if self.score.scoreR >= self.winScore:
                Message(self.screen).print("Right payer wins !")
                self.isEnded = True

    def draw(self):
        """ Dessine le nouvel état du jeu """
        # Vide l'écran en replacant le background
        self.all.clear(self.screen, self.background)
        # Dessine tous les sprites dans la surface de l'écran
        dirty = self.all.draw(self.screen)
        # Remplace le background des zones modifiées par le mouvement des sprites
        pg.display.update(dirty)

    def serveL(self):
        """ Fait un service à gauche """
        self.ball.setR(self.paddleL,(0.5,0.5))

    def serveR(self):
        """ Fait un service à droite """
        self.ball.setL(self.paddleR,(-0.5,-0.5))