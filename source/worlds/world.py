import pickle


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

        print(self.obj_matrix)

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
