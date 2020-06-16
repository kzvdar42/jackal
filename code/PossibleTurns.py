from collections import defaultdict

from GameMap import Tile, Coords


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


def direction_offset(coords, side, direction):
    offset = Coords(*{  # by default forward
        0: (1, 0),
        1: (0, -1),
        2: (-1, 0),
        3: (0, 1)
    }[side])
    if direction == 'backwards':
        offset = -offset
    elif direction == 'left':
        offset = Coords(*(reversed(offset)))
    elif direction == 'right':
        offset = Coords(*reversed(-offset))
    elif direction != 'forward':
        raise ValueError('Unknown direction')
    return coords + offset


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


def water(game_map, cur_player, cur_char):
    # If on the ship, can move only forward or left/right with the ship.
    cur_coords, pl_side = cur_char.coords, cur_player.side
    if cur_coords == cur_player.ship_coords:
        res = [direction_offset(cur_coords, pl_side, 'forward')]
        # Can move left/right till ship will be on the shore.
        left = direction_offset(cur_coords, pl_side, 'left')
        if game_map[direction_offset(left, pl_side, 'forward')].tile_type != 'water':
            res.append(left)
        right = direction_offset(cur_coords, pl_side, 'right')
        if game_map[direction_offset(right, pl_side, 'forward')].tile_type != 'water':
            res.append(right)
        return res
    pos_turns = default_turns(game_map, cur_player, cur_char)
    pos_turns = [coord for coord in pos_turns if game_map.is_in_bounds(coord) and game_map[coord].tile_type == 'water']
    return pos_turns


def dir_straight(game_map, cur_player, cur_char):
    ch_coords = cur_char.coords
    return [straight_offset(ch_coords, game_map[ch_coords].direction)]


def dir_0_180(game_map, cur_player, cur_char):
    ch_coords = cur_char.coords
    pos_turns = []
    for angle in (0, 180):
        direction = (game_map[ch_coords].direction + angle) % 360
        pos_turns.append(straight_offset(ch_coords, direction))
    return pos_turns


def dir_uplr(game_map, cur_player, cur_char):
    pos_turns = []
    for direction in (0, 90, 180, 270):
        pos_turns.append(straight_offset(cur_char.coords, direction))
    return pos_turns


def dir_45(game_map, cur_player, cur_char):
    ch_coords = cur_char.coords
    return [diagonal_offset(ch_coords, game_map[ch_coords].direction)]


def dir_45_225(game_map, cur_player, cur_char):
    ch_coords = cur_char.coords
    pos_turns = []
    for angle in (0, 180):
        direction = (game_map[ch_coords].direction + angle) % 360
        pos_turns.append(diagonal_offset(ch_coords, direction))
    return pos_turns


def dir_diagonal(game_map, cur_player, cur_char):
    pos_turns = []
    for direction in (0, 90, 180, 270):
        pos_turns.append(diagonal_offset(cur_char.coords, direction))
    return pos_turns


def dir_0_135_270(game_map, cur_player, cur_char):
    ch_coords = cur_char.coords
    pos_turns = []
    direction = game_map[ch_coords].direction
    pos_turns.append(straight_offset(ch_coords, direction))
    direction = (direction + 90) % 360
    pos_turns.append(diagonal_offset(ch_coords, direction))
    direction = (direction + 180) % 360
    pos_turns.append(straight_offset(ch_coords, direction))
    return pos_turns


def baloon(game_map, cur_player, cur_char):
    return [cur_player.ship_coords]


def plane(game_map, cur_player, cur_char):
    if not game_map[cur_char.coords].active:
        return default_turns(game_map, cur_player, cur_char)
    pos_turns = []
    for x in range(0, 13):
        for y in range(0, 13):
            pos_turns.append((x, y))
    return pos_turns


def cannon(game_map, cur_player, cur_char):
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


def crocodile(game_map, cur_player, cur_char):
    return [cur_char.prev_coords]


def ice_lake(game_map, cur_player, cur_char):
    diff = cur_char.coords - cur_char.prev_coords
    return [cur_char.coords + diff]


def horses(game_map, cur_player, cur_char):
    pos_turns = [(-1, -2), (-2, -1), (-1, 2), (2, -1),
                 (1, -2), (-2, 1), (1, 2), (2, 1)]
    pos_turns = [cur_char.coords + offset for offset in pos_turns]
    return pos_turns


def spinning(game_map, cur_player, cur_char):
    max_spin = Tile.get_max_spin(game_map[cur_char.coords].tile_type)
    if cur_char.spin_counter >= max_spin:
        return default_turns(game_map, cur_player, cur_char)
    return [cur_char.coords]


def drinking_rum(game_map, cur_player, cur_char):
    if cur_char.state == 'alive':
        return default_turns(game_map, cur_player, cur_char)
    return []


def trap(game_map, cur_player, cur_char):
    if cur_char.state == 'alive':
        return default_turns(game_map, cur_player, cur_char)
    return []


__tile_type_to_turns = {
    'water': water,
    'dir_straight': dir_straight,
    'dir_0_180': dir_0_180,
    'dir_uplr': dir_uplr,
    'dir_45': dir_45,
    'dir_45_225': dir_45_225,
    'dir_diagonal': dir_diagonal,
    'dir_0_135_270': dir_0_135_270,
    'baloon': baloon,
    'plane': plane,
    'cannon': cannon,
    'crocodile': crocodile,
    'ice_lake': ice_lake,
    'horses': horses,
    'spinning_2': spinning,
    'spinning_3': spinning,
    'spinning_4': spinning,
    'spinning_5': spinning,
    'drinking_rum': drinking_rum,
    'trap': trap,
}


tile_type_to_turns = defaultdict(lambda: default_turns)
tile_type_to_turns.update(__tile_type_to_turns)


def get_possible_turns(game_map, players, cur_player, cur_char):
    tile_type = game_map[cur_char.coords].tile_type
    # Get the list of possible turns.
    pos_turns = tile_type_to_turns[tile_type](game_map, cur_player, cur_char)
    # XXX: Force turns into Coords format.
    pos_turns = [Coords(*coords) for coords in pos_turns]
    # Accept turn only if it in map bounds.
    pos_turns = [coord for coord in pos_turns if game_map.is_in_bounds(coord)]
    # Accept turn only if you can step on this tile right now.
    pos_turns = [coord for coord in pos_turns if game_map[coord].can_step(game_map, players, cur_player, cur_char, coord)]
    return pos_turns
