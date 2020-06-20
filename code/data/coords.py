from collections.abc import Iterable
import operator


class Coords(Iterable):
    """Class for coords and math associated with them."""

    def __init__(self, x, y):
        self.coords = x, y

    def __perform_op(self, operation, other, inplace=False, from_right=False):
        x, y = self.coords
        if not isinstance(other, Iterable):
            other = (other, other)
        if from_right:
            x, y, other = *other, (x, y)
        # TODO: Better comment for the assert.
        assert len(other) == 2, "Length should be two."
        x = operation(x, other[0])
        y = operation(y, other[1])
        if inplace:
            self.coords = x, y
        return Coords(x, y)

    def get_coords(self):
        return self.coords

    def set_coords(self, x, y):
        self.coords = x, y

    def __getitem__(self, idx):
        return self.coords[idx]

    def __setitem__(self, idx, value):
        new_coords = list(self.coords)
        new_coords[idx] = value
        self.coords = tuple(new_coords)

    def copy(self):
        return Coords(*self.coords)

    def __iter__(self):
        for val in self.coords:
            yield val

    def __len__(self):
        return 2

    def __repr__(self):
        return f'<Coords: {self.coords}>'

    def __hash__(self):
        return hash(self.coords)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.coords == other.coords
        else:
            return self.coords[0] == other[0] and self.coords[1] == other[1]

    def __add__(self, other):
        return self.__perform_op(operator.add, other)
    __radd__ = __add__

    def __mul__(self, other):
        return self.__perform_op(operator.mul, other)
    __rmul__ = __mul__

    def __neg__(self):
        return Coords(-self.coords[0], -self.coords[1])

    def __sub__(self, other):
        return self.__perform_op(operator.sub, other)

    def __rsub__(self, other):
        return self.__perform_op(operator.sub, other, from_right=True)

    def __floordiv__(self, other):
        return self.__perform_op(operator.floordiv, other)

    def __rfloordiv__(self, other):
        return self.__perform_op(operator.floordiv, other, from_right=True)


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
