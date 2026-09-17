import pygame as pg

class Datas(object):
    #The time between two wave in millisecond
    TIME_BETWEEN_WAVE = 5000
    #The time before the boss spawn in millisecond
    TIME_BEFORE_BOSS = 20000

    # Chaque ennemi tué avance l'horloge, donc rapproche l'arrivée du boss
    # (tuer plus vite = boss plus tôt)
    KILL_TIME_BONUS = 1000  # ms

    # Délai (explosion du joueur) avant d'afficher l'écran de game over
    DEATH_COOLDOWN = 1300 # ms

    def __del__(self):
        del self.enemies_group
        del self.player_group
        del self.projectiles_group
        del self.enemy_projectiles_group
        del self.coins_group
        del self.popups_group
        del self.particles_group
        del self.explosions_group
        del self.hearts_group
        del self.boss_group
        del self.bombs_group
        del self.shields_group
        del self.stage
        del self.time
        del self.screen
        del self.groups
        del self

    def __init__(self, screen: pg.Surface) -> None:
        self.screen = screen

        self.groups = [pg.sprite.Group() for _ in range(12)]

        (self.enemies_group,
            self.player_group,
            self.projectiles_group,
            self.enemy_projectiles_group,
            self.coins_group,
            self.popups_group,
            self.particles_group,
            self.explosions_group,
            self.hearts_group,
            self.boss_group,
            self.bombs_group,
            self.shields_group) = self.groups

        self.stage = 1
        self.time = 0

        self.bg_image1 = pg.image.load('Eclipsoide/images/backgroundGame1.png')
        self.bg_image1 = pg.transform.scale(self.bg_image1, (screen.get_width(), screen.get_height()))
        self.bg_image2 = pg.image.load('Eclipsoide/images/backgroundGame2.png')
        self.bg_image2 = pg.transform.scale(self.bg_image2, (screen.get_width(), screen.get_height()))