import pygame, sys, os

BASE_IMG_PATH = "data/images/"

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + "/" + img_name))
    return images

def render_text(surface, text, font, color, position):
    img = font.render(text, True, color)
    surface.blit(img, position)

class Animation:
    def __init__(self, images : list, duration = 5, loop = True) -> None:
        self.images = images
        self.duration = duration
        self.loop = loop
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (len(self.images) * self.duration)
        else:
            self.frame = min(self.frame + 1, len(self.images) * self.duration - 1)
            if self.frame >= len(self.images) * self.duration - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.duration)]  
