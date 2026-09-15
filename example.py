import pygame
import constantes
from player import Player

def main():
    pygame.init()
    screen = pygame.display.set_mode(constantes.SCREEN_SIZE)
    clock = pygame.time.Clock()
    running = True
    player = Player(screen=screen, speed=500)
    group = pygame.sprite.Group()
    group.add(player)

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        group.update(dt)
        screen.fill("blue")
        group.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()