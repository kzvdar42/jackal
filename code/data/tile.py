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
        self.active = True
        self.objects = []

    def open(self):
        self.is_open = True
        pass

    def __repr__(self):
        return f'<Tile: {self.tile_type}>'