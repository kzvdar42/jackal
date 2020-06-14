from collections import defaultdict


def default_turns(game_map, cur_player, cur_char):
    pos_turns = []
    for y_offset in range(-1, 2):
        for x_offset in range(-1, 2):
            # Skip character coords
            if x_offset == 0 and y_offset == 0:
                continue
            x, y = cur_char.coords + (x_offset, y_offset)
            pos_turns.append((x, y))
    return pos_turns

def __water_turns(game_map, cur_player, cur_char):
    pos_turns = default_turns(game_map, cur_player, cur_char)
    pos_turns = [coord for coord in pos_turns if game_map.is_in_bounds(coord) and game_map[coord].tile_type == 'water']
    return pos_turns

def straight_offset(coords, direction):
    return coords + {
        0: (0, -1),
        90: (1, 0),
        180: (0, 1),
        270: (-1, 0),
    }[direction]

def diagonal_offset(coords, direction):
    return coords + {
        0: (1, -1),
        90: (1, 1),
        180: (-1, 1),
        270: (-1, -1),
    }[direction]

def __dir_straight_turns(game_map, cur_player, cur_char):
    ch_coords = cur_char.coords
    return [straight_offset(ch_coords, game_map[ch_coords].direction)]

def __dir_0_180_turns(game_map, cur_player, cur_char):
    ch_coords = cur_char.coords
    pos_turns = []
    for angle in (0, 180):
        direction = (game_map[ch_coords].direction + angle) % 360
        pos_turns.append(straight_offset(ch_coords, direction))
    return pos_turns

def __dir_uplr_turns(game_map, cur_player, cur_char):
    pos_turns = []
    for direction in (0, 90, 180, 270):
        pos_turns.append(straight_offset(cur_char.coords, direction))
    return pos_turns

def __dir_45_turns(game_map, cur_player, cur_char):
    ch_coords = cur_char.coords
    return [diagonal_offset(ch_coords, game_map[ch_coords].direction)]

def __dir_45_225_turns(game_map, cur_player, cur_char):
    ch_coords = cur_char.coords
    pos_turns = []
    for angle in (0, 180):
        direction = (game_map[ch_coords].direction + angle) % 360
        pos_turns.append(diagonal_offset(ch_coords, direction))
    return pos_turns

def __dir_diagonal_turns(game_map, cur_player, cur_char):
    pos_turns = []
    for direction in (0, 90, 180, 270):
        pos_turns.append(diagonal_offset(cur_char.coords, direction))
    return pos_turns

def __dir_0_135_270_turn(game_map, cur_player, cur_char):
    ch_coords = cur_char.coords
    pos_turns = []
    direction = game_map[ch_coords].direction
    pos_turns.append(straight_offset(ch_coords, direction))
    direction = (direction + 90) % 360
    pos_turns.append(diagonal_offset(ch_coords, direction))
    direction = (direction + 180) % 360
    pos_turns.append(straight_offset(ch_coords, direction))
    return pos_turns

def __baloon_turn(game_map, cur_player, cur_char):
    return [cur_player.ship_coords]

def __plane_turn(game_map, cur_player, cur_char):
    pos_turns = []
    # TODO: Make this behavior one time only.
    # TODO: Add all tiles, not only the ones which `can_step` returns True.
    for x in range(0, 13):
        for y in range(0, 13):
            pos_turns.append((x, y))
    return pos_turns

def __cannon_turn(game_map, cur_player, cur_char):
    cur_coords = cur_char.coords.copy()
    direction = game_map[cur_coords].direction
    if direction == 0:
        cur_coords[1] = 0
    elif direction == 180:
        cur_coords[1] = 12
    elif direction == 90:
        cur_coords[0] = 12
    elif direction == 270:
        cur_coords[0] = 0
    return [cur_coords]

def __crocodile_turns(game_map, cur_player, cur_char):
    return [cur_char.prev_coords]

def __ice_lake_turns(game_map, cur_player, cur_char):
    diff = cur_char.coords - cur_char.prev_coords
    return [cur_char.coords + diff]

def __horses_turns(game_map, cur_player, cur_char):
    pos_turns = [(-1, -2), (-2, -1), (-1, 2), (2, -1), (1, -2), (-2, 1), (1, 2), (2, 1)]
    pos_turns = [cur_char.coords + offset for offset in pos_turns]
    return pos_turns

__tile_type_to_turns = {
    'water': __water_turns,
    'dir_straight': __dir_straight_turns,
    'dir_0_180': __dir_0_180_turns,
    'dir_uplr': __dir_uplr_turns,
    'dir_45': __dir_45_turns,
    'dir_45_225': __dir_45_225_turns,
    'dir_diagonal': __dir_diagonal_turns,
    'dir_0_135_270': __dir_0_135_270_turn,
    'baloon': __baloon_turn,
    'plane': __plane_turn,
    'cannon': __cannon_turn,
    'crocodile': __crocodile_turns,
    'ice_lake': __ice_lake_turns,
    'horses': __horses_turns,
}

def get_possible_turns(tile_type, game_map, cur_player, cur_char):
    tile_type_to_turns = defaultdict(lambda: default_turns)
    tile_type_to_turns.update(__tile_type_to_turns)

    pos_turns = tile_type_to_turns[tile_type](game_map, cur_player, cur_char)
    # Accept turn only if it in map bounds.
    pos_turns = [coord for coord in pos_turns if game_map.is_in_bounds(coord)]
    # Accept turn only if you can step on this tile right now.
    pos_turns = [coord for coord in pos_turns if game_map[coord].can_step(game_map, cur_player, cur_char, coord)]
    return pos_turns
