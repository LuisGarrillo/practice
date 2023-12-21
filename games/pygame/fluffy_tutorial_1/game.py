import pygame, sys, random, math
from scripts.entities import Player, Enemy
from scripts.tilemap import Tilemap
from scripts.utils import load_image, load_images, Animation
from scripts.clouds import Cloud 
from scripts.particle import Particle
from scripts.sparks import Spark


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
            "enemy/idle": Animation(load_images("entities/enemy/idle"), duration=6),
            "enemy/run": Animation(load_images("entities/enemy/run"), duration=4),
            "gun": load_image("gun.png"),
            "projectile": load_image("projectile.png"),
            "player": load_image("entities/player.png"),
            "player/idle" : Animation(load_images("entities/player/idle"), duration=6),
            "player/run" : Animation(load_images("entities/player/run"), duration=4),
            "player/jump" : Animation(load_images("entities/player/jump")),
            "player/slide" : Animation(load_images("entities/player/slide")),
            "player/wall_slide" : Animation(load_images("entities/player/wall_slide")),
            "particle/leaf": Animation(load_images("particles/leaf"), duration=20, loop=False),
            "particle/particle": Animation(load_images("particles/particle"), duration=20, loop=False),
        }

        self.player = Player(self, (50, 50), (8, 15))
        self.running = False
        self.movement = [False, False]

        self.tilemap = Tilemap(self)
        try:
            self.tilemap.load("map.json")
        except FileNotFoundError:
            pass

        self.clouds = Cloud(self.assets["clouds"])

        self.load_level(0)

    def load_level(self, map_id) -> None:
        self.tilemap.load("data/maps/" + str(map_id) + ".json")

        self.leaf_spawners = []
        for tree in self.tilemap.extract([("large_decor", 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree["pos"][0], 4 + tree["pos"][1], 23, 13))
        
        self.enemies = []
        for spawner in self.tilemap.extract([("spawners", 0), ("spawners", 1)]):
            if spawner["variant"] == 0:
                self.player.position = spawner["pos"]
            else:
                self.enemies.append(Enemy(self, spawner["pos"], (8, 15)))

        self.particles = []
        self.projectiles= []
        self.sparks = []

        self.scroll = [0, 0]
        self.dead = 0

    def run(self) -> None:
        level = 0
        while True:
            if not self.enemies:
                level += 1
                if level > 2:
                    level = 0
                self.load_level(level)
            
            if self.dead:
                self.dead += 1
                if self.dead > 40:
                    self.load_level(level)

            self.display.blit(self.assets["background"], (0, 0))
            
            self.scroll[0] += (self.player.rect().x - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().y - self.display.get_height() / 2 - self.scroll[1]) / 10
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rectangle in self.leaf_spawners:
                if random.random() * 49999 < rectangle.width * rectangle.height:
                    position = (rectangle.x + random.random() * rectangle.width, rectangle.y + random.random() * rectangle.height / 2)
                    self.particles.append(Particle(self, "leaf", position, velocity = (-0.1, 0.3), frame=random.randint(0, 20)))
            
            self.clouds.update()
            self.clouds.render(self.display, render_scroll)

            self.tilemap.render(self.display, render_scroll)

            for enemy in self.enemies:
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            if not self.dead:
                self.player.update(self.tilemap, (self.movement[0] - self.movement[1], 0))
                self.player.render(self.display, render_scroll)

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, render_scroll)
                if kill:
                    self.sparks.remove(spark)

            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets["projectile"]
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    for _ in range (4):
                            self.sparks.append(Spark(self.projectiles[-1][0], random.random() - 0.5 + ( math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                    self.projectiles.remove(projectile)
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        for _ in range (30):
                            angle =  random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, "particle", self.player.rect().center,  velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                        
                        self.dead += 1
                        

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, render_scroll)
                if particle.type == "leaf":
                    particle.position[0] += math.sin(particle.animation.frame * 0.035) * 0.5
                if kill:
                    self.particles.remove(particle)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.movement[0] = True
                    if event.key == pygame.K_LEFT:
                        self.movement[1] = True
                    if event.key == pygame.K_f :
                        self.player.jump()
                    if event.key == pygame.K_d:
                        self.player.dash()
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