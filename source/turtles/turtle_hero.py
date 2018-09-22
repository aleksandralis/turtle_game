import pygame, random
# Let's import the Car Class

GREEN = (20, 255, 140)
GREY = (210, 210, 210)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PURPLE = (255, 0, 255)
BLACK = (0,0,0)
WIDTH = 100
HEIGHT = 50

class Turtle(pygame.sprite.Sprite):
    # This class represents a turtle. It derives from the "Sprite" class in Pygame.

    def __init__(self, type, size_coeff, name, position):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # Pass in the name of the turtle, type, size, and its x and y position
        # Set the background color and set it to be transparent
        self.name = name
        self.image = pygame.Surface([WIDTH * size_coeff, HEIGHT * size_coeff])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)

        self.size = size_coeff
        self.type = type
        # Draw the turtle (a rectangle!)
        pygame.draw.rect(self.image, BLACK, [0, 0, WIDTH * size_coeff, HEIGHT * size_coeff])
        # Instead we could load a proper picture of a turtle...
        # self.image = pygame.image.load("turtle.png").convert_alpha()

        # Fetch the rectangle object that has the dimensions of the image and set position.
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]

    def moveRight(self, pixels):
        self.rect.x += pixels

    def moveLeft(self, pixels):
        self.rect.x -= pixels

    def moveUp(self, pixels):
        self.rect.y -= pixels

    def moveDown(self, pixels):
        self.rect.y += pixels

    def changeSpeed(self, speed):
        self.speed = speed


