from collections import defaultdict

from GameMap import Tile

def default_start(game_map, cur_player, cur_char):
    pass


def __spinning(game_map, cur_player, cur_char):
    max_spin = Tile.get_max_spin(game_map[cur_char.coords].tile_type)
    assert cur_char.spinning_counter <= max_spin, "Spin counter can't be greater than max_spin"
    if cur_char.spinning_counter < 1:
        cur_char.spinning_counter = 1


def __drinking_rum(game_map, cur_player, cur_char):
    if cur_char.state == 'alive':
        cur_char.state = 'drunk'
    elif cur_char.state == 'drunk':
        cur_char.state = 'hangover'
    elif cur_char.state == 'hangover':
        cur_char.state = 'alive'

__tile_type_to_start = {
    'spinning_2': __spinning,
    'spinning_3': __spinning,
    'spinning_4': __spinning,
    'spinning_5': __spinning,
    'drinking_rum': __drinking_rum,
}


def start_step(game_map, cur_player, cur_char):
    tile_type_to_start = defaultdict(lambda: default_start)
    tile_type_to_start.update(__tile_type_to_start)

    tile_type = game_map[cur_char.coords].tile_type
    # Perform preliminary operations.
    tile_type_to_start[tile_type](game_map, cur_player, cur_char)
