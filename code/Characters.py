from GameMap import get_side_center_coords


class Character:
    """Game character.
    Possible `ch_types` are: `pirate`.
    """

    def __init__(self, coords, ch_type):
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

    def __init__(self, color, side):
        self.color = color
        self.corner = side
        start_coords = get_side_center_coords(side)
        self.characters = [Character(start_coords, ch_type='pirate')
                           for _ in range(3)]
