import os
import random

import numpy as np
from PIL import Image
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt


def resize_and_rotate_img(tile_img, tile_size, direction):
    """Resize and rotate an image.

    :param tile_img: Image to process
    :param tile_size: Size to be matched
    :param direction: Rotation direction in `__tile_dirs` key format
    :return: Processed image
    """

    res_img = tile_img.copy()
    res_img = res_img.resize((tile_size, tile_size))

    if direction:
        res_img = res_img.rotate(direction)

    return res_img


class Tile:

    @staticmethod
    def get_tile_dirs():
        """Tile direction format."""
        return [  # TODO: change to a more readable format ('left', 'right', etc.)
            0,  # ->
            90,  # ↑
            180,  # <-
            270,  # ↓
        ]

    def __init__(self, tile_type, direction):
        self.tile_type = tile_type
        self.direction = direction
        self.is_open = False
        self.objects = []

    def open(self):
        self.is_open = True
        pass

    def step(self, pirate, direction):
        pass


class GameMap:
    # Shape of the game map
    @staticmethod
    def get_map_shape():
        return (13, 13)

    # All game tiles in format {tile_type}:{amount}
    @staticmethod
    def __get_all_tiles():
        return {
            'empty': 40,
            'dir_straight': 3,
            'dir_45': 3,
            'dir_45_225': 3,
            'dir_0_180': 3,
            'dir_0_135_270': 3,
            'dir_diagonal': 3,
            'dir_uplr': 3,
            'horses': 2,
            'spinning_2': 5,
            'spinning_3': 4,
            'spinning_4': 2,
            'spinning_5': 1,
            'ice_lake': 6,
            'trap': 3,
            'cannon': 2,
            'fort': 2,
            'aborigine': 1,
            'drinking_rum': 4,
            'crocodile': 4,
            'ogre': 1,
            'baloon': 2,
            'plane': 1,
            'money_1': 5,
            'money_2': 5,
            'money_3': 3,
            'money_4': 2,
            'money_5': 1,
        }

    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.game_map = self.__create_map()

    @staticmethod
    def __is_in_water(x, y):
        """Check if this coordinates are in water."""
        return (
            x == 0 or y == 0 or
            x == 12 or y == 12 or
            (x == 1 and y == 1) or
            (x == 11 and y == 11) or
            (x == 1 and y == 11) or
            (x == 11 and y == 1)
        )

    @staticmethod
    def __prob_dist(tiles):
        """Get the probability distribution of tiles."""
        dist = []
        total = sum(tiles.values())
        for num in tiles.values():
            dist.append(num / total)
        return dist

    @staticmethod
    def get_side_center_coords(side):
        """Get the starting coordinates for a given side.
        :param side: {0: <-, 1: ↑, 2: ->, 3: ↓}
        :return: tuple of coordinates (x, y)
        """
        map_shape = GameMap.get_map_shape()
        axis_centers = list(map(lambda x: np.floor(x / 2.0), map_shape))
        return {
            0: (0, axis_centers[1]),
            1: (axis_centers[0], map_shape[1] - 1),
            2: (map_shape[0] - 1, axis_centers[1]),
            3: (axis_centers[0], 0),
        }[side]

    def __create_map(self):
        """Create a random game map.

        :return: numpy array with Tile values."""
        map_shape = GameMap.get_map_shape()
        game_map = np.empty(map_shape, dtype=Tile)
        tiles = GameMap.__get_all_tiles()
        for x in range(map_shape[0]):
            for y in range(map_shape[1]):
                # Check if this is a water tile1
                if self.__is_in_water(x, y):
                    tile_type = 'water'
                else:
                    tile_type = np.random.choice(
                        list(tiles), 1, p=self.__prob_dist(tiles))[0]
                    tiles[tile_type] -= 1

                    # If no tiles of this type left, delete them
                    if not tiles[tile_type]:
                        del tiles[tile_type]

                # Set random direction
                tile_dir = random.sample(Tile.get_tile_dirs(), 1)[0]
                game_map[y][x] = Tile(tile_type, tile_dir)

        assert len(tiles) == 0, \
            'All tiles must be used during the map creation!'
        return game_map

    def resize_and_rotate_img(self, tile_img, direction):
        return resize_and_rotate_img(tile_img, self.tile_size, direction)

    def get_tile_pixel_inds(self, coords):
        x, y = coords
        return (slice(*self.scale_coords((x, x + 1))),
                slice(*self.scale_coords((y, y + 1))))

    def scale_coords(self, coords):
        x, y = coords
        return (x * self.tile_size,
                y * self.tile_size)

    def unscale_coords(self, coords):
        x, y = coords
        return (x // self.tile_size,
                y // self.tile_size)

    def map_to_img(self):
        """Create a full image of a map."""
        map_img = np.zeros(
            (*self.scale_coords(self.game_map.shape), 3), dtype=np.uint8)
        closed_tile_img = Image.open(os.path.join(
            'tile_images', 'back.png'))
        for coords, tile in np.ndenumerate(self.game_map):
            if tile.tile_type == 'water':
                # TODO: Add 'water' tile image.
                tile_img = np.zeros((self.tile_size, self.tile_size, 3))
            else:
                if not tile.is_open:
                    tile_img = closed_tile_img
                else:
                    tile_img = Image.open(os.path.join(
                        'tile_images', tile.tile_type + '.png'))
                tile_img = resize_and_rotate_img(
                    tile_img, self.tile_size, tile.direction)
            map_img[self.get_tile_pixel_inds(coords)] = tile_img
        return Image.fromarray(map_img)

    def display_players(self, painter: QPainter, players):
        for player in players:
            for character in player.characters:
                if character.ch_type == 'pirate':
                    color = QColor(*color_to_rgb(player.color))
                painter.setBrush(QBrush(color, Qt.SolidPattern))
                painter.drawEllipse(*self.scale_coords(character.coords),
                                    self.tile_size, self.tile_size)


# @staticmethod
def color_to_rgb(game_color):
    return {
        'red': (238, 29, 35),
        'white': (255, 255, 255),
        'black': (35, 31, 32),
        'yellow': (255, 221, 23),
    }[game_color]
