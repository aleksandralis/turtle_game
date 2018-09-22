import pickle

import numpy as np
import pygame


class StaticBlock(pygame.sprite.Sprite):
    """
    A class for defining a block of "obstacle", like for example block of grass
    """

    def __init__(self, x, y, units_w, units_h, images, is_deadly):
        """
        A base class for static obstacles, like blocks of solid ground, but also for water, lava, spikes etc.
        :params x, y: coordinates of the origin of block, in pixels
        :params units_w, units_h: width and height of the block (in units)
        :param images: a set of images associated with the block. Might contain several images (it's dependent on class children)
        :param is_deadly: specifies, whether touching the block is deadly for the hero
        """
        # Call the parent class (Sprite) constructor
        super().__init__()

        # specify block params
        self.is_deadly = is_deadly

        # gets image appropriate for the block and uses it as a block surface
        block_image = self.get_image(units_w, units_h, images)
        self.image = pygame.surfarray.make_surface(block_image)
        self.rect = self.image.get_rect()

        self.set_position(x, y)

    def set_position(self, x, y):
        """
        Sets block position
        :param x: x, in pixels
        :param y: y, in pixels
        :return:
        """
        self.rect.x = x
        self.rect.y = y

    def get_image(self, units_w, units_h, images):
        """Creates an image appropriate for the block"""
        raise NotImplementedError

    def move_block(self, dx, dy):
        """
        Moves block by given pixels. Needed for simulating camera movement
        :param dx: pixels increment in x axis
        :param dy: pixels increment in y axis
        """
        self.rect.x += dx
        self.rect.y += dy


class BottomBlock(StaticBlock):
    """
    A class for defining static objects that are moving the bottom of the screen, therefore usually contains two types of images: a top one and a (possibly repeated) bottom one,
    connected with the end of the screen
    """

    def __init__(self, x, y, units_w, units_h, images, is_deadly):
        super().__init__(x, y, units_w, units_h, images, is_deadly)

    def get_image(self, units_w, units_h, images):
        top_img = images['top_img']
        result_img = np.concatenate([top_img] * units_w, axis=1)  # repeat image units_w times

        if units_h > 1:  # a block contains more than one block (must have also a bottom block)
            bottom_img = images['bottom_img']
            bottom_img = np.concatenate([bottom_img] * units_w, axis=1)  # repeat image units_w times

            # if there are multiple bottom blocks needed (we already used two of them, one for top block, second for first bottom block)
            if units_h - 2 > 0:
                bottom_img = np.concatenate([bottom_img] * (units_w - 2), axis=0)  # repeat image remaining unit_h - 2 times

            # final top and bottom concat
            result_img = np.concatenate([result_img, bottom_img], axis=0)

        # oddly, pygame images are rotated counterclockwise of 90 degrees
        result_img = np.rot90(result_img, 1)
        return result_img


