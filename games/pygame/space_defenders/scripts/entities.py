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

    def rect(self):
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])

    def update(self, movement=(0,0)) -> None:
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        self.position[0] += frame_movement[0]
        self.position[1] += frame_movement[1]

    def render(self, surface) -> None:
        surface.blit(self.game.assets[self.type], self.position)


class Player(PhysicsEntity):
    def __init__(self, game, position, size, health) -> None:
        super().__init__(game, "player", position, size, health)
        self.health = 3
        self.invincibility = 0
        self.shoot_cooldown = 0

    def update(self, movement=(0,0)) -> None:
        super().update(movement)
        if self.invincibility:
            self.invincibility -= 1
        if self.shoot_cooldown:
            self.shoot_cooldown -= 1

    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 45
            self.game.projectiles.append(Projectile(self.game, (self.position[0] + self.size[0], self.position[1] + self.size[1]/2), (32, 32)))

    def hit(self):
        self.health -= 1
        self.invincibility = 60
        


class BasicEnemy(PhysicsEntity):
    def __init__(self, game, position, size, health) -> None:
        super().__init__(game, "basic_enemy", position, size, health)
    
    def update(self, movement=(0,0)) -> None:
        super().update(movement)
        self.velocity[0] = -4

class HeavyEnemy(PhysicsEntity):
    def __init__(self, game, position, size, health) -> None:
        super().__init__(game, "heavy_enemy", position, size, health)
    
    def update(self, movement=(0,0)) -> None:
        super().update(movement)
        self.velocity[0] = -2

    