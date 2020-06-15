from collections import defaultdict


class Character:
    """Game character.
    Possible `ch_types` are: `pirate`.
    """

    @staticmethod
    def possible_states():
        return [
            'alive',
            'drunk',
            'hangover',
            'trapped',
        ]

    def __init__(self, coords, ch_type: str):
        self.coords = coords
        self.ch_type = ch_type
        self.state = 'alive'
        self.spin_counter = -1
        self.prev_coords = coords

    def move(self, coords):
        self.prev_coords = self.coords
        self.coords = coords


class Player:
    """Game player."""

    @staticmethod
    def _get_possible_colors():
        return [
            'red',
            'white',
            'black',
            'yellow',
        ]

    def __init__(self, color, start_coords, side):
        self.color = color
        self.side = side
        self.ship_coords = start_coords
        self.characters = [Character(start_coords, ch_type='pirate')
                           for _ in range(3)]
    
    def add_character(self, start_coords, ch_type):
        self.characters.append(Character(start_coords, ch_type))


# @staticmethod
def map_players_to_positions(players):
    # TODO: Find a better way to understand if players are on the same tile.
    positions = defaultdict(list)
    for player in players:
        for character in player.characters:
            positions[character.coords].append((character, player.color))
    return positions
