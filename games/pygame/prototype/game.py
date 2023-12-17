import pygame, sys, random

from scripts.entities import PhysicsEntity
from scripts.utils import load_image

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Space defenders")

        self.screen = pygame.display.set_mode((960, 540))
        self.clock = pygame.time.Clock()

        self.assets = {
            "player" : load_image("assets/player.png"),
            "basic_enemy": load_image("assets/basic_enemy.png")
        }

        self.player = PhysicsEntity(self, "player", (75, 270), (100, 100))
        self.movement = [False, False]

    def run(self):
        counter = 0
        basic_enemy = None
        while True:
            self.screen.fill((0, 0, 0))

            if counter == 6:
                basic_enemy = PhysicsEntity(self, "basic_enemy", (960, random.randint(0, 540)), (100, 100))

            if basic_enemy:
                basic_enemy.update((-5, 0))
                basic_enemy.render(self.screen)
                if basic_enemy.position[0] < 0:
                    basic_enemy = None
                    counter = 0

            self.player.update((0, (self.movement[1] - self.movement[0]) * 3.5))
            self.player.render(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.movement[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = False
                
            pygame.display.update()
            self.clock.tick(60)
            counter += 1

Game().run()
    