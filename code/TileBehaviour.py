from collections import defaultdict


def __empty(game_map, cur_player, cur_char, coords):
    return True

def __water(game_map, cur_player, cur_char, coords):
    ch_coords = cur_char.coords
    cur_tile_type = game_map[ch_coords].tile_type
    return (
        cur_player.ship_coords == coords or
        'dir' in cur_tile_type or
        cur_tile_type in ['water', 'cannon', 'horses']
    )

__tile_type_to_behavior = {
    'empty': __empty,
    'water': __water,
}

def get_tile_behavior(tile_type):
    tile_type_to_behavior = defaultdict(lambda: lambda game_map, cur_player, cur_char, coord: True)
    tile_type_to_behavior.update(__tile_type_to_behavior)
    return tile_type_to_behavior[tile_type]
