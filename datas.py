import pygame as pg

class Datas(object):
    #The time between two wave in millisecond
    TIME_BETWEEN_WAVE = 5000
    #The time before the boss spawn in millisecond
    TIME_BEFORE_BOSS = 30000

    # Délai (explosion du joueur) avant d'afficher l'écran de game over
    DEATH_COOLDOWN = 1300 # ms

    def __init__(self, screen: pg.Surface) -> None:
        self.screen = screen

        self.groups = [pg.sprite.Group() for _ in range(12)]

        self.enemies_group = self.groups[0]
        self.player_group = self.groups[1]
        self.projectiles_group = self.groups[2]
        self.enemy_projectiles_group = self.groups[3]
        self.coins_group = self.groups[4]
        self.popups_group = self.groups[5]
        self.particles_group = self.groups[6]
        self.explosions_group = self.groups[7]
        self.hearts_group = self.groups[8]
        self.boss_group = self.groups[9]
        self.bombs_group = self.groups[10]
        self.shields_group = self.groups[11]

        self.stage = 1
        self.time = 0

        self.bg_image1 = pg.image.load('images/backgroundGame1.png')
        self.bg_image1 = pg.transform.scale(self.bg_image1, (screen.get_width(), screen.get_height()))
        self.bg_image2 = pg.image.load('images/backgroundGame2.png')
        self.bg_image2 = pg.transform.scale(self.bg_image2, (screen.get_width(), screen.get_height()))