from collections import defaultdict

from GameMap import Tile
from Characters import map_players_to_positions

def default_start(game_map, players, cur_player, cur_char):
    characters = map_players_to_positions(players).get(cur_char.coords)
    cl_to_player = {pl.color:pl for pl in players}
    for character, pl_color in characters:
        if pl_color != cur_player.color:
            character.coords = cl_to_player[pl_color].ship_coords

def continue_step(game_map, players, cur_player, cur_char):
    default_start(game_map, players, cur_player, cur_char)
    return False

def stop_step(game_map, players, cur_player, cur_char):
    default_start(game_map, players, cur_player, cur_char)
    return True

def __spinning(game_map, players, cur_player, cur_char):
    max_spin = Tile.get_max_spin(game_map[cur_char.coords].tile_type)
    assert cur_char.spin_counter <= max_spin, "Spin counter can't be greater than max_spin"
    if cur_char.spin_counter < 1:
        cur_char.spin_counter = 1
    # Move other players on the same spin subtile to their ship.
    characters = map_players_to_positions(players).get(cur_char.coords)
    cl_to_player = {pl.color:pl for pl in players}
    for character, pl_color in characters:
        if character.spin_counter == cur_char.spin_counter and pl_color != cur_player.color:
            character.coords = cl_to_player[pl_color].ship_coords
    return True


def __drinking_rum(game_map, players, cur_player, cur_char):
    if cur_char.state == 'alive' and cur_char.prev_coords != cur_char.coords:
        cur_char.state = 'drunk'
    elif cur_char.state == 'drunk':
        cur_char.state = 'hangover'
    elif cur_char.state == 'hangover':
        cur_char.state = 'alive'
        cur_char.prev_coords = cur_char.coords
    return True

def __ogre(game_map, players, cur_player, cur_char):
    cur_player.characters.remove(cur_char)
    return True

def __aborigine(game_map, players, cur_player, cur_char):
    if len(cur_player.characters) < 3:
        cur_player.add_character(cur_char.coords, ch_type='pirate')
    return True

def __trap(game_map, players, cur_player, cur_char):
    characters = map_players_to_positions(players).get(cur_char.coords)
    is_smn_trapped = any(map(lambda x: x[0].state == 'trapped' and x[0] != cur_char, characters))
    cl_to_player = {pl.color:pl for pl in players}
    for character, pl_color in characters:
        # Skip current character.
        if character  == cur_char:
            continue
        # Untrap all other characters.
        character.state = 'alive'
        character.prev_coords = cur_char.coords
        # If other player kick him.
        if pl_color != cur_player.color:
            character.coords = cl_to_player[pl_color].ship_coords
    # If noone was trapped, you get trapped.
    if not is_smn_trapped and cur_char.prev_coords != cur_char.coords:
        cur_char.state = 'trapped'
    else:
        cur_char.state = 'alive'
        cur_char.prev_coords = cur_char.coords
    return True


def __water(game_map, players, cur_player, cur_char):
    characters = map_players_to_positions(players).get(cur_char.coords)
    cl_to_player = {pl.color:pl for pl in players}
    players = players.copy()
    players.remove(cl_to_player[cur_player.color])
    # If character is in the other player's ship, kill him.
    if cur_char.coords in map(lambda pl: pl.ship_coords, players):
        cur_player.characters.remove(cur_char)
    # If other players are on the same tile, kill them.
    else:
        for character, pl_color in characters:
            if pl_color != cur_player.color:
                cl_to_player[pl_color].characters.remove(character)
    return True


__tile_type_to_start = {
    'spinning_2': __spinning,
    'spinning_3': __spinning,
    'spinning_4': __spinning,
    'spinning_5': __spinning,
    'drinking_rum': __drinking_rum,
    'ogre': __ogre,
    'aborigine': __aborigine,
    'trap': __trap,
    'water': __water,
    'dir_straight': continue_step,
    'dir_0_180': continue_step,
    'dir_uplr': continue_step,
    'dir_45': continue_step,
    'dir_45_225': continue_step,
    'dir_diagonal': continue_step,
    'dir_0_135_270': continue_step,
    'ice_lake': continue_step,
    'horses': continue_step,
    'cannon': continue_step,
    'crocodile': continue_step,
    'baloon': continue_step,
}


tile_type_to_start = defaultdict(lambda: stop_step)
tile_type_to_start.update(__tile_type_to_start)


def start_step(game_map, players, cur_player, cur_char):
    tile_type = game_map[cur_char.coords].tile_type
    # Perform preliminary operations.
    return tile_type_to_start[tile_type](game_map, players, cur_player, cur_char)
