# from GameMap import Coords


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
        self.spinning_counter = -1
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
