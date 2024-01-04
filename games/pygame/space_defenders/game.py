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
            "game_over": load_image("assets/game_over.png"),
            "planets": load_images("assets/planets"),
            "background":load_image("background.png"),
            "explosion": Animation(load_images("explosion"), loop=False, duration=8),
            "player/idle": Animation(load_images("assets/player/idle"), 8),
            "player/shooting": Animation(load_images("assets/player/shooting"), 6),
            "slash": Animation(load_images("assets/slash"), 10),
            "projectile": Animation(load_images("projectile"), 10),
            "basic_enemy": Animation(load_images("assets/enemies/basic_enemy")),
            "heavy_enemy": Animation(load_images("assets/enemies/heavy_enemy")),
            "fast_enemy": Animation(load_images("assets/enemies/fast_enemy")),
            "directed_enemy": Animation(load_images("assets/enemies/directed_enemy")),
            "energy_0": load_image("assets/energy_banner/energy_banner_00.png"),
            "energy_1": load_image("assets/energy_banner/energy_banner_01.png"),
            "energy_2": load_image("assets/energy_banner/energy_banner_02.png"),
            "energy_3": load_image("assets/energy_banner/energy_banner_03.png"),
            "planet_life": load_image("assets/planet_life.png"),
            "level_banner": load_image("assets/level.png"),
            "score_banner": load_image("assets/score_banner.png")
        }

        self.sfxs = {
            "laser": pygame.mixer.Sound("data/sfxs/laser.wav"),
            "explosion": pygame.mixer.Sound("data/sfxs/explosion.wav"),
            "hit": pygame.mixer.Sound("data/sfxs/hit.wav"),
            "level_up": pygame.mixer.Sound("data/sfxs/level_up.wav"),
            "planet_hit": pygame.mixer.Sound("data/sfxs/planet_hit.wav"),
        }

        self.sfxs["laser"].set_volume(0.6)
        self.sfxs["explosion"].set_volume(0.3)
        self.sfxs["hit"].set_volume(0.4)
        self.sfxs["level_up"].set_volume(0.6)
        self.sfxs["planet_hit"].set_volume(0.8)

        self.title_playing = False
        self.game_playing = False
        self.victory_playing = False

        self.screens = {
            "tutorial_1": load_image("tutorials/tutorial_1.png"),
            "tutorial_2": load_image("tutorials/tutorial_2.png"),
        }

        self.dialogues = {
            "tutorial_1": Dialogue(
                ("Use the arrow keys to move and \npress F to shoot.", ), 2
            ),
            "tutorial_2": Dialogue(
                ("If you get hit you'll lose energy, \nif you let enemies pass through \nour planet will lose life.",
                 "Save us from the human army \ninvasion!"), 2
            ),
        }

        self.planets = Planets(self.assets["planets"])

    def start(self, score=0, level=0):
        self.player = Player(self, (37, self.display.get_height()/2), (40, 48), 3)
        self.movement = [False, False]
        self.projectiles = []
        self.explosions = []

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
            if self.on_game and not self.game_playing:
                pygame.mixer.music.stop()
                pygame.mixer.music.load("data/music/game.wav")
                pygame.mixer.music.play(-1)
                self.victory_playing = False
                self.game_playing = True
            self.player.update((0, (self.movement[1] - self.movement[0]) * 3.5))
            if not self.player.invincibility or self.player.invincibility % 10 == 0:
                self.player.render(self.display)

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
                        self.sfxs["planet_hit"].play()
                        self.enemies.remove(enemy)
                        self.planet_health -= 1
                    if enemy.rect().colliderect(self.player.rect()) and not self.player.invincibility:
                        self.sfxs["hit"].play()
                        for _ in range(1):
                                position = (random.randint(int(self.player.position[0]), int(self.player.position[0] + self.player.size[0])), random.randint(int(self.player.position[1]), int(self.player.position[1] + self.player.size[1])))
                                explosion = Animation(load_images("explosion"), loop=False, duration=3)
                                self.explosions.append((explosion, position))
                        self.player.hit()
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
                        self.sfxs["hit"].play()
                        if enemy.health == 0:
                            self.sfxs["explosion"].play()
                            for _ in range(2):
                                position = (random.randint(int(enemy.position[0]), int(enemy.position[0] + enemy.size[0])), random.randint(int(enemy.position[1]), int(enemy.position[1] + enemy.size[1])))
                                explosion = Animation(load_images("explosion"), loop=False, duration=3)
                                self.explosions.append((explosion, position))
                            self.enemies.remove(enemy)
                            self.score += 1
                        break

            for explosion in self.explosions.copy():
                explosion[0].update()
                if explosion[0].done:
                    self.explosions.remove(explosion)
                self.display.blit(explosion[0].img(), explosion[1])            
                        
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
                self.display.blit(self.assets["game_over"], ((self.display.get_width() - self.assets["game_over"].get_width())/2, self.display.get_height()/4))
                self.display.blit(self.assets["sub_title"], ((self.display.get_width() - self.assets["sub_title"].get_width())/2, self.display.get_height()/4 + self.assets["game_over"].get_height() + 10))
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
                    self.sfxs["level_up"].play()
                    self.load_level(self.level + 1)

                self.load_enemies(self.level)

        def title_sreen():
            if self.on_title_sreen and not self.title_playing:
                pygame.mixer.music.load("data/music/title.wav")
                pygame.mixer.music.play()
                self.title_playing = True
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
            if self.finished and not self.victory_playing:
                pygame.mixer.music.stop()
                pygame.mixer.music.load("data/music/victory.wav")
                pygame.mixer.music.play()
                self.victory_playing = True
                self.game_playing = False

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
            self.display.blit(self.assets["background"], (0, 0))
            self.planets.update()
            self.planets.render(self.display)

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
    