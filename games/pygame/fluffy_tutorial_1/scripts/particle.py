class Particle:
    def __init__(self, game, particle_type, postition, velocity=[0, 0], frame = 0) -> None:
        self.game = game
        self.type = particle_type
        self.position = list(postition)
        self.velocity = list(velocity)
        self.frame = frame
        self.animation = self.game.assets["particle/" + particle_type].copy()
        self.transparency = 10

    def update(self):
        kill = self.animation.done
        self.transparency += 10
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

        self.animation.update()

        return kill
    
    def render(self, surface, offset=(0, 0)):
        image = self.animation.img()
        image.set_alpha(self.transparency)
        surface.blit(
            image,
            (self.position[0] - offset[0] - image.get_width() // 2, 
             self.position[1] - offset[1] - image.get_height() // 2)
        )