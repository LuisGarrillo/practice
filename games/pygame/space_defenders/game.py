import pygame, sys, random

from scripts.entities import Player, BasicEnemy, HeavyEnemy
from scripts.utils import load_image, load_images, Animation

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Space defenders")

        self.screen = pygame.display.set_mode((960, 540))
        self.display = pygame.Surface((480, 270))
        self.clock = pygame.time.Clock()

        self.assets = {
            "player" : load_image("assets/player.png"),
            "projectile": Animation(load_images("projectile"), 10),
            "basic_enemy": load_image("assets/basic_enemy.png"),
            "heavy_enemy": load_image("assets/heavy_enemy.png")
        }

        self.load(score=0)

    def load(self, score=0):
        self.player = Player(self, (37, self.display.get_height()/2), (50, 50), 3)
        self.movement = [False, False]
        self.projectiles = []

        self.planet_health = 3
        self.score = score

        self.enemies = []
        self.basic_enemy_counter = 0
        self.heavy_enemy_counter = 0

    def run(self):
        def reset_counter(type):
            if type == "basic_enemy":
                self.basic_enemy_counter = 0
            if type == "heavy_enemy":
                self.heavy_enemy_counter = 0

        while True:
            self.display.fill((0, 0, 0))

            if self.basic_enemy_counter == 60:
                self.enemies.append(BasicEnemy(self, (self.display.get_width() - 50, random.randint(20, self.display.get_height() - 20)), (50, 50), 1))
            if self.heavy_enemy_counter == 60:
                self.enemies.append(HeavyEnemy(self, (self.display.get_width() - 50, random.randint(20, self.display.get_height() - 20)), (50, 50), 2))   

            
            self.player.update((0, (self.movement[1] - self.movement[0]) * 3.5))
            if not self.player.invincibility or self.player.invincibility % 10 == 0:
                self.player.render(self.display)

            for enemy in self.enemies.copy():
                enemy.update()
                enemy.render(self.display)
                if enemy.position[0] < 0:
                    self.enemies.remove(enemy)
                    reset_counter(enemy.type)
                if enemy.rect().colliderect(self.player.rect()) and not self.player.invincibility:
                    self.player.hit()
                    self.enemies.remove(enemy)
                    
                    reset_counter(enemy.type)
        
            for projectile in self.projectiles.copy():
                kill = projectile.update(5)
                projectile.render(self.display)
                if kill:
                    self.projectiles.remove(projectile)
                for enemy in self.enemies.copy():
                    if enemy.rect().colliderect(projectile.rect()):
                        enemy.health -= 1
                        if enemy.health == 0:
                            self.enemies.remove(enemy)
                            self.score += 1
                            reset_counter(enemy.type)
                        self.projectiles.remove(projectile)
                        
                        

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.movement[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        self.player.shoot()
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)
            self.basic_enemy_counter += 1
            if self.score >= 10:
                self.heavy_enemy_counter += 1


Game().run()
    