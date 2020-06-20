from collections import defaultdict

from code import GameMap
from code.data import Coords, Player
from code.behaviour import start_step, tile_type_to_is_final, get_possible_turns, get_tile_behavior, finish_step

from PyQt5.QtGui import QPainter


class GameLogic:
    """The main logic of the game."""

    def __init__(self, num_of_players: int, tile_size: int = 64):
        assert num_of_players >= 1 and num_of_players <= 4

        # Init the game map.
        self.game_map = GameMap(tile_size=tile_size)

        # Open all tiles. (For Debug)
        # for x in range(0, 13):
        #     for y in range(0, 13):
        #         self.game_map[y][x].open()

        # Init players.
        self.num_of_players = num_of_players
        self.move_start_coords = None
        self.moved = False
        self.cycles = None
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

    def _get_alive_characters(self):
        cur_player = self._get_current_player()
        characters = list(filter(lambda ch: ch.state == 'alive', cur_player.characters))
        if len(characters) == 0:
            self.next_player()
            return self._get_alive_characters()
        # If the counter is bigger than possible, reset it.
        if self.cur_character >= len(characters):
            self.cur_character = 0
        return characters

    def _get_current_character(self):
        characters = self._get_alive_characters()
        return characters[self.cur_character]

    def _move_character(self, coords):
        """Move the current character to the given coords.

        :param coords: coords to move to
        :return: True if some field is opened, False otherwise
        """
        # Move if inside the bounds.
        pos_turns = self._get_possible_turns()
        if (self.game_map.is_in_bounds(coords) and coords in pos_turns):
            cur_char = self._get_current_character()
            cur_player = self._get_current_player()
            prev_coords = cur_char.coords
            finish_step(self.game_map, cur_player, cur_char, coords)
            self._get_current_character().move(coords)
            is_finalized = start_step(self.game_map, self.players, cur_player, cur_char)
            # If first move and not finalized perform check for the cycle.
            if not is_finalized and not self.moved:
                cycle_starts = self.detect_cycles()
                self.cycles = {cs: False for cs in cycle_starts}
                self.move_start_coords = prev_coords
            self.moved = True
            # If on the cycle starter, increase the counter.
            if self.cycles and coords in self.cycles:
                # If stepped two times, it means that you returned back to the cycle start.
                # Terminate the character and move to the next player.
                if self.cycles[coords]:
                    cur_player.characters.remove(cur_char)
                    is_finalized = True
                else:
                    self.cycles[coords] = True
            # if turn end, switch to next player.
            if is_finalized:
                self.next_player()
            # Open corresponding tile. And return true to update the map.
            if not self.game_map[coords].is_open:
                self.game_map[coords].open()
                return True
        return False

    def detect_cycles(self):

        def _return_leaves(tree):
            """Return leaves of given tree.
            """
            res = set()
            if isinstance(tree, Coords):
                res.add(tree)
            else:
                for nodes in tree.values():
                    for node in nodes:
                        res.update(_return_leaves(node))
            return res

        def _detect_cycles(tree):
            """Detect path cycles and return the start of them.
            """
            n_cycles, cycles = 0, []
            if isinstance(tree, Coords):
                return cycles
            for coord, nodes in tree.items():
                for node in nodes:
                    leaves = _return_leaves(node)
                    # If can only return to this coord, it's a loop.
                    if coord in leaves and len(leaves) == 1:
                        n_cycles += 1
                    else:
                        cycles.extend(_detect_cycles(node))
                # If number of loops is equal to number of subtrees, this node is a start of the loop.
                if nodes and n_cycles == len(nodes):
                    cycles = [coord]
            return cycles

        path_tree, _ = self.get_path_tree()
        return _detect_cycles(path_tree)

    def get_path_tree(self, been_in=None):
        been_in = been_in or set()
        cur_char = self._get_current_character()
        # Save state.
        init_coord, init_prev = cur_char.coords, cur_char.prev_coords
        paths = defaultdict(list)
        # Get list of possible turns.
        for coord in self._get_possible_turns():
            # If not visited this tile yet, continue.
            if coord not in been_in:
                # If turn is not finalized in this tile, continue
                if not tile_type_to_is_final[self.game_map[coord].tile_type]:
                    been_in.add(coord)
                    cur_char.move(coord)
                    sub_paths, been_in = self.get_path_tree(been_in)
                    # If no sub-paths, set coord as sub-path.
                    if not sub_paths:
                        sub_paths = coord
                    paths[init_coord].append(sub_paths)
                else:
                    paths[init_coord].append(coord)
        # Restore state.
        cur_char.coords, cur_char.prev_coords = init_coord, init_prev
        return paths, been_in

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

    def pick_money(self):
        cur_char = self._get_current_character()
        cur_tile = self.game_map[cur_char.coords]
        if cur_char.object is not None:
            # If already moved, bring object to the starting tile of this move.
            if not self.moved:
                cur_tile.get_object_from(cur_char)
            else:
                self.game_map[self.move_start_coords].get_object_from(cur_char)
        elif 'money' in cur_tile.objects and cur_tile.objects['money'] > 0:
            self.game_map[cur_char.coords].objects['money'] -= 1
            cur_char.object = 'money'
        else:
            return False
        return True

    def _get_possible_turns(self):
        """Get possible turns for current character.
        """
        # Getting character can change the current player.
        cur_char = self._get_current_character()
        cur_player = self._get_current_player()

        # Get possible turns.
        args = self.game_map, self.players, cur_player, cur_char
        pos_turns = get_possible_turns(*args)
        # Accept turn only if you can step on this tile right now.
        def can_step(coord): return get_tile_behavior(self.game_map[coord].tile_type)(*args, coord)
        pos_turns = [coord for coord in pos_turns if can_step(coord)]
        return pos_turns

    def display_map(self, painter: QPainter):
        return self.game_map.display_map(painter)

    def get_map_shape(self):
        return self.game_map.scale_coords(self.game_map.get_map_shape())

    def display_objects_on_map(self, painter: QPainter):
        return self.game_map.display_objects_on_map(painter)

    def display_players(self, painter: QPainter):
        return self.game_map.display_players(painter, self.players, self._get_current_character())

    def display_possible_turns(self, painter: QPainter):
        pos_turns = self._get_possible_turns()
        return self.game_map.display_possible_turns(painter, pos_turns)

    def next_player(self):
        self.moved = False
        self.move_start_coords = None
        self.cycles = None
        self.cur_player = (self.cur_player + 1) % self.num_of_players
        cur_player = self._get_current_player()
        # Perform `start_step` for each character.
        for cur_char in cur_player.characters:
            start_step(self.game_map, self.players, cur_player, cur_char)

    def next_character(self):
        # Can move only if not yet moved.
        if not self.moved:
            characters = self._get_alive_characters()
            self.cur_character = (self.cur_character + 1) % len(characters)
