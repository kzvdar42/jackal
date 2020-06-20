from collections import Counter, defaultdict


__objects_on_open = {
    'money_1': {'money': 1},
    'money_2': {'money': 2},
    'money_3': {'money': 3},
    'money_4': {'money': 4},
    'money_5': {'money': 5},
}

objects_on_open = defaultdict(dict)
objects_on_open.update(__objects_on_open)


class Tile:

    @staticmethod
    def get_tile_dirs():
        """Tile direction format."""
        return [  # TODO: change to a more readable format ('left', 'right', etc.)
            0,  # ↑
            90,  # ->
            180,  # ↓
            270,  # <-
        ]

    @staticmethod
    def get_max_spin(tile_type):
        return {
            'spinning_2': 2,
            'spinning_3': 3,
            'spinning_4': 4,
            'spinning_5': 5,
        }[tile_type]

    def __init__(self, tile_type, direction):
        self.tile_type = tile_type
        self.direction = direction
        self.is_open = False
        self.objects = Counter()
        self.active = True

    def open(self):
        self.is_open = True
        self.objects.update(objects_on_open[self.tile_type])
        pass

    def add_object(self, object: str):
        if object:
            self.objects.update([object])

    def get_object_from(self, character):
        if character.object is not None:
            self.objects.update([character.object])
        character.object = None

    def __repr__(self):
        return f'<Tile: {self.tile_type}>'