class World:
    """
    Class responsible for drawing world and populating it with static sprites.
    """

    def __init__(self, grid_file_path):
        """
        Initializes world.
        :param grid_file_path: the pickle file, describing world (its size and objects matrix)
        """
        self.cell_types = {
            0: 'GROUND',
            1: 'PLATFORM',
            2: 'WATER',
            3: 'LOOT_CRATE',
            4: 'DEADLY_GROUND',
            5: 'CHECKPOINT_GROUND',
            6: 'EMPTY_CELL'
        }

        self.cell_type_ids = {v: k for k, v in self.cell_types.items()}

        grid_info = pickle.load(open(grid_file_path, "rb"))

        self.world_h = grid_info['img_h']
        self.world_w = grid_info['img_w']
        self.cell_h = grid_info['cell_w']
        self.cell_w = grid_info['cell_h']
        self.obj_matrix = grid_info['objects_matrix']

        connected_objects = self.find_connected_components()
        print(connected_objects)

    def find_vertically_connected(self, matrix, background_idx):
        """
        Finds connected objects (for eg. parts of ground that belong to the same group), clusters them and returns them as a list of objects. Works vertically
        :param matrix: matrix of objects, extracted from grid_info
        :param background_idx: index of background cells in matrix - will be omitted during computations
        :return: list of lists, where each sublist contains information about objects in column, when there were some
        """
        # 1st pass - simple, vertical finding of connected components
        vertical_objects = []
        for c in range(matrix.shape[1]):  # iterate over columns
            column_objects = []
            col = matrix[:, c]

            # if all cells contain only backgrounds, there is no object to append to the list
            if all(item == background_idx for item in col):
                continue

            # slow and fast runner iteration
            runner_slow, runner_fast = 0, 0
            while runner_slow < len(col):
                # skim through unimportant background cells in considered column
                if col[runner_slow] == background_idx:
                    runner_slow += 1
                else:
                    current_type = col[runner_slow]
                    runner_fast = runner_slow + 1

                    # find out, where does the current sequence of objects ends
                    while runner_fast < len(col):
                        if col[runner_fast] != current_type:  # stop looking for current object, when you find cell of different type
                            break
                        runner_fast += 1

                    column_objects.append({'type': self.cell_types[current_type], 'y': runner_slow, 'x': c, 'height': runner_fast - runner_slow})
                    runner_slow = runner_fast

            vertical_objects.append(column_objects)
        return vertical_objects

    def find_horizontally_connected(self, objects_in_columns):
        """
        Tries to find objects connected horizontally
        :param objects_in_columns: list of lists, containing information about objects in columns
        :return: list of objects, describing their positions and sizes (in units from matrix, not pixels)
        """
        connected_objects = []
        temporary_objects = []  # objects that may not be yet fully connected

        for objects in objects_in_columns:  # iterate over columns
            x = objects[0]['x']  # not every column contained objects, so we need to extract its x position

            # for all objects in the single column
            for obj in objects:
                # there should be at most one, however I use list comprehension for readability (also for convenient None check later)
                matching_objects = [temp_obj for temp_obj in temporary_objects if temp_obj['y'] == obj['y'] and temp_obj['height'] == obj['height']]

                if matching_objects:  # if adjacent object was found
                    updated_object = matching_objects[0]
                    updated_object['width'] += 1
                    temporary_objects[temporary_objects.index(matching_objects[0])] = updated_object
                else:  # no adjacent object was found - so the object in column should start a new connected object
                    new_object = obj
                    new_object['width'] = 1
                    new_object['x'] = x
                    temporary_objects.append(new_object)

            # cleaning the temporary list, if it's not empty
            if temporary_objects:
                inactive_objects = [obj for obj in temporary_objects if obj['x'] + obj['width'] < x]  # these objects are already finished
                connected_objects.extend(inactive_objects)

                temporary_objects = [obj for obj in temporary_objects if not (obj['x'] + obj['width'] < x)]  # these objects are still active

        # move last object from temporary list to list of connected objects
        connected_objects.extend(temporary_objects)
        return connected_objects

    def find_connected_components(self):
        """
        Finds connected components of rectangular shape
        :return: list of connected objects
        """
        vertically_connected = self.find_vertically_connected(self.obj_matrix, self.cell_type_ids['EMPTY_CELL'])
        connected_list = self.find_horizontally_connected(vertically_connected)
        return connected_list


world = World('world_instances/world_1/grid_info.p')

#
# SCREENWIDTH = 800
# SCREENHEIGHT = 600
#
# t = cv2.imread('/media/carlo/My Files/DL Playground/turtle_game/source/worlds/assets/grass_block.png')
# b = cv2.imread('/media/carlo/My Files/DL Playground/turtle_game/source/worlds/assets/dirt_block.png')
#
# t = cv2.cvtColor(t, cv2.COLOR_BGR2RGB)
# b = cv2.cvtColor(b, cv2.COLOR_BGR2RGB)
#
# block_images = {'top_img': t, 'bottom_img': b}
# block = BottomBlock(200, 200, 5, 1, block_images, True)
#
# size = (SCREENWIDTH, SCREENHEIGHT)
# screen = pygame.display.set_mode(size)
#
# all_sprites_list = pygame.sprite.Group()
# all_sprites_list.add(block)
#
# carryOn = True
# clock = pygame.time.Clock()
#
# while carryOn:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             carryOn = False
#     all_sprites_list.update()
#     all_sprites_list.draw(screen)
#     pygame.display.flip()
#     clock.tick(60)
#
# pygame.quit()
