import pygame, sys, random

import player

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Space defenders")

        self.screen = pygame.display.set_mode((960, 540))
        self.clock = pygame.time.Clock()

        self.player = player.Player()

    def run(self):
        while True:
            self.screen.fill((0, 0, 0))
            self.player.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                self.player.player_movement(event)
                

            pygame.display.update()
            self.clock.tick(60)

Game().run()
    