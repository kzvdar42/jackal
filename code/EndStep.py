from collections import defaultdict

from GameMap import Tile


def default_end(game_map, cur_player, cur_char, coords):
    pass


def spinning(game_map, cur_player, cur_char, coords):
    max_spin = Tile.get_max_spin(game_map[cur_char.coords].tile_type)
    if cur_char.spin_counter < max_spin:
        cur_char.spin_counter += 1
    else:
        cur_char.spin_counter = -1


def plane(game_map, cur_player, cur_char, coords):
    plane_tile = game_map[cur_char.coords]
    if plane_tile.active:
        plane_tile.active = False


def water(game_map, cur_player, cur_char, coords):
    cur_coords = cur_char.coords
    # If want to move the ship, move everyone on it.
    if cur_coords == cur_player.ship_coords and game_map[coords].tile_type == 'water':
        cur_player.ship_coords = coords
        for char in cur_player.characters:
            if char.coords == cur_coords:
                char.move(coords)


__tile_type_to_step = {
    'spinning_2': spinning,
    'spinning_3': spinning,
    'spinning_4': spinning,
    'spinning_5': spinning,
    'plane': plane,
    'water': water,
}


tile_type_to_step = defaultdict(lambda: default_end)
tile_type_to_step.update(__tile_type_to_step)


def finish_step(game_map, cur_player, cur_char, coords):
    tile_type = game_map[cur_char.coords].tile_type
    tile_type_to_step[tile_type](game_map, cur_player, cur_char, coords)
