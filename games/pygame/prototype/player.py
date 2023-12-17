import pygame

class Player:
    def __init__(self) -> None:
        self.player_pos = [75, 270]
        self.movement = [False, False]

    def player_movement(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.movement[0] = True
            if event.key == pygame.K_DOWN:
                self.movement[1] = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.movement[0] = False
            if event.key == pygame.K_DOWN:
                self.movement[1] = False

    def update(self, screen):
        self.player_pos[1] += (self.movement[1] - self.movement[0]) * 3.5
        player_box = pygame.Rect(
            self.player_pos[0], self.player_pos[1], 100, 100
        )
        pygame.draw.rect(screen, (255, 255, 200), player_box)
        
