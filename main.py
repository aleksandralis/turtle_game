import pygame

from source.turtles.turtle_hero import TurtleHero, JumpStates
from source.worlds.world import World

SCREENWIDTH = 1200
SCREENHEIGHT = 750
GREEN = (20, 255, 140)

size = (SCREENWIDTH, SCREENHEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Turtle Game")

# create turtle
playerTurtle = TurtleHero("normal", 0.5, "Karol1", (100, 600))

# create world
world = World('source/worlds/world_instances/world_1/grid_info.p', 'source/worlds/assets', SCREENWIDTH, SCREENHEIGHT)
world_sprites = world.get_sprites()
world.update(screen)

# Allowing the user to close the window...
carryOn = True
clock = pygame.time.Clock()

all_sprites_list = pygame.sprite.Group()
all_sprites_list.add(playerTurtle)

# current turtle position
turtle_x = playerTurtle.x
turtle_y = playerTurtle.y
# difference between current and previous turtle position
delta_x = 0
delta_y = 0
# minimal increment
min_delta = 0.1

while carryOn:
    for event in pygame.event.get():
        keys2 = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            carryOn = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and playerTurtle.is_jumping == JumpStates.IDLE:
                playerTurtle.init_jump(400, 800)
            if event.key == pygame.K_RIGHT and not keys2[pygame.K_RCTRL]:
                # print("init right !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                playerTurtle.init_move_right()
            elif event.key == pygame.K_RIGHT and keys2[pygame.K_RCTRL]:
                # print("init fast right!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                playerTurtle.init_move_fast_right()
            elif event.key == pygame.K_LEFT and keys2[pygame.K_RCTRL]:
                playerTurtle.init_move_fast_left()
            elif event.key == pygame.K_LEFT and not keys2[pygame.K_RCTRL]:
                playerTurtle.init_move_left()
            elif event.key == pygame.K_RCTRL and keys2[pygame.K_RIGHT]:
                playerTurtle.init_move_fast_right()
            elif event.key == pygame.K_RCTRL and keys2[pygame.K_LEFT]:
                playerTurtle.init_move_fast_left()
            elif event.key == pygame.K_z:
                playerTurtle.update_hide_anim()
            elif event.key == pygame.K_x:
                playerTurtle.update_die_anim()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RCTRL and keys2[pygame.K_RIGHT]:
                playerTurtle.init_move_right()
            elif event.key == pygame.K_RCTRL and keys2[pygame.K_LEFT]:
                playerTurtle.init_move_left()

    keys = pygame.key.get_pressed()
    # if keys[pygame.K_LEFT]:
    #    playerTurtle.moveLeft(5)
    # if keys[pygame.K_RIGHT]:
    # playerTurtle.moveRight(5)
    if keys[pygame.K_UP]:
        playerTurtle.move_up(5)
    if keys[pygame.K_DOWN]:
        playerTurtle.move_down(5)
    if not keys[pygame.K_RIGHT] and not keys[pygame.KMOD_CTRL] and not keys[pygame.K_LEFT]:
        playerTurtle.stop_move()

    all_sprites_list.update()
    #print(playerTurtle.rect.bottomright)
    if playerTurtle.speed_act != 0 or playerTurtle.speed_target != 0:
        new_x = playerTurtle.move()
        delta_x = -int(new_x - turtle_x) if abs(new_x - turtle_x) >= min_delta else 0
        world.move_world(delta_x, 0)
        delta_x = world.find_collisions_x(playerTurtle, delta_x)
        print(delta_x)
        playerTurtle.x = playerTurtle.x + delta_x
        turtle_x = playerTurtle.x
    if playerTurtle.is_jumping != JumpStates.IDLE:
        new_y = playerTurtle.jump(400, 800)
        delta_y = -int(new_y - turtle_y) if abs(new_y - turtle_y) >= min_delta else 0
        turtle_y = new_y
    else:
        delta_y = 0

    # Drawing on Screen
    #print(delta_x)
    if delta_x != 0 or delta_y != 0:
        world.move_world(delta_x, delta_y)



    world.update(screen)


    # Now let's draw all the sprites in one go. (For now we only have 1 sprite!)
    all_sprites_list.draw(screen)

    # Refresh Screen
    pygame.display.flip()

    # Number of frames per secong e.g. 60
    clock.tick(60)

pygame.quit()
