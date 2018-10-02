import pygame, random
from enum import Enum
import os
import math
class JumpStates(Enum):
    IDLE = 0
    UP = 1
    DOWN = 2

class Turtle(pygame.sprite.Sprite):
    # This class represents a turtle. It derives from the "Sprite" class in Pygame.

    def __init__(self, type, size_coeff, name, position):
        """
        :param type: turtle type (TODO: define)
        :param size_coeff: SIZE_COEFF - turtle size scaling
        :param name: name strinf
        :param position: creation postition in pixels - tuple (x,y), starting from left, top corner
        """
        # Call the parent class (Sprite) constructor
        super().__init__()
        self.GREEN = (20, 255, 140)
        self.GREY = (210, 210, 210)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.PURPLE = (255, 0, 255)
        self.BLACK = (0, 0, 0)
        self.WIDTH = 64
        self.HEIGHT = 64
        self.init_sub = (0,0) #default icon column and row

        # Pass in the name of the turtle, type, size, and its x and y position
        # Set the background color and st it to be transparent
        self.name = name
        self.image = self.get_image(self.WIDTH * self.init_sub[0] , self.HEIGHT * self.init_sub[1], self.WIDTH, self.HEIGHT)
        # self.image.fill(self.WHITE)
        # self.image.set_colorkey(self.WHITE)

        self.size = size_coeff
        self.type = type
        # Draw the turtle (a rectangle!)
        #pygame.draw.rect(self.image, self.BLACK, [0, 0, self.WIDTH * size_coeff, self.HEIGHT * size_coeff])
        # Instead we could load a proper picture of a turtle...
        #self.image = pygame.image.load("turtle.png").convert_alpha()

        # Fetch the rectangle object that has the dimensions of the image and set position.
        self.rect = self.image.get_rect()
        self.rect.x = float(position[0])
        self.tmp_x_float = float(position[0])
        self.rect.y = position[1]

    def get_image(self, x, y, w, h):
        raise NotImplementedError

    def move_right(self, pixels):
        self.rect.x += pixels

    def move_left(self, pixels):
        self.rect.x -= pixels

    def move_up(self, pixels):
        self.rect.y -= pixels

    def move_down(self, pixels):
        self.rect.y += pixels


