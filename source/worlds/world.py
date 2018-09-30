import cv2
import os
import pickle

import numpy as np
import pygame

from source.worlds.grid_generator import cell_types


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
        # idk why, but normal images are rotated 90deg in pygame, so we need to reverse this process
        return np.rot90(images['top_img'], 1)

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

            # repeat bottom block units_h - 1 times (because we already have one unit_h for top block)
            if units_h - 2 > 0:
                bottom_img = np.concatenate([bottom_img] * (units_h - 1), axis=0)  # repeat image remaining unit_h - 2 times

            # final top and bottom concat
            result_img = np.concatenate([result_img, bottom_img], axis=0)

        # oddly, pygame images are rotated counterclockwise of 90 degrees
        result_img = np.rot90(result_img, 1)
        return result_img


class World:
    """
    Class responsible for drawing world and populating it with static sprites.
    """

    def __init__(self, grid_file_path, screen_w, screen_h, cell_types=cell_types):
        """
        Initializes world.
        :param grid_file_path: the pickle file, describing world (its size and objects matrix)
        """
        self.__screen_w = screen_w
        self.__screen_h = screen_h

        self.cell_types = {i: k for i, k in enumerate(cell_types.keys())}
        self.cell_type_ids = {v: k for k, v in self.cell_types.items()}

        grid_info = pickle.load(open(grid_file_path, "rb"))

        self.__world_h = grid_info['img_h']
        self.__world_w = grid_info['img_w']
        self.__cell_h = grid_info['cell_h']
        self.__cell_w = grid_info['cell_w']
        self.__obj_matrix = grid_info['objects_matrix']

        connected_objects = self.find_connected_components()

        self.assets = self.load_assets('assets', [key for key in self.cell_type_ids.keys() if key is not 'EMPTY_CELL'])

        self.__sprites = self.make_sprites(connected_objects)

    def move_world(self, dx, dy):
        """Moves world by dx and dy pixels"""
        for sprite in self.__sprites:
            sprite.move_block(dx, dy)

    def find_screen_offset(self, screen_h):
        """Finds world-screen difference and returns corresponding offset"""
        dy = screen_h - self.__world_h
        return dy

    def get_sprites(self):
        """Returns a list of sprites of world obstacles"""
        return self.__sprites

    def load_assets(self, path, cell_names):
        """
        Loads assets for cell types, based on names; assigning additional information to them. Each asset must be named according to rules:
        NAME-MODE-FEATURE1-FEATURE2-FEATUREn.png. Also does all neccessary preprocessing, like resizing etc.

        NAME - specifies the name of type, like ground, deadly ground etc.
        MODE - TOP / BOTTOM, specifies type of block (for example top block of grass and bottom block of dirt), all blocks must have at least their top version
        FEATURE - available from list: DEADLY (specifies, wheter the block is deadly in touch), TRANSPARENT (specifies, whether the block should be transparent),
                PHYSICAL - wheter the object should react with the turtle (for example water shouldn't, turtle should go through it),
                MASKABLE - wheter a mask should be created

        :param path: path to root directory of assets
        :param cell_types: dictionary with types
        :return: dict {cell_name: assets}
        """
        assets = {}
        filenames = os.listdir(path)
        for cell_name in cell_names:
            asset_info = {}

            # find all assets associated to the cell type
            associated_filenames = [name for name in filenames if name.startswith(cell_name.lower())]
            if not associated_filenames:  # all cell types must have the associated assets!
                raise Exception("There are no assets associated to {}!".format(cell_name))

            # assign images to assets
            images = {}
            for asset_name in associated_filenames:
                # preprocess image (load, scale, bgr to rgb color conversion)
                img = cv2.imread(os.path.join(path, asset_name))
                img = cv2.resize(img, (self.__cell_w, self.__cell_h))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                if 'top' in asset_name:
                    images['top_img'] = img

                    # assign another features
                    asset_info['deadly'] = True if 'deadly' in asset_name else False
                    asset_info['transparent'] = True if 'transparent' in asset_name else False
                    asset_info['physical'] = True if 'physical' in asset_name else False
                    asset_info['maskable'] = True if 'maskable' in asset_name else False

                elif 'bottom' in asset_name:
                    images['bottom_img'] = img
                asset_info['images'] = images
            assets[cell_name] = asset_info

        return assets

    def make_sprites(self, connected_objects):
        """Creates pygame sprites from list of connected components, transforming them from unitary units into pixels"""
        # compute screen offset
        dy = self.find_screen_offset(self.__screen_h)

        all_sprites = pygame.sprite.Group()
        for i, obj in enumerate(connected_objects):
            asset = self.assets[obj['type']]
            x = obj['x'] * self.__cell_w
            y = obj['y'] * self.__cell_h

            # if bottom-expandable asset
            if 'bottom_img' in asset['images'].keys():
                sprite = BottomBlock(x, y + dy, obj['width'], obj['height'], asset['images'], asset['deadly'])
                all_sprites.add(sprite)
            else:
                sprite = StaticBlock (x, y + dy, obj['width'], obj['height'], asset['images'], asset['deadly'])
                all_sprites.add(sprite)
        return all_sprites

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
            x = objects[0]['x']  # not every column must contain objects, so we need to extract its x position

            # for all objects in the single column
            for obj in objects:
                # there should be at most one, however I use list comprehension for readability (also for convenient None check later)
                matching_objects = [temp_obj for temp_obj in temporary_objects if temp_obj['y'] == obj['y']
                                    and temp_obj['height'] == obj['height']
                                    and temp_obj['type'] == obj['type']]

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
                inactive_objects = [obj for obj in temporary_objects if obj['x'] + obj['width'] < x + 1]  # these objects are already finished
                connected_objects.extend(inactive_objects)

                temporary_objects = [obj for obj in temporary_objects if obj not in inactive_objects]  # these objects are still active

        # move last object from temporary list to list of connected objects
        connected_objects.extend(temporary_objects)
        return connected_objects

    def find_connected_components(self):
        """
        Finds connected components of rectangular shape
        :return: list of connected objects
        """
        vertically_connected = self.find_vertically_connected(self.__obj_matrix, self.cell_type_ids['EMPTY_CELL'])
        connected_list = self.find_horizontally_connected(vertically_connected)
        return connected_list

# >>>>>>>>>>>>>>>>> only for testing!!! todo remove
if __name__ == '__main__':
    SCREENWIDTH = 1200
    SCREENHEIGHT = 750

    world = World('world_instances/world_1/grid_info.p', SCREENWIDTH, SCREENHEIGHT)
    sprites = world.get_sprites()

    size = (SCREENWIDTH, SCREENHEIGHT)
    screen = pygame.display.set_mode(size)

    carryOn = True
    clock = pygame.time.Clock()

    while carryOn:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                carryOn = False
        screen.fill((0, 0, 0))
        world.move_world(-1,0)
        sprites.update()
        sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
# >>>>>>>>>>>>>>>>> only for testing!!!