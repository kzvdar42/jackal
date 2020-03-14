import os
import random
from typing import List, Tuple
import numpy as np
from collections import defaultdict
from collections.abc import Iterable
from functools import partial
import operator

from Characters import Character

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


class Coords:
    """Class for coords and math associated with them."""

    def __init__(self, x, y):
        self.coords = x, y

    def __perform_op(self, operation, other, inplace=False, from_right=False):
        x, y = self.coords
        if not isinstance(other, Iterable):
            other = (other, other)
        if from_right:
            x, y, other = *other, (x, y)
        # TODO: Better comment for the assert.
        assert len(other) == 2, "Length should be two."
        x = operation(x, other[0])
        y = operation(y, other[1])
        if inplace:
            self.coords = x, y
        return Coords(x, y)

    def get_coords(self):
        return self.coords

    def set_coords(self, x, y):
        self.coords = x, y

    def __getitem__(self, idx):
        return self.coords[idx]

    def __setitem__(self, idx, value):
        self.coords[idx] = value

    def __len__(self):
        return 2

    def __hash__(self):
        return hash(self.coords)

    def __eq__(self, other):
        return self.coords == other.coords

    def __add__(self, other):
        return self.__perform_op(operator.add, other)
    __radd__ = __add__

    def __mul__(self, other):
        return self.__perform_op(operator.mul, other)
    __rmul__ = __mul__

    def __sub__(self, other):
        return self.__perform_op(operator.sub, other)

    def __rsub__(self, other):
        return self.__perform_op(operator.sub, other, from_right=True)

    def __floordiv__(self, other):
        return self.__perform_op(operator.floordiv, other)

    def __rfloordiv__(self, other):
        return self.__perform_op(operator.floordiv, other, from_right=True)


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
        return Coords(13, 13)

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
            0: Coords(0, axis_centers[1]),
            1: Coords(axis_centers[0], map_shape[1] - 1),
            2: Coords(map_shape[0] - 1, axis_centers[1]),
            3: Coords(axis_centers[0], 0),
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
        return (slice(*self.scale_coords(Coords(x, x + 1))),
                slice(*self.scale_coords(Coords(y, y + 1))))

    def scale_coords(self, coords):
        if not isinstance(coords, Coords):
            coords = Coords(*coords)
        return coords * self.tile_size

    def unscale_coords(self, coords: Coords):
        if not isinstance(coords, Coords):
            coords = Coords(*coords)
        return coords // self.tile_size

    def map_to_img(self):
        """Create a full image of a map."""
        print(self.scale_coords(self.game_map.shape))
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

    def display_players(self, painter: QPainter,
                        players: List[Character], cur_character: Character):

        def get_character_color(color):
            if character.ch_type == 'pirate':
                return QColor(*color_to_rgb(color))
            else:
                raise NotImplemented('The color for non pirate characters is not yet defined.')

        # TODO: Find a better way to understand if players are on the same tile.
        # Extract positions.
        positions = defaultdict(list)
        for player in players:
            for character in player.characters:
                positions[character.coords].append((character, player.color))
        # Display the characters at each position.
        for pos, characters in positions.items():
            for i, (character, ch_color) in enumerate(characters):
                painter.setBrush(QBrush(get_character_color(ch_color), Qt.SolidPattern))
                ellipse_size = self.tile_size / len(characters)
                painter.drawEllipse(*(i * ellipse_size + self.scale_coords(pos)),
                                    ellipse_size, ellipse_size)
                # Display the glow outside the current player.
                if character is cur_character:
                    painter.setBrush(QBrush(QColor(*color_to_rgb('green')), Qt.SolidPattern))
                    painter.drawEllipse(*(self.scale_coords(pos) + (i + 1 / 4) * ellipse_size),
                                        ellipse_size / 2, ellipse_size / 2)


# @staticmethod
def color_to_rgb(game_color):
    return {
        'red': (238, 29, 35),
        'white': (255, 255, 255),
        'black': (35, 31, 32),
        'yellow': (255, 221, 23),
        'green': (127, 255, 0),
    }[game_color]
