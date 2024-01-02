import pygame, sys, random

from scripts.entities import Player, BasicEnemy, HeavyEnemy, FastEnemy, DirectedEnemy
from scripts.utils import load_image, load_images, render_text, Animation, Dialogue
from scripts.planets import Planets

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Space defenders")

        self.screen = pygame.display.set_mode((960, 540))
        self.display = pygame.Surface((480, 270))
        self.clock = pygame.time.Clock()

        self.dialogue_font = pygame.font.SysFont("Arial", 10)
        self.score_font = pygame.font.SysFont("Arial", 20)
        self.game_over_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.speed_up = False

        self.offset = [0, 0]
        self.playing = True
        self.on_title_sreen = True
        self.on_game = False
        self.on_tutorial = False
        self.game_over = False
        self.advance = False
        self.finished = False

        self.assets = {
            "tilte": load_image("assets/title.png"),
            "sub_title": load_image("assets/sub_title.png"),
            "planets": load_images("assets/planets"),
            "player/idle": Animation(load_images("assets/player/idle"), 8),
            "player/shooting": Animation(load_images("assets/player/shooting"), 6),
            "player/sword": Animation(load_images("assets/player/sword"), 10, loop=False),
            "slash": Animation(load_images("assets/slash"), 10),
            "projectile": Animation(load_images("projectile"), 10),
            "basic_enemy": load_image("assets/enemies/basic_enemy.png"),
            "heavy_enemy": load_image("assets/enemies/heavy_enemy.png"),
            "fast_enemy": load_image("assets/enemies/fast_enemy.png"),
            "directed_enemy": load_image("assets/enemies/directed_enemy.png"),
            "energy_0": load_image("assets/energy_banner/energy_banner_00.png"),
            "energy_1": load_image("assets/energy_banner/energy_banner_01.png"),
            "energy_2": load_image("assets/energy_banner/energy_banner_02.png"),
            "energy_3": load_image("assets/energy_banner/energy_banner_03.png"),
            "planet_life": load_image("assets/planet_life.png"),
            "level_banner": load_image("assets/level.png"),
            "score_banner": load_image("assets/score_banner.png")
        }

        self.screens = {
            "tutorial_1": load_image("tutorials/tutorial_1.png"),
            "tutorial_2": load_image("tutorials/tutorial_2.png"),
        }

        self.dialogues = {
            "tutorial_1": Dialogue(
                ("Use the arrow keys to move and \npress F to shoot.", ), 3
            ),
            "tutorial_2": Dialogue(
                ("If you get hit you'll lose energy, \nif you let enemies pass through \nour planet will lose life.",
                 "Save us from the human army \ninvasion!"), 3
            ),
        }

        self.planets = Planets(self.assets["planets"])

    def start(self, score=0, level=0):
        self.player = Player(self, (37, self.display.get_height()/2), (40, 48), 3)
        self.movement = [False, False]
        self.projectiles = []

        self.planet_health = 3
        self.score = score
        self.timer = 0
        self.level = level
        self.tutorial_level = 1
        self.level_duration = 3600

        self.enemies = []
        self.basic_enemy_counter = 1
        self.heavy_enemy_counter = 1
        self.fast_enemy_counter  = 1
        self.directed_enemy_counter = 1

        self.basic_enemy_cap = 100
        self.heavy_enemy_cap = 240
        self.fast_enemy_cap = 180
        self.directed_enemy_cap = 180

        self.load_level(self.level)

    def load_enemies(self, level):
        if level == 0:
            self.basic_enemy_counter += 1
        elif level == 1:
            self.basic_enemy_counter += 1
            self.heavy_enemy_counter += 1
        elif level == 2:
            self.fast_enemy_counter += 1
        elif level == 3:
            self.heavy_enemy_counter += 1
            self.fast_enemy_counter += 1
        elif level == 4:
            self.directed_enemy_counter += 1
        elif level == 5:
            self.directed_enemy_counter += 1
            self.heavy_enemy_counter += 1
            self.basic_enemy_counter += 1
        elif level > 5:
            self.finished = True
            self.on_game = False

    def load_level(self, level=0):  
        self.level = level
        self.basic_enemy_counter = 1
        self.heavy_enemy_counter = 1
        self.fast_enemy_counter = 1
        self.directed_enemy_counter = 1

        if level == 0 or level == 2 or level == 4:
            self.level_duration = 1800
        if level == 1 or level == 3:
            self.level_duration = 3600

    def run(self):
        def game_loop():
            self.display.fill((67, 59, 103))

            self.planets.update()
            self.planets.render(self.display)

            self.player.update((0, (self.movement[1] - self.movement[0]) * 3.5))
            if not self.player.invincibility or self.player.invincibility % 10 == 0:
                self.player.render(self.display)

            if self.player.sword_active and self.player.sword_cooldown < 20:
                self.assets["slash"].update()
                self.display.blit(self.assets["slash"].img(), self.player.sword_rect())

            if self.playing:
                if self.basic_enemy_counter % self.basic_enemy_cap == 0:
                    self.enemies.append(BasicEnemy(self, (self.display.get_width(), random.randint(self.player.size[1] * 1.5, self.display.get_height() - self.player.size[1])), (50, 25), 1))
                if self.heavy_enemy_counter % self.heavy_enemy_cap == 0:
                    self.enemies.append(HeavyEnemy(self, (self.display.get_width(), random.randint(self.player.size[1] * 1.5, self.display.get_height() - self.player.size[1])), (50, 50), 2))   
                if self.fast_enemy_counter % self.fast_enemy_cap == 0:
                    self.enemies.append(FastEnemy(self, (self.display.get_width(), random.randint(self.player.size[1] * 1.5, self.display.get_height() - self.player.size[1])), (50, 15), 1))
                if self.directed_enemy_counter % self.directed_enemy_cap == 0:
                    self.enemies.append(DirectedEnemy(self, (self.display.get_width(), random.choice((self.player.size[1] * 1.5, self.display.get_height() - self.player.size[1]))), (50, 15), 1))

                for enemy in self.enemies.copy():
                    enemy.update()
                    enemy.render(self.display)
                    if enemy.position[0] < 0:
                        self.enemies.remove(enemy)
                        self.planet_health -= 1
                    if enemy.rect().colliderect(self.player.rect()) and not self.player.invincibility:
                        self.player.hit()
                        self.enemies.remove(enemy)
                    elif self.player.sword_active and self.player.sword_cooldown < 20 and enemy.rect().colliderect(self.player.sword_rect()):
                        self.score += 1
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
                    self.start(level=self.level, score=0)
                    self.playing = True
                    self.game_over = False
                    self.advance = False

            self.display.blit(self.assets["energy_" + str(self.player.health)], (0, 0))
            self.display.blit(self.assets["planet_life"], (self.assets["energy_" + str(self.player.health)].get_width(), 0))
            self.display.blit(self.assets["score_banner"], (self.display.get_width() - self.assets["score_banner"].get_width(), 0))
            self.display.blit(self.assets["level_banner"], (self.display.get_width() - self.assets["score_banner"].get_width() * 2, 0))

            render_text(self.display, str(self.score), self.score_font, (0, 0, 0), (self.display.get_width() - 40, self.assets["score_banner"].get_height()/3))
            render_text(self.display, str(self.level + 1), self.score_font, (0, 0, 0), (self.display.get_width() - 40 - self.assets["score_banner"].get_width(), self.assets["level_banner"].get_height()/3))
            render_text(self.display, str(self.planet_health), self.score_font, (0, 0, 0), (self.assets["planet_life"].get_width() + self.assets["planet_life"].get_width()/1.5, self.assets["planet_life"].get_height()/3))

            if self.player.health == 0 or self.planet_health == 0:
                self.playing = False
                self.game_over = True

            else:
                self.timer += 1
            
                if self.timer % self.level_duration == 0:
                    self.load_level(self.level + 1)

                self.load_enemies(self.level)

        def title_sreen():
            self.display.fill((67, 59, 103))

            self.planets.update()
            self.planets.render(self.display)

            self.display.blit(self.assets["tilte"], ((self.display.get_width() - self.assets["tilte"].get_width())/2, self.display.get_height()/4))
            self.display.blit(self.assets["sub_title"], ((self.display.get_width() - self.assets["sub_title"].get_width())/2, self.display.get_height()/4 + self.assets["tilte"].get_height() + 10))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.start(level=0)
                        self.on_title_sreen = False
                        self.on_game = True
                        if self.tutorial_level == 1:
                            self.on_tutorial = True

        def tutorial():
            self.display.blit(self.screens["tutorial_" + str(self.tutorial_level)], (0, 0))
            self.dialogues["tutorial_" + str(self.tutorial_level)].update()
            self.dialogues["tutorial_" + str(self.tutorial_level)].render(self.display, self.dialogue_font, (255, 255, 255), (180, 7))
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.advance = True

            if self.advance and self.dialogues["tutorial_" + str(self.tutorial_level)].done:
                if self.dialogues["tutorial_" + str(self.tutorial_level)].advance():
                    self.advance = False
                else:
                    self.tutorial_level += 1
                    self.advance = False
                if self.tutorial_level == 3:
                    self.on_tutorial = False
            else:
                self.advance = False

        def finished_screen():
            self.display.fill((67, 59, 103))

            if self.score > 110:
                grade = "S"
            elif self.score > 100:
                grade = "A"
            elif self.score > 80:
                grade = "B"
            elif self.score > 60:
                grade = "C"
            else:
                grade = "D"

            text = "You win! Grade: " + grade + "\nPress Space to Play Again"
            render_text(self.display, text, self.game_over_font, (255, 255, 255), ((self.display.get_width() - len(text)*7.5)/2, self.display.get_height()/2 - 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.start(level=0)
                        self.finished = False
                        self.on_game = True

        while True:
            if self.on_title_sreen:
                title_sreen()

            elif self.on_game:
                if self.on_tutorial:
                    tutorial()
                else:
                    game_loop()

            elif self.finished:
                finished_screen()

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)
        


Game().run()
    