import pygame
from source.turtles.turtle_hero import Turtle, Turtle_Hero

SCREENWIDTH = 800
SCREENHEIGHT = 600
GREEN = (20, 255, 140)

size = (SCREENWIDTH, SCREENHEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Turtle Game")

playerTurtle = Turtle_Hero("normal", 0.5, "Karol1", (200, 200))

# Allowing the user to close the window...
carryOn = True
clock = pygame.time.Clock()

all_sprites_list = pygame.sprite.Group()
all_sprites_list.add(playerTurtle)

while carryOn:
    for event in pygame.event.get():
        keys2 = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            carryOn = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and playerTurtle.is_jumping == 0:
                playerTurtle.init_jump(400, 800)
            if event.key == pygame.K_RIGHT and not keys2[pygame.KMOD_CTRL]:
                playerTurtle.init_move_right()
            elif event.key == pygame.K_RIGHT and keys2[pygame.KMOD_CTRL]:
                playerTurtle.init_move_fast_right()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.KMOD_CTRL and keys2[pygame.K_RIGHT]:
                playerTurtle.init_move_right()

    keys = pygame.key.get_pressed()
    #if keys[pygame.K_LEFT]:
    #    playerTurtle.moveLeft(5)
    #if keys[pygame.K_RIGHT]:
        #playerTurtle.moveRight(5)
    if keys[pygame.K_UP]:
        playerTurtle.moveUp(5)
    if keys[pygame.K_DOWN]:
        playerTurtle.moveDown(5)
    if not keys[pygame.K_RIGHT] and not keys[pygame.KMOD_CTRL]:
        playerTurtle.stop_move()

    all_sprites_list.update()
    if playerTurtle.is_jumping != 0:
        playerTurtle.jump(400, 800)

    if playerTurtle.speed_act != 0 or playerTurtle.speed_target != 0:
        playerTurtle.move()
    # Drawing on Screen
    screen.fill(GREEN)
    # Now let's draw all the sprites in one go. (For now we only have 1 sprite!)
    all_sprites_list.draw(screen)

    # Refresh Screen
    pygame.display.flip()

    # Number of frames per secong e.g. 60
    clock.tick(60)

pygame.quit()
