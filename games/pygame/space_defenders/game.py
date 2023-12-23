import pygame, sys, random

from scripts.entities import Player, BasicEnemy, HeavyEnemy, FastEnemy
from scripts.utils import load_image, load_images, render_text, Animation

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Space defenders")

        self.screen = pygame.display.set_mode((960, 540))
        self.display = pygame.Surface((480, 270))
        self.clock = pygame.time.Clock()
        self.score_font = pygame.font.SysFont("Arial", 20)
        self.game_over_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.playing = True
        self.game_over = False
        self.advance = False

        self.assets = {
            "player/idle": Animation(load_images("assets/player/idle"), 6),
            "player/shooting": Animation(load_images("assets/player/shooting"), 6),
            "player/sword": Animation(load_images("assets/player/sword"), 10, loop=False),
            "slash": Animation(load_images("assets/slash"), 10),
            "projectile": Animation(load_images("projectile"), 10),
            "basic_enemy": load_image("assets/basic_enemy.png"),
            "heavy_enemy": load_image("assets/heavy_enemy.png"),
            "fast_enemy": load_image("assets/fast_enemy.png"),
            "energy_0": load_image("assets/energy_0.png"),
            "energy_1": load_image("assets/energy_1.png"),
            "energy_2": load_image("assets/energy_2.png"),
            "energy_3": load_image("assets/energy_3.png"),
            "score_banner": load_image("assets/score_banner.png")
        }

        self.start(level=0)

    def start(self, score=0, level=0):
        self.player = Player(self, (37, self.display.get_height()/2), (32, 32), 3)
        self.movement = [False, False]
        self.projectiles = []

        self.planet_health = 3
        self.score = score
        self.timer = 0
        self.level = level

        self.enemies = []
        self.basic_enemy_counter = 1
        self.heavy_enemy_counter = 1
        self.fast_enemy_counter  = 1
        self.basic_enemy_cap = 120
        self.heavy_enemy_cap = 240
        self.fast_enemy_cap = 180

        self.load_level(0)

    def load_enemies(self, level):
        if level == 0:
            self.basic_enemy_counter += 1
        elif level == 1:
            self.basic_enemy_counter += 1
            self.heavy_enemy_counter += 1
        elif level == 2:
            self.fast_enemy_counter += 1

    def load_level(self, level=0):  
        self.level = level

        if self.game_over:
            self.playing = True
            self.game_over = False
        ...

    def run(self):
        def reset_counter(type):
            if type == "basic_enemy":
                self.basic_enemy_counter = 1
            if type == "heavy_enemy":
                self.heavy_enemy_counter = 1

        while True:
            self.display.fill((67, 59, 103))

            
            
            self.player.update((0, (self.movement[1] - self.movement[0]) * 3.5))
            if not self.player.invincibility or self.player.invincibility % 10 == 0:
                self.player.render(self.display)

            if self.player.sword_active and self.player.sword_cooldown < 20:
                self.assets["slash"].update()
                self.display.blit(self.assets["slash"].img(), self.player.sword_rect())

            if self.playing:
                if self.basic_enemy_counter % self.basic_enemy_cap == 0:
                    self.enemies.append(BasicEnemy(self, (self.display.get_width(), random.randint(self.player.size[1], self.display.get_height() - self.player.size[1])), (50, 25), 1))
                if self.heavy_enemy_counter % self.heavy_enemy_cap == 0:
                    self.enemies.append(HeavyEnemy(self, (self.display.get_width(), random.randint(self.player.size[1], self.display.get_height() - self.player.size[1])), (50, 50), 2))   
                if self.fast_enemy_counter % self.fast_enemy_cap == 0:
                    self.enemies.append(FastEnemy(self, (self.display.get_width(), random.randint(self.player.size[1], self.display.get_height() - self.player.size[1])), (50, 15), 1))

                for enemy in self.enemies.copy():
                    enemy.update()
                    enemy.render(self.display)
                    if enemy.position[0] < 0:
                        self.enemies.remove(enemy)
                    if enemy.rect().colliderect(self.player.rect()) and not self.player.invincibility:
                        self.player.hit()
                        self.enemies.remove(enemy)
                    elif self.player.sword_active and self.player.sword_cooldown < 20 and enemy.rect().colliderect(self.player.sword_rect()):
                        self.enemies.remove(enemy)
        
            for projectile in self.projectiles.copy():
                kill = projectile.update(5)
                projectile.render(self.display)
                if kill:
                    self.projectiles.remove(projectile)

                for enemy in self.enemies.copy():
                    if enemy.rect().colliderect(projectile.rect()):
                        enemy.health -= 1
                        self.projectiles.remove(projectile)
                        if enemy.health == 0:
                            self.enemies.remove(enemy)
                            self.score += 1
                        break
                        
                        

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if self.playing:
                        if event.key == pygame.K_UP:
                            self.movement[0] = True
                        if event.key == pygame.K_DOWN:
                            self.movement[1] = True
                        if event.key == pygame.K_f:
                            self.player.shoot()
                        if event.key == pygame.K_d:
                            self.player.sword()
                    else:
                        if event.key == pygame.K_SPACE:
                            self.advance = True
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = False

            if self.game_over:
                text = "Game over\nPress Space to Play Again"
                render_text(self.display, text, self.game_over_font, (255, 255, 255), ((self.display.get_width() - len(text)*7.5)/2, self.display.get_height()/2 - 30))
                if self.advance:
                    self.start(self.level)
                    self.advance = False

            self.display.blit(self.assets["energy_" + str(self.player.health)], (0, 0))
            self.display.blit(self.assets["score_banner"], (self.display.get_width() -80, 0))
            render_text(self.display, str(self.score), self.score_font, (0, 0, 0), (self.display.get_width() - 40, 5))

            if self.player.health == 0:
                self.playing = False
                self.game_over = True

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)
            self.timer += 1
            
            if self.timer % 3600 == 0:
                self.load_level(self.level + 1)

            self.load_enemies(self.level)
        


Game().run()
    