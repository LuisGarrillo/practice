import pygame, sys

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption('testing')

        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()


    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            self.clock.tick(60)