class TurtleHero(Turtle):
    def __init__(self, type, size_coeff, name, position):
        print(__file__)
        self.image_sheet = pygame.image.load('sv_turtle_sheet.png').convert_alpha()
        super().__init__(type, size_coeff, name, position)
        self.ACC = 600
        self.TICK = 1 / 60.0
        self.SPEED_FAST = 300
        self.SPPED_SLOW = 150
        self.is_jumping = JumpStates.IDLE
        self.dist_to_jump = 0
        self.initial_y = 0
        self.jump_counter = 0
        self.moving = 0
        self.speed = 0
        self.speed_act = 0
        self.speed_target = 0
        ######animation##########
        self.init_sub = (7,0)# default icon column and row
        self.image = self.get_image(self.WIDTH * self.init_sub[0], self.HEIGHT * self.init_sub[1], self.WIDTH, self.HEIGHT)
        self.walk_r = [(6, 0), (7, 0), (8, 0)]  # icons of walk right column and row
        self.i_count = 0  # counter for walking speed
        self.hide_anim = (0, 3)  # icon of hide column and row
        self.die_anim = (6, 5)  # icon of die column and row
        self.right = 1  # turtle waling right flag

    def get_image(self, x, y, w, h):
        return self.image_sheet.subsurface((x, y, w, h))

    def init_jump(self, initial_v, grav_acc):
        self.is_jumping = JumpStates.UP
        self.dist_to_jump = (initial_v) ** 2 / (2 * grav_acc)
        print("init jump")
        print(self.dist_to_jump)
        self.initial_y = self.rect.y
        self.jump_counter = self.jump_counter + 1

    def changeSpeed(self, speed):
        self.speed = speed

    def init_move_right(self):
        self.i_count = 0
        self.speed_target = self.SPPED_SLOW

    def init_move_fast_right(self):
        self.i_count = 0
        self.speed_target = self.SPEED_FAST

    def init_move_left(self):
        self.i_count = 0
        self.speed_target = -1 * self.SPPED_SLOW

    def init_move_fast_left(self):
        self.i_count = 0
        self.speed_target = -1 * self.SPEED_FAST

    def stop_move(self):
        self.speed_target = 0

    def move(self):
        if self.speed_target == round(self.speed_act, 1):  # constant motion
            self.tmp_x_float = self.rect.x + self.speed_target * (self.TICK)
            self.rect.x = self.tmp_x_float + 0.5
        elif self.speed_target > self.speed_act:  # uniformly accelerated motion
            self.tmp_x_float = self.rect.x + self.speed_act * (self.TICK) + self.ACC * (self.TICK) ** 2 / 2
            self.speed_act = self.speed_act + self.ACC * (self.TICK)
            self.rect.x = self.tmp_x_float + 0.5
        elif self.speed_target < self.speed_act:  # uniformly deccelerated motion
            self.tmp_x_float = self.rect.x + self.speed_act * (self.TICK) - self.ACC * (self.TICK) ** 2 / 2
            self.speed_act = self.speed_act - self.ACC * (self.TICK)
            self.rect.x = self.tmp_x_float + 0.5
        if self.speed_act < 0.01 and self.speed_act > -0.01:  # if zero (precision 0.1) - stop entirely
            self.speed_act = 0.0
        self.update_moving_animation()
        # print("actual " + str(self.speed_act), "target " + str(self.speed_target))

    def jump(self, initial_v, grav_acc):
        if self.is_jumping == JumpStates.UP:
            self.rect.y = self.initial_y - initial_v * (self.jump_counter * self.TICK) + grav_acc * (self.jump_counter * self.TICK) ** 2 / 2
            print(self.rect.y)
            self.jump_counter = self.jump_counter + 1
            if self.initial_y - self.rect.y >= self.dist_to_jump:
                self.is_jumping = JumpStates.DOWN
                self.jump_counter = 1
                print("down")
                self.rect.y = self.initial_y - self.dist_to_jump
        elif self.initial_y >= self.rect.y and self.is_jumping == JumpStates.DOWN:
            self.rect.y = self.initial_y - self.dist_to_jump + grav_acc * (self.jump_counter * self.TICK) ** 2 / 2
            print(self.rect.y)
            self.jump_counter = self.jump_counter + 1
            if self.initial_y <= self.rect.y:
                self.is_jumping = JumpStates.IDLE
                self.dist_to_jump = 0
                self.rect.y = self.initial_y
                self.initial_y = 0
                self.jump_counter = 0
                print("end")

    def get_image_from_sprite_sheet(self, column, row):
        return self.get_image(column * self.WIDTH, row * self.HEIGHT, self.WIDTH, self.HEIGHT)

    def update_anim_stop_right(self):
        self.image = self.get_image_from_sprite_sheet(self.walk_r[1][0], self.walk_r[1][1])

    def update_anim_stop_left(self):
        self.image = self.get_image_from_sprite_sheet(self.walk_r[1][0], self.walk_r[1][1])
        self.image = pygame.transform.flip(self.image, True, False)

    def update_anim_walk_right(self, iter):
        count = self.i_count // iter
        self.image = self.get_image_from_sprite_sheet(self.walk_r[count][0], self.walk_r[count][1])
        self.i_count = (self.i_count + 1) % len(self.walk_r * iter)

    def update_anim_walk_left(self, iter):
        count = self.i_count // iter
        self.image = self.get_image_from_sprite_sheet(self.walk_r[count][0], self.walk_r[count][1])
        self.image = pygame.transform.flip(self.image, True, False)
        self.i_count = (self.i_count + 1) % len(self.walk_r * iter)

    def update_hide_anim(self):
        self.image = self.get_image_from_sprite_sheet(self.hide_anim[0], self.hide_anim[1])

    def update_die_anim(self):
        self.image = self.get_image_from_sprite_sheet(self.die_anim[0], self.die_anim[1])

    def update_moving_animation(self):
        if self.speed_act > 0.01:
            self.right = 1
            if self.speed_target == self.SPEED_FAST:
                self.update_anim_walk_right(2)
            else:
                self.update_anim_walk_right(6)
        elif self.speed_act < -0.1:
            self.right = 0
            if self.speed_target == self.SPEED_FAST * (-1):
                self.update_anim_walk_left(2)
                print("update 2 left")
            else:
                self.update_anim_walk_left(6)
                print("update 6 left")
        elif self.right:
            self.update_anim_stop_rigth()
        else:
            self.update_anim_stop_left()
