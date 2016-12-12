import random

from .tilecolor import TileColor
from .neotiles import TileSize, TilePosition


class TileHandler:
    # TODO: replace size getter with num_cols and num_rows
    """

    :param size:
    """
    def __init__(self):
        self._data = None
        self._default_color = TileColor(
            red=random.random(),
            green=random.random(),
            blue=random.random(),
            white=random.random()
        )

        self._size = TileSize(1, 1)
        self._init_pixels()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = TileSize(*value)
        self._init_pixels()

    @property
    def pixels(self):
        return self._pixels

    def _init_pixels(self, color=None):
        # A two-dimension array of pixel colors for the tile.
        display_color = self._default_color if color is None else color

        self._pixels = [
            [display_color for col in range(self._size.cols)]
            for row in range(self._size.rows)
        ]

    def data(self, in_data):
        self._data = in_data

    def clear(self):
        self._init_pixels(color=TileColor(0, 0, 0, 0))

    def set_pixel(self, pos, color):
        """

        :param pos: (TilePos)
        :param color:
        :return:
        """
        # Our pixel matrix is indexed by row number first, then column within
        # the row.
        pos = TilePosition(*pos)
        self._pixels[pos.y][pos.x] = color

