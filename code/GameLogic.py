from GameMap import GameMap
from Characters import Player


class GameLogic:
    """The main logic of the game."""

    def __init__(self, num_of_players: int):
        assert num_of_players >= 1 and num_of_players <= 4

        # Init the game map.
        self.game_map = GameMap(tile_size=64)

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
        x, y = self.game_map.unscale_coords(pos)
        self.game_map.game_map[y][x].is_open = True

    def _get_current_character(self):
        return self.players[self.cur_player].characters[self.cur_character]

    def move_character(self, direction):
        character = self._get_current_character()
        x, y = character.coords
        if direction == 'right':
            new_x, new_y = x + 1, y
        elif direction == 'left':
            new_x, new_y = x - 1, y
        elif direction == 'up':
            new_x, new_y = x, y - 1
        elif direction == 'down':
            new_x, new_y = x, y + 1
        max_vals = GameMap.get_map_shape()
        if 0 <= new_x < max_vals[0] and 0 <= new_y < max_vals[1]:
            character.move((new_x, new_y))

    def get_map_image(self):
        return self.game_map.map_to_img()

    def display_players(self, painter):
        return self.game_map.display_players(painter, self.players)

    def next_player(self):
        self.cur_player = (self.cur_player + 1) % self.num_of_players
