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

        # cell types and associated colours
        self.cell_types = {
            "GROUND": {'color': (0, 0, 0), 'info': "black, for solid ground, where turtle can safely walk"},
            "PLATFORM": {'color': (0, 255, 0), 'info': "green, for hanging platforms, where turtle can safely jump"},
            "WATER": {'color': (255, 0, 0), 'info': "blue, for water, swimmable by turtle"},
            "LOOT_CRATE": {'color': (19, 69, 139), 'info': "brown, for loot crates with snails and other edible things"},
            "DEADLY_GROUND": {'color': (0, 0, 255), 'info': "red, for deadly grounds (where turtle dies)"},
            "CHECKPOINT_GROUND": {'color': (0, 255, 255), 'info': "yellow, for places with checkpoints"}
        }

    def make_legend(self, img_w):
        """
        Creates an image with legend made of colors and their inforiptions
        :param img_w: width of the image
        :return: image with legend
        """
        # make color rectangles bigger than standard cells
        cell_w = self.cell_w * 2
        cell_h = self.cell_h * 2

        total_height = len(self.cell_types) * self.cell_w
        background = np.ones(shape=[total_height, img_w, 3], dtype=np.uint8) * 255

        # for each possible cell colour, draw a simple rectagnel with it and add a textual infoription
        for i, (_, v) in enumerate(self.cell_types.items()):
            cv2.rectangle(background, (0, i * cell_h), (cell_w, (i + 1) * cell_h - 1), color=v['color'], thickness=-1)  # fill rectangle
            cv2.putText(background, v['info'], (cell_w + 20, i * cell_h + cell_h // 2), cv2.FONT_HERSHEY_TRIPLEX, 0.3, (0, 0, 0))
        return background

    def create_empty_grid(self, rows, cols):
        """
        Creates empty grid
        :param rows: number of rows in grid
        :param cols: number of columns in grid
        :return: grid as an image and basic description
        """
        img_h = rows * self.cell_h
        img_w = cols * self.cell_w

        # make empty white image, 3 channels
        background = np.ones(shape=[img_h, img_w, 3], dtype=np.uint8) * 255

        # draw black horizontal and vertical lines (for all but last pixels in on the right/bottom side of the image)
        for y in range(rows):
            cv2.line(background, (0, y * self.cell_h), (img_w, y * self.cell_h), color=(128, 128, 128))
        for x in range(cols):
            cv2.line(background, (x * self.cell_w, 0), (x * self.cell_w, img_h), color=(128, 128, 128))

        # generate lines also at last pixels at right/bottom side of the image
        cv2.line(background, (0, img_h - 1), (img_w, img_h - 1), color=(128, 128, 128))  # horizontal
        cv2.line(background, (img_w - 1, 0), (img_w - 1, img_h), color=(128, 128, 128))  # vertical

        # add grid info and legend
        legend = self.make_legend(img_w)
        grid_info = {'rows': rows,
                     'cols': cols,
                     'cell_w': self.cell_w,
                     'cell_h': self.cell_h,
                     'img_w': img_w,
                     'img_h': img_h,
                     'legend_h': legend.shape[0],
                     'objects': []}
        background = np.vstack([legend, background])
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
        cv2.imwrite(os.path.join(world_path, 'empty_grid.png'), grid)
        pickle.dump(grid_info, open(os.path.join(world_path, 'grid_info.p'), 'wb'))


generator = GridGenerator(cell_w=20, cell_h=10)
grid, grid_info = generator.create_empty_grid(rows=15, cols=20)
generator.save_world('world_1', grid, grid_info)
