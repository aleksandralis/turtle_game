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
        if event.type == pygame.QUIT:
            carryOn = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and playerTurtle.is_jumping == 0:
                playerTurtle.init_jump(400, 800)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        playerTurtle.moveLeft(5)
    if keys[pygame.K_RIGHT]:
        playerTurtle.moveRight(5)
    if keys[pygame.K_UP]:
        playerTurtle.moveUp(5)
    if keys[pygame.K_DOWN]:
        playerTurtle.moveDown(5)

    all_sprites_list.update()
    if playerTurtle.is_jumping != 0:
        playerTurtle.jump(400, 800)
    # Drawing on Screen
    screen.fill(GREEN)
    # Now let's draw all the sprites in one go. (For now we only have 1 sprite!)
    all_sprites_list.draw(screen)

    # Refresh Screen
    pygame.display.flip()

    # Number of frames per secong e.g. 60
    clock.tick(60)

pygame.quit()
