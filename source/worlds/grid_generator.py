import argparse
import os
import pathlib
import pickle

import cv2
import numpy as np


class GridGenerator:
    """
    Generates grid like maps. Allows for generation of new, empty grids as well as loading existing grid and creating a game level info out of it.
    """

    def __init__(self, cell_w=None, cell_h=None):
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
            "CHECKPOINT_GROUND": {'color': (0, 255, 255), 'info': "yellow, for places with checkpoints"},
            "EMPTY_CELL": {'color': (255, 255, 255), 'info': "empty cell"}
        }

    def find_color_index(self, rgb_val: tuple):
        """
        Based on rgb color tuple, finds the index of the associated cell type
        :param rgb_val: tuple (r,g,b)
        :return: index of cell type
        """
        colors = [v['color'] for _, v in self.cell_types.items()]
        try:
            return colors.index(rgb_val)
        except KeyError:
            raise Exception("{} not in available cell color types!".format(rgb_val))

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

        # for each possible cell colour, draw a simple rectangle with it and add a textual description
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
                     'objects_matrix': None}
        background = np.vstack([legend, background])
        return background, grid_info

    def save_world(self, world_name, grid=None, grid_info=None):
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
        if grid is not None:
            cv2.imwrite(os.path.join(world_path, 'empty_grid.png'), grid)
        if grid_info is not None:
            pickle.dump(grid_info, open(os.path.join(world_path, 'grid_info.p'), 'wb'))

    def load_world(self, world_name, grid_image_name):
        """
        Loads current grid (specified by grid image name) and the corresponding grid info
        :param world_name: name of the world
        :param grid_image_name: name of the image with grid
        :return: grid image, grid info
        """
        world_path = os.path.join('world_instances', world_name)
        grid = cv2.imread(os.path.join(world_path, grid_image_name))
        grid_info = pickle.load(open(os.path.join(world_path, 'grid_info.p'), 'rb'))
        return grid, grid_info

    def update_grid_info(self, colored_grid, current_info):
        """
        Makes an update of a grid (usually the colored one)
        :param colored_grid: grid with colors overlaid
        :param current_info: current dictionary with info about grid
        :return: updated grid dictionary
        """
        cell_w = current_info['cell_w']
        cell_h = current_info['cell_h']
        img_start = current_info['legend_h']
        rows = current_info['rows']
        cols = current_info['cols']

        # fille a matrix associated with cells with values reffering to the indices of the appropriate cell types
        objects_matrix = np.ones([rows, cols], np.int8) * -1
        grid = colored_grid[img_start:, :, :]
        for y in range(rows):
            y_c = y * cell_h + cell_h // 2
            for x in range(cols):
                x_c = x * cell_w + cell_w // 2
                type = self.find_color_index(tuple(grid[y_c, x_c]))
                objects_matrix[y, x] = type

        current_info['objects_matrix'] = objects_matrix
        return current_info


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("world_name", help="name of the world")
    # flags referring to work mode (either create new or update existing grid)
    parser.add_argument("--create", help="flag | use when you want to create new grid", action="store_true")
    parser.add_argument("--update", help="flag | use when you want to update information about existing (perhaps colored) grid", action="store_true")
    parser.add_argument("--rows", help="number of rows in newly created grid (use only with --create)", type=int)
    parser.add_argument("--cols", help="number of columns in newly created grid (use only with --create)", type=int)
    parser.add_argument("--w", help="width of a single cell in newly created grid (use only with --create)", type=int)
    parser.add_argument("--h", help="height of a single cell in newly created grid (use only with --create)", type=int)
    parser.add_argument("--grid_name", help="name of image with grid to modify (use only with --update)", type=str)

    args = parser.parse_args()

    # at LEAST and at MOST one flat must be provided
    if args.create and args.update:
        raise Exception('You must provide either --create or --update flag, not both!')
    elif not (args.create or args.update):
        raise Exception('One of --create or --update flags must be provided!')
    else:
        # either create new or modify existing grid
        if args.create:
            if not all([args.rows, args.cols, args.w, args.h]):
                raise Exception('All of parameters: --rows, --cols, --w, --h must be provided when --create is used!')
            else:
                generator = GridGenerator(cell_w=args.w, cell_h=args.h)
                grid, grid_info = generator.create_empty_grid(rows=args.rows, cols=args.cols)
                generator.save_world(args.world_name, grid, grid_info)
        elif args.update:
            if not args.grid_name:
                raise Exception('When --update is used, a --grid_name must be provided!')
            generator = GridGenerator()
            grid, grid_info = generator.load_world(args.world_name, args.grid_name)
            updated_grid_info = generator.update_grid_info(grid, grid_info)
            generator.save_world(args.world_name, None, grid_info)
