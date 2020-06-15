import os
import random
from typing import List, Tuple
import numpy as np
from collections import defaultdict
from collections.abc import Iterable
from functools import partial
import operator

from Characters import Player, Character, map_players_to_positions
from CanStep import get_tile_behavior

from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QImage
from PyQt5.QtCore import Qt, QRect


class Coords(Iterable):
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
        new_coords = list(self.coords)
        new_coords[idx] = value
        self.coords = tuple(new_coords)

    def copy(self):
        return Coords(*self.coords)

    def __iter__(self):
        for val in self.coords:
            yield val

    def __len__(self):
        return 2

    def __repr__(self):
        return f'<Coords: {self.coords}>'

    def __hash__(self):
        return hash(self.coords)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.coords == other.coords
        else:
            return self.coords[0] == other[0] and self.coords[1] == other[1]

    def __add__(self, other):
        return self.__perform_op(operator.add, other)
    __radd__ = __add__

    def __mul__(self, other):
        return self.__perform_op(operator.mul, other)
    __rmul__ = __mul__

    def __neg__(self):
        return Coords(-self.coords[0], -self.coords[1])

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
            0,  # ↑
            90,  # ->
            180,  # ↓
            270,  # <-
        ]
    
    @staticmethod
    def get_max_spin(tile_type):
        return {
            'spinning_2': 2,
            'spinning_3': 3,
            'spinning_4': 4,
            'spinning_5': 5,
        }[tile_type]

    def __init__(self, tile_type, direction):
        self.tile_type = tile_type
        self.direction = direction
        self.is_open = False
        self.active = True
        self.objects = []
        self.can_step = get_tile_behavior(tile_type)

    def open(self):
        self.is_open = True
        pass
    
    def __repr__(self):
        return f'<Tile: {self.tile_type}>'


class GameMap:
    # Shape of the game map
    @staticmethod
    def get_map_shape():
        return Coords(13, 13)

    @staticmethod
    def is_in_bounds(coord: Coords) -> bool:
        for ax_val in coord:
            if ax_val < 0 or ax_val > 12:
                return False
        return True

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
        self.tile_images = self.load_tile_images('tile_images', self.tile_size)

    @staticmethod
    def load_tile_images(path, tile_size):
        """Load tile images from the given path and scale to the tile_size.
        """
        tile_images = {}
        tile_types = set(GameMap.__get_all_tiles())
        tile_types.update(['back', 'boat_black', 'boat_red',
                           'boat_white', 'boat_yellow'])
        for tile_type in tile_types:
            tile_image = QImage(os.path.join(path, f'{tile_type}.png'))
            tile_image = tile_image.scaled(tile_size, tile_size)
            tile_images[tile_type] = tile_image
        return tile_images

    @staticmethod
    def __is_in_water(coords):
        """Check if this coordinates are in water."""
        x, y = coords
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
        axis_centers = list(map(lambda x: int(np.floor(x / 2.0)), map_shape))
        return {
            0: Coords(0, axis_centers[1]),
            1: Coords(axis_centers[0], map_shape[1] - 1),
            2: Coords(map_shape[0] - 1, axis_centers[1]),
            3: Coords(axis_centers[0], 0),
        }[side]

    def __getitem__(self, idx):
        if isinstance(idx, Coords):
            x, y = idx
            return self.game_map[x][y]
        else:
            return self.game_map[idx]

    def __create_map(self):
        """Create a random game map.

        :return: numpy array with Tile values."""
        map_shape = GameMap.get_map_shape()
        game_map = np.empty(map_shape, dtype=Tile)
        tiles = GameMap.__get_all_tiles()
        for x in range(map_shape[0]):
            for y in range(map_shape[1]):
                # Check if this is a water tile1
                if self.__is_in_water((x, y)):
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
                game_map[x][y] = Tile(tile_type, tile_dir)

        assert len(tiles) == 0, \
            'All tiles must be used during the map creation!'
        return game_map

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

    def display_map(self, painter: QPainter):
        for coord, tile in np.ndenumerate(self.game_map):
            # TODO: Add 'water' tile image.
            if tile.tile_type == 'water':
                continue
            if tile.is_open:
                tile_img = self.tile_images[tile.tile_type]
            else:
                tile_img = self.tile_images['back']
            # Move to the center of tile, rotate, move back
            painter.translate(*self.scale_coords(Coords(*coord) + (0.5, 0.5)))
            painter.rotate(tile.direction)
            painter.drawImage(*self.scale_coords((-0.5, -0.5)), tile_img)
            painter.resetTransform()

    def display_players(self, painter: QPainter,
                        players: List[Player], cur_character: Character):

        def get_character_color(color):
            if character.ch_type == 'pirate':
                return QColor(*color_to_rgb(color))
            else:
                raise NotImplemented('The color for non pirate characters is not yet defined.')

        # Display each player's ship.
        for player in players:
            pl_boat = QImage(os.path.join('tile_images', f'boat_{player.color}.png'))
            pl_boat = pl_boat.scaled(self.tile_size, self.tile_size)
            painter.drawImage(*self.scale_coords(player.ship_coords), pl_boat)

        # Extract positions.
        positions = map_players_to_positions(players)
        # Display the characters at each position.
        for pos, characters in positions.items():
            for i, (character, ch_color) in enumerate(characters):
                ellipse_size = self.tile_size / len(characters)
                painter.save()
                painter.setBrush(QBrush(get_character_color(ch_color), Qt.SolidPattern))
                rect_pos = self.scale_coords(pos) + i * ellipse_size
                rect = QRect(*rect_pos, ellipse_size, ellipse_size)
                painter.drawEllipse(rect)
                # Display red circle if character is drunk/trapped.
                if character.state in ['drunk', 'hangover', 'trapped']:
                    painter.setBrush(Qt.NoBrush)
                    color = 'red' if character.state in ['drunk', 'trapped'] else 'orange'
                    painter.setPen(QPen(QColor(color), 15))
                    painter.drawEllipse(rect)
                # Display counter if character is on spinning tile.
                elif 'spinning' in self[pos].tile_type:
                    painter.setPen(QPen(QColor('black'), 3))
                    text = str(character.spin_counter)
                    text_br = painter.boundingRect(rect, Qt.AlignCenter, text)
                    painter.drawText(text_br, 1, text)
                # Display the glow outside the current player.
                if character is cur_character:
                    painter.setBrush(Qt.NoBrush)
                    painter.setPen(QPen(QColor(*color_to_rgb('green')), 5))
                    painter.drawEllipse(rect)
                painter.restore()

    def display_possible_turns(self, painter: QPainter, poss_turns: List[Coords]):
        for coord in poss_turns:
            painter.save()
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(*color_to_rgb('green')), 5))
            rect_size = self.tile_size
            painter.drawRect(*(self.scale_coords(coord)), rect_size, rect_size)
            painter.restore()


# @staticmethod
def color_to_rgb(game_color):
    return {
        'red': (238, 29, 35, 170),
        'white': (255, 255, 255, 170),
        'black': (35, 31, 32, 170),
        'yellow': (255, 221, 23, 170),
        'green': (127, 255, 0, 170),
    }[game_color]
