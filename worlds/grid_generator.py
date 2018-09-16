import os
import pathlib
import pickle

import cv2
import numpy as np


class GridGenerator:
    """
    Generates grid like maps. Allows for generation of new, empty grids as well as loading existing grid and creating a game level info out of it.
    """
    def __init__(self, cell_w, cell_h):
        """
        Initializes the Grid Generator
        :param cell_w: width of a single cell in grid (in pixels)
        :param cell_h: height of a single cell in grid (in pixels)
        """
        self.cell_w = cell_w
        self.cell_h = cell_h

        self.world_root = 'world_instances'

    def create_empty_grid(self, rows, cols):
        """
        Creates empty grid
        :param rows: number of rows in grid
        :param cols: number of columns in grid
        :return: grid as an image and basic grid description
        """
        img_h = rows * self.cell_h
        img_w = cols * self.cell_w

        # make empty white image
        background = np.ones(shape=[img_h, img_w], dtype=np.uint8) * 255

        # draw horizontal and vertical lines (for all but last pixels in on the right/bottom side of the image)
        for y in range(rows):
            cv2.line(background, (0, y * self.cell_h), (img_w, y * self.cell_h), color=0)
        for x in range(cols):
            cv2.line(background, (x * self.cell_w, 0), (x * self.cell_w, img_h), color=0)

        # generate lines also at last pixels at right/bottom side of the image
        cv2.line(background, (0, img_h - 1), (img_w, img_h - 1), color=0)  # horizontal
        cv2.line(background, (img_w - 1, 0), (img_w - 1, img_h), color=0)  # vertical

        grid_info = {'rows': rows,
                     'cols': cols,
                     'cell_w': self.cell_w,
                     'cell_h': self.cell_h,
                     'img_w': img_w,
                     'img_h': img_h,
                     'objects': []}
        return background, grid_info

    def save_world(self, world_name, grid, grid_info):
        """
        Saves world on disc.
        :param world_name: world name
        :param grid: image of grid
        :param grid_info: dictionary with information about grid
        """
        # create world dir if does not exist yet
        world_path = os.path.join(self.world_root, world_name)
        pathlib.Path(world_path).mkdir(parents=True, exist_ok=True)

        # save world
        cv2.imwrite(os.path.join(world_path, 'grid.png'), grid)
        pickle.dump(grid_info, open(os.path.join(world_path, 'grid_info.p'), 'wb'))


generator = GridGenerator(cell_w=20, cell_h=10)
grid, grid_info = generator.create_empty_grid(rows=15, cols=20)
generator.save_world('world_1', grid, grid_info)
