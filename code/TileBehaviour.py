from collections import defaultdict


def __empty(game_map, cur_player, cur_char, coords):
    return True

def __water(game_map, cur_player, cur_char, coords):
    x, y = cur_char.coords
    if cur_player.ship_coords == coords:
        return True
    elif 'dir' in game_map[y][x].tile_type:
        return True
    elif game_map[y][x].tile_type == 'water':
        return True
    return False

__tile_type_to_behavior = {
    'empty': __empty,
    'water': __water,
}

def get_tile_behavior(tile_type):
    tile_type_to_behavior = defaultdict(lambda: lambda game_map, cur_player, cur_char, coord: True)
    tile_type_to_behavior.update(__tile_type_to_behavior)
    return tile_type_to_behavior[tile_type]
