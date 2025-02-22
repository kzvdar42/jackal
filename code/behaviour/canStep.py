from collections import defaultdict

from code.data import map_players_to_positions


def default_behavior(game_map, players, cur_player, cur_char, coords):
    # If character is holding money, he can't kick others.
    if cur_char.object == 'money':
        characters = map_players_to_positions(players).get(coords, [])
        for character, pl_color in characters:
            if pl_color != cur_player.color:
                return False
    
    # Can if character is not holding money or tile is already open.
    return cur_char.object != 'money' or game_map[coords].is_open


def water(game_map, players, cur_player, cur_char, coords):
    ch_coords = cur_char.coords
    cur_tile_type = game_map[ch_coords].tile_type
    return (
        cur_player.ship_coords == coords or
        'dir' in cur_tile_type or
        cur_tile_type in ['water', 'cannon', 'horses', 'ice_lake', 'plane']
    )


def fort(game_map, players, cur_player, cur_char, coords):
    if cur_char.object is not None:
        return False
    characters = map_players_to_positions(players).get(coords, [])
    for character, pl_color in characters:
        if pl_color != cur_player.color:
            return False
    return True


__tile_type_to_behavior = {
    'empty': default_behavior,
    'water': water,
    'fort': fort,
    'aborigine': fort,
}


def get_tile_behavior(tile_type):
    tile_type_to_behavior = defaultdict(lambda: default_behavior)
    tile_type_to_behavior.update(__tile_type_to_behavior)
    return tile_type_to_behavior[tile_type]
