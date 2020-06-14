from collections import defaultdict

from GameMap import Tile

def default_end(game_map, cur_player, cur_char):
    pass

def __spinning(game_map, cur_player, cur_char):
    max_spin = Tile.get_max_spin(game_map[cur_char.coords].tile_type)
    if cur_char.spinning_counter < max_spin:
        cur_char.spinning_counter += 1
    else:
        cur_char.spinning_counter = -1

def __plane(game_map, cur_player, cur_char):
    plane_tile = game_map[cur_char.coords]
    if plane_tile.active:
        plane_tile.active = False

__tile_type_to_step = {
    'spinning_2': __spinning,
    'spinning_3': __spinning,
    'spinning_4': __spinning,
    'spinning_5': __spinning,
    'plane': __plane,
}


def finish_step(game_map, cur_player, cur_char):
    tile_type_to_step = defaultdict(lambda: default_end)
    tile_type_to_step.update(__tile_type_to_step)

    tile_type = game_map[cur_char.coords].tile_type
    tile_type_to_step[tile_type](game_map, cur_player, cur_char)
