import pygame
from scripts.projectile import Projectile

class PhysicsEntity:
    def __init__(self, game, entity_type, position, size, health) -> None:
        self.game = game
        self.type = entity_type
        self.position = list(position)
        self.size = size
        self.velocity = [0, 0]
        self.health = health
        self.wait = False
        self.action = ""

    def rect(self):
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + "/" + self.action].copy()

    def update(self, movement=(0,0)) -> None:
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        if not self.wait:
            self.position[0] += frame_movement[0]
            self.position[1] += frame_movement[1]

        self.animation.update()

    def render(self, surface) -> None:
        surface.blit(self.animation.img(), (self.position[0], self.position[1]))


class Player(PhysicsEntity):
    def __init__(self, game, position, size, health) -> None:
        super().__init__(game, "player", position, size, health)
        self.health = 3

        self.invincibility = 0
        self.shoot_cooldown = 0
        self.sword_active = False
        self.sword_cooldown = 0

        self.set_action("idle")

    def sword_rect(self):
        return pygame.Rect(self.position[0] + self.size[0]/2, self.position[1] - 16, 48, 80)

    def update(self, movement=[0, 0]) -> None:
        super().update(movement)
        if self.position[1] > self.game.display.get_height() - self.size[1] or self.position[1] < self.game.assets["energy_0"].get_height():
            self.position[1] = min(max(self.position[1], self.game.assets["energy_0"].get_height()), self.game.display.get_height() - self.size[1])
            
        if self.invincibility:
            self.invincibility -= 1

        if self.shoot_cooldown:
            self.shoot_cooldown -= 1
            if self.shoot_cooldown == 10:
                self.wait = False

        if not self.wait:
            self.set_action("idle")


    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 25
            self.game.projectiles.append(Projectile(self.game, (self.position[0] + self.size[0], self.position[1] + self.size[1]/2), (32, 32)))
            self.wait = True
            self.set_action("shooting")


    def hit(self):
        self.health -= 1
        self.invincibility = 60
    
    def sword(self):
        if self.sword_cooldown == 0 and not self.sword_active:
            self.sword_cooldown = 30
            self.sword_active = True
            self.wait = True
            self.set_action("sword")
        


class BasicEnemy(PhysicsEntity):
    def __init__(self, game, position, size, health) -> None:
        super().__init__(game, "basic_enemy", position, size, health)
        self.animation = self.game.assets[self.type].copy()
    
    def update(self, movement=(0, 0)) -> None:
        super().update(movement)
        self.velocity[0] = -4

class HeavyEnemy(PhysicsEntity):
    def __init__(self, game, position, size, health) -> None:
        super().__init__(game, "heavy_enemy", position, size, health)
        self.animation = self.game.assets[self.type].copy()
    
    def update(self, movement=(0, 0)) -> None:
        super().update(movement)
        self.velocity[0] = -2

class FastEnemy(PhysicsEntity):
    def __init__(self, game, position, size, health) -> None:
        super().__init__(game, "fast_enemy", position, size, health)
        self.animation = self.game.assets[self.type].copy()
    
    def update(self, movement=(0, 0)) -> None:
        super().update(movement)
        self.velocity[0] = (min(-3, self.velocity[0] - 0.2))

class DirectedEnemy(PhysicsEntity):
    def __init__(self, game, position, size, health) -> None:
        super().__init__(game, "directed_enemy", position, size, health)
        self.animation = self.game.assets[self.type].copy()

    def update(self, movement=(0, 0)) -> None:
        self.velocity[0] = -6
        if self.position[1] < self.game.player.position[1] + self.game.player.size[1]/2:
            self.velocity[1] = 1
        elif self.position[1] > self.game.player.position[1] + self.game.player.size[1]/2:
            self.velocity[1] = -1
        else:
            self.velocity[1] = 0
        super().update(movement)

    