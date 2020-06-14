from GameMap import GameMap, Coords
from Characters import Player
from TileTurns import get_possible_turns

from PyQt5.QtGui import QPainter


class GameLogic:
    """The main logic of the game."""

    def __init__(self, num_of_players: int, tile_size:int=64):
        assert num_of_players >= 1 and num_of_players <= 4

        # Init the game map.
        self.game_map = GameMap(tile_size=tile_size)

        # Open all tiles. (For Debug)
        # for x in range(0, 13):
        #     for y in range(0, 13):
        #         self.game_map[y][x].is_open = True

        # Init players.
        self.num_of_players = num_of_players
        self.cur_player = 0
        self.cur_character = 0
        self.players = []
        colors = Player._get_possible_colors()  # TODO: Shuffle colors?
        for i in range(num_of_players):
            start_coords = self.game_map.get_side_center_coords(side=i)
            self.players.append(Player(colors[i], start_coords, side=i))

    def mouse_click(self, pos):
        mouse_coords = self.game_map.unscale_coords(pos)
        return self._move_character(mouse_coords)

    def _get_current_player(self):
        return self.players[self.cur_player]

    def _get_current_character(self):
        return self._get_current_player().characters[self.cur_character]

    def _move_character(self, coords):
        """Move the current character to the given coords.

        :param coords: coords to move to
        :return: True if some field is opened, False otherwise
        """
        # Move if inside the bounds.
        max_vals = GameMap.get_map_shape()
        pos_turns = self._get_possible_turns()
        if (0 <= coords[0] < max_vals[0] and
            0 <= coords[1] < max_vals[1] and
                coords in pos_turns):
            self._get_current_character().move(coords)
            if not self.game_map[coords].is_open:
                # Open corresponding tile. And return true to update the map.
                self.game_map[coords].is_open = True
                return True
        return False

    def move_character(self, direction):
        """Move the current character ingiven direction.

        :param direction: one of ('right', 'left', 'up', 'down')
        :return: True if some field is opened, False otherwise
        """
        coords = self._get_current_character().coords
        if direction == 'right':
            coords += (1, 0)
        elif direction == 'left':
            coords += (-1, 0)
        elif direction == 'up':
            coords += (0, -1)
        elif direction == 'down':
            coords += (0, 1)
        return self._move_character(coords)

    def _get_possible_turns(self):
        """Get possible turns for current character.
        """
        cur_player = self._get_current_player()
        cur_char = self._get_current_character()
        ch_coords = cur_char.coords

        # If on the ship, can move only forward.
        # TODO: Handle ship movement.
        if ch_coords == cur_player.ship_coords:
            return [ch_coords + {
                        0: (1, 0),
                        1: (0, -1),
                        2: (-1, 0),
                        3: (0, 1)
                    }[cur_player.side]]
        tile_type = self.game_map[ch_coords].tile_type
        pos_turns = get_possible_turns(tile_type, self.game_map, cur_player, cur_char)
        return pos_turns

    def display_map(self, painter: QPainter):
        return self.game_map.display_map(painter)
    
    def get_map_shape(self):
        return self.game_map.scale_coords(self.game_map.get_map_shape())

    def display_players(self, painter: QPainter):
        return self.game_map.display_players(painter, self.players, self._get_current_character())

    def display_possible_turns(self, painter: QPainter):
        pos_turns = self._get_possible_turns()
        return self.game_map.display_possible_turns(painter, pos_turns)

    def next_player(self):
        self.cur_player = (self.cur_player + 1) % self.num_of_players
