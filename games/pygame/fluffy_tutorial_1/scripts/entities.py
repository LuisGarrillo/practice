import pygame, math, random
from scripts.particle import Particle
from scripts.sparks import Spark
class PhysicsEntity:
    def __init__(self, game, entity_type, position, size) -> None:
        self.game = game
        self.type = entity_type
        self.position = list(position)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.last_movement = (0, 0)

        self.action = ""
        self.animation_offset = (-3, -3)
        self.flip = False
        self.set_action("idle")

        self.fall_cap = 5

    def rect(self):
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + "/" + self.action].copy()

    def update(self, tilemap, movement=(0,0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.position[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.position):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.position[0] = entity_rect.x

        self.position[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.position):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.position[1] = entity_rect.y

        self.velocity[1] = min(self.fall_cap, self.velocity[1] + 0.2)

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        if self.collisions["right"] or self.collisions["left"]:
            self.velocity[0] = 0

        self.animation.update()

    def render(self, surface, offset = (0, 0)):
        surface.blit(
            pygame.transform.flip(self.animation.img(), self.flip, False), 
            (self.position[0] - offset[0] + self.animation_offset[0], self.position[1] - offset[1] + self.animation_offset[1])
        )
        #surface.blit(
        #    self.game.assets["player"], 
        #    (self.position[0] - offset[0], self.position[1] - offset[1])
        #)
class Enemy(PhysicsEntity):
    def __init__(self, game, position, size) -> None:
        super().__init__(game, "enemy", position, size)
        self.walking = 0
    
    
    def update(self, tilemap, movement=(0,0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.position[1] + 23)):
                if self.collisions["right"] or self.collisions["left"]:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                distance = (self.game.player.position[0] - self.position[0], self.game.player.position[1] - self.position[1])
                if abs(distance[1]) < 16:
                    if self.flip and distance[0] < 0:
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for _ in range (4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))

                    elif not self.flip and distance[0] > 0:
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for _ in range (4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
        elif random.random() < 0.01:
            self.walking =  random.randint(30, 120)
            self.set_action("run")
        else:
            self.set_action("idle")

        super().update(tilemap, movement=movement)

        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                for _ in range (30):
                    angle =  random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, "particle", self.rect().center,  velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                return True
    
    def render(self, surface, offset=(0, 0)):
        super().render(surface, offset=offset)

        if self.flip:
            surface.blit(
                pygame.transform.flip(self.game.assets["gun"], True, False), 
                (self.rect().centerx - 4 - self.game.assets["gun"].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surface.blit(self.game.assets["gun"], (self.rect().centerx + self.game.assets["gun"].get_width() - offset[0], self.rect().centery - offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, position, size) -> None:
        super().__init__(game, "player", position, size)
        self.dashes = 1
        self.dashing = 0
        self.air_time = 0
        self.wall_slide = False
        self.jumps = 2

    def update(self, tilemap, movement=(0, 0), ):
        super().update(tilemap, movement=movement)

        if abs(self.dashing) in {60,50}:
            for _ in range(20):     
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                particle_velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, "particle", self.rect().center, velocity=particle_velocity, frame=random.randint(0, 7)))
        
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            self.velocity[1] = 0
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            particle_velocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, "particle", self.rect().center, velocity=particle_velocity, frame=random.randint(0, 7)))

        if self.game.movement[0] and self.game.running:
            self.velocity[0] = min(5, self.velocity[0] + 0.05)
        elif self.game.movement[1] and self.game.running:
            self.velocity[0] = max(-5, self.velocity[0] - 0.05)
        else:
            if self.velocity[0] > 0:
                self.velocity[0] = max(0, self.velocity[0] - 0.1)
            elif self.velocity[0] < 0:
                self.velocity[0] = min(0, self.velocity[0] + 0.1)

        self.air_time += 1
        self.fall_cap = 5
        
        if self.collisions["down"]:
            self.air_time = 0
            self.jumps = 2
            self.dashes = 1

        self.wall_slide = False
        if (self.collisions["right"] or self.collisions["left"]) and self.air_time > 4:
            self.wall_slide = True
            self.flip = not self.collisions["right"]
            self.set_action("wall_slide")
        
        if self.wall_slide:
            self.fall_cap = 1.5
            
        elif self.air_time > 4:
            self.set_action("jump")
                 
        elif not movement[0] == 0:
            self.set_action("run")
        else:
            self.set_action("idle")
    
    def render(self, surface, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surface, offset=offset)
        else:
            ...
            

    def jump(self):
        if self.wall_slide:
            self.jumps += 1
            self.dashes += 1
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -4
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -4
            self.jumps = max(0, self.jumps - 1)        
        elif self.jumps:
            self.velocity[1] = -5
            self.jumps = max(0, self.jumps - 1)

    def dash(self):
        if self.dashes and not self.dashing and not self.game.running:
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60

        self.dashes = max(0, self.dashes -1)
