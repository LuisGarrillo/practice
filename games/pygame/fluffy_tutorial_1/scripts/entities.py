import pygame

class PhysicsEntity:
    def __init__(self, game, entity_type, position, size) -> None:
        self.game = game
        self.type = entity_type
        self.position = list(position)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

    def rect(self):
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])

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

        self.velocity[1] = min(5, self.velocity[1] + 0.2)

        if self.game.movement[0] and self.game.running:
            self.velocity[0] = min(2, self.velocity[0] + 0.05)
        elif self.game.movement[1] and self.game.running:
            self.velocity[0] = max(-2, self.velocity[0] - 0.05)
        else:
            if self.velocity[0] > 0 and self.velocity[1] != 0:
                self.velocity[0] = max(0, self.velocity[0] - 0.075)
            elif self.velocity[0] < 0 and self.velocity[1] != 0:
                self.velocity[0] = min(0, self.velocity[0] + 0.075)


        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        if self.collisions["right"] or self.collisions["left"]:
            self.velocity[0] = 0

    def render(self, surface, offset = (0, 0)):
        surface.blit(
            self.game.assets["player"], 
            (self.position[0] - offset[0], self.position[1] - offset[1])
        )
