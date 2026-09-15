import pygame
import constantes
from player import Player
from projectile import Projectile

def main():
    pygame.init()
    screen = pygame.display.set_mode(constantes.SCREEN_SIZE)
    clock = pygame.time.Clock()
    running = True

    projectile_group = pygame.sprite.Group()

    player = Player(screen=screen, speed=300, projectiles=projectile_group)
    player_group = pygame.sprite.Group()
    player_group.add(player)


    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        player_group.update(dt)
        projectile_group.update(dt)

        screen.fill("black")

        player_group.draw(screen)
        projectile_group.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()