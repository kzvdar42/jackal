# from GameMap import Coords


class Character:
    """Game character.
    Possible `ch_types` are: `pirate`.
    """

    def __init__(self, coords, ch_type: str):
        self.coords = coords
        self.ch_type = ch_type

    def move(self, coords):
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
