import pygame, sys
from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap
from scripts.utils import load_image, load_images
from scripts.clouds import Cloud 


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("testing")

        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        
        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "background": load_image("background.png"),
            "clouds": load_images("clouds"),
            "player": load_image("entities/player.png")
        }

        self.player = PhysicsEntity(self, "player", (50, 50), (8, 15))
        self.running = False
        self.movement = [False, False]

        self.tilemap = Tilemap(self)
        self.clouds = Cloud(self.assets["clouds"])
        self.scroll = [0, 0]

    def run(self) -> None:
        while True:
            self.display.blit(self.assets["background"], (0, 0))
            
            self.scroll[0] += (self.player.rect().x - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().y - self.display.get_height() / 2 - self.scroll[1]) / 10
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.clouds.update()
            self.clouds.render(self.display, render_scroll)

            self.tilemap.render(self.display, render_scroll)

            self.player.update(self.tilemap, (self.movement[0] - self.movement[1], 0))
            self.player.render(self.display, render_scroll)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.movement[0] = True
                    if event.key == pygame.K_LEFT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP :
                        self.player.velocity[1] = -4
                    if event.key == pygame.K_SPACE:
                        self.running = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT:
                        self.movement[0] = False
                    if event.key == pygame.K_LEFT:
                        self.movement[1] = False
                    if event.key == pygame.K_SPACE:
                        self.running = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Game().run()