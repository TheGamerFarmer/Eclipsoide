import pygame
import constantes

def main():
    pygame.init()
    screen = pygame.display.set_mode(constantes.SCREEN_SIZE)
    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill("blue")
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()