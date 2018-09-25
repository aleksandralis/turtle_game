import pygame, random

# Let's import the Car Class

GREEN = (20, 255, 140)
GREY = (210, 210, 210)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PURPLE = (255, 0, 255)
BLACK = (0, 0, 0)
WIDTH = 100
HEIGHT = 50


class Turtle(pygame.sprite.Sprite):
    # This class represents a turtle. It derives from the "Sprite" class in Pygame.

    def __init__(self, type, size_coeff, name, position):
        """
        :param type:
        :param size_coeff:
        :param name:
        :param position:
        """
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
        self.rect.x = float(position[0])
        self.tmp_x_float = float(position[0])
        self.rect.y = position[1]
        self.moving = 0
        self.speed_act = 0
        self.speed_target = 0

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

    def init_move_right(self):
        self.speed_target = 150

    def init_move_fast_right(self):
        self.speed_target = 300

    def init_move_left(self):
        self.speed_target = -150

    def init_move_fast_left(self):
        self.speed_target = -300

    def stop_move(self):
        self.speed_target = 0

    def move(self):
        if self.speed_target == round(self.speed_act,1):
            self.tmp_x_float = self.rect.x + self.speed_target * (1.0/60.0)
            self.rect.x = self.tmp_x_float + 0.5
            #print("const")
        elif self.speed_target>self.speed_act:
            #print("speed up")
            self.tmp_x_float = self.rect.x + self.speed_act * (1.0/60) + 150 *(1.0/60.0)**2/2
            self.speed_act = self.speed_act + 150*(1/60)
            self.rect.x = self.tmp_x_float + 0.5
        elif self.speed_target<self.speed_act:
            #print("speed down")
            self.tmp_x_float = self.rect.x + self.speed_act * (1/60) - 150 *(1/60)**2/2
            self.speed_act = self.speed_act - 150*(1/60)
            self.rect.x = self.tmp_x_float + 0.5
        if self.speed_act < 0.01 and self.speed_act > -0.01:
            self.speed_act = 0.0
        print("actual " + str(self.speed_act), "target " + str(self.speed_target))

class Turtle_Hero(Turtle):
    def __init__(self, type, size_coeff, name, position):
        super().__init__(type, size_coeff, name, position)
        self.is_jumping = 0
        self.dist_to_jump = 0
        self.initial_y = 0
        self.jump_counter = 0

    def init_jump(self, initial_v, grav_acc):
        self.is_jumping = 1
        self.dist_to_jump = (initial_v) ** 2 / (2 * grav_acc)
        print("init jump")
        print(self.dist_to_jump)
        self.initial_y = self.rect.y
        self.jump_counter = self.jump_counter + 1

    def jump(self, initial_v, grav_acc):
        if self.is_jumping == 1:
            self.rect.y = self.initial_y - initial_v * (self.jump_counter / 60) + grav_acc * (self.jump_counter / 60) ** 2 / 2
            print(self.rect.y)
            self.jump_counter = self.jump_counter + 1
            if self.initial_y - self.rect.y >= self.dist_to_jump:
                self.is_jumping = 2
                self.jump_counter = 1
                print("down")
                self.rect.y = self.initial_y - self.dist_to_jump
        elif self.initial_y >= self.rect.y and self.is_jumping == 2:
            self.rect.y = self.initial_y - self.dist_to_jump + grav_acc * (self.jump_counter / 60) ** 2 / 2
            print(self.rect.y)
            self.jump_counter = self.jump_counter + 1
            if self.initial_y <= self.rect.y:
                self.is_jumping = 0
                self.dist_to_jump = 0
                self.rect.y = self.initial_y
                self.initial_y = 0
                self.jump_counter = 0
                print("end")